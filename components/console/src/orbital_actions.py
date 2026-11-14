#!/usr/bin/env python3
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# File SHA-256: SHA256SUMS
# v0.7.1 — Operator actions run IF AND ONLY IF their verification gates pass.
"""Bounded, non-shell backend operations for the PyQt6 Orbital dashboard.

This module must not modify services or security response policies. It can create
new, untrusted candidate files and request existing native Neural Core operations.
"""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

from orbital_backend import (HEADER, SEAL, HOME, JOURNAL, HOST, NEURAL,
                             verify_rate_journal, sha256, canonical)

RATE_ROOT = HOME/'.local/state/bci-orbital-gui/candidates'
PYC = HOME/'.local/opt/bci-orbital-neural/0.2.0/src'
PACKET_RUNNER = Path('/opt/bci-orbital-dynamic/0.4.1/scripts/runner.py')
MAX_OUTPUT=1024*1024

class Hold(RuntimeError):
    pass


def bounded(argv, timeout=20, env=None):
    """Execute fixed argv IF AND ONLY IF a validated program path exists."""
    if not argv or not Path(str(argv[0])).is_file() and '/' in str(argv[0]):
        raise Hold('Executable missing: '+str(argv[0] if argv else '?'))
    try:
        run=subprocess.run([str(x) for x in argv],capture_output=True,timeout=timeout,
            text=True,check=False,env=env)
    except (OSError,subprocess.TimeoutExpired) as exc:
        raise Hold('Operation unavailable or timed out') from exc
    if len(run.stdout)+len(run.stderr)>MAX_OUTPUT:
        raise Hold('Operation output exceeds safe limit')
    if run.returncode:
        raise Hold((run.stderr or run.stdout or 'Execution failed')[-1600:])
    return run.stdout.strip()


def verified_preparation_status(data):
    """Readiness means eligible for review only, not approved benign training."""
    matched=data.get('journal_valid') is True
    hours=int(data.get('hours') or 0); days=float(data.get('days') or 0.)
    count=int(data.get('neural_window_count') or 0)
    ctx=data.get('current_context')
    summary=(data.get('journal') or {}).get('contexts',{}).get(ctx,{})
    gaps=summary.get('gaps', ['unknown'])
    try:
        last=datetime.fromisoformat(summary['last'].replace('Z','+00:00'))
        age=(datetime.now(timezone.utc)-last.astimezone(timezone.utc)).total_seconds()
    except (ValueError,KeyError,AttributeError):age=-1
    fresh=0<=age<=12*60
    iface=(data.get('current_interface')==summary.get('network_interface')
           and data.get('current_interface') not in ('unknown',None))
    history_safe=(summary.get('any_gaps') is False and
                  summary.get('timestamps_monotonic') is True and
                  summary.get('provenance_consistent') is True and
                  summary.get('future_observations') is False)
    qualified=bool(history_safe and matched and ctx and ctx.startswith('ctx-') and count>=80 and
                   hours>=24 and days>=7 and not gaps and iface and fresh)
    return {'qualified_for_review':qualified,'windows':count,'hours':hours,
            'days':round(days,4),'journal_valid':matched,'context':ctx,
            'no_reported_gaps':not gaps and summary.get('any_gaps') is False,
            'history_safe':history_safe,'last_window_fresh':fresh,
            'interface_matches':iface,'training_authorized':False,
            'baseline_approved':False,'containment_authorized':False}


def make_candidate(data, directory=RATE_ROOT):
    """Write a new qualified, context-only candidate from a verified journal.

    Never changes the live journal or approves the data as benign. Re-checks the
    current live context and journal chain IF AND ONLY IF readiness passes.
    """
    ready=verified_preparation_status(data)
    if not ready['qualified_for_review']:
        raise Hold('HOLD: 7 days, 24 distinct hours, 80 windows, clean/current context required. '+json.dumps(ready))
    journal=verify_rate_journal(JOURNAL)
    if (not journal['valid'] or journal['count']!=(data.get('journal') or {}).get('count')
            or journal['head']!=(data.get('journal') or {}).get('head')):
        raise Hold('HOLD: Live journal changed or failed integrity verification; refresh first')
    context=ready['context']
    samples=[]
    with JOURNAL.open('r',encoding='utf-8') as stream:
        for line in stream:
            obj=json.loads(line)
            win=obj['window']
            if win.get('context')==context:
                if win.get('trust')!='unreviewed_live' or win.get('gaps'):
                    raise Hold('HOLD: Candidate contains unreviewed gaps or unexpected trust class')
                samples.append(win)
    if len(samples)!=ready['windows']:
        raise Hold('HOLD: Context selection changed during preparation')
    directory=Path(directory)
    if directory.is_symlink():raise Hold('Unsafe candidate directory')
    directory.mkdir(parents=True,exist_ok=True,mode=0o700)
    if directory.stat().st_mode & 0o077:raise Hold('Unsafe candidate directory permissions')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    dest=directory/f'orbital-candidate-{stamp}.jsonl'
    payload=(''.join(canonical(w)+'\n' for w in samples)).encode()
    digest=hashlib.sha256(payload).hexdigest()
    flags=os.O_CREAT|os.O_EXCL|os.O_WRONLY|getattr(os,'O_NOFOLLOW',0)
    fd=os.open(dest,flags,0o600)
    with os.fdopen(fd,'wb') as out:
        out.write(payload);out.flush();os.fsync(out.fileno())
    side=Path(str(dest)+'.sha256')
    fd=os.open(side,flags,0o600)
    with os.fdopen(fd,'w',encoding='utf-8') as out:
        out.write(f'{digest}  {dest.name}\n');out.flush();os.fsync(out.fileno())
    return {'header':HEADER,'developer_seal':SEAL,'status':'CANDIDATE_ONLY',
            'dataset':str(dest),'sha256':digest,'windows':len(samples),
            'context':context,'classification':'unreviewed_live',
            'training_authorized':False,'containment_authorized':False}


def neural_command(*args, timeout=25):
    if not NEURAL.is_file():raise Hold('Neural CLI missing')
    return bounded([NEURAL,*args],timeout=timeout)


def review_candidate(path,context):
    p=Path(path)
    if not p.is_file() or p.is_symlink() or p.suffix!='.jsonl':
        raise Hold('Select a regular JSONL dataset')
    return neural_command('review','--input',p,'--context',context)


def host_evidence():
    return bounded([HOST,'integrity','verify'],timeout=12)


def packet_evidence_with_polkit():
    """Explicit opt-in privilege path; never invoked by automatic refresh."""
    from shutil import which
    if not PACKET_RUNNER.is_file():raise Hold('Root packet runner v0.4.1 missing')
    executable=which('pkexec')
    if not executable:raise Hold('pkexec is unavailable. Use sudo from a trusted terminal to verify packet evidence.')
    return bounded([executable,'/usr/bin/python3','-I','-B',PACKET_RUNNER,'verify'],timeout=45)


def service_logs(kind='host'):
    specs={
      'host':['journalctl','--user','-u','bci-orbital-v2.service','-n','65','--no-pager','-l'],
      'neural':['journalctl','--user','-u','bci-orbital-neural.service','-n','65','--no-pager','-l'],
      'packet':['journalctl','-u','bci-orbital-dynamic.service','-n','65','--no-pager','-l'],
    }
    if kind not in specs:raise Hold('Unsupported service journal')
    return bounded(specs[kind],timeout=8)
