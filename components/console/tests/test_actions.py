#!/usr/bin/env python3
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# File SHA-256: SHA256SUMS
# Tests PASS IF AND ONLY IF gated operations preserve evidence and refuse unsafe requests.
from __future__ import annotations
import ast
import hashlib
import json
import sys
import tempfile
from datetime import datetime,timezone,timedelta
from pathlib import Path
from unittest import TestCase, main, mock
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'src'))
import orbital_actions as a
from orbital_backend import HEADER,SEAL,FEATURES,ZERO,canonical,sha256

ROOT=Path(__file__).resolve().parent.parent


def fake_data(path,ts=None):
    ts=ts or datetime.now(timezone.utc)
    context='ctx-fixture'
    win={'schema':'bci.neural.window.v1','header':HEADER,'developer_seal':SEAL,
         'trust':'unreviewed_live','context':context,'ts':ts.isoformat(),
         'features':{k:1.0 for k in FEATURES},'gaps':[],
         'coverage':['process','listener','network','storage'],
         'measurement_provenance':{'host_id':'host-fixture','route_id':'route-fixture',
                  'network_interface':'usb0','throughput_source':'/proc/net/dev'}}
    obj={'seq':1,'prev_hash':ZERO,'window':win}
    obj['entry_hash']=hashlib.sha256(canonical([1,ZERO,win]).encode()).hexdigest()
    path.write_text(canonical(obj)+'\n')
    return {'journal_valid':True,'journal':{'count':1,'contexts':{context:{
              'windows':1,'distinct_hours':1,'elapsed_days':0,'last':ts.isoformat(),
              'network_interface':'usb0','gaps':[]}}},
            'neural_window_count':1,'hours':1,'days':0,
            'current_context':context,'current_interface':'usb0'}

class BackendTests(TestCase):
    def test_readiness_fail_closed(self):
        self.assertFalse(a.verified_preparation_status({})['qualified_for_review'])
        self.assertFalse(a.verified_preparation_status({'journal_valid':False,
             'neural_window_count':1000,'hours':48,'days':10})['qualified_for_review'])
    def test_candidate_refuses_early_data(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'rate.jsonl';data=fake_data(p)
            with mock.patch.object(a,'JOURNAL',p):
                with self.assertRaises(a.Hold):a.make_candidate(data,Path(d)/'candidates')
            self.assertFalse((Path(d)/'candidates').exists())
    def test_candidate_does_not_touch_journal(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'rate.jsonl';data=fake_data(p)
            initial=sha256(p)
            ctx=data['current_context']
            data.update(neural_window_count=80,hours=24,days=8)
            data['journal']['contexts'][ctx].update(windows=80,distinct_hours=24,elapsed_days=8)
            # This fixture is deliberately inconsistent with the journal count;
            # the second integrity gate must reject it without any writes.
            with mock.patch.object(a,'JOURNAL',p):
                with self.assertRaises(a.Hold):a.make_candidate(data,Path(d)/'candidates')
            self.assertEqual(initial,sha256(p))
    def test_neural_cmd_missing(self):
        with mock.patch.object(a,'NEURAL',Path('/nonexistent/orbital-neural')):
            with self.assertRaises(a.Hold):a.neural_command('train')
    def test_logs_no_shell(self):
        with self.assertRaises(a.Hold):a.service_logs('random-command')
    def test_source_uses_persistent_thread(self):
        src=(ROOT/'src/orbital_gui.py').read_text()
        self.assertIn('self.poller=Poller(self)',src)
        self.assertNotIn('deleteLater(',src)
        self.assertNotIn('self.skin',src)
        self.assertIn('self.globe',src)
        self.assertIn('self.actions',src)
        ast.parse(src)
    def test_original_globe_crop_exact(self):
        crop=ROOT/'assets/orbital-globe-exact.png'
        self.assertEqual(sha256(crop),'26136ad4f714c66c628a727ae3561a23b8a338f77b1278db6a2bec08d179d65b')
        self.assertEqual(sha256(ROOT/'assets/orbital-approved-mockup.png'),
            'f2b5f9659c7311e40e24ea2d6e04c01d6de53ec03285359a28386bd5e99bdd28')
    def test_install_does_not_touch_services(self):
        script=(ROOT/'scripts/install.sh').read_text()
        self.assertNotIn('systemctl enable',script)
        self.assertNotIn('systemctl restart',script)
        self.assertNotIn('sha256sum -c',script)
        self.assertIn('without any hash requirement',script)
        self.assertIn('orbital-globe-exact.png',script)
        self.assertIn('bci-orbital-gui/0.7.0',script)
    def test_actions_defined(self):
        src=(ROOT/'src/orbital_gui.py').read_text()
        for name in ('System Status','Verify Evidence','Neural Status','Services',
                     'Generate Report','Policy & Control','Train Status',
                     'Prepare','Review','Run','Evaluate','Promote','Rollback','View All'):
            self.assertIn("'"+name+"'",src)
    def test_bin_sidecar_atomic_report(self):
        from orbital_backend import write_operator_report
        with tempfile.TemporaryDirectory() as d:
            report,digest=write_operator_report(Path(d)/'private',
                {'header':HEADER,'developer_seal':SEAL})
            self.assertEqual(sha256(report),digest)
            self.assertEqual(Path(str(report)+'.sha256').read_text().split()[0],digest)

if __name__=='__main__':main()
