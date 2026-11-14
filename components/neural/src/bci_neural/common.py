# BEACON COMPUTING INITIATIVE | Orbital Neural Core
# Developer Seal: CJB-DEV-2026
# File SHA-256: SHA256SUMS
"""Strict data shapes, hashes and atomic create-only report/model artifacts."""
from __future__ import annotations
import hashlib
import json
import math
import os
from pathlib import Path
from datetime import datetime, timezone

HEADER = 'BEACON COMPUTING INITIATIVE'
SEAL = 'CJB-DEV-2026'
SCHEMA = 'bci.neural.window.v1'
MODEL_SCHEMA = 'bci.neural.autoencoder.v1'
# Fixed order is part of the model architecture, never derived from file order.
FEATURES = (
    'process_count', 'listener_count', 'outbound_count', 'inbound_count',
    'remote_unique_count', 'usb_mount_count', 'risky_process_count',
    'public_listener_count', 'unusual_remote_port_count',
    'rx_kib_per_second', 'tx_kib_per_second', 'visibility_issue_count',
)
COVERAGE = {'process', 'listener', 'network', 'storage'}
HOLD = 3


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def digest(data: bytes):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for piece in iter(lambda: f.read(1024*1024), b''):
            h.update(piece)
    return h.hexdigest()


def parse_time(value):
    if not isinstance(value, str):
        raise ValueError('time must be an offset-aware ISO 8601 string')
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as exc:
        raise ValueError('invalid timestamp') from exc
    if dt.tzinfo is None or dt.year < 2020 or dt > datetime.now(timezone.utc).replace(microsecond=0):
        raise ValueError('invalid, future, or timezone-free timestamp')
    return dt.astimezone(timezone.utc)


def validate_window(item):
    if (not isinstance(item, dict) or item.get('schema') != SCHEMA or
            item.get('header') != HEADER or item.get('developer_seal') != SEAL):
        raise ValueError('window schema, BCI header or developer seal mismatch')
    dt = parse_time(item.get('ts'))
    ctx = item.get('context')
    if not isinstance(ctx, str) or len(ctx) > 150 or not ctx or ctx == 'ctx-unknown':
        raise ValueError('unqualified network context')
    vals = item.get('features')
    if not isinstance(vals, dict) or set(vals) != set(FEATURES):
        raise ValueError('exact feature schema required')
    for k in FEATURES:
        v = vals[k]
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0 or v > 1e12:
            raise ValueError('invalid nonnegative feature: ' + k)
    if item.get('trust') not in ('unreviewed_live', 'untrusted_legacy', 'approved_candidate', 'synthetic_demo'):
        raise ValueError('invalid trust classification')
    coverage = item.get('coverage')
    if not isinstance(coverage, list) or len(coverage) != len(set(coverage)) or any(not isinstance(x,str) for x in coverage):
        raise ValueError('invalid coverage')
    if not set(coverage) <= COVERAGE:
        raise ValueError('unknown sensor coverage')
    gaps = item.get('gaps')
    if not isinstance(gaps,list) or len(gaps)>16 or any(not isinstance(s,str) or len(s)>200 for s in gaps):
        raise ValueError('invalid sensor gaps')
    return dt


def load_jsonl(path, max_rows=200000):
    out=[]
    with Path(path).open('r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if i>max_rows: raise ValueError('dataset exceeds max rows')
            if len(line)>16384: raise ValueError('oversized record')
            if not line.strip(): continue
            item=json.loads(line)
            validate_window(item)
            out.append(item)
    if not out: raise ValueError('empty dataset')
    return out


def _exclusive_write(path, data):
    path = Path(path)
    if path.is_symlink() or path.exists():
        raise FileExistsError('refusing to overwrite or follow output: '+str(path))
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.parent.is_symlink():
        raise ValueError('refusing symlink output parent')
    fd = os.open(path, os.O_CREAT|os.O_EXCL|os.O_WRONLY|getattr(os,'O_NOFOLLOW',0), 0o600)
    try:
        with os.fdopen(fd,'wb') as writer:
            writer.write(data); writer.flush(); os.fsync(writer.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def write_hashed(path, payload):
    """Create output and SHA256 sidecar IF AND ONLY IF neither exists."""
    path = Path(path)
    side = Path(str(path)+'.sha256')
    if path.exists() or side.exists() or path.is_symlink() or side.is_symlink():
        raise FileExistsError('output or SHA256 sidecar exists')
    if not isinstance(payload,bytes):
        payload=(json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
    _exclusive_write(path,payload)
    try:
        _exclusive_write(side,f'{digest(payload)}  {path.name}\n'.encode())
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    return digest(payload)


def verify_sidecar(path):
    path=Path(path); side=Path(str(path)+'.sha256')
    if not side.is_file() or side.is_symlink() or path.is_symlink():
        raise ValueError('missing checksum or symlink')
    expected=side.read_text().strip().split()
    if len(expected)!=2 or expected[1]!=path.name or expected[0]!=file_digest(path):
        raise ValueError('SHA-256 checksum mismatch')
    return expected[0]


def window(context,ts,features,trust,coverage,gaps=None,source=None):
    obj={'header':HEADER,'developer_seal':SEAL,'schema':SCHEMA,'ts':ts,'context':context,'features':features,
         'trust':trust,'coverage':sorted(coverage),'gaps':gaps or [],'source':source or 'unspecified'}
    validate_window(obj)
    return obj
