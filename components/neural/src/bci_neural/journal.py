# BEACON COMPUTING INITIATIVE | Orbital Neural Core
# Developer Seal: CJB-DEV-2026
# File SHA-256: SHA256SUMS
"""Append-only, SHA-256 chained local candidate observation journal."""
from __future__ import annotations
import fcntl
import json
import os
from pathlib import Path
from .common import canonical,digest,validate_window,write_hashed

ZERO='0'*64


def verify(path):
    last=ZERO;n=0;records=[]
    path=Path(path)
    if not path.is_file() or path.is_symlink():raise ValueError('journal missing/unsafe')
    with path.open('r',encoding='utf-8') as f:
        for line in f:
            if len(line)>20000:raise ValueError('oversized journal record')
            obj=json.loads(line)
            sample=obj['window']; validate_window(sample)
            if obj['seq']!=n+1 or obj['prev_hash']!=last:
                raise ValueError(f'journal sequence or prev hash mismatch at {n+1}')
            expected=digest(canonical([obj['seq'],last,sample]).encode())
            if obj['entry_hash']!=expected:
                raise ValueError(f'journal hash mismatch at {n+1}')
            last=expected;n+=1;records.append(sample)
    return n,last,records


def append(path,observation):
    """Append IF AND ONLY IF existing journal verifies fully and record validates."""
    validate_window(observation)
    path=Path(path);path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    if path.is_symlink():raise ValueError('unsafe journal path')
    lock=Path(str(path)+'.lock')
    with lock.open('a+') as f:
        os.chmod(lock,0o600)
        fcntl.flock(f.fileno(),fcntl.LOCK_EX)
        if path.exists(): n,prev,_=verify(path)
        else:n,prev=0,ZERO
        seq=n+1
        entry={'seq':seq,'prev_hash':prev,'window':observation}
        entry['entry_hash']=digest(canonical([seq,prev,observation]).encode())
        flags=os.O_APPEND|os.O_CREAT|os.O_WRONLY|getattr(os,'O_NOFOLLOW',0)
        fd=os.open(path,flags,0o600)
        with os.fdopen(fd,'a',encoding='utf-8') as out:
            out.write(canonical(entry)+'\n');out.flush();os.fsync(out.fileno())
        return entry['entry_hash']


def freeze(journal,dest,context=None):
    count,head,items=verify(journal)
    if not count:raise ValueError('empty journal')
    selected=[r for r in items if context is None or r['context']==context]
    if not selected:raise ValueError('no windows for requested context')
    payload=('\n'.join(canonical(r) for r in selected)+'\n').encode()
    output_sha=write_hashed(dest,payload)
    return {'windows':len(selected),'journal_count':count,'journal_head_sha256':head,
            'dataset_sha256':output_sha,'context':context or 'MIXED',
            'trust':'unreviewed_live'}
