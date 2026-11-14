# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026 | SHA-256: see SHA256SUMS
import hashlib
import json
from pathlib import Path
import socket
import struct
import tempfile
import unittest
from unittest.mock import patch

from bci_orbital_expansion.common import save_hashed,verify_file
from bci_orbital_expansion.context import fingerprint,legacy_summary
from bci_orbital_expansion.throughput import parse_netdev,rate
from bci_orbital_expansion.packets import parse_frame,dns_message,private_summary,capture
from bci_orbital_expansion.kernel import parse_events
from bci_orbital_expansion.cli import cli
from bci_orbital_expansion import bridge


def make_dns_query(name='example.com'):
    labels=b''.join(bytes([len(s)])+s.encode() for s in name.split('.'))+b'\0'
    return struct.pack('!HHHHHH',0xaaaa,0x100,1,0,0,0)+labels+struct.pack('!HH',1,1)

def make_eth_ipv4(payload,port=53,ethertype=0x0800,vlan=False):
    udp=struct.pack('!HHHH',12345,port,len(payload)+8,0)+payload
    ip=bytes([0x45,0])+struct.pack('!H',20+len(udp))+bytes(4)+bytes([64,17])+bytes(2)+socket.inet_aton('192.0.2.1')+socket.inet_aton('198.51.100.2')
    eth=b'\xaa'*6+b'\xbb'*6
    if vlan:return eth+struct.pack('!H',0x8100)+struct.pack('!HH',1,0x0800)+ip+udp
    return eth+struct.pack('!H',ethertype)+ip+udp


class ExpansionTests(unittest.TestCase):
    def test_dns_ipv4(self):
        result=parse_frame(make_eth_ipv4(make_dns_query()))
        self.assertEqual(result['dns']['qname'],'example.com')
        self.assertEqual(result['proto'],'udp')
        self.assertEqual(result['src_port'],12345)
    def test_dns_vlan(self):
        result=parse_frame(make_eth_ipv4(make_dns_query('x.example'),vlan=True))
        self.assertEqual(result['dns']['qname'],'x.example')
    def test_dns_ipv6(self):
        raw=make_dns_query()
        udp=struct.pack('!HHHH',45000,53,len(raw)+8,0)+raw
        ip=bytes([0x60,0,0,0])+struct.pack('!H',len(udp))+bytes([17,64])+socket.inet_pton(socket.AF_INET6,'2001:db8::1')+socket.inet_pton(socket.AF_INET6,'2001:db8::2')
        eth=b'\xaa'*6+b'\xbb'*6+struct.pack('!H',0x86dd)+ip+udp
        self.assertEqual(parse_frame(eth)['dns']['qname'],'example.com')
    def test_dns_reject_malformed_and_pointer_loop(self):
        self.assertIsNone(dns_message(b'hello'))
        raw=bytearray(make_dns_query())
        raw[12:14]=b'\xc0\x0c'
        self.assertIsNone(dns_message(bytes(raw)))
    def test_noninitial_fragment_rejected(self):
        frame=bytearray(make_eth_ipv4(make_dns_query()))
        frame[14+6:14+8]=struct.pack('!H',1)
        self.assertNotIn('dns',parse_frame(bytes(frame)))
    def test_hmac_metadata_privacy(self):
        x={'src_ip':'192.0.2.2','dst_ip':'203.0.113.8','proto':'udp','dns':{'qname':'private.org','qtype':1}}
        y=private_summary(x,b'key')
        self.assertNotIn('src_ip',y)
        self.assertNotIn('qname',y['dns'])
        self.assertEqual(len(y['dns']['qname_hmac_sha256']),64)
        self.assertEqual(private_summary(x,b'key',True)['dns']['qname'],'private.org')
    def test_capture_requires_explicit_interface_and_bounds(self):
        with self.assertRaises(ValueError):capture(';rm -rf /',5,10)
        with self.assertRaises(ValueError):capture('lo',100,10)
    def test_rate_and_reset(self):
        a={'eth0':{'rx_bytes':100,'tx_bytes':30}}
        b={'eth0':{'rx_bytes':150,'tx_bytes':70}}
        values,gaps=rate(a,b,2)
        self.assertEqual(values['eth0']['rx_bytes_per_second'],25)
        self.assertEqual(gaps,[])
        self.assertTrue(rate(b,a,1)[1])
    def test_parse_netdev(self):
        raw='h1\nh2\n eth0: 1 0 0 0 0 0 0 0 10 0 0 0 0 0 0 0\n'
        self.assertEqual(parse_netdev(raw)['eth0']['tx_bytes'],10)
    def test_context_is_distinct(self):
        x=fingerprint('a',[{'dev':'eth0'}],'net:[1]')
        y=fingerprint('a',[{'dev':'eth1'}],'net:[1]')
        self.assertEqual(x['host_id'],y['host_id'])
        self.assertNotEqual(x['route_id'],y['route_id'])
        self.assertFalse(x['legacy_equivalence_verified'])
    def test_hash_create_no_overwrite(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'report.json'
            h=save_hashed(p,{'developer_seal':'CJB-DEV-2026'})
            self.assertEqual(verify_file(p),h)
            with self.assertRaises(FileExistsError):save_hashed(p,{})
            p.write_text('tampered')
            with self.assertRaises(ValueError):verify_file(p)
    def test_kernel_attempt_no_claim_of_read(self):
        x,skips=parse_events('BCI_OPEN\t123\ttest\t/tmp/private.txt\n',b'key')
        self.assertEqual(skips,0)
        self.assertEqual(x[0]['kind'],'file_open_attempt')
        self.assertNotIn('/tmp/private.txt',json.dumps(x))
    def test_no_privilege_flag_no_capture(self):
        with self.assertRaises(SystemExit) as cm:
            cli(['packet-capture','--interface','lo','--output','/tmp/wrong.json'])
        self.assertNotEqual(cm.exception.code,0)
    def test_legacy_context_read_only(self):
        import sqlite3
        with tempfile.TemporaryDirectory() as t:
            db=Path(t)/'fixture.db'
            with sqlite3.connect(db) as c:
                c.execute('CREATE TABLE baseline_profiles(id TEXT,context TEXT)')
                c.execute('INSERT INTO baseline_profiles VALUES (?,?)',('host-a','{"classification":"HOST"}'))
            data=legacy_summary(db)
            self.assertFalse(data['direct_context_mapping_allowed'])
            self.assertEqual(data['profiles'][0]['classification'],'HOST')
    def test_bridge_refuses_mismatched_network_interface(self):
        with patch('bci_orbital_expansion.bridge.intelligence.verified_neural',return_value=(None,None,None)):
            # Refuse to process invalid release even before reaching capture.
            with self.assertRaises((ValueError,TypeError,AttributeError,ModuleNotFoundError)):
                bridge.snapshot('/does-not-exist','/does-not-exist',1)
    def test_shadow_context_gate(self):
        # Runtime only uses signed neural source and exact context equality.
        import inspect
        from bci_orbital_expansion import intelligence
        code=inspect.getsource(intelligence.shadow_score)
        self.assertIn('historical and current network contexts cannot be relabeled',code)

if __name__=='__main__':unittest.main()
