# BEACON COMPUTING INITIATIVE | Orbital Neural Core
# Developer Seal: CJB-DEV-2026
# File SHA-256: SHA256SUMS
"""Nonintrusive live sensor snapshot bridge and bounded read-only legacy conversion."""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone
import importlib.util
import ipaddress
import json
import math
import os
from pathlib import Path
import sqlite3
from urllib.parse import quote
from .common import FEATURES, file_digest, window, parse_time


def installed_sensor_module(release_dir):
    release=Path(release_dir).resolve(strict=True)
    module=release/'src/bci_orbital/sensors.py'
    manifest=release/'SHA256SUMS'
    if not module.is_file() or not manifest.is_file() or module.is_symlink():
        raise ValueError('HOLD: sensor source/manifest missing or unsafe')
    entries={}
    for line in manifest.read_text().splitlines():
        digest,relative=line.split(maxsplit=1)
        entries[relative.lstrip('*').removeprefix('./')]=digest
    if entries.get('src/bci_orbital/sensors.py')!=file_digest(module):
        raise ValueError('HOLD: installed Orbital sensor source integrity mismatch')
    spec=importlib.util.spec_from_file_location('bci_verified_sensors',module)
    if spec is None or spec.loader is None:raise ValueError('HOLD: cannot import sensors')
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _global(address):
    try:return ipaddress.ip_address(address).is_global
    except (ValueError,TypeError):return False


def snapshot_window(snap, timestamp=None):
    if not isinstance(snap,dict) or snap.get('context') in (None,'ctx-unknown'):
        raise ValueError('HOLD: source has no attested context')
    processes=snap.get('processes',[])
    sockets=snap.get('sockets',[])
    usb=snap.get('usb_mounts',[])
    if not isinstance(processes,list) or not isinstance(sockets,list) or not isinstance(usb,list):
        raise ValueError('malformed Orbital snapshot')
    listeners=[s for s in sockets if s.get('state') in ('LISTEN','UNCONN')]
    remote=[s for s in sockets if _global(s.get('peer_ip'))]
    inbound=[s for s in sockets if s.get('state')=='ESTAB' and s.get('local_port') in
             {l.get('local_port') for l in listeners} and s.get('peer_ip')]
    suspect=[p for p in processes if (p.get('exe') or '').startswith(('/tmp/','/var/tmp/','/dev/shm/')) or
             str(p.get('exe') or '').endswith(' (deleted)') or p.get('suspect_browser_mappings')]
    unique={(s.get('peer_ip'),s.get('peer_port')) for s in remote}
    unusual_ports=sum(s.get('peer_port') not in (80,443,53,123,22,853) for s in remote)
    fields={
        'process_count':len(processes),'listener_count':len(listeners),
        'outbound_count':len(remote),'inbound_count':len(inbound),
        'remote_unique_count':len(unique),'usb_mount_count':len(usb),
        'risky_process_count':len(suspect),
        'public_listener_count':sum(s.get('local_ip') in ('0.0.0.0','::') for s in listeners),
        'unusual_remote_port_count':unusual_ports,
        'rx_kib_per_second':0,'tx_kib_per_second':0,
        'visibility_issue_count':len(snap.get('visibility_issues',[])),
    }
    issues=['throughput_rates_not_available_in_v0.1.0_collector']+list(snap.get('visibility_issues',[]))[:10]
    return window(snap['context'], timestamp or datetime.now(timezone.utc).isoformat(timespec='seconds'),
                  fields,'unreviewed_live',{'process','listener','network','storage'},issues,
                  'verified_orbital_v0.1.0_sensors')


def _new_bucket():
    return {'listener':set(),'remote':set(),'inbound':set(),'in_count':[],
            'rx':[],'tx':[],'n':0,'unusual':0,'public':0}


