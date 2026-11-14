# BEACON COMPUTING INITIATIVE | Orbital Neural Core
# Developer Seal: CJB-DEV-2026
# File SHA-256: SHA256SUMS
"""Auditable evidence-correlation rules, not open-ended machine reasoning."""
from __future__ import annotations
from datetime import timedelta
from .common import HEADER, SEAL, parse_time, canonical, digest

CATEGORIES={'process_suspicious','file_read','file_write','outbound','usb_mount','dns_query','listener','sensor_gap'}


def validate_evidence(e):
    if not isinstance(e,dict) or e.get('kind') not in CATEGORIES:
        raise ValueError('unknown evidence kind')
    parse_time(e.get('ts'))
    for k in ('context','source','event_id','host'):
        if not isinstance(e.get(k),str) or not e[k] or len(e[k])>150:
            raise ValueError('missing/oversized evidence attribute: '+k)
    if e.get('process_key') is not None and (not isinstance(e['process_key'],str) or len(e['process_key'])>150):
        raise ValueError('invalid stable process identity')
    return True


def correlate(events,window_minutes=5):
    """Does not infer exfiltration from simultaneous events or shared PID alone.

    Requires explicit stable process_key (PID + start time or stronger) and
    two different sensor sources for any sequence hypothesis.
    """
    if not 1<=window_minutes<=30: raise ValueError('bad correlation window')
    for e in events:validate_evidence(e)
    ordered=sorted(events,key=lambda r:parse_time(r['ts']))
    hypotheses=[]; seen=set()
    sequences=[('process_suspicious','outbound','suspicious-process-outbound'),
               ('file_read','outbound','file-read-followed-by-outbound'),
               ('file_write','outbound','file-write-followed-by-outbound')]
    for left,right,rule in sequences:
        for x in ordered:
            if x['kind']!=left or not x.get('process_key'):continue
            for y in ordered:
                if y['kind']!=right or y.get('process_key')!=x['process_key'] or y['context']!=x['context'] or y['host']!=x['host']:
                    continue
                if x['source']==y['source']:continue
                dt=parse_time(y['ts'])-parse_time(x['ts'])
                if not timedelta(seconds=0)<=dt<=timedelta(minutes=window_minutes):continue
                ids=(rule,x['event_id'],y['event_id'])
                if ids in seen:continue
                seen.add(ids)
                hypotheses.append({'rule_id':rule, 'evidence_ids':[x['event_id'],y['event_id']],
                                   'independent_sources':sorted([x['source'],y['source']]),
                                   'classification':'corroborated_sequence_for_review',
                                   'severity':'medium',
                                   'interpretation':'Events associated with the same stable process identity in time order; contents, intent and exfiltration are NOT established.'})
    # Separate weak coincidence notice; never counted as corroborated.
    usb=[x for x in ordered if x['kind']=='usb_mount']
    remote=[x for x in ordered if x['kind']=='outbound']
    for x in usb:
        for y in remote:
            if y['context']!=x['context'] or y['host']!=x['host']: continue
            if abs((parse_time(x['ts'])-parse_time(y['ts'])).total_seconds())<=window_minutes*60:
                hypotheses.append({'rule_id':'usb-network-temporal-cooccurrence',
                                   'evidence_ids':[x['event_id'],y['event_id']],
                                   'independent_sources':list(sorted({x['source'],y['source']})),
                                   'classification':'weak_cooccurrence_only','severity':'info',
                                   'interpretation':'Temporal coincidence only; no file transfer is demonstrated.'})
                break
    return {'header':HEADER,'developer_seal':SEAL,'evidence_events':len(events),
            'hypotheses':hypotheses,'automatic_containment_authorized':False,
            'limitations':['No packet contents or proof of exfiltration',
                'Independent sensors and stable process identity are required for sequence claims',
                'No neural score can override deterministic response safeguards']}
