# BEACON COMPUTING INITIATIVE | Orbital Cyber Defense
# Developer Seal: CJB-DEV-2026
# File SHA-256: see SHA256SUMS
"""BCI Orbital operational CLI. All mutations require explicit commands."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import shutil
import signal
import sys
import time
from .engine import Engine, reference_data
from .response import check_capability, quarantine, release, safe_target, setup_scoped_table, remove_own_table, nft
from .sensors import network_context
from .store import Store, utcnow

EXIT_HOLD = 3

def home_dir():
    if os.environ.get('BCI_ORBITAL_HOME'):
        return Path(os.environ['BCI_ORBITAL_HOME']).expanduser()
    return Path(os.environ.get('XDG_STATE_HOME', str(Path.home()/'.local/state')))/'bci-orbital-v2'

def pprint(x):
    print(json.dumps(x,indent=2,sort_keys=True))

def interactive_phrase(required):
    if not sys.stdin.isatty():
        raise RuntimeError('an interactive local TTY is required')
    print(f'Type {required} to confirm: ',end='',flush=True)
    return input().strip() == required

def ready_stats(store,ctx,minimum_days):
    s = store.baseline_stats(ctx)
    if not s['first'] or not s['last']:
        return False,s,'no recorded scans'
    elapsed = (datetime.fromisoformat(s['last'])-datetime.fromisoformat(s['first'])).total_seconds()
    enough = elapsed >= minimum_days*86400 and s['hours'] >= 24
    return enough,s,f'requires >= {minimum_days} elapsed days and >= 24 distinct scan hours'

def prequalified(store):
    return (store.control('operator_authorized')=='yes'
            and store.control('recovery_verified')=='yes' and check_capability())

def do_drill(store):
    if not check_capability():
        raise RuntimeError('recovery drill requires root and nftables; use system service for containment')
    # Recovery test uses a reserved documentation address, never actual traffic.
    test_ip='198.51.100.254'
    setup_scoped_table()
    try:
        nft(['add','element','inet','bci_orbital_v2','bci_quarantine_v4','{',test_ip,'timeout','300s','}'])
        nft(['delete','element','inet','bci_orbital_v2','bci_quarantine_v4','{',test_ip,'}'])
        # Test that the isolated table can be removed; skip if any active target exists.
        # Existing quarantines are never removed by this drill.
    except Exception:
        raise
    store.set_control('recovery_verified','yes')
    store.event('operator','recovery-drill-passed','info',{'test_address':test_ip,'nft_isolation':'scoped'})

def run_once(store):
    return Engine(store).scan()

def main(argv=None):
    parser=argparse.ArgumentParser(prog='bci-orbital-v2',description='BCI Orbital Cyber Defense v0.1.0')
    parser.add_argument('--state-dir',help='override persistent state (tests/isolated deployments)')
    sub=parser.add_subparsers(dest='cmd',required=True)
    sub.add_parser('scan',help='single read-only host scan; writes only Orbital evidence DB')
    sub.add_parser('run',help='monitor in foreground every 60 seconds')
    sub.add_parser('status',help='current status, profile and sensor coverage')
    base=sub.add_parser('baseline',help='baseline state and approvals')
    base_sub=base.add_subparsers(dest='action',required=True)
    base_sub.add_parser('status')
    p=base_sub.add_parser('extend');p.add_argument('--days',type=int,choices=[14],required=True)
    base_sub.add_parser('approve')
    p=base_sub.add_parser('import-history');p.add_argument('path',type=Path);p.add_argument('--sha256',required=True)
    resp=sub.add_parser('response',help='bounded containment management')
    resp_sub=resp.add_subparsers(dest='action',required=True)
    resp_sub.add_parser('drill')
    resp_sub.add_parser('authorize')
    resp_sub.add_parser('arm')
    resp_sub.add_parser('disarm')
    p=resp_sub.add_parser('release');p.add_argument('ip')
    p=resp_sub.add_parser('ioc-add');p.add_argument('ip');p.add_argument('--note',required=True)
    integrity=sub.add_parser('integrity')
    integrity.add_argument('action',choices=['verify'])
    logs=sub.add_parser('events');logs.add_argument('--limit',type=int,default=15)
    p=sub.add_parser('export');p.add_argument('path',type=Path)
    args=parser.parse_args(argv)
    if args.state_dir:
        state=Path(args.state_dir)
    else:
        state=home_dir()
    os.umask(0o077)
    store=Store(state)
    ctx,ctx_err=network_context()
    try:
        if args.cmd=='scan':
            pprint(run_once(store));return 0
        if args.cmd=='run':
            print('BCI Orbital active; Ctrl+C to terminate. Monitoring is not equivalent to a clean-host determination.',flush=True)
            while True:
                try:
                    result=run_once(store)
                    print(json.dumps({'ts':utcnow(),**result},sort_keys=True),flush=True)
                except Exception as exc:
                    # Fail visible; an unexpected collector error must not be concealed.
                    store.event('engine','scan-exception','high',{'error':type(exc).__name__,'detail':str(exc)[:250]})
                    print('SCAN ERROR:',repr(exc),file=sys.stderr,flush=True)
                time.sleep(60)
        if args.cmd=='status':
            integrity,n,bad=store.verify_chain()
            pprint({'header':'BEACON COMPUTING INITIATIVE', 'developer_seal':'CJB-DEV-2026',
                    'version':'0.1.0','state_dir':str(state),'context':ctx,
                    'context_warning':ctx_err,'profile':store.baseline_stats(ctx),
                    'reference_classification':reference_data()['classification'],
                    'response_mode':store.control('response_mode','dry-run'),
                    'recovery_verified':store.control('recovery_verified')=='yes',
                    'operator_authorized':store.control('operator_authorized')=='yes',
                    'live_capability':bool(check_capability()), 'email_enabled':False,
                    'event_chain_ok':integrity,'event_count':n,'first_bad_seq':bad,
                    'coverage_limitations':['No kernel/eBPF coverage','No on-host DNS query capture',
                        'No malicious behavior guaranteed detectable','No proof of exfiltration from co-occurrence']})
            return 0 if integrity else EXIT_HOLD
        if args.cmd=='baseline':
            if args.action=='status':
                allowed=7+int(store.control('extension_days','0'))
                ready,stats,reason=ready_stats(store,ctx,allowed)
                pprint({'context':ctx,'reference_is_host_trained':False,'minimum_days':allowed,
                        'ready_for_review':ready,'rule':reason,'stats':stats})
                return 0
            if args.action=='import-history':
                source=args.path.expanduser().resolve(strict=True)
                expected=args.sha256.lower()
                if len(expected)!=64 or any(c not in '0123456789abcdef' for c in expected):
                    raise RuntimeError('expected SHA-256 must be 64 hex characters')
                digest=hashlib.sha256()
                with source.open('rb') as reader:
                    for chunk in iter(lambda: reader.read(1024*1024),b''):
                        digest.update(chunk)
                computed=digest.hexdigest()
                if computed != expected:
                    raise RuntimeError('historical import SHA-256 mismatch; no rows imported')
                # Imported history is stored separately and remains untrusted; never
                # grants baseline approval or suppresses live anomaly alerts.
                validated=[]
                with source.open('r',encoding='utf-8') as reader:
                    lines=list(reader)
                if len(lines)>200000:
                    raise RuntimeError('import exceeds 200,000 lines')
                for idx,line in enumerate(lines,1):
                    if not line.strip():
                        continue
                    if idx>200000:
                        raise RuntimeError('import exceeds 200,000 lines')
                    item=json.loads(line)
                    if set(item)!={'ts','context','category','value'}:
                        raise RuntimeError(f'history line {idx}: requires ts/context/category/value')
                    dt=datetime.fromisoformat(item['ts'])
                    if dt.tzinfo is None or dt>datetime.now(timezone.utc) or dt.year<2020:
                        raise RuntimeError(f'history line {idx}: invalid timestamp')
                    if item['context']!=ctx or ctx=='ctx-unknown':
                        raise RuntimeError(f'history line {idx}: context mismatch')
                    if item['category'] not in ('exe','listener','remote','usb'):
                        raise RuntimeError(f'history line {idx}: category not supported')
                    if not isinstance(item['value'],str) or len(item['value'])>500:
                        raise RuntimeError(f'history line {idx}: invalid value')
                    validated.append((item['ts'],ctx,item['category'],item['value'],computed))
                with store.con:
                    store.con.executemany('INSERT OR IGNORE INTO historical_observations VALUES(?,?,?,?,?)',validated)
                store.event(ctx,'historical-import','info',{'rows_validated':len(validated),
                             'source_sha256':computed,'trusted_for_approval':False})
                pprint({'rows_imported':len(validated),'source_sha256':computed,
                        'live_baseline_approval_affected':False,'classification':'untrusted historical evidence'})
                return 0
            if args.action=='extend':
                store.set_control('extension_days','14')
                store.event(ctx,'baseline-learning-extended','info',{'additional_days':14})
                print('Learning review extended from 7 days to 21 days.');return 0
            if ctx=='ctx-unknown':
                raise RuntimeError('unknown network context cannot be approved')
            allowed=7+int(store.control('extension_days','0'))
            ready,stats,why=ready_stats(store,ctx,allowed)
            if not ready:
                print('HOLD: baseline is not ready: '+why);pprint(stats);return EXIT_HOLD
            if not interactive_phrase('APPROVE-BCI-BASELINE'):
                print('HOLD: no approval');return EXIT_HOLD
            digest=store.approve(ctx,'operator-reviewed-local-learning')
            if prequalified(store):
                store.set_control('response_mode','armed')
                store.event(ctx,'response-auto-armed','info',{'why':'approved and prequalified'})
            print('APPROVED SHA256:',digest,'MODE:',store.control('response_mode','dry-run'))
            return 0
        if args.cmd=='response':
            if args.action=='drill':
                do_drill(store)
                print('Scoped nftables add/delete drill PASS; limited recovery test, not full disaster recovery.');return 0
            if args.action=='authorize':
                if not interactive_phrase('AUTHORIZE-BCI-CONTAINMENT'):
                    print('HOLD: not authorized');return EXIT_HOLD
                store.set_control('operator_authorized','yes')
                store.event('operator','response-operator-authorization','info',{'method':'interactive-local-confirmation'})
                print('Operator confirmation recorded; not a high-assurance identity proof.');return 0
            if args.action=='arm':
                if not store.approved(ctx) or not prequalified(store):
                    print('HOLD: approved profile, recovery drill, local authorization and root+nft required')
                    return EXIT_HOLD
                if not interactive_phrase('ARM-BCI-ORBITAL'):
                    return EXIT_HOLD
                store.set_control('response_mode','armed')
                store.event(ctx,'response-armed','info',{'gating':'approved plus recovery plus local authorization'})
                print('ARMED: two independent indicators + operator IOC required before any block.');return 0
            if args.action=='disarm':
                store.set_control('response_mode','dry-run')
                store.event(ctx,'response-disarmed','info',{})
                print('Response disarmed. Existing TTL rules expire after at most 300 seconds.');return 0
            if args.action=='release':
                if not interactive_phrase('RELEASE-BCI-QUARANTINE'):
                    return EXIT_HOLD
                release(args.ip)
                with store.con:
                    store.con.execute('DELETE FROM quarantines WHERE ip=?',(args.ip,))
                store.event(ctx,'quarantine-released','info',{'ip':args.ip});return 0
            if args.action=='ioc-add':
                ip=str(ipaddress.ip_address(args.ip))
                if not safe_target(ip,reference_data()):
                    print('HOLD: protected or nonpublic IPs cannot be registered for blocking');return EXIT_HOLD
                if not interactive_phrase('REGISTER-BCI-IOC'):
                    return EXIT_HOLD
                store.add_ioc(ip,args.note)
                print('Operator-provided IOC registered. Not independently verified malware.');return 0
        if args.cmd=='integrity':
            ok,count,bad=store.verify_chain()
            pprint({'chain_valid':ok,'events_verified':count,'first_bad_seq':bad,
                    'limitation':'A hash chain detects edits only when a trusted prior root/head hash is retained independently.'})
            return 0 if ok else EXIT_HOLD
        if args.cmd=='events':
            pprint(store.recent(max(1,min(args.limit,200))));return 0
        if args.cmd=='export':
            dest=args.path.expanduser().resolve()
            if dest.exists():
                raise RuntimeError('refusing to overwrite existing evidence export')
            dest.parent.mkdir(parents=True,exist_ok=True)
            with dest.open('x',encoding='utf-8') as out:
                for row in store.con.execute('SELECT * FROM events ORDER BY seq'):
                    out.write(json.dumps(dict(row),sort_keys=True)+'\n')
            sha=hashlib.sha256(dest.read_bytes()).hexdigest()
            manifest=dest.with_suffix(dest.suffix+'.sha256')
            manifest.write_text(f'{sha}  {dest.name}\n')
            print('EXPORTED',dest,'SHA-256',sha);return 0
        return 1
    except (RuntimeError, OSError, ValueError) as exc:
        print('HOLD:',exc,file=sys.stderr)
        return EXIT_HOLD
    except KeyboardInterrupt:
        return 130
    finally:
        store.close()