def legacy_export(path,max_rows=50000,profile=None):
    """Legacy data are converted into UNTRUSTED, profile-isolated, aggregate-only windows.

    This deliberately does not map Chance-era context ids onto BCI current ids.
    """
    path=Path(path)
    if max_rows<1 or max_rows>200000:raise ValueError('max rows out of bounds')
    if path.is_symlink() or not path.is_file():raise ValueError('invalid legacy DB path')
    uri='file:'+quote(str(path.resolve()),safe='/')+'?mode=ro'
    db=sqlite3.connect(uri,uri=True,timeout=5)
    try:
        db.execute('PRAGMA query_only=ON')
        cols={r[1] for r in db.execute('PRAGMA table_info(baseline_observations)')}
        if not {'profile_id','time','feature','value'}<=cols:
            raise ValueError('HOLD: incompatible legacy schema')
        buckets=defaultdict(_new_bucket)
        if profile:
            rows=db.execute('SELECT profile_id,time,feature,value FROM baseline_observations WHERE profile_id=? LIMIT ?', (profile,max_rows))
        else:
            rows=db.execute('SELECT profile_id,time,feature,value FROM baseline_observations LIMIT ?', (max_rows,))
        accepted=0
        for pid,ts,feature,raw in rows:
            try:
                time=parse_time(str(ts))
                key=(str(pid),time.replace(minute=(time.minute//5)*5,second=0,microsecond=0))
                b=buckets[key]
                # No raw remote addresses are written into neural datasets.
                if feature=='live.listener':
                    x=json.loads(raw)
                    if isinstance(x,dict):
                        b['listener'].add((str(x.get('protocol')),str(x.get('local_ip')),int(x.get('local_port'))))
                        if x.get('exposure') in ('public','wildcard','external') or x.get('local_ip') in ('0.0.0.0','::'):
                            b['public']+=1
                elif feature in ('outbound.peer','historical.OUTBOUND_PEER_OBSERVED'):
                    x=json.loads(raw)
                    if isinstance(x,dict):
                        b['remote'].add((str(x.get('protocol')),str(x.get('remote_ip')),int(x.get('remote_port'))))
                        if x.get('remote_port') not in (80,443,53,123,22,853):b['unusual']+=1
                elif feature=='inbound.peer':
                    x=json.loads(raw)
                    if isinstance(x,dict):b['inbound'].add((str(x.get('remote_ip')),x.get('listener_port')))
                elif feature=='live.inbound_count':
                    b['in_count'].append(max(0.,float(raw)))
                elif feature=='live.rx_bytes_per_second':
                    b['rx'].append(max(0.,float(raw))/1024)
                elif feature=='live.tx_bytes_per_second':
                    b['tx'].append(max(0.,float(raw))/1024)
                elif feature=='live.sample':pass
                else:continue
                accepted+=1
            except (TypeError,ValueError,OverflowError,json.JSONDecodeError):
                continue
        outputs=[]
        for (pid,t),b in sorted(buckets.items()):
            vals=dict.fromkeys(FEATURES,0)
            vals.update({'listener_count':len(b['listener']),
                         'outbound_count':len(b['remote']),
                         'remote_unique_count':len({r[1] for r in b['remote']}),
                         'inbound_count':max([len(b['inbound'])]+b['in_count']),
                         'public_listener_count':b['public'],
                         'unusual_remote_port_count':b['unusual'],
                         'rx_kib_per_second':sum(b['rx'])/len(b['rx']) if b['rx'] else 0,
                         'tx_kib_per_second':sum(b['tx'])/len(b['tx']) if b['tx'] else 0})
            outputs.append(window('legacy:'+pid,t.isoformat(timespec='seconds'),vals,
                                  'untrusted_legacy',{'listener','network'},
                                  ['no_process_or_storage_coverage_in_sample'],
                                  'chance_legacy_baseline_observations'))
        return outputs,{'input_rows_accepted':accepted,'windows':len(outputs),'profile_count':len({r['context'] for r in outputs}),
                        'source_classification':'UNTRUSTED_LEGACY','remapped_to_current_host':False,
                        'limitations':['No previous baseline approvals or saved versions verified',
                                       'Time window aggregation can inflate listener/peer counts',
                                       'Observed network peers are not trusted destinations']}
    finally:db.close()
