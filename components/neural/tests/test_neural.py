# BEACON COMPUTING INITIATIVE | Orbital Neural Core
# Developer Seal: CJB-DEV-2026
# File SHA-256: SHA256SUMS
"""Positive and negative tests for learning, trust, provenance, correlation."""
from __future__ import annotations
from datetime import datetime,timezone,timedelta
import json
import os
from pathlib import Path
import random
import sqlite3
import sys
import tempfile
import unittest
from bci_neural.common import FEATURES,canonical,digest,file_digest,load_jsonl,window,verify_sidecar,write_hashed
from bci_neural.journal import append,verify,freeze
from bci_neural.model import score,train,validate_model
from bci_neural.reason import correlate
from bci_neural.sources import legacy_export,snapshot_window,installed_sensor_module
from bci_neural.cli import stats,cli

START=(datetime.now(timezone.utc)-timedelta(days=12)).replace(microsecond=0)

def row(i=0,context='ctx-test',trust='unreviewed_live'):
    f=dict.fromkeys(FEATURES,0)
    f.update({'process_count':120+(i%7),'listener_count':12+i%3,'outbound_count':3+i%2,
              'remote_unique_count':2,'inbound_count':i%3,'rx_kib_per_second':7+i%3,
              'tx_kib_per_second':5+i%2})
    return window(context,(START+timedelta(hours=3*i)).isoformat(),f,trust,
                  {'network','listener','process','storage'})


def ev(kind,minutes,source='sensor-a',process_key='A/123',host='h1',context='ctx-test',event_id=None):
    return {'kind':kind,'ts':(START+timedelta(minutes=minutes)).isoformat(),
            'source':source,'event_id':event_id or kind+str(minutes),'process_key':process_key,
            'host':host,'context':context}

class NeuralTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir=Path(self.tmp.name)

    def test_window_validates(self):
        self.assertEqual(row()['features']['process_count'],120)

    def test_window_nan_rejected(self):
        r=row();r['features']['process_count']=float('nan')
        from bci_neural.common import validate_window
        with self.assertRaises(ValueError):validate_window(r)

    def test_window_unknown_feature_rejected(self):
        r=row();r['features']['not_in_schema']=1
        from bci_neural.common import validate_window
        with self.assertRaises(ValueError):validate_window(r)

    def test_no_future_timestamp(self):
        r=row();r['ts']=(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()
        from bci_neural.common import validate_window
        with self.assertRaises(ValueError):validate_window(r)

    def test_hashed_file_and_tamper(self):
        f=self.dir/'report.json'
        write_hashed(f,{'seal':'CJB-DEV-2026'})
        self.assertEqual(verify_sidecar(f),file_digest(f))
        f.write_text('changed')
        with self.assertRaises(ValueError):verify_sidecar(f)

    def test_no_artifact_overwrite(self):
        f=self.dir/'x.json';write_hashed(f,{'x':1})
        with self.assertRaises(FileExistsError):write_hashed(f,{'x':2})

    def test_journal_chain_freeze(self):
        f=self.dir/'journal';append(f,row(0));append(f,row(1))
        n,head,rows=verify(f)
        self.assertEqual(n,2)
        out=self.dir/'frozen.jsonl'
        report=freeze(f,out)
        self.assertEqual(report['journal_head_sha256'],head)
        self.assertEqual(len(load_jsonl(out)),2)
        self.assertEqual(verify_sidecar(out),file_digest(out))

    def test_journal_tamper_detected(self):
        f=self.dir/'journal';append(f,row(0))
        f.write_text(f.read_text().replace('ctx-test','ctx-evil'))
        with self.assertRaises(ValueError):verify(f)
        with self.assertRaises(ValueError):append(f,row(1))

    def test_qualified_stats_gate(self):
        s=stats([row(i) for i in range(80)],'ctx-test')
        self.assertTrue(s['ready_for_operator_training_review'])
        self.assertGreaterEqual(s['span_days'],7)

    def test_early_stats_hold(self):
        s=stats([row(i) for i in range(8)],'ctx-test')
        self.assertFalse(s['ready_for_operator_training_review'])

    def test_train_and_score(self):
        rows=[row(i) for i in range(85)]
        m=train(rows,'ctx-test','approval-test',seed=440,epochs=12)
        self.assertTrue(validate_model(m))
        normal=score(m,row(84))
        self.assertEqual(normal['context'],'ctx-test')
        abnormal=row(84);abnormal['features']['outbound_count']=1000
        anomaly=score(m,abnormal)
        self.assertTrue(anomaly['candidate_anomaly'])
        self.assertGreater(anomaly['anomaly_score_mse'],normal['anomaly_score_mse'])
        self.assertEqual(m['model_state'],'candidate_unpromoted')

    def test_context_mismatch_denied(self):
        m=train([row(i) for i in range(80)],'ctx-test','approval-test',epochs=1)
        with self.assertRaises(ValueError):score(m,row(1,'ctx-other'))

    def test_no_mixed_context_train(self):
        with self.assertRaises(ValueError):train([row(i) for i in range(79)]+[row(80,'ctx-other')], 'ctx-test','approval-test',epochs=1)

    def test_invalid_model_weights(self):
        m=train([row(i) for i in range(80)],'ctx-test','approval-test',epochs=1)
        m['layers'][0]['w'][0][0]=float('nan')
        with self.assertRaises(ValueError):validate_model(m)

    def test_correlates_same_process_two_sensors(self):
        res=correlate([ev('file_read',0),ev('outbound',3,source='net')])
        self.assertEqual(len(res['hypotheses']),1)
        self.assertEqual(res['hypotheses'][0]['rule_id'],'file-read-followed-by-outbound')
        self.assertFalse(res['automatic_containment_authorized'])

    def test_no_correlation_on_different_host(self):
        res=correlate([ev('file_read',0),ev('outbound',3,source='net',host='other')])
        self.assertFalse(res['hypotheses'])

    def test_no_correlation_on_different_context(self):
        res=correlate([ev('file_read',0),ev('outbound',3,source='net',context='ctx-other')])
        self.assertFalse(res['hypotheses'])

    def test_no_correlation_without_process_key(self):
        res=correlate([ev('file_read',0,process_key=None),ev('outbound',3,source='net',process_key=None)])
        self.assertFalse(res['hypotheses'])

    def test_no_correlation_one_sensor(self):
        res=correlate([ev('file_read',0),ev('outbound',3)])
        self.assertFalse(res['hypotheses'])

    def test_no_correlation_reversed_order(self):
        res=correlate([ev('file_read',6),ev('outbound',3,source='net')])
        self.assertFalse(res['hypotheses'])

    def test_usb_cooccurrence_is_weak(self):
        res=correlate([ev('usb_mount',0),ev('outbound',3,source='net')])
        self.assertEqual(res['hypotheses'][0]['classification'],'weak_cooccurrence_only')

    def test_snapshot_no_raw_addresses(self):
        snap={'context':'ctx-123','processes':[{'exe':'/bin/bash'}],
              'sockets':[{'state':'ESTAB','peer_ip':'8.8.8.8','peer_port':443,'local_port':58000}],
              'usb_mounts':[],'visibility_issues':[]}
        x=snapshot_window(snap)
        self.assertEqual(x['features']['outbound_count'],1)
        self.assertNotIn('8.8.8.8',canonical(x))

    def test_snapshot_unknown_context_hold(self):
        with self.assertRaises(ValueError):snapshot_window({'context':'ctx-unknown'})

    def test_legacy_export_keeps_profiles_untrusted(self):
        src=self.dir/'evidence.sqlite'
        db=sqlite3.connect(src)
        db.execute('CREATE TABLE baseline_observations(event_id TEXT,profile_id TEXT,host TEXT,time TEXT,feature TEXT,value TEXT)')
        ts=START.isoformat()
        raw=canonical({'protocol':'tcp','remote_ip':'203.0.113.24','remote_port':8443})
        db.execute('INSERT INTO baseline_observations VALUES(?,?,?,?,?,?)',('id','network-one','host',ts,'outbound.peer',raw))
        db.execute('INSERT INTO baseline_observations VALUES(?,?,?,?,?,?)',('id2','network-two','host',ts,'outbound.peer',raw))
        db.commit();db.close()
        rows,report=legacy_export(src)
        self.assertEqual(len(rows),2)
        self.assertEqual(report['profile_count'],2)
        self.assertTrue(all(r['trust']=='untrusted_legacy' for r in rows))
        self.assertNotIn('203.0.113.24',canonical(rows))

    def test_legacy_export_missing_schema_hold(self):
        src=self.dir/'evidence.sqlite'
        db=sqlite3.connect(src);db.execute('CREATE TABLE other(x TEXT)');db.close()
        with self.assertRaises(ValueError):legacy_export(src)

    def test_cli_training_requires_approval(self):
        inp=self.dir/'data.jsonl'
        data=('\n'.join(canonical(row(i)) for i in range(80))+'\n').encode()
        write_hashed(inp,data)
        with self.assertRaises(ValueError):
            cli(['train','--input',str(inp),'--context','ctx-test','--approval',str(self.dir/'missing.json'),
                 '--output',str(self.dir/'model.json')])

    def test_cli_training_rejects_mismatched_approval(self):
        inp=self.dir/'data.jsonl'
        write_hashed(inp, ('\n'.join(canonical(row(i)) for i in range(80))+'\n').encode())
        approve=self.dir/'approval.json'
        write_hashed(approve,{'schema':'bci.neural.training-approval.v1','scope':'CANDIDATE_NEURAL_TRAINING_ONLY',
                              'context':'ctx-test','dataset_sha256':'0'*64})
        with self.assertRaises(ValueError):
            cli(['train','--input',str(inp),'--context','ctx-test','--approval',str(approve),
                 '--output',str(self.dir/'model.json')])

if __name__=='__main__':unittest.main()
