# BEACON COMPUTING INITIATIVE | Orbital Kernel Evidence Bridge
# Developer Seal: CJB-DEV-2026 | SHA-256: see SHA256SUMS
"""Operator-authorized bounded bpftrace file-open and exec attempt observations.

This records syscall entry attempts, never claims file reads/writes succeeded.
No audit rules, kernel settings or host files are modified.
"""
from __future__ import annotations
import hashlib
import hmac
import os
import re
import shutil
import subprocess
import secrets
from .common import report

TRACE='''tracepoint:syscalls:sys_enter_openat
{ printf("BCI_OPEN\\t%llu\\t%s\\t%s\\n", pid, comm, str(args.filename)); }
tracepoint:syscalls:sys_enter_execve
{ printf("BCI_EXEC\\t%llu\\t%s\\t%s\\n", pid, comm, str(args.filename)); }
'''
LINE=re.compile(r'^(BCI_OPEN|BCI_EXEC)\t(\d{1,12})\t([^\t\n]{1,100})\t([^\n]{0,4096})$')

def process_key(pid):
    try:
        raw=open(f'/proc/{pid}/stat',encoding='utf-8').read()
        # The comm field can contain spaces and parentheses. Split after LAST ') '.
        rest=raw.rsplit(') ',1)[1].split()
        start=rest[19]  # field 22, rest begins with field 3
        boot=open('/proc/sys/kernel/random/boot_id').read().strip()
        return f'{boot}:{pid}:{start}'
    except (OSError,IndexError,ValueError):return None

def parse_events(text,key,limit=2000):
    events=[];skips=0
    for line in text.splitlines():
        if len(events)>=limit:break
        match=LINE.match(line)
        if not match:
            if line.startswith('BCI_'):skips+=1
            continue
        kind,pid_s,comm,path=match.groups();pid=int(pid_s)
        # Paths can expose private filenames; use keyed hashes by default.
        events.append({'kind':'file_open_attempt' if kind=='BCI_OPEN' else 'exec_attempt',
                       'pid':pid,'process_key':process_key(pid),
                       'comm':comm,'path_hmac_sha256':hmac.new(key,path.encode(),hashlib.sha256).hexdigest(),
                       'evidence_strength':'syscall_entry_attempt_only',
                       'process_identity_stable':process_key(pid) is not None})
    return events,skips

def collect(seconds=3,max_events=2000):
    if not 1<=seconds<=20 or not 1<=max_events<=2000:raise ValueError('HOLD: trace limits exceeded')
    if not shutil.which('bpftrace'):raise RuntimeError('HOLD: bpftrace not installed; no kernel events collected')
    try:
        p=subprocess.run(['bpftrace','-q','-e',TRACE],capture_output=True,text=True,
                         timeout=seconds,check=False,env={**os.environ,'LC_ALL':'C'})
        # bpftrace runs continuously: hitting timeout is expected; subprocess.run kills it.
        stdout=p.stdout;exit_code=p.returncode;partial=False
    except subprocess.TimeoutExpired as exc:
        stdout=(exc.stdout or b'').decode(errors='replace') if isinstance(exc.stdout,bytes) else (exc.stdout or '')
        exit_code=None;partial=True
    if not partial and exit_code not in (0,None):raise RuntimeError('HOLD: bpftrace exited with error; no successful trace inferred')
    key=secrets.token_bytes(32);events,skips=parse_events(stdout,key,max_events)
    return report('kernel_ebpf_observation',events=events,parsed_events=len(events),invalid_records=skips,
                  trace_seconds_requested=seconds,trace_interrupted_by_bounded_timeout=partial,
                  gaps=['syscall entry does not prove file access succeeded',
                        'openat/execve only; not comprehensive file read/write telemetry',
                        'PID may exit before stable identity can be read',
                        'event output may be truncated or dropped by tracing mechanism'],
                  source='bpftrace Linux syscall tracepoints',automatic_containment_authorized=False)
