#!/usr/bin/env python3
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# File SHA-256: SHA256SUMS
# Native Orbital AI v0.8.2 — The original 12→8→3→8→12 model is the ONLY learned model.
# Render a neural claim IF AND ONLY IF the original checkpoint and report hashes match.
"""Evidence-bound question interface for Orbital's *own* trained neural model.

No external LLM, APIs, shell execution, model promotion or protective action.
Natural language dispatch here is a transparent deterministic intent router, NOT
an LLM. Neural inference is exclusively performed by the original bci_neural
v0.2.0 scorer on model-compatible, independently hash-verified input data.
"""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import math
import os
import re

HEADER = 'BEACON COMPUTING INITIATIVE'
SEAL = 'CJB-DEV-2026'
VERSION = '0.8.3'
MODEL_SHA = '493ba54a8edb0fed347994dc41f5ee682156527f13e717a3d366ae80bc3cf4b0'
SCORES_SHA = '79e1675118844c3da4c18958f5d29d7a4543fc21c945b6bac75dd8fc9716882f'
CONTEXT = 'legacy:host-37a8558d8c9f442400f3fb44'
MAX_BYTES = 3 * 1024 * 1024


def ai_root(home=None):
    return Path(home or Path.home()) / '.local/state/bci-orbital-ai-v0.8.0'


def _verified(path: Path, expected: str):
    """Load original JSON artifact only IF AND ONLY IF pinned digest matches."""
    path = Path(path)
    if not path.is_file() or path.is_symlink():
        raise ValueError('Original model artifact is not installed (run the opt-in import script).')
    if path.stat().st_size > MAX_BYTES:
        raise ValueError('Model artifact is unexpectedly large')
    with path.open('rb') as f:
        raw = f.read(MAX_BYTES+1)
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected:
        raise ValueError('HOLD: original model/report SHA-256 differs from the trained checkpoint')
    obj = json.loads(raw)
    if not isinstance(obj,dict) or obj.get('developer_seal') != SEAL:
        raise ValueError('HOLD: invalid BCI artifact identity')
    return obj


def original_model(home=None):
    model = _verified(ai_root(home)/'artifacts/legacy-model.json', MODEL_SHA)
    if (model.get('context')!=CONTEXT or model.get('model_state')!='candidate_unpromoted'
        or model.get('architecture') != [12,8,3,8,12]
        or len(model.get('features',[])) != 12
        or len(model.get('layers',[])) != 4
        or not isinstance(model.get('anomaly_threshold'),(int,float))
        or not math.isfinite(model['anomaly_threshold'])):
        raise ValueError('HOLD: neural model schema/context mismatch')
    return model


def original_scores(home=None):
    model=original_model(home)
    report=_verified(ai_root(home)/'artifacts/legacy-shadow-scores.json',SCORES_SHA)
    if report.get('model_sha256')!=MODEL_SHA or report.get('containment_authorized') is not False:
        raise ValueError('HOLD: scoring report not linked to original neural model')
    rows=report.get('outputs')
    if not isinstance(rows,list) or len(rows)!=610 or any(not isinstance(r,dict) or
        r.get('context')!=model['context'] or r.get('trust')!='untrusted_legacy' for r in rows):
        raise ValueError('HOLD: score report provenance/context mismatch')
    return sorted((r for r in rows if r.get('candidate_anomaly')),key=lambda r:r['anomaly_score_mse'],reverse=True)


def model_state(home=None):
    try:
        m=original_model(home)
        try: outliers=len(original_scores(home))
        except (ValueError,OSError,KeyError,TypeError):outliers=None
        return {'available':True,'model_sha256':MODEL_SHA,'context':m['context'],
          'architecture':m['architecture'],'threshold':m['anomaly_threshold'],
          'validation_mse':m.get('validation_mse'),'candidate_anomalies':outliers,
          'state':m['model_state'],'live_scoring':False,'containment':False}
    except (ValueError,OSError,KeyError,TypeError,json.JSONDecodeError) as exc:
        return {'available':False,'reason':str(exc)[:220],
          'context':CONTEXT,'live_scoring':False,'containment':False}



