#!/usr/bin/env python3
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# File SHA-256: SHA256SUMS
# Test gates pass IF AND ONLY IF read-only operations meet safety requirements.
import unittest
import tempfile
from pathlib import Path
import json
import hashlib
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'src'))
import orbital_backend as b

class Tests(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(b.SEAL,'CJB-DEV-2026')
        self.assertEqual(b.HEADER,'BEACON COMPUTING INITIATIVE')
    def test_absent_journal(self):
        with tempfile.TemporaryDirectory() as d:
            r=b.verify_rate_journal(Path(d)/'absent.jsonl')
            self.assertFalse(r['valid'])
    def test_bad_journal(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'j.jsonl';p.write_text('{bad json}\n')
            self.assertFalse(b.verify_rate_journal(p)['valid'])
    def test_unsafe_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'j.jsonl';p.write_text('')
            q=Path(d)/'link';q.symlink_to(p)
            self.assertFalse(b.verify_rate_journal(q)['valid'])
    def test_chain_good(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'journal.jsonl'
            w={'schema':'bci.neural.window.v1','header':b.HEADER,'developer_seal':b.SEAL,
                'trust':'unreviewed_live','context':'ctx-test','ts':'2026-11-11T08:00:00+00:00',
                'features':{k:1.0 for k in b.FEATURES},'gaps':[],
                'measurement_provenance':{'host_id':'host-test','route_id':'route-test','network_interface':'usb0'}}
            en={'seq':1,'prev_hash':b.ZERO,'window':w}
            en['entry_hash']=hashlib.sha256(b.canonical([1,b.ZERO,w]).encode()).hexdigest()
            p.write_text(b.canonical(en)+'\n')
            r=b.verify_rate_journal(p)
            self.assertTrue(r['valid']);self.assertEqual(r['count'],1)
            self.assertEqual(r['contexts']['ctx-test']['windows'],1)
            en['entry_hash']='0'*64;p.write_text(b.canonical(en)+'\n')
            self.assertFalse(b.verify_rate_journal(p)['valid'])
    def test_report_has_hash(self):
        with tempfile.TemporaryDirectory() as d:
            path,h=b.write_operator_report(Path(d)/'r',{'header':b.HEADER,'developer_seal':b.SEAL})
            self.assertEqual(h,b.sha256(path))
            self.assertIn('CJB-DEV-2026',path.read_text())
            self.assertIn(h,Path(str(path)+'.sha256').read_text())
    def test_no_shell_in_run(self):
        self.assertEqual(b.safe_run(['/definitely/missing/bci']),None)
    def test_interface_invalid(self):
        self.assertIsNone(b.net_bytes('bad;rm -rf /'))
    def test_skin_exact_dimensions(self):
        import struct
        source=Path(__file__).resolve().parent.parent/'assets/orbital-approved-mockup.png'
        raw=source.read_bytes()
        self.assertEqual(raw[:8],b'\x89PNG\r\n\x1a\n')
        self.assertEqual(struct.unpack('>II',raw[16:24]),(1672,941))
    def test_gui_has_globe_preserved(self):
        # Exact approved screenshot fingerprint includes every pixel of the globe.
        source=Path(__file__).resolve().parent.parent/'assets/orbital-approved-mockup.png'
        self.assertEqual(b.sha256(source),'f2b5f9659c7311e40e24ea2d6e04c01d6de53ec03285359a28386bd5e99bdd28')

if __name__=='__main__':unittest.main()
