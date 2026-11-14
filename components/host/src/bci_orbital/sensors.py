# BEACON COMPUTING INITIATIVE | Orbital Cyber Defense
# Developer Seal: CJB-DEV-2026
# File SHA-256: see SHA256SUMS
"""Read-only host sensors. Missing visibility is reported, never assumed clean."""
from __future__ import annotations
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

PID_RE = re.compile(r'pid=(\d+)')

def command(args, timeout=8):
    if not shutil.which(args[0]):
        return None, f'{args[0]} not installed'
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout,
                           check=False, env={**os.environ, 'LC_ALL':'C'})
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, f'{args[0]} failed: {type(exc).__name__}'
    if p.returncode:
        return None, f'{args[0]} exit={p.returncode}: {p.stderr[:100]}'
    return p.stdout, None

def endpoint(text):
    # Supports IPv4/IPv6 ss endpoint forms; no DNS resolution performed.
    if text in ('*',''):
        return None, None
    if text.startswith('[') and ']:' in text:
        addr, port = text[1:].rsplit(']:',1)
    elif ':' in text:
        addr, port = text.rsplit(':',1)
    else:
        return None, None
    if addr.startswith('['):
        addr = addr[1:]
    if addr in ('*', ''):
        addr = '0.0.0.0'
    if addr == '::ffff:':
        return None, None
    try:
        return str(ipaddress.ip_address(addr.split('%')[0])), int(port)
    except (ValueError, TypeError):
        return None, None

def get_connections():
    out, error = command(['ss','-H','-n','-a','-t','-u','-p'])
    if out is None:
        return [], error
    items = []
    for line in out.splitlines():
        fields = line.split()
        if len(fields) < 6:
            continue
        proto, state = fields[0].lower(), fields[1].upper()
        if proto not in ('tcp','udp'):
            continue
        # Fields: Netid State Recv-Q Send-Q Local Peer Process
        local_ip, local_port = endpoint(fields[4])
        peer_ip, peer_port = endpoint(fields[5])
        if local_port is None:
            continue
        match = PID_RE.search(' '.join(fields[6:]))
        items.append({'proto':proto, 'state':state, 'local_ip':local_ip,
                      'local_port':local_port, 'peer_ip':peer_ip,
                      'peer_port':peer_port, 'pid':int(match.group(1)) if match else None})
    return items, None

def proc_info():
    items = []
    errors = 0
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():
            continue
        try:
            pid = int(p.name)
            comm = (p / 'comm').read_text(errors='replace').strip()[:100]
            try:
                exe = os.readlink(p / 'exe')
            except OSError:
                exe = None
            rawcmd = (p / 'cmdline').read_bytes()[:4096]
            entry = {'pid':pid, 'name':comm, 'exe':exe,
                     'cmdline_sha256':hashlib.sha256(rawcmd).hexdigest() if rawcmd else None,
                     'suspect_browser_mappings':[]}
            if any(x in comm.lower() for x in ('firefox','chromium','chrome','brave')):
                try:
                    mappings = (p / 'maps').read_text(errors='replace').splitlines()
                    anomalies = set()
                    for line in mappings:
                        tail = line.split(maxsplit=5)
                        path = tail[-1] if len(tail) >= 6 else ''
                        if ('/tmp/' in path or '/dev/shm/' in path or
                            ('(deleted)' in path and (' .so' in path or '.so ' in path))):
                            anomalies.add(path[:220])
                    entry['suspect_browser_mappings'] = sorted(anomalies)[:8]
                except (OSError, PermissionError):
                    pass
            items.append(entry)
        except (OSError, PermissionError, UnicodeError):
            errors += 1
    return items, (f'{errors} /proc process entries unreadable' if errors else None)

def usb_storage():
    out, err = command(['lsblk','-J','-o','NAME,TRAN,MOUNTPOINT,TYPE'],timeout=10)
    if out is None:
        return [], err
    try:
        rows = json.loads(out).get('blockdevices',[])
    except ValueError:
        return [], 'lsblk JSON unavailable'
    mounts = []
    def walk(node, parent_usb=False):
        is_usb = parent_usb or node.get('tran') == 'usb'
        if is_usb and node.get('mountpoint'):
            mounts.append({'device':node.get('name'), 'mountpoint':node.get('mountpoint')})
        for ch in node.get('children',[]) or []:
            walk(ch, is_usb)
    for row in rows:
        walk(row)
    return mounts, None

def network_context():
    out, err = command(['ip','-j','route','show','default'])
    if out is None:
        return 'ctx-unknown', err
    try:
        routes = json.loads(out)
        if not routes:
            return 'ctx-unknown', 'no default route; context cannot be attested'
        relevant = sorted([{'dev':r.get('dev'), 'gateway':r.get('gateway'),
                            'table':r.get('table','main')} for r in routes], key=lambda x:json.dumps(x,sort_keys=True))
    except ValueError:
        return 'ctx-unknown', 'ip route JSON invalid'
    digest = hashlib.sha256(json.dumps(relevant,sort_keys=True).encode()).hexdigest()[:16]
    return 'ctx-'+digest, None

def collect():
    context, ctxt_err = network_context()
    connections, socket_err = get_connections()
    processes, proc_err = proc_info()
    mounts, usb_err = usb_storage()
    issues = [x for x in (ctxt_err, socket_err, proc_err, usb_err) if x]
    return {'context':context, 'sockets':connections, 'processes':processes,
            'usb_mounts':mounts, 'visibility_issues':issues}