def baseline_report(live:dict|None=None, home=None):
    """Assemble read-only baseline facts from authoritative live Orbital status.

    No inference, no baseline approval, no promotion, no fallback invented values.
    A neural checkpoint is NOT an operator-approved behavioral baseline.
    """
    data=live if isinstance(live,dict) else {}
    host=data.get('host_status') if isinstance(data.get('host_status'),dict) else {}
    baseline=data.get('host_baseline_status') if isinstance(data.get('host_baseline_status'),dict) else {}
    profile=baseline.get('stats') if isinstance(baseline.get('stats'),dict) else host.get('profile')
    profile=profile if isinstance(profile,dict) else {}
    j=data.get('journal') if isinstance(data.get('journal'),dict) else {}
    context=data.get('current_context','unavailable')
    m=model_state(home)
    def bounded_number(value):
        return value if isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and value>=0 else None
    cats=profile.get('categories') if isinstance(profile.get('categories'),dict) else {}
    approved=profile.get('approved',baseline.get('approved'))
    if not isinstance(approved,bool):approved=None
    return {
        'header':HEADER,'developer_seal':SEAL,
        'reference_classification':host.get('reference_classification','not reported'),
        'host_observation_context':baseline.get('context',host.get('context','unavailable')),
        'host_profile_available':bool(profile),
        'host_baseline_approved':approved,
        'host_profile_observations':bounded_number(profile.get('n')),
        'host_profile_distinct_hours':bounded_number(profile.get('hours')),
        'host_profile_first':profile.get('first'),
        'host_profile_last':profile.get('last'),
        'host_categories':{str(k):v for k,v in cats.items() if isinstance(v,int) and v>=0},
        'host_ready_for_review':baseline.get('ready_for_review') if isinstance(baseline.get('ready_for_review'),bool) else None,
        'live_context':context,
        'live_journal_valid':j.get('valid') is True,
        'live_journal_windows':bounded_number(data.get('neural_window_count')),
        'live_distinct_hours':bounded_number(data.get('hours')),
        'live_elapsed_days':bounded_number(data.get('days')),
        'live_trust':'unreviewed_live',
        'experimental_model_imported':m.get('available') is True,
        'experimental_model_context':m.get('context',CONTEXT),
        'experimental_model_state':m.get('state','unavailable'),
        'experimental_model_baseline_approved':False,
        'live_inference_enabled':False,
        'containment_authorized':False,
    }


def describe_baselines(live:dict|None=None,home=None):
    """Return grounded human text; unknown is NOT a synonym for unapproved."""
    r=baseline_report(live,home)
    def show(x):return 'not reported' if x is None else str(x)
    approval=('YES' if r['host_baseline_approved'] is True else
              'NO' if r['host_baseline_approved'] is False else 'NOT VERIFIED')
    categories=r['host_categories']
    cattext=', '.join(f'{k}: {v}' for k,v in sorted(categories.items())) if categories else 'not reported'
    ref=r['reference_classification'].replace('_',' ')
    reftext=('curated reference rules (not host-trained)' if
        r['reference_classification']=='curated_generic_reference_not_host_trained' else ref)
    state=('available' if r['host_profile_available'] else 'not retrievable')
    review=r['host_ready_for_review']
    readiness='YES' if review is True else 'NO' if review is False else 'NOT REPORTED'
    valid='PASS' if r['live_journal_valid'] else 'NOT VERIFIED'
    return ('Orbital currently has separate baseline and learning layers:\n'
            f'1. Generic reference: {reftext}. These rules are not evidence of normal behavior on your host.\n'
            f'2. Host behavioral profile ({state}): context {show(r["host_observation_context"])}; '
            f'operator approved: {approval}; observations: {show(r["host_profile_observations"])}; '
            f'distinct hours: {show(r["host_profile_distinct_hours"])}; '
            f'categories: {cattext}; ready for review: {readiness}.\n'
            f'3. New rate-aware live candidate: context {show(r["live_context"])}; '
            f'journal integrity: {valid}; {show(r["live_journal_windows"])} windows; '
            f'{show(r["live_distinct_hours"])} distinct hours; '
            f'{show(r["live_elapsed_days"])} elapsed days; trust: unreviewed_live.\n'
            f'4. Historical neural model: {"imported" if r["experimental_model_imported"] else "not installed or not verified"}; '
            f'context {show(r["experimental_model_context"])}; '
            'experimental only, NOT an approved live baseline.\n'
            'No cross-context trust promotion, live neural inference, or automatic containment is authorized.')


def _match(prompt, *words):
    return any(re.search(r'\b'+re.escape(word)+r'\b',prompt) for word in words)


