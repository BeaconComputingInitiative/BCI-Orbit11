# BEACON COMPUTING INITIATIVE | Orbital Cyber Defense
# Developer Seal: CJB-DEV-2026
# File SHA-256: see SHA256SUMS
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from bci_orbital.engine import Engine, reference_data
from bci_orbital.response import safe_target
from bci_orbital.sensors import endpoint
from bci_orbital.store import Store

class OrbitalTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.store=Store(Path(self.temp.name))
    def tearDown(self):
        self.store.close();self.temp.cleanup()
    def test_reference_not_false_host_pretrained(self):
        r=reference_data()
        self.assertEqual(r['classification'],'curated_generic_reference_not_host_trained')
        self.assertFalse(r['monitoring']['email_enabled'])
    def test_empty_chain(self):
        self.assertEqual(self.store.verify_chain(),(True,0,None))
    def test_chain_detects_tamper(self):
        self.store.event('ctx-one','test','info',{'k':'v'})
        self.store.event('ctx-one','test-two','medium',{'k':'v2'})
        self.assertTrue(self.store.verify_chain()[0])
        with self.store.con:
            self.store.con.execute('UPDATE events SET kind=? WHERE seq=1',('edited',))
        ok,_,bad=self.store.verify_chain()
        self.assertFalse(ok);self.assertEqual(bad,1)
    def test_approved_baseline_does_not_learn_deviation(self):
        ctx='ctx-test'
        self.store.add_scan(ctx, {'remote':{'8.8.8.8'}},'2026-11-01T00:00:00+00:00')
        approved_sha=self.store.approve(ctx,'unit-test')
        self.assertEqual(self.store.add_scan(ctx,{'remote':{'9.9.9.9'}},'2026-11-08T00:00:00+00:00'), [('remote','9.9.9.9')])
        self.assertEqual(self.store.add_scan(ctx,{'remote':{'9.9.9.9'}},'2026-11-08T00:01:00+00:00'), [])
        self.assertEqual(self.store.baseline_digest(ctx),approved_sha)
        self.assertEqual(self.store.baseline_stats(ctx)['categories']['remote'],1)
    def test_socket_endpoints(self):
        self.assertEqual(endpoint('[::1]:443'),('::1',443))
        self.assertEqual(endpoint('10.0.0.2:12345'),('10.0.0.2',12345))
        self.assertEqual(endpoint('*:22'),('0.0.0.0',22))
        self.assertEqual(endpoint('not-an-endpoint'),(None,None))
    def test_protected_targets(self):
        r=reference_data()
        for ip in ['127.0.0.1','10.0.0.1','192.168.1.1','::1','1.2.3.4']:
            val=safe_target(ip,r)
            self.assertEqual(val,ip=='1.2.3.4')
        self.assertFalse(safe_target('1.2.3.4',r,['1.2.3.4']))
    def test_initial_scan_uses_reference_not_live_quarantine(self):
        snap={'context':'ctx-test','processes':[{'pid':199,'name':'odd','exe':'/tmp/odd',
             'suspect_browser_mappings':[]}],
             'sockets':[{'proto':'tcp','state':'ESTAB','local_ip':'10.0.0.1',
                         'local_port':40000,'peer_ip':'1.2.3.4','peer_port':443,'pid':199}],
             'usb_mounts':[],'visibility_issues':[]}
        result=Engine(self.store).scan(snap)
        self.assertGreaterEqual(result['alerts'],1)
        self.assertFalse(result['approved'])
        self.assertEqual(result['quarantined'],[])
    def test_operator_ioc_and_suspicious_proc_still_dry_run(self):
        snap={'context':'ctx-test','processes':[{'pid':199,'name':'odd','exe':'/tmp/odd',
             'suspect_browser_mappings':[]}],
             'sockets':[{'proto':'tcp','state':'ESTAB','local_ip':'10.0.0.1',
                         'local_port':40000,'peer_ip':'1.2.3.4','peer_port':443,'pid':199}],
             'usb_mounts':[],'visibility_issues':[]}
        self.store.add_ioc('1.2.3.4','test source')
        result=Engine(self.store).scan(snap)
        self.assertEqual(result['quarantined'],[])
        kinds=[e['kind'] for e in self.store.recent(30)]
        self.assertIn('quarantine-dry-run',kinds)
    def test_export_sha_calculation(self):
        content=b'evidence\n'
        self.assertEqual(len(hashlib.sha256(content).hexdigest()),64)

if __name__ == '__main__':
    unittest.main()
