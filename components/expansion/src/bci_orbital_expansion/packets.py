# BEACON COMPUTING INITIATIVE | Orbital Packet and DNS Collector
# Developer Seal: CJB-DEV-2026 | SHA-256: see SHA256SUMS
"""Bounded AF_PACKET read-only capture. No packet payloads are persisted.

Requires CAP_NET_RAW in the capture process network namespace. Checksums describe
captured frame bytes, not all wire traffic, and cannot establish exfiltration.
"""
from __future__ import annotations
import hashlib
import hmac
import ipaddress
import os
import socket
import struct
import time
from .common import report, digest

ETH_ALL=0x0003

def _ip4(data):
    if len(data)<20 or data[0]>>4 !=4:return None
    hlen=(data[0]&15)*4
    if hlen<20 or len(data)<hlen:return None
    if struct.unpack('!H',data[6:8])[0]&0x1fff:return None  # noninitial fragment
    length=struct.unpack('!H',data[2:4])[0]
    if length <hlen:return None
    return (str(ipaddress.ip_address(data[12:16])),str(ipaddress.ip_address(data[16:20])),data[9],data[hlen:min(length,len(data))])

def _ip6(data):
    if len(data)<40 or data[0]>>4 !=6:return None
    proto=data[6]
    # IPv6 extension headers require an explicit decoder; do not falsely parse them as TCP/UDP.
    if proto not in (6,17):return None
    length=struct.unpack('!H',data[4:6])[0]
    return (str(ipaddress.ip_address(data[8:24])),str(ipaddress.ip_address(data[24:40])),proto,data[40:min(40+length,len(data))])

def _dns_label(payload,offset):
    labels=[];visited=set();pos=offset;end=None
    for _ in range(80):
        if pos>=len(payload):return None
        if pos in visited:return None
        visited.add(pos)
        n=payload[pos]
        if n&0xc0==0xc0:
            if pos+1>=len(payload):return None
            ptr=((n&0x3f)<<8)|payload[pos+1]
            if ptr>=len(payload):return None
            if end is None:end=pos+2
            pos=ptr;continue
        if n&0xc0:return None
        pos+=1
        if n==0:return ('.'.join(labels).lower(),pos if end is None else end)
        if n>63 or pos+n>len(payload):return None
        label=payload[pos:pos+n]
        try:labels.append(label.decode('ascii'))
        except UnicodeDecodeError:return None
        pos+=n
    return None

def dns_message(payload):
    if len(payload)<12:return None
    flags=struct.unpack('!H',payload[2:4])[0]
    questions=struct.unpack('!H',payload[4:6])[0]
    if questions<1:return None
    item=_dns_label(payload,12)
    if item is None:return None
    qname,after=item
    if after+4>len(payload):return None
    qtype=struct.unpack('!H',payload[after:after+2])[0]
    return {'qname':qname,'qtype':qtype,'reply':bool(flags&0x8000),'rcode':flags&15}

def parse_frame(frame):
    if len(frame)<14:return {'proto':'unparsed','reason':'short_ethernet_frame'}
    etype=struct.unpack('!H',frame[12:14])[0];offset=14
    for _ in range(2):
        if etype not in (0x8100,0x88a8):break
        if len(frame)<offset+4:return {'proto':'unparsed','reason':'short_vlan_frame'}
        etype=struct.unpack('!H',frame[offset+2:offset+4])[0];offset+=4
    ip=_ip4(frame[offset:]) if etype==0x0800 else _ip6(frame[offset:]) if etype==0x86dd else None
    if ip is None:return {'proto':'unparsed','reason':'unsupported_l2_or_ip_fragment'}
    src,dst,proto,data=ip
    result={'src_ip':src,'dst_ip':dst,'proto':{6:'tcp',17:'udp'}.get(proto,str(proto))}
    if proto not in (6,17) or len(data)<4:return result
    sport,dport=struct.unpack('!HH',data[:4]);result.update(src_port=sport,dst_port=dport)
    payload=b''
    if proto==17 and len(data)>=8:
        udp_length=struct.unpack('!H',data[4:6])[0]
        if udp_length>=8:payload=data[8:min(len(data),udp_length)]
    elif proto==6 and len(data)>=20:
        off=(data[12]>>4)*4
        if off>=20 and len(data)>=off:payload=data[off:]
    if (sport==53 or dport==53) and payload:
        if proto==6:
            if len(payload)<2:return result
            dns_size=struct.unpack('!H',payload[:2])[0]
            if dns_size>len(payload)-2:return result # TCP reassembly unavailable
            payload=payload[2:2+dns_size]
        item=dns_message(payload)
        if item:result['dns']=item
    return result

def private_summary(parsed,key,include_metadata=False):
    d={k:v for k,v in parsed.items() if k not in ('src_ip','dst_ip','dns')}
    for name in ('src_ip','dst_ip'):
        if name in parsed:
            d[name if include_metadata else name+'_hmac_sha256']=(parsed[name] if include_metadata else hmac.new(key,parsed[name].encode(),hashlib.sha256).hexdigest())
    if 'dns' in parsed:
        dns=dict(parsed['dns']); name=dns.pop('qname')
        dns['qname' if include_metadata else 'qname_hmac_sha256']=(name if include_metadata else hmac.new(key,name.encode(),hashlib.sha256).hexdigest())
        d['dns']=dns
    return d

def capture(interface,seconds=5,max_packets=1500,include_metadata=False):
    if not interface or len(interface)>15 or not interface.replace('_','').replace('-','').replace('.','').isalnum():
        raise ValueError('HOLD: explicit valid network interface required')
    if not (1<=seconds<=60 and 1<=max_packets<=10000):raise ValueError('HOLD: bounded capture only')
    names={x[1] for x in socket.if_nameindex()}
    if interface not in names:raise ValueError('HOLD: interface not present')
    if not hasattr(socket,'AF_PACKET'):raise RuntimeError('Linux AF_PACKET unavailable')
    try:s=socket.socket(socket.AF_PACKET,socket.SOCK_RAW,socket.htons(ETH_ALL))
    except PermissionError as exc:raise PermissionError('HOLD: CAP_NET_RAW required for the capture process') from exc
    try:
        s.bind((interface,0)); key=os.urandom(32)
        end=time.monotonic()+seconds
        rows=[]; total=0;dns_count=0;truncated=0;start=time.monotonic()
        while len(rows)<max_packets and time.monotonic()<end:
            s.settimeout(max(.001,min(.5,end-time.monotonic())))
            try:data,addr=s.recvfrom(65535)
            except socket.timeout:continue
            total+=len(data)
            parsed=parse_frame(data)
            if 'dns' in parsed:dns_count+=1
            rows.append({'frame_sha256':digest(data),'captured_bytes':len(data),
                         'metadata':private_summary(parsed,key,include_metadata)})
        elapsed=max(.001,time.monotonic()-start)
        return report('packet_dns_capture',interface=interface,duration_seconds=round(elapsed,3),
                      captured_packets=len(rows),captured_bytes=total,dns_messages_parsed=dns_count,
                      capture_bytes_per_second=round(total/elapsed,3),events=rows,
                      privacy='frame hashes only; raw payload discarded; HMAC metadata by default',
                      endpoint_hmac_key_retained=False,
                      gaps=['AF_PACKET may drop frames; no loss counter','DNS over HTTPS/TLS not decoded',
                            'No TCP reassembly; fragmented packets not decoded','No process attribution from AF_PACKET alone'],
                      network_response_authorized=False)
    finally:s.close()