def respond(message:str, live:dict|None=None, home=None):
    """Route natural-language questions deterministically to verified Orbital data.

    No learned language ability is claimed, and no prompt is ever executed as code.
    """
    q=' '.join(str(message).strip().casefold().split())[:1200]
    data=live or {}
    state=model_state(home)
    context=str(data.get('current_context','unavailable'))
    statuses=data.get('states') or {}
    journal=data.get('journal') or {}
    def with_model():
        if not state['available']:
            return ('The original neural checkpoint is not accessible in this BCI account. '
                    'Import the verified legacy checkpoint with scripts/import-trained-model.sh. '
                    'I will not invent model predictions.\nDetails: '+state['reason'])
        return None

    if not q or _match(q,'help','commands','questions','capabilities'):
        return ('I am Orbital AI, the native interface to the Orbital autoencoder and verified evidence. '
                'I can answer: "model status", "what anomalies did you find?", '
                '"explain anomaly 1", "system status", "network context", '
                '"training readiness", "what are your baselines?", "evidence integrity", or "can you score live?".\n'
                'I do not use a language model or external AI service; question routing is rule-based.')
    if _match(q,'baseline','baselines','behavioral profile','behavioral profiles','normal behavior'):
        return describe_baselines(data,home)
    if _match(q,'collector','packet collector','storage quota','quota','why stopped','restart limit'):
        raw=(data.get('service_details') or {}).get('packet',{})
        condition=data.get('packet_condition','unknown')
        if condition=='quota_hold':
            return ('Packet collector: EVIDENCE QUOTA HOLD. Orbital observed the exact quota-HOLD '
                    'message in the packet service journal. systemd state: '
                    f'{raw.get("ActiveState","unknown")}; result: {raw.get("Result","unknown")}. '
                    'Preserve existing evidence and investigate archival/storage limits before any restart. '
                    'The neural detector did not diagnose an attack.')
        return (f'Packet collector condition: {condition}; service state: '
                f'{raw.get("ActiveState","unknown")}; result: {raw.get("Result","unknown")}. '
                'Quota exhaustion is not confirmed unless its own journal supplies the HOLD message.')
    if _match(q,'hack','attacker','compromised','threat actor','who attacked'):
        return ('Neither the anomaly model nor these aggregate logs can identify an attacker or prove '
                'compromise. A statistical deviation requires independent process/network evidence '
                'and analyst review. No containment is authorized.')
    if _match(q,'train','training','ready','retrain'):
        n=int(data.get('neural_window_count',0) or 0)
        hours=int(data.get('hours',0) or 0)
        days=float(data.get('days',0) or 0)
        ok=bool(data.get('journal_valid') and n>=80 and hours>=24 and days>=7)
        return (f'Live candidate training: {n}/80 windows, {hours}/24 distinct hours, '
                f'{days:.2f}/7 elapsed days. Context: {context}.\n'
                f'Numerical readiness: {"MET FOR REVIEW" if ok else "HOLD"}; '
                'independent evidence qualification, explicit approval and evaluation remain necessary. '
                'The legacy model is unpromoted and is not eligible to train itself automatically.')
    if _match(q,'anomalies','anomaly','outliers','unusual','abnormal','explain','why flagged'):
        msg=with_model()
        if msg:return msg
        try: anomalies=original_scores(home)
        except (ValueError,OSError,KeyError,TypeError,json.JSONDecodeError) as exc:
            return 'Original model loaded; its original scored evidence is unavailable: '+str(exc)[:200]
        ordinal=re.search(r'(?:anomaly|outlier|number|#)\s*(\d+)',q)
        if ordinal:
            index=int(ordinal.group(1))-1
            if not 0<=index<len(anomalies):return f'Available candidate anomalies: 1–{len(anomalies)}.'
            row=anomalies[index]
            names=', '.join(f"{v['feature']} ({v['squared_reconstruction_error']:.2f})" for v in row.get('top_contributors',[])[:4])
            return (f'Original model anomaly #{index+1}: {row["ts"]}.\n'
                    f'Reconstruction MSE: {row["anomaly_score_mse"]:.4f}; '
                    f'threshold: {row["threshold"]:.4f}.\n'
                    f'Main contributing features: {names}.\n'
                    'Interpretation: statistical novelty in untrusted legacy telemetry, not evidence of malicious intent.')
        result=[f'The original trained autoencoder flagged {len(anomalies)} of 610 historical windows. '
                'All were untrusted legacy data and none is a confirmed attack.']
        for i,r in enumerate(anomalies,1):
            top=(r.get('top_contributors') or [{}])[0].get('feature','unavailable')
            result.append(f'{i}. {r["ts"]}: MSE {r["anomaly_score_mse"]:.4f} (top contributor: {top}).')
        result.append('Ask "explain anomaly 1" for its actual learned feature deviations.')
        return '\n'.join(result)
    if _match(q,'model','neural','weights','learned','architecture','brain','intelligence'):
        msg=with_model()
        if msg:return msg
        return (f'Original Orbital neural model: {" → ".join(map(str,state["architecture"]))} autoencoder.\n'
                f'Checkpoint SHA-256: {state["model_sha256"]}\n'
                f'Trained context: {state["context"]}; status: {state["state"]}.\n'
                f'Validation reconstruction MSE: {state["validation_mse"]:.6f}; '
                f'anomaly threshold: {state["threshold"]:.6f}.\n'
                'It detects statistical feature deviations; it does not understand arbitrary language. '
                'This interface maps supported questions onto real model outputs and verified evidence.')
    if _match(q,'score','predict','inference','live'):
        if not state['available']:return with_model()
        return (f'Live neural scoring HOLD. Original model context: {state["context"]}; '
                f'current live context: {context}. They are not interchangeable.\n'
                'Use “Score verified dataset” with a hash-verified JSONL file from the exact legacy '
                'context to invoke the original native scorer. No inference or containment will run automatically.')
    if _match(q,'context','environment','interface','usb0','network'):
        return (f'Current live context: {context}\n'
                f'Network interface: {data.get("current_interface","unknown")}\n'
                f'Live host fingerprint: {data.get("host_id","unavailable")}\n'
                f'Live route fingerprint: {data.get("route_id","unavailable")}\n'
                f'Historical trained context: {CONTEXT}. No equivalence has been approved.')
    if _match(q,'evidence','hash','integrity','journal','packet','dns'):
        return (f'Live rate-aware journal verification: {"PASS" if journal.get("valid") else "NOT VERIFIED"}; '
                f'{journal.get("count",0)} records.\n'
                f'Current packet service: {statuses.get("packet","unknown")}. '
                'The GUI cannot read root-private packet evidence without separate permission. '
                'An active service is not proof that every packet is captured; the hash chain '
                'requires independent anchoring for stronger tamper detection.')
    if _match(q,'status','health','services','running','working','today'):
        return ('Service status (live snapshot):\n'
                f'Host monitor: {statuses.get("host","unknown")}\n'
                f'Packet collector: {statuses.get("packet","unknown")}\n'
                f'Neural timer: {statuses.get("neural","unknown")}\n'
                f'Context: {context}\n'
                f'Original model loaded: {"YES" if state["available"] else "NO"}; '
                'live neural inference: DISABLED; automatic containment: DISABLED.')
    return ('I can only answer supported evidence-backed questions. No language model is used. '
            'Ask "help" for supported prompts. I will not guess, execute shell commands, '
            'or claim a threat that the neural model did not establish.')


