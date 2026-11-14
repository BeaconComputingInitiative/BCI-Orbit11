#!/usr/bin/env python3
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Stage P0/P1 regression tests — no host mutation
# PASS IF AND ONLY IF observed service, neural context and data-sensor gates hold.
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'src'))
import orbital_backend as b
import orbital_actions as a
import orbital_ai as ai

class RemediationTests(unittest.TestCase):
    def test_packet_failure_without_journal_is_not_quota(self):
        r={'ActiveState':'failed','Result':'start-limit-hit','ExecMainStatus':'3'}
        self.assertEqual(b.packet_service_condition(r,''),'restart_limit')
    def test_quota_requires_logged_evidence(self):
        r={'ActiveState':'failed','Result':'start-limit-hit','ExecMainStatus':'3'}
        self.assertEqual(b.packet_service_condition(r,'HOLD: evidence storage quota reached; export/archive before resuming'),'quota_hold')
        self.assertEqual(b.packet_service_condition(r,'some other service failure'),'restart_limit')
        r['ExecMainStatus']='1'
        self.assertEqual(b.packet_service_condition(r,'HOLD: evidence storage quota reached'),'restart_limit')
    def test_active_collector_never_labelled_quota(self):
        r={'ActiveState':'active','Result':'success','ExecMainStatus':'0'}
        self.assertEqual(b.packet_service_condition(r,'HOLD: evidence storage quota reached'),'active')
    def test_failed_counter_read_is_unavailable_not_zero(self):
        self.assertIsNone(b.net_bytes('hostile;interface'))
        self.assertIsNone(b.net_bytes('thisinterfacecannotexist-99'))
    def test_systemd_details_parse(self):
        raw='ActiveState=failed\nSubState=failed\nResult=start-limit-hit\nExecMainStatus=3\nNRestarts=52'
        with patch.object(b,'safe_run',return_value=raw):
            d=b.systemd_details('bci-orbital-dynamic.service')
        self.assertEqual(d['Result'],'start-limit-hit')
        self.assertEqual(d['ExecMainStatus'],'3')
    def test_earliest_and_latest_samples_not_now_minus_oldest(self):
        # 7 days require actual window span, not only an old first observation.
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'journal.jsonl'
            prev=b.ZERO
            from datetime import datetime,timedelta,timezone
            base=datetime.now(timezone.utc)-timedelta(days=8)
            ts=[base,base+timedelta(hours=1),base+timedelta(hours=2)]
            with p.open('w') as f:
                for n,dt in enumerate(ts,1):
                    w={'schema':'bci.neural.window.v1','header':b.HEADER,'developer_seal':b.SEAL,
                      'trust':'unreviewed_live','context':'ctx-test','ts':dt.isoformat(),
                      'features':{k:1.0 for k in b.FEATURES},'gaps':[],
                      'measurement_provenance':{'host_id':'host-test','route_id':'route-test','network_interface':'usb0'}}
                    record={'seq':n,'prev_hash':prev,'window':w}
                    record['entry_hash']=hashlib.sha256(b.canonical([n,prev,w]).encode()).hexdigest()
                    prev=record['entry_hash']
                    f.write(b.canonical(record)+'\n')
            result=b.verify_rate_journal(p)
            self.assertTrue(result['valid'])
            self.assertLess(result['contexts']['ctx-test']['elapsed_days'],1)
    def test_same_context_provenance_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'journal.jsonl'
            prev=b.ZERO
            with p.open('w') as f:
                for n,route in enumerate(('route-original','route-different'),1):
                    w={'schema':'bci.neural.window.v1','header':b.HEADER,'developer_seal':b.SEAL,
                       'trust':'unreviewed_live','context':'ctx-constant','ts':f'2026-11-13T10:0{n}:00+00:00',
                       'features':{k:1.0 for k in b.FEATURES},'gaps':[],
                       'measurement_provenance':{'host_id':'host-original','route_id':route,'network_interface':'usb0'}}
                    record={'seq':n,'prev_hash':prev,'window':w}
                    record['entry_hash']=hashlib.sha256(b.canonical([n,prev,w]).encode()).hexdigest()
                    prev=record['entry_hash'];f.write(b.canonical(record)+'\n')
            result=b.verify_rate_journal(p)
            self.assertFalse(result['valid'])
            self.assertIn('provenance mismatch',result['error'])
    def test_readiness_gate_requires_no_historical_gaps(self):
        from datetime import datetime,timezone
        summary={'last':datetime.now(timezone.utc).isoformat(),
                 'network_interface':'usb0','any_gaps':True,
                 'timestamps_monotonic':True,'provenance_consistent':True,
                 'future_observations':False,'gaps':[]}
        data={'journal_valid':True,'hours':24,'days':8,'neural_window_count':90,
              'current_context':'ctx-good','current_interface':'usb0',
              'journal':{'contexts':{'ctx-good':summary}}}
        self.assertFalse(a.verified_preparation_status(data)['qualified_for_review'])
    def test_baseline_cannot_claim_live_model(self):
        result=ai.respond('what are your baselines',{'current_context':'ctx-current',
           'journal':{'valid':True},'neural_window_count':80,'hours':24,'days':7})
        self.assertIn('not installed or not verified',result)
        self.assertIn('NOT an approved live baseline',result)
    def test_ai_quota_intent_grounded(self):
        sample={'packet_condition':'quota_hold','service_details':{'packet':{
          'ActiveState':'failed','Result':'start-limit-hit'}}}
        r=ai.respond('why is my packet collector stopped?',sample)
        self.assertIn('EVIDENCE QUOTA HOLD',r)
        self.assertIn('not',r.lower())
    def test_gui_version_and_missing_sample_guard_in_source(self):
        src=(Path(__file__).resolve().parent.parent/'src/orbital_gui.py').read_text()
        self.assertIn("'Orbital v'+VERSION",src)
        self.assertIn('if nb is not None',src)
        self.assertIn('self.poller.finished.connect(self._finish_pending_close)',src)
        self.assertNotIn('self.poller.deleteLater',src)
    def test_guard_script_does_not_modify_evidence(self):
        script=(Path(__file__).resolve().parent.parent/'scripts/packet-quota-guard.sh').read_text()
        self.assertIn('RestartPreventExitStatus=3',script)
        self.assertNotIn('rm -rf',script)
        self.assertNotIn('systemctl restart',script)
        self.assertNotIn('reset-failed',script)

if __name__=='__main__':unittest.main()
