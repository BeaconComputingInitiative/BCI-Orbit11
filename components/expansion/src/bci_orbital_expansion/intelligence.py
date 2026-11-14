# BEACON COMPUTING INITIATIVE | Orbital Evidence and Neural Integration
# Developer Seal: CJB-DEV-2026 | SHA-256: see SHA256SUMS
"""Strictly shadow-only inference and auditable candidate adaptation proposals."""
from __future__ import annotations
import importlib
import json
import math
from pathlib import Path
import sys
from .common import report, filehash, verify_file


def verified_neural(release):
    path=Path(release).resolve(strict=True)
    manifest=path/'SHA256SUMS'
    if not manifest.is_file() or manifest.is_symlink():raise ValueError('HOLD: neural source manifest missing')
    entries={}
    for line in manifest.read_text().splitlines():
        bits=line.split(maxsplit=1)
        if len(bits)!=2:raise ValueError('HOLD: malformed source manifest')
        entries[bits[1].lstrip('*').removeprefix('./')]=bits[0]
    for name in ('src/bci_neural/__init__.py','src/bci_neural/common.py','src/bci_neural/model.py','src/bci_neural/reason.py','src/bci_neural/sources.py'):
        file=path/name
        if file.is_symlink() or not file.is_file() or entries.get(name)!=filehash(file):
            raise ValueError('HOLD: neural source hash mismatch: '+name)
    sys.path.insert(0,str(path/'src'))
    return importlib.import_module('bci_neural.common'),importlib.import_module('bci_neural.model'),importlib.import_module('bci_neural.reason')

def shadow_score(model_path,dataset_path,neural_release):
    common,modelmod,_=verified_neural(neural_release)
    model_sha=verify_file(model_path);dataset_sha=verify_file(dataset_path)
    m=json.loads(Path(model_path).read_text())
    modelmod.validate_model(m)
    windows=common.load_jsonl(dataset_path)
    if any(w['context']!=m['context'] for w in windows):
        raise ValueError('HOLD: historical and current network contexts cannot be relabeled')
    if any(w['trust']!='approved_candidate' for w in windows):
        raise ValueError('HOLD: live shadow scoring requires separately qualified candidate windows')
    for w in windows:
        if set(w['coverage']) != {'process','listener','network','storage'}:
            raise ValueError('HOLD: incomplete feature coverage')
        if any('throughput' in g or 'missing' in g or 'unavailable' in g for g in w['gaps']):
            raise ValueError('HOLD: sensor gap cannot be encoded as zero')
    scores=[modelmod.score(m,w) for w in windows]
    return report('neural_shadow_scoring',model_sha256=model_sha,candidate_sha256=dataset_sha,
                  scored=len(scores),candidate_anomalies=sum(bool(s['candidate_anomaly']) for s in scores),
                  scores=scores,model_promoted=False,live_response_enabled=False,
                  interpretation='Novelty only; scores are neither malware probability nor proof of attribution.')

def reason(evidence_path,neural_release):
    _,_,reasoner=verified_neural(neural_release)
    evidence_sha=verify_file(evidence_path)
    data=json.loads(Path(evidence_path).read_text())
    events=data.get('evidence')
    if not isinstance(events,list) or len(events)>2000:raise ValueError('HOLD: invalid evidence set')
    result=reasoner.correlate(events)
    return report('reasoning_hypotheses',source_sha256=evidence_sha,analysis=result,
                  verified_evidence_provenance='SOURCE_CHECKSUM_ONLY; authenticity not independently established',
                  human_attribution_possible=False,containment_authorized=False)

def proposal(previous_path,current_path,neural_release):
    common,_,_=verified_neural(neural_release)
    a_sha=verify_file(previous_path);b_sha=verify_file(current_path)
    a=common.load_jsonl(previous_path);b=common.load_jsonl(current_path)
    contexts={x['context'] for x in a+b}
    if len(contexts)!=1:raise ValueError('HOLD: mixed contexts; no adaptation')
    if any(x['trust']!='approved_candidate' for x in a+b):
        raise ValueError('HOLD: adaptation requires reviewed approved candidate data')
    if len(a)<80 or len(b)<80:raise ValueError('HOLD: insufficient independent windows')
    changes=[]
    for k in common.FEATURES:
        v1=sum(x['features'][k] for x in a)/len(a)
        v2=sum(x['features'][k] for x in b)/len(b)
        changes.append({'feature':k,'earlier_mean':round(v1,4),'later_mean':round(v2,4),
                        'relative_shift':round((v2-v1)/max(1,abs(v1)),4)})
    return report('retraining_proposal',earlier_sha256=a_sha,later_sha256=b_sha,
                  context=next(iter(contexts)),changes=changes,
                  review_required=True,training_started=False,model_promoted=False,
                  containment_authorized=False)
