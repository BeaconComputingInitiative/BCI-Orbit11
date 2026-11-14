# BEACON COMPUTING INITIATIVE | Orbital Expansion
# Developer Seal: CJB-DEV-2026 | SHA-256: see SHA256SUMS
"""Create-only hashed reports and safe, bounded serialization."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone

HEADER = 'BEACON COMPUTING INITIATIVE'
SEAL = 'CJB-DEV-2026'

def utcnow():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def digest(data: bytes):
    return hashlib.sha256(data).hexdigest()

def filehash(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1<<20), b''):
            h.update(block)
    return h.hexdigest()

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)

def verify_file(path):
    f = Path(path); s = Path(str(f) + '.sha256')
    if f.is_symlink() or s.is_symlink() or not f.is_file() or not s.is_file():
        raise ValueError('HOLD: hashed file or checksum missing/symlink')
    parts = s.read_text().strip().split()
    if len(parts) != 2 or parts[1] != f.name or parts[0] != filehash(f):
        raise ValueError('HOLD: checksum mismatch')
    return parts[0]

def _exclusive(path, payload):
    p=Path(path)
    if p.is_symlink() or p.exists(): raise FileExistsError('HOLD: refusing overwrite')
    if p.parent.is_symlink(): raise ValueError('HOLD: output parent symlink')
    p.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    fd=os.open(str(p),os.O_CREAT|os.O_EXCL|os.O_WRONLY|getattr(os,'O_NOFOLLOW',0),0o600)
    try:
        with os.fdopen(fd,'wb') as file:
            file.write(payload); file.flush(); os.fsync(file.fileno())
    except BaseException:
        p.unlink(missing_ok=True)
        raise

def save_hashed(path, obj):
    p=Path(path); side=Path(str(p)+'.sha256')
    if p.exists() or side.exists() or p.is_symlink() or side.is_symlink():
        raise FileExistsError('HOLD: report already exists')
    payload=(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
    _exclusive(p,payload)
    try: _exclusive(side,(digest(payload)+'  '+p.name+'\n').encode())
    except BaseException:
        p.unlink(missing_ok=True)
        raise
    return digest(payload)

def report(kind,**kwargs):
    return dict(header=HEADER,developer_seal=SEAL,version='0.3.0',type=kind,generated_utc=utcnow(),**kwargs)


def save_jsonl_hashed(path, objects):
    """Create immutable line-oriented candidates IF AND ONLY IF filenames are unused."""
    p=Path(path);side=Path(str(p)+'.sha256')
    if any(x.exists() or x.is_symlink() for x in (p,side)):
        raise FileExistsError('HOLD: candidate already exists')
    if not objects:raise ValueError('HOLD: no windows to write')
    payload=(''.join(canonical(item)+'\n' for item in objects)).encode()
    _exclusive(p,payload)
    try:_exclusive(side,(digest(payload)+'  '+p.name+'\n').encode())
    except BaseException:
        p.unlink(missing_ok=True)
        raise
    return digest(payload)
