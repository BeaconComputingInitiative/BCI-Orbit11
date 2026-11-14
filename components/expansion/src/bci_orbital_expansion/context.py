# BEACON COMPUTING INITIATIVE | Orbital Context Engine
# Developer Seal: CJB-DEV-2026 | SHA-256: see SHA256SUMS
"""Keep host identity, routing identity, and legacy profile IDs distinct."""
from __future__ import annotations
from .common import digest, canonical, report
import json
import os
import platform
import subprocess
from pathlib import Path
from urllib.parse import quote
import sqlite3


def _read(path):
    try: return Path(path).read_text().strip()
    except OSError: return None

def default_routes():
    try:
        p=subprocess.run(['ip','-j','route','show','default'],capture_output=True,text=True,timeout=3,check=False)
        if p.returncode: return [],['ip route command failed']
        routes=json.loads(p.stdout)
        return sorted([{'dev':r.get('dev'),'gateway':r.get('gateway'),'table':r.get('table','main')} for r in routes],key=canonical),[]
    except (OSError,ValueError,subprocess.TimeoutExpired): return [],['ip route unavailable']

def fingerprint(host_secret=None,routes=None,namespace=None):
    # This host fingerprint is NOT a remote user's identity or attestation.
    if host_secret is None:host_secret=_read('/etc/machine-id')
    if routes is None:routes,_=default_routes()
    if namespace is None:
        try:namespace=os.readlink('/proc/self/ns/net')
        except OSError:namespace='unknown'
    host_id='host-'+digest((host_secret or 'unknown').encode())[:24] if host_secret else 'host-unattested'
    net_id='route-'+digest(canonical({'routes':routes,'netns':namespace}).encode())[:24] if routes else 'route-unattested'
    return {'host_id':host_id,'route_id':net_id,'namespace':namespace,
            'legacy_equivalence_verified':False,
            'note':'Host and route fingerprints are local identifiers, not proof of legitimate network identity.'}

def context_snapshot():
    routes,gaps=default_routes()
    result=fingerprint(routes=routes)
    return report('context_snapshot',**result,route_count=len(routes),gaps=gaps,
                  neural_v02_context_binding='NOT_VERIFIED')

def legacy_summary(db_path,limit=100):
    """Read only selected descriptive profile columns, no automatic ID mapping."""
    p=Path(db_path)
    if p.is_symlink() or not p.is_file():raise ValueError('HOLD: legacy SQLite missing/symlink')
    uri='file:'+quote(str(p.resolve()),safe='/')+'?mode=ro'
    with sqlite3.connect(uri,uri=True,timeout=3) as db:
        db.execute('PRAGMA query_only=ON')
        cols={x[1] for x in db.execute('PRAGMA table_info(baseline_profiles)')}
        if not {'id','context'} <= cols:raise ValueError('HOLD: missing legacy baseline profile schema')
        rows=db.execute('SELECT id,context FROM baseline_profiles LIMIT ?',(min(max(limit,1),200),)).fetchall()
    profiles=[]
    for name,raw in rows:
        try:
            j=json.loads(raw)
            if not isinstance(j,dict):j={}
        except (TypeError,ValueError):j={}
        profiles.append({'id':str(name)[:130],'classification':str(j.get('classification','UNKNOWN'))[:80],
                         'vpn_or_mesh':j.get('vpn_or_mesh'),
                         'container_network':j.get('container_network'),
                         'context_identity_verified':False})
    return report('legacy_context_candidates',profiles=profiles,
                  direct_context_mapping_allowed=False,
                  statement='Historical labels are candidate context descriptions, NOT verified matches.')
