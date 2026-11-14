#!/usr/bin/env python3
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Project: Orbital Group 15 - Rate-Aware Neural Telemetry
# Version: 0.5.1
# File SHA-256: companion BCI-Orbital-Group15-v0.5.1.py.sha256
# Execution continues IF AND ONLY IF preceding integrity gates succeed.
"""Four-stage qualified migration from zero-filled neural telemetry to rate-aware telemetry.

Unprivileged execution only.  A single script runs:
  1. Source, identity, and service verification.
  2. Measurement of a full live window via v0.3.0 expansion.
  3. Verification and append to a SEPARATE hash-chained candidate journal.
  4. Explicitly authorized replacement of the existing neural service ExecStart.

The existing systemd timer is retained; no duplicate timer is created.
Original journal, model, packet evidence, and containment configuration are untouched.
No neural training or scoring is performed here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone

HEADER = 'BEACON COMPUTING INITIATIVE'
SEAL = 'CJB-DEV-2026'
VERSION = '0.5.1'
SCRIPT = 'BCI-Orbital-Group15-v0.5.1.py'
UNIT = 'bci-orbital-neural.service'
TIMER = 'bci-orbital-neural.timer'
MAX_JSON = 4 * 1024 * 1024
ROOT = Path('/home/bci')
RELEASES = {
    'host': ROOT / '.local/opt/bci-orbital-v2/0.1.0',
    'neural': ROOT / '.local/opt/bci-orbital-neural/0.2.0',
    'expansion': ROOT / '.local/opt/bci-orbital-expansion/0.3.0',
}
BIN = ROOT / '.local/bin/bci-orbital-expansion'
NEURAL_BIN = ROOT / '.local/bin/bci-orbital-neural'
STATE = ROOT / '.local/state/bci-orbital-integration-v0.5.1'
JOURNAL = STATE / 'rate-aware-journal.jsonl'
DEST = ROOT / '.local/opt/bci-orbital-integration/0.5.1' / SCRIPT
UNIT_PATH = ROOT / '.config/systemd/user' / UNIT

class Hold(Exception):
    pass

def utc():
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

def sha(path: Path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def private_dir(p: Path):
    if p.is_symlink():
        raise Hold('symlinked private directory: ' + str(p))
    p.mkdir(parents=True, exist_ok=True, mode=0o700)
    if p.stat().st_mode & 0o077:
        raise Hold('private directory has unsafe permissions: ' + str(p))
    return p

def new_run():
    private_dir(STATE)
    root = private_dir(STATE / 'runs')
    p = root / ('group15-' + utc() + '-' + secrets.token_hex(4))
    p.mkdir(mode=0o700)
    return p

def atomic_file(p: Path, contents: bytes):
    if p.exists() or p.is_symlink():
        raise Hold('refusing overwrite: ' + str(p))
    if p.parent.is_symlink():
        raise Hold('output parent is symlink')
    fd = os.open(p, os.O_EXCL | os.O_CREAT | os.O_WRONLY | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(contents)
            f.flush()
            os.fsync(f.fileno())
    except BaseException:
        p.unlink(missing_ok=True)
        raise

def save_json(p: Path, obj):
    contents = (json.dumps(obj, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    atomic_file(p, contents)
    atomic_file(Path(str(p) + '.sha256'), (hashlib.sha256(contents).hexdigest() + '  ' + p.name + '\n').encode())
    return hashlib.sha256(contents).hexdigest()

def verify_sidecar(path: Path):
    side = Path(str(path) + '.sha256')
    if any(p.is_symlink() or not p.is_file() for p in (path,side)):
        raise Hold('missing or symlinked artifact/sidecar: ' + str(path))
    if side.stat().st_size > 200:
        raise Hold('oversized checksum sidecar')
    bits = side.read_text(encoding='ascii').strip().split()
    if len(bits) != 2 or bits[0] != sha(path) or bits[1] != path.name:
        raise Hold('checksum mismatch: ' + str(path))
    return bits[0]

def verify_manifest(root: Path):
    if root.is_symlink() or not root.is_dir():
        raise Hold('release directory invalid: '+str(root))
    mf = root / 'SHA256SUMS'
    if mf.is_symlink() or not mf.is_file():
        raise Hold('manifest absent: ' + str(root))
    ms = Path(str(mf)+'.sha256')
    if ms.exists() or ms.is_symlink():
        verify_sidecar(mf)
    seen=set()
    for line in mf.read_text(encoding='ascii').splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        m=re.fullmatch(r'([a-f0-9]{64})  (.+)',line)
        if not m:
            raise Hold('invalid manifest entry')
        dig,name=m.groups()
        name=name.removeprefix('./')
        rel=Path(name)
        if rel.is_absolute() or '..' in rel.parts or name in seen:
            raise Hold('unsafe manifest path')
        seen.add(name)
        p=root/rel
        if p.is_symlink() or not p.is_file() or sha(p)!=dig:
            raise Hold('source SHA-256 mismatch: ' + name)
    if not seen:
        raise Hold('empty source manifest')
    return len(seen)

def run(argv, timeout=60):
    try:
        p=subprocess.run([str(x) for x in argv], text=True, capture_output=True,
             timeout=timeout, env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'}, check=False)
    except (OSError,subprocess.TimeoutExpired) as e:
        raise Hold('command unavailable/timed out: '+str(argv[:2])) from e
    if len(p.stdout)>MAX_JSON or len(p.stderr)>MAX_JSON:
        raise Hold('oversized command output')
    if p.returncode:
        raise Hold('command failed: '+str(argv[:3])+' | '+p.stderr[-400:])
    return p.stdout.strip()

def command_json(argv,timeout=60):
    try:
        x=json.loads(run(argv,timeout))
    except json.JSONDecodeError as e:
        raise Hold('command JSON decode failed: '+str(argv[:2])) from e
    if not isinstance(x,dict) or x.get('header')!=HEADER or x.get('developer_seal')!=SEAL:
        raise Hold('unexpected BCI command schema')
    return x

def assert_bci():
    if os.geteuid()==0 or os.environ.get('USER')!='bci' or Path.home()!=ROOT:
        raise Hold('run as unprivileged /home/bci user; never via sudo')

def validated_window(ctx,window):
    if window.get('schema')!='bci.neural.window.v1' or window.get('trust')!='unreviewed_live':
        raise Hold('wrong window schema or trust')
    if not window.get('context','').startswith('ctx-'):
        raise Hold('unexpected/unknown live context')
    prov=window.get('measurement_provenance') or {}
    if (prov.get('host_id')!=ctx.get('host_id') or
        prov.get('route_id')!=ctx.get('route_id') or
        prov.get('throughput_source')!='/proc/net/dev' or
        not prov.get('network_interface')):
        raise Hold('unstable or missing network/host provenance')
    if 'throughput_rates_not_available_in_v0.1.0_collector' in window.get('gaps',[]):
        raise Hold('placeholder throughput present')
    if set(window.get('coverage',[]))!={'process','listener','network','storage'}:
        raise Hold('incomplete feature coverage')
    return prov

def verified_imports():
    # Only after manifest checks; the imported code cannot be run as root.
    source = RELEASES['neural'] / 'src'
    if str(source) not in sys.path:
        sys.path.insert(0,str(source))
    from bci_neural.common import validate_window
    from bci_neural.journal import append, verify
    return validate_window, append, verify

def collect_one(run_dir: Path):
    # This function is called by the existing five-minute timer after explicit swap.
    for root in RELEASES.values():
        verify_manifest(root)
    ctx_path=run_dir/'context.json'
    win_path=run_dir/'live-window.jsonl'
    command_json([BIN, 'context', '--output', ctx_path],timeout=30)
    verify_sidecar(ctx_path)
    ctx=json.loads(ctx_path.read_text(encoding='utf-8'))
    command_json([BIN, 'capture-window', '--orbital-release',RELEASES['host'],
                  '--neural-release',RELEASES['neural'], '--seconds','2',
                  '--output',win_path],timeout=50)
    verify_sidecar(win_path)
    data=win_path.read_text(encoding='utf-8').splitlines()
    if len(data)!=1 or len(data[0])>16384:
        raise Hold('expected exactly one bounded window')
    w=json.loads(data[0])
    validate,append,verify=verified_imports()
    validate(w)
    prov=validated_window(ctx,w)
    private_dir(STATE)
    head=append(JOURNAL,w)
    n,actual_head,_=verify(JOURNAL)
    if actual_head!=head:
        raise Hold('appended journal did not verify')
    details={'header':HEADER,'developer_seal':SEAL,'version':VERSION,
             'status':'RATE_AWARE_WINDOW_VERIFIED','trust':w['trust'],
             'context':w['context'],'host_id':prov['host_id'],
             'route_id':prov['route_id'],'network_interface':prov['network_interface'],
             'source_window_sha256':sha(win_path),'journal_head_sha256':head,
             'journal_entries_verified':n,'gaps':w['gaps'],
             'model_promoted':False,'training_authorized':False,
             'containment_authorized':False}
    report_hash=save_json(run_dir/'capture-report.json',details)
    return details,report_hash

def report_manifest(run_dir:Path):
    lines=[]
    for p in sorted(run_dir.iterdir()):
        if p.is_file() and not p.is_symlink():
            lines.append(f'{sha(p)}  {p.name}\n')
    atomic_file(run_dir/'SHA256SUMS',''.join(lines).encode())
    atomic_file(run_dir/'SHA256SUMS.sha256',(sha(run_dir/'SHA256SUMS')+'  SHA256SUMS\n').encode())
    return sha(run_dir/'SHA256SUMS')

def collection_mode():
    assert_bci()
    verify_sidecar(Path(__file__).absolute())
    run_dir=new_run()
    result,_=collect_one(run_dir)
    report_manifest(run_dir)
    print(json.dumps(result,indent=2))
    print('PASS: BCI RATE-AWARE COLLECTION VERIFIED; no training or response')

def make_unit(script_path:Path):
    # systemd unit is a generated file and is included in the deployment manifest.
    return (f'''# BEACON COMPUTING INITIATIVE\n# Developer Seal: {SEAL}\n# File SHA-256: deployment SHA256SUMS\n# Execution IF AND ONLY IF source/runtime integrity gates pass.\n[Unit]\nDescription=BCI Orbital neural sidecar rate-aware candidate feature capture\nAfter=default.target\n\n[Service]\nType=oneshot\nExecStart=/usr/bin/python3 -B {script_path} --collect\nUMask=0077\nNoNewPrivileges=yes\nPrivateTmp=yes\nProtectControlGroups=yes\nProtectKernelModules=yes\nProtectKernelTunables=yes\nRestrictSUIDSGID=yes\nTimeoutStartSec=90s\n''').encode()

def safe_replace_unit(new_bytes:bytes, backup:Path):
    if UNIT_PATH.is_symlink() or not UNIT_PATH.is_file():
        raise Hold('existing neural service unit missing or symlinked')
    old=UNIT_PATH.read_bytes()
    atomic_file(backup,old)
    atomic_file(Path(str(backup)+'.sha256'), (hashlib.sha256(old).hexdigest()+'  '+backup.name+'\n').encode())
    temp=UNIT_PATH.parent/(UNIT+'.new-'+secrets.token_hex(4))
    atomic_file(temp,new_bytes)
    os.chmod(temp,0o600)
    os.replace(temp,UNIT_PATH)
    return old

def rollback(old:bytes):
    # Best-effort restore after a failed install; no evidence data is rolled back.
    temp=UNIT_PATH.parent/(UNIT+'.rollback-'+secrets.token_hex(4))
    atomic_file(temp,old)
    os.replace(temp,UNIT_PATH)
    try:
        run(['systemctl','--user','daemon-reload'],timeout=20)
        run(['systemctl','--user','start',TIMER],timeout=20)
    except Hold:
        pass

def install_mode():
    assert_bci()
    src=Path(__file__).absolute()
    if src.name != SCRIPT:
        raise Hold('script must keep versioned release filename')
    script_hash=verify_sidecar(src)
    os.umask(0o077)
    print(HEADER+'\nDeveloper Seal: '+SEAL)
    print('Group 15 — Four Steps / One Script')
    print('=== STEP 1/4: VERIFY RELEASES + SERVICES ===')
    file_counts={k:verify_manifest(v) for k,v in RELEASES.items()}
    if run(['systemctl','--user','is-active','bci-orbital-v2.service'])!='active':
        raise Hold('Orbital v2 not active')
    if run(['systemctl','--user','is-active',TIMER])!='active':
        raise Hold('neural timer not active')
    run_dir=new_run()
    save_json(run_dir/'step1-releases.json',{
        'header':HEADER,'developer_seal':SEAL,'source_script_sha256':script_hash,
        'release_files_verified':file_counts,'old_timer_active':True})
    print('PASS: installed sources and monitoring services verified')
    print('=== STEP 2/4: COLLECT VERIFIED RATE-AWARE WINDOW ===')
    details,_=collect_one(run_dir)
    print('PASS: rate-aware window captured for context '+details['context'])
    print('=== STEP 3/4: VERIFY SEPARATE CANDIDATE JOURNAL ===')
    validate,append,verify=verified_imports()
    n,head,windows=verify(JOURNAL)
    if n<1 or head!=details['journal_head_sha256']:
        raise Hold('journal mismatch after capture')
    # The previous neural journal is NEVER modified or merged with this one.
    save_json(run_dir/'step3-journal.json',{
        'header':HEADER,'developer_seal':SEAL,'candidate_journal':str(JOURNAL),
        'current_window_count':n,'context_counts':{c:sum(w['context']==c for w in windows)
                for c in sorted(set(w['context'] for w in windows))},
        'journal_head_sha256':head,'training_approved':False,
        'legacy_data_merged':False})
    print('PASS: independent rate-aware candidate journal verified')
    print('=== STEP 4/4: OPTIONAL SAME-TIMER SERVICE UPGRADE ===')
    if not sys.stdin.isatty():
        print('HOLD: Interactive authorization unavailable; no service change')
        report_manifest(run_dir)
        print('Candidate/report directory: '+str(run_dir))
        return
    print('This replaces ONLY the existing neural service command, not its timer.')
    print('Original neural journal and security evidence remain unchanged.')
    phrase=input('Type ACTIVATE-RATE-AWARE to authorize service update: ').strip()
    if phrase!='ACTIVATE-RATE-AWARE':
        print('HOLD: Authorization declined; rate-aware sample remains untrusted')
        report_manifest(run_dir)
        print('Candidate/report directory: '+str(run_dir))
        return
    private_dir(DEST.parent)
    original_bytes=src.read_bytes()
    if DEST.exists() or DEST.is_symlink():
        if DEST.is_symlink() or verify_sidecar(DEST)!=script_hash:
            raise Hold('installed script differs from verified release; refusing overwrite')
    else:
        atomic_file(DEST,original_bytes)
        atomic_file(Path(str(DEST)+'.sha256'), (script_hash+'  '+DEST.name+'\n').encode())
    verify_sidecar(DEST)
    unit_bytes=make_unit(DEST)
    if UNIT_PATH.is_file() and not UNIT_PATH.is_symlink() and UNIT_PATH.read_bytes()==unit_bytes:
        if run(['systemctl','--user','is-active',TIMER])!='active':
            raise Hold('rate-aware unit already installed but timer inactive; examine service')
        save_json(run_dir/'step4-activation.json',{
            'header':HEADER,'developer_seal':SEAL,
            'status':'RATE_AWARE_SERVICE_ALREADY_CONFIGURED',
            'service_unit_sha256':sha(UNIT_PATH),
            'existing_timer_reused':True,'old_journal_preserved':True,
            'containment_authorized':False,'training_authorized':False})
        report_manifest(run_dir)
        print('PASS: rate-aware neural service already configured; no duplicate installation')
        print('Report: '+str(run_dir))
        return
    unit_backup=run_dir/'previous-neural.service'
    old=None
    timer_stopped=False
    try:
        run(['systemctl','--user','stop',TIMER],timeout=20)
        timer_stopped=True
        old=safe_replace_unit(unit_bytes,unit_backup)
        run(['systemctl','--user','daemon-reload'],timeout=20)
        run(['systemctl','--user','start',UNIT],timeout=90)
        run(['systemctl','--user','start',TIMER],timeout=20)
        if run(['systemctl','--user','is-active',TIMER])!='active':
            raise Hold('neural timer failed to restart')
        _,_,new_records=verify(JOURNAL)
        if len(new_records)<=n:
            raise Hold('new service did not append a verified window')
    except Exception:
        if old is not None:
            rollback(old)
        elif timer_stopped:
            try:run(['systemctl','--user','start',TIMER],timeout=20)
            except Hold:pass
        raise
    deploy={'header':HEADER,'developer_seal':SEAL,
            'status':'RATE_AWARE_NEURAL_TIMER_ACTIVATED',
            'installed_script_sha256':sha(DEST),
            'service_unit_sha256':sha(UNIT_PATH),
            'old_service_unit_backup_sha256':sha(unit_backup),
            'existing_timer_reused':True,'duplicate_timer_created':False,
            'old_journal_preserved':True,'containment_authorized':False,
            'model_training_authorized':False}
    save_json(run_dir/'step4-activation.json',deploy)
    print('PASS: existing five-minute neural timer now collects measured throughput')
    print('PASS: original journal/model/evidence retained')
    report_manifest(run_dir)
    print('Report: '+str(run_dir))
    print('SHA-256 manifest: '+sha(run_dir/'SHA256SUMS'))
    print('HOLD: model training, live scoring, and containment not authorized')

class SelfTests(unittest.TestCase):
    def test_sidecar_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'one.json'
            save_json(p,{'header':HEADER,'developer_seal':SEAL})
            self.assertEqual(verify_sidecar(p),sha(p))
    def test_sidecar_tamper(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'one.json'
            save_json(p,{'header':HEADER})
            p.write_text('tampered')
            with self.assertRaises(Hold):verify_sidecar(p)
    def test_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);(p/'a').write_text('abc')
            (p/'SHA256SUMS').write_text('# comment\n'+sha(p/'a')+'  ./a\n')
            self.assertEqual(verify_manifest(p),1)
    def test_manifest_rejects_traversal(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);(p/'SHA256SUMS').write_text('0'*64+'  ../bad\n')
            with self.assertRaises(Hold):verify_manifest(p)
    def test_window_accept_valid_provenance(self):
        ctx={'host_id':'host-1','route_id':'route-1'}
        item={'schema':'bci.neural.window.v1','trust':'unreviewed_live',
              'context':'ctx-abc','coverage':['process','listener','network','storage'],
              'gaps':[],'measurement_provenance':{'host_id':'host-1','route_id':'route-1',
              'throughput_source':'/proc/net/dev','network_interface':'usb0'}}
        self.assertEqual(validated_window(ctx,item)['network_interface'],'usb0')
    def test_window_reject_missing_rate(self):
        ctx={'host_id':'host-1','route_id':'route-1'}
        item={'schema':'bci.neural.window.v1','trust':'unreviewed_live',
              'context':'ctx-abc','coverage':['process','listener','network','storage'],
              'gaps':['throughput_rates_not_available_in_v0.1.0_collector'],
              'measurement_provenance':{'host_id':'host-1','route_id':'route-1',
              'throughput_source':'/proc/net/dev','network_interface':'usb0'}}
        with self.assertRaises(Hold):validated_window(ctx,item)
    def test_window_reject_context_mismatch(self):
        ctx={'host_id':'host-1','route_id':'route-1'}
        item={'schema':'bci.neural.window.v1','trust':'unreviewed_live',
              'context':'ctx-abc','coverage':['process','listener','network','storage'],
              'gaps':[],'measurement_provenance':{'host_id':'host-other','route_id':'route-1',
              'throughput_source':'/proc/net/dev','network_interface':'usb0'}}
        with self.assertRaises(Hold):validated_window(ctx,item)
    def test_unit_keeps_no_privilege(self):
        unit=make_unit(Path('/home/bci/example.py')).decode()
        self.assertIn('NoNewPrivileges=yes',unit)
        self.assertNotIn('sudo',unit)
        self.assertIn('--collect',unit)
    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'a';atomic_file(p,b'a')
            with self.assertRaises(Hold):atomic_file(p,b'b')

def main():
    ap=argparse.ArgumentParser(description='BCI Orbital Group 15 v0.5.1; four steps in one script')
    flags=ap.add_mutually_exclusive_group()
    flags.add_argument('--collect',action='store_true',help='timer operation; verified measured-rate candidate capture')
    flags.add_argument('--self-test',action='store_true')
    flags.add_argument('--status',action='store_true',help='read-only rate-aware journal status')
    args=ap.parse_args()
    if args.self_test:
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(SelfTests)
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() else 2
    try:
        if args.collect:
            collection_mode()
        elif args.status:
            assert_bci()
            verify_sidecar(DEST)
            for r in RELEASES.values():verify_manifest(r)
            _,_,verify=verified_imports()
            count,head,items=verify(JOURNAL)
            print(json.dumps({'header':HEADER,'developer_seal':SEAL,
                'journal_entries':count,'journal_head_sha256':head,
                'contexts':{k:sum(w['context']==k for w in items)
                     for k in sorted(set(w['context'] for w in items))},
                'training_authorized':False,'containment_authorized':False},indent=2))
        else:
            install_mode()
        return 0
    except (Hold,OSError,ValueError,KeyError,json.JSONDecodeError) as e:
        print('HOLD: '+str(e),file=sys.stderr)
        return 3

if __name__=='__main__':
    sys.exit(main())
