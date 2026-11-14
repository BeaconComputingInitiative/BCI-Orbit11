#!/usr/bin/env python3
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# File SHA-256: SHA256SUMS
# Project: Orbital PyQt6 Control Plane v0.8.1
# Execution succeeds IF AND ONLY IF input and integrity conditions hold.
"""Read-only, bounded data adapter for Orbital's already-running components.

No privileged commands, no training, no model promotion, and no containment.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone

HEADER = 'BEACON COMPUTING INITIATIVE'
SEAL = 'CJB-DEV-2026'
VERSION = '0.8.3'
HOME = Path.home()
JOURNAL = HOME / '.local/state/bci-orbital-integration-v0.5.1/rate-aware-journal.jsonl'
NEURAL = HOME / '.local/bin/bci-orbital-neural'
HOST = HOME / '.local/bin/bci-orbital-v2'
ZERO = '0'*64
MAX_JSON = 128 * 1024
FEATURES = ('process_count', 'listener_count', 'outbound_count','inbound_count',
            'remote_unique_count','usb_mount_count','risky_process_count',
            'public_listener_count','unusual_remote_port_count',
            'rx_kib_per_second','tx_kib_per_second','visibility_issue_count')


def canonical(item):
    return json.dumps(item, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False)


def sha256(path: Path):
    h = hashlib.sha256()
    with path.open('rb') as src:
        for chunk in iter(lambda: src.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def safe_run(argv, timeout=3):
    """Non-shell, bounded subprocess: only fixed executable argument lists."""
    try:
        p = subprocess.run([str(v) for v in argv], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=timeout, check=False,
            env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    except (OSError, subprocess.TimeoutExpired):
        return None
    if p.returncode or len(p.stdout) > MAX_JSON:
        return None
    return p.stdout.decode('utf-8', errors='replace').strip()


def safe_json_cmd(argv, timeout=4):
    raw = safe_run(argv, timeout=timeout)
    if raw is None:
        return None
    try:
        obj = json.loads(raw)
    except (TypeError, ValueError):
        return None
    return obj if isinstance(obj, dict) else None


def systemd_details(unit, user=False):
    """Read authoritative systemd fields; never infer successful capture from 'activating'.

    No shell, privilege escalation, unit modification, or model action occurs.
    """
    fields=('ActiveState','SubState','Result','ExecMainStatus','NRestarts')
    argv=['systemctl']+(['--user'] if user else [])+['show',unit,'--no-pager']
    # Keep systemctl arguments fixed; response is untrusted diagnostic data.
    for field in fields:
        argv.extend(('-p',field))
    raw=safe_run(argv,timeout=3)
    result={k:'unknown' for k in fields}
    if raw is None:
        return result
    for line in raw.splitlines():
        key,sep,value=line.partition('=')
        if sep and key in result and len(value)<256:
            result[key]=value.strip()
    return result


def systemd_state(unit,user=False):
    state=systemd_details(unit,user)['ActiveState'].lower()
    return state if state in ('active','inactive','failed','activating','deactivating','reloading') else 'unknown'


def packet_service_condition(details, logs):
    """Distinguish proven quota HOLD from restart-limit or unknown failure.

    A restart limit alone does not prove quota exhaustion. Evidence must be
    visible in the packet collector's own recent journal output.
    """
    state=str(details.get('ActiveState','unknown')).lower()
    if state=='active':
        return 'active'
    lines=str(logs or '')[-16000:]
    if ('HOLD: evidence storage quota reached' in lines and
            str(details.get('ExecMainStatus'))=='3' and
            str(details.get('Result')) in ('exit-code','start-limit-hit')):
        return 'quota_hold'
    if str(details.get('Result'))=='start-limit-hit':
        return 'restart_limit'
    if state=='failed':
        return 'failed'
    if state=='activating':
        return 'starting'
    return state if state in ('inactive','deactivating') else 'unknown'


def default_interface():
    route = safe_run(['ip','-4','route','get','1.1.1.1'], timeout=2)
    match = re.search(r'\bdev\s+([a-zA-Z0-9_.:@+-]+)', route or '')
    return match.group(1) if match else 'unknown'


def net_bytes(iface):
    if not re.fullmatch(r'[A-Za-z0-9_.:@+-]{1,60}', iface):
        return None
    base = Path('/sys/class/net') / iface / 'statistics'
    try:
        return (int((base/'rx_bytes').read_text()), int((base/'tx_bytes').read_text()))
    except (OSError,ValueError):
        return None


def cpu_counters():
    try:
        nums = [int(x) for x in Path('/proc/stat').read_text().splitlines()[0].split()[1:]]
        return sum(nums), nums[3] + (nums[4] if len(nums)>4 else 0)
    except (OSError,ValueError,IndexError):
        return (0,0)


def memory_percent():
    try:
        lines = Path('/proc/meminfo').read_text().splitlines()
        vals = {x.split(':',1)[0]: int(x.split(':',1)[1].split()[0]) for x in lines if ':' in x}
        total = vals['MemTotal']
        return max(0,min(100, round(100*(1-vals.get('MemAvailable',total)/total))))
    except (OSError, KeyError, ValueError, ZeroDivisionError):
        return None


def disk_percent():
    try:
        disk = shutil.disk_usage(str(HOME))
        return round(100*disk.used/disk.total) if disk.total else None
    except OSError:
        return None


def verify_rate_journal(path=JOURNAL, max_bytes=100*1024*1024):
    """Verify exact v0.2 journal chain and strict current sample identity."""
    path=Path(path)
    if not path.is_file() or path.is_symlink() or path.stat().st_size>max_bytes:
        return {'valid': False, 'error':'Journal absent or unsafe', 'count': 0, 'contexts':{}}
    last=ZERO
    counts={}
    times={}
    last_window={}
    context_provenance={}
    any_gaps={}
    timestamp_monotonic={}
    future_observations={}
    n=0
    try:
        with path.open('r',encoding='utf-8') as stream:
            for line in stream:
                n+=1
                if n>200000 or len(line)>20000:
                    raise ValueError('oversized journal')
                obj=json.loads(line)
                win=obj['window']; ctx=win['context']
                if (win.get('header')!=HEADER or win.get('developer_seal')!=SEAL or
                    win.get('schema')!='bci.neural.window.v1' or
                    win.get('trust')!='unreviewed_live' or
                    not isinstance(ctx,str) or not ctx.startswith('ctx-') or
                    set(win.get('features',{}))!=set(FEATURES)):
                    raise ValueError('invalid record schema')
                if obj['seq']!=n or obj['prev_hash']!=last:
                    raise ValueError('broken sequence')
                d=hashlib.sha256(canonical([n,last,win]).encode()).hexdigest()
                if obj['entry_hash']!=d:
                    raise ValueError('journal hash mismatch')
                last=d
                try:
                    dt=datetime.fromisoformat(win['ts'].replace('Z','+00:00'))
                    if dt.tzinfo is None:raise ValueError('naive timestamp')
                    dt=dt.astimezone(timezone.utc)
                except (TypeError,ValueError):
                    raise ValueError('invalid timestamp')
                lineage=win.get('measurement_provenance') or {}
                signature=(lineage.get('host_id'),lineage.get('route_id'),lineage.get('network_interface'))
                if any(not isinstance(v,str) or not v or v=='unknown' for v in signature):
                    raise ValueError('missing host/route provenance')
                if ctx in context_provenance and context_provenance[ctx]!=signature:
                    raise ValueError('same-context provenance mismatch')
                context_provenance[ctx]=signature
                existing=times.get(ctx,[])
                if existing and dt<existing[-1]:
                    timestamp_monotonic[ctx]=False
                else:
                    timestamp_monotonic.setdefault(ctx,True)
                any_gaps[ctx]=any_gaps.get(ctx,False) or bool(win.get('gaps'))
                future_observations[ctx]=future_observations.get(ctx,False) or (dt>datetime.now(timezone.utc))
                times.setdefault(ctx,[]).append(dt)
                counts[ctx]=counts.get(ctx,0)+1
                last_window[ctx]=win
    except (OSError,ValueError,KeyError,TypeError) as exc:
        return {'valid':False,'error':str(exc)[:120], 'count':n,'contexts':{}}
    summary={}
    for ctx,count in counts.items():
        t=times[ctx]
        summary[ctx]={
            'windows': count, 'distinct_hours': len({x.replace(minute=0,second=0,microsecond=0) for x in t}),
            'elapsed_days': max(0,(max(t)-min(t)).total_seconds()/86400),
            'last':max(t).isoformat(), 'features':last_window[ctx]['features'],
            'gaps':last_window[ctx].get('gaps',[]),
            'any_gaps':any_gaps.get(ctx,False),
            'provenance_consistent':True,
            'timestamps_monotonic':timestamp_monotonic.get(ctx,True),
            'future_observations':future_observations.get(ctx,False),
            'host_id':last_window[ctx].get('measurement_provenance',{}).get('host_id','unknown'),
            'route_id':last_window[ctx].get('measurement_provenance',{}).get('route_id','unknown'),
            'network_interface':last_window[ctx].get('measurement_provenance',{}).get('network_interface','unknown'),
        }
    return {'valid':True,'count':n,'head':last,'contexts':summary,'error':None}


def recent_events():
    raw=safe_run(['journalctl','--user','-u','bci-orbital-v2.service','-n','6',
                  '--no-pager','-o','short-iso'], timeout=3)
    if not raw:return []
    events=[]
    for ln in raw.splitlines()[-6:]:
        if '"alerts": 1' in ln or '"alerts":1' in ln:
            label='Host monitor: one alert during scan'
        elif '"alerts": 0' in ln or '"alerts":0' in ln:
            label='Host monitoring scan completed'
        elif 'sensor-visibility' in ln:
            label='Sensor visibility limitation reported'
        else:
            label='Host monitoring journal entry'
        events.append({'time':ln[:25], 'label':label})
    return list(reversed(events))


def snapshot(include_integrity=False):
    service_details={
      'host':systemd_details('bci-orbital-v2.service',user=True),
      'neural':systemd_details('bci-orbital-neural.timer',user=True),
      'packet':systemd_details('bci-orbital-dynamic.service'),
    }
    states={key: (d['ActiveState'].lower() if d['ActiveState'].lower() in
            ('active','inactive','failed','activating','deactivating') else 'unknown')
            for key,d in service_details.items()}
    packet_logs=None
    if states['packet']!='active':
        packet_logs=safe_run(['journalctl','-u','bci-orbital-dynamic.service',
                '-n','45','--no-pager','-o','cat'],timeout=3)
    packet_condition=packet_service_condition(service_details['packet'],packet_logs)
    journal=verify_rate_journal()
    ctxs=journal.get('contexts',{})
    selected=max(ctxs.items(),key=lambda kv:kv[1]['last'])[0] if ctxs else None
    active=ctxs.get(selected,{})
    counts=active.get('features',{})
    neural=safe_json_cmd([NEURAL,'status']) if NEURAL.is_file() else None
    host=safe_json_cmd([HOST,'status']) if HOST.is_file() else None
    host_baseline=safe_json_cmd([HOST,'baseline','status']) if HOST.is_file() else None
    services_up=sum(x=='active' for x in states.values())
    record={
      'header':HEADER,'developer_seal':SEAL,'version':VERSION,
      'timestamp_utc':datetime.now(timezone.utc).isoformat(),
      'hostname':os.uname().nodename,
      'states':states,'service_details':service_details,
      'packet_condition':packet_condition,'services_up':services_up,
      'current_interface':default_interface(),
      'cpu_counters':cpu_counters(),'mem_pct':memory_percent(),'disk_pct':disk_percent(),
      'journal':journal,'current_context':selected or 'unavailable',
      'host_id':active.get('host_id','unavailable'),
      'route_id':active.get('route_id','unavailable'),
      'neural_window_count':active.get('windows',0),
      'hours':active.get('distinct_hours',0),
      'days':active.get('elapsed_days',0),
      'features':counts,
      'journal_valid':journal.get('valid',False),
      'neural_status':neural,'host_status':host,
      'host_baseline_status':host_baseline,
      'events':([{'time':'CURRENT','label':
         'Packet collector: evidence quota reached; collection is stopped' if packet_condition=='quota_hold'
         else 'Packet collector: restart limit reached; inspect service journal'}]
         if packet_condition in ('quota_hold','restart_limit') else [])+recent_events(),
      'training_authorized':False,'containment_authorized':False,
      'model_state':'UNPROMOTED / HOLD',
    }
    if include_integrity and HOST.is_file():
        record['host_integrity']=safe_json_cmd([HOST,'integrity','verify'],timeout=6)
    return record


def write_operator_report(directory:Path, data:dict):
    """Create-only SHA-256 audited report; no overwrite."""
    directory=Path(directory).expanduser()
    directory.mkdir(parents=True,exist_ok=True,mode=0o700)
    if directory.is_symlink() or directory.stat().st_mode & 0o077:
        raise ValueError('unsafe report directory')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    dest=directory/f'orbital-gui-{stamp}.json'
    payload={k:v for k,v in data.items() if k!='cpu_counters'}
    content=(json.dumps(payload,indent=2,sort_keys=True,default=str)+'\n').encode('utf-8')
    fd=os.open(dest,os.O_CREAT|os.O_EXCL|os.O_WRONLY|getattr(os,'O_NOFOLLOW',0),0o600)
    with os.fdopen(fd,'wb') as f:
        f.write(content);f.flush();os.fsync(f.fileno())
    checksum=hashlib.sha256(content).hexdigest()
    side=dest.with_name(dest.name+'.sha256')
    fd=os.open(side,os.O_CREAT|os.O_EXCL|os.O_WRONLY|getattr(os,'O_NOFOLLOW',0),0o600)
    with os.fdopen(fd,'w',encoding='utf-8') as out:
        out.write(f'{checksum}  {dest.name}\n')
        out.flush()
        os.fsync(out.fileno())
    return dest,checksum