def score_argv(input_path:str,home=None):
    """Native model scoring is allowed IF AND ONLY IF pinned checkpoint is verified."""
    original_model(home)
    p=Path(input_path).expanduser()
    if not p.is_file() or p.is_symlink() or not Path(str(p)+'.sha256').is_file():
        raise ValueError('HOLD: model input requires a regular JSONL file and SHA-256 sidecar')
    if not Path(str(ai_root(home)/'artifacts/legacy-model.json')+'.sha256').is_file():
        raise ValueError('HOLD: imported original model SHA-256 sidecar missing')
    exe=Path(home or Path.home())/'.local/bin/bci-orbital-neural'
    if not exe.is_file() or not os.access(exe,os.X_OK):
        raise ValueError('HOLD: native Orbital v0.2.0 neural scorer unavailable')
    dest_dir=ai_root(home)/'scores'
    dest_dir.mkdir(parents=True,exist_ok=True,mode=0o700)
    if dest_dir.is_symlink() or dest_dir.stat().st_mode&0o077:
        raise ValueError('HOLD: unsafe score report directory')
    dest=dest_dir/('neural-score-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json')
    return [str(exe),'score','--model',str(ai_root(home)/'artifacts/legacy-model.json'),
            '--input',str(p),'--output',str(dest)]
