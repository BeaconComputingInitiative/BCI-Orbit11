# BEACON COMPUTING INITIATIVE | Orbital Neural Core
# Developer Seal: CJB-DEV-2026
# File SHA-256: SHA256SUMS
"""Fail-closed standalone CLI: neural scores can NEVER request containment."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import random
import sys
from . import __version__
from .common import FEATURES, HEADER, SEAL, HOLD, canonical, digest, file_digest, load_jsonl, parse_time, validate_window, verify_sidecar, window, write_hashed
from .journal import append,freeze,verify
from .model import score, train, validate_model
from .reason import correlate
from .sources import installed_sensor_module,legacy_export,snapshot_window


def display(obj):
    print(json.dumps(obj,indent=2,sort_keys=True))


def stats(rows,context):
    chosen=[r for r in rows if r['context']==context]
    if not chosen:raise ValueError('no rows for specified context')
    timestamps=sorted(parse_time(r['ts']) for r in chosen)
    distinct_hours=len({x.strftime('%Y-%m-%dT%H') for x in timestamps})
    span=(timestamps[-1]-timestamps[0]).total_seconds()/86400
    coverage=set.intersection(*(set(r['coverage']) for r in chosen))
    trust=Counter(r['trust'] for r in chosen)
    return {'samples':len(chosen),'span_days':round(span,4),'distinct_scan_hours':distinct_hours,
            'coverage_intersection':sorted(coverage),'trust_breakdown':dict(trust),
            'first':timestamps[0].isoformat(),'last':timestamps[-1].isoformat(),
            'gaps_present':sorted({g for r in chosen for g in r['gaps']})[:16],
            'ready_for_operator_training_review':len(chosen)>=80 and distinct_hours>=24 and span>=7,
            'no_automatic_trust_promotion':True}


def confirm(required):
    if not sys.stdin.isatty():raise ValueError('HOLD: requires interactive local terminal')
    return input('Type '+required+' to confirm: ').strip()==required


def cli(argv=None):
    p=argparse.ArgumentParser(prog='bci-orbital-neural',description='BCI Orbital Neural Core v0.2.0 (isolated, no containment)')
    p.add_argument('--state-dir',type=Path,default=Path.home()/'.local/state/bci-orbital-neural-v0.2.0')
    sub=p.add_subparsers(dest='cmd',required=True)
    sub.add_parser('status')
    cap=sub.add_parser('capture',help='capture one feature window from hash-verified installed Orbital sensors')
    cap.add_argument('--orbital-release',type=Path,default=Path.home()/'.local/opt/bci-orbital-v2/0.1.0')
    fre=sub.add_parser('freeze',help='freeze verified append-only journal into hashed training candidate')
    fre.add_argument('--output',type=Path,required=True);fre.add_argument('--context')
    inspect=sub.add_parser('review',help='inspect candidate dataset qualification, no write')
    inspect.add_argument('--input',type=Path,required=True);inspect.add_argument('--context',required=True)
    approve=sub.add_parser('approve-training',help='local operator training approval, NEVER baseline approval')
    approve.add_argument('--input',type=Path,required=True);approve.add_argument('--context',required=True)
    approve.add_argument('--output',type=Path,required=True)
    approve.add_argument('--allow-untrusted-legacy',action='store_true')
    learn=sub.add_parser('train',help='train isolated candidate model, requires dataset approval')
    learn.add_argument('--input',type=Path,required=True);learn.add_argument('--context',required=True)
    learn.add_argument('--approval',type=Path,required=True);learn.add_argument('--output',type=Path,required=True)
    learn.add_argument('--epochs',type=int,default=90)
    check=sub.add_parser('score',help='score one or more candidate windows, no system response')
    check.add_argument('--model',type=Path,required=True);check.add_argument('--input',type=Path,required=True)
    check.add_argument('--output',type=Path,required=True)
    legacy=sub.add_parser('legacy-export',help='read Chance legacy SQLite, export aggregate untrusted feature windows')
    legacy.add_argument('--source',type=Path,required=True);legacy.add_argument('--output',type=Path,required=True)
    legacy.add_argument('--limit',type=int,default=50000);legacy.add_argument('--profile')
    think=sub.add_parser('reason',help='explain evidence correlations with explicit uncertainty')
    think.add_argument('--input',type=Path,required=True);think.add_argument('--output',type=Path,required=True)
    ver=sub.add_parser('verify');ver.add_argument('path',type=Path);ver.add_argument('--journal',action='store_true')
    demo=sub.add_parser('demo',help='train only on synthetic data; NEVER host security baseline')
    demo.add_argument('--output',type=Path,required=True)
    args=p.parse_args(argv)
    os.umask(0o077)
    state=args.state_dir
    if args.cmd=='status':
        journal=state/'candidate-journal.jsonl'
        if journal.exists():
            n,head,records=verify(journal)
            contexts=dict(Counter(r['context'] for r in records))
        else:n,head,contexts=0,None,{}
        display({'header':HEADER,'developer_seal':SEAL,'version':__version__,
                 'neural_core':'ISOLATED_SHADOW_MODE','capture_journal':str(journal),
                 'captured_windows':n,'journal_head_sha256':head,'contexts':contexts,
                 'response_capability':False,'training':'requires explicit manual review and approval'})
    elif args.cmd=='capture':
        sensors=installed_sensor_module(args.orbital_release)
        snap=sensors.collect()
        item=snapshot_window(snap)
        head=append(state/'candidate-journal.jsonl',item)
        display({'header':HEADER,'developer_seal':SEAL,'capture':'CANDIDATE_ONLY',
                 'context':item['context'],'features':item['features'],'gaps':item['gaps'],
                 'chain_head_sha256':head,'orbital_v2_changed':False,'containment_changed':False})
    elif args.cmd=='freeze':
        display({'header':HEADER,'developer_seal':SEAL,**freeze(state/'candidate-journal.jsonl',args.output,args.context)})
    elif args.cmd=='review':
        verify_sidecar(args.input)
        display({'header':HEADER,'developer_seal':SEAL,'context':args.context,
                 'classification':'REVIEW_ONLY','dataset_sha256':file_digest(args.input),
                 **stats(load_jsonl(args.input),args.context)})
    elif args.cmd=='approve-training':
        verify_sidecar(args.input)
        rows=load_jsonl(args.input)
        if len(rows)!=sum(r['context']==args.context for r in rows):
            raise ValueError('HOLD: dataset has multiple contexts; freeze per context first')
        review=stats(rows,args.context)
        if not review['ready_for_operator_training_review']:
            raise ValueError('HOLD: fewer than 7 elapsed days / 24 distinct hours / 80 samples')
        is_legacy=any(r['trust']=='untrusted_legacy' for r in rows)
        if is_legacy and not args.allow_untrusted_legacy:
            raise ValueError('HOLD: legacy history requires explicit --allow-untrusted-legacy')
        if 'network' not in review['coverage_intersection'] or 'listener' not in review['coverage_intersection']:
            raise ValueError('HOLD: network and listener visibility required')
        allowed_gaps={'throughput_rates_not_available_in_v0.1.0_collector',
                      'no_process_or_storage_coverage_in_sample'}
        unknown_gaps=set(review['gaps_present'])-allowed_gaps
        if unknown_gaps:
            raise ValueError('HOLD: sensor visibility gaps require repair/requalification: '+repr(sorted(unknown_gaps)))
        display({'header':HEADER,'developer_seal':SEAL,'REVIEW':review,
                 'dataset_sha256':file_digest(args.input),
                 'risk':'Training approval does NOT mean these observations were benign or baseline-approved.'})
        phrase='REVIEW-UNTRUSTED-LEGACY' if is_legacy else 'APPROVE-NEURAL-TRAINING'
        if not confirm(phrase):raise ValueError('HOLD: approval not given')
        approval={'header':HEADER,'developer_seal':SEAL,'schema':'bci.neural.training-approval.v1',
                  'context':args.context,'dataset_sha256':file_digest(args.input),
                  'source_trust':review['trust_breakdown'],'review':review,
                  'signed_cryptographically':False,
                  'scope':'CANDIDATE_NEURAL_TRAINING_ONLY',
                  'not_authorized':['baseline-approval','automatic-containment','host-action'],
                  'operator_confirmation':phrase,'reviewed_utc':datetime.now(timezone.utc).isoformat()}
        display({'approval_sha256':write_hashed(args.output,approval),'scope':approval['scope']})
    elif args.cmd=='train':
        verify_sidecar(args.input)
        verify_sidecar(args.approval)
        approval=json.loads(args.approval.read_text())
        if approval.get('schema')!='bci.neural.training-approval.v1' or approval.get('scope')!='CANDIDATE_NEURAL_TRAINING_ONLY':
            raise ValueError('HOLD: wrong approval type')
        if approval.get('context')!=args.context or approval.get('dataset_sha256')!=file_digest(args.input):
            raise ValueError('HOLD: dataset or context differs from operator-approved snapshot')
        rows=load_jsonl(args.input)
        if any(r['context']!=args.context for r in rows):raise ValueError('HOLD: mixed-context training')
        if not stats(rows,args.context)['ready_for_operator_training_review']:
            raise ValueError('HOLD: review gates no longer met')
        model=train(rows,args.context,file_digest(args.approval),epochs=args.epochs)
        model['training_classification']='OPERATOR_REVIEWED_CANDIDATE_UNPROMOTED'
        display({'model_sha256':write_hashed(args.output,model),
                 'context':args.context,'validation_mse':model['validation_mse'],
                 'threshold':model['anomaly_threshold'],
                 'model_state':model['model_state'],'containment_authorized':False})
    elif args.cmd=='score':
        model_sha=verify_sidecar(args.model)
        verify_sidecar(args.input)
        model=json.loads(args.model.read_text());validate_model(model)
        rows=load_jsonl(args.input)
        out={'header':HEADER,'developer_seal':SEAL,'model_sha256':model_sha,
             'source_sha256':file_digest(args.input), 'outputs':[score(model,r) for r in rows],
             'containment_authorized':False}
        display({'report_sha256':write_hashed(args.output,out),'scored':len(rows),
                 'candidate_anomalies':sum(r['candidate_anomaly'] for r in out['outputs'])})
    elif args.cmd=='legacy-export':
        rows,report=legacy_export(args.source,args.limit,args.profile)
        if not rows:raise ValueError('HOLD: no convertible legacy observations')
        payload=('\n'.join(canonical(r) for r in rows)+'\n').encode()
        d=write_hashed(args.output,payload)
        display({'header':HEADER,'developer_seal':SEAL,'dataset_sha256':d,**report,
                 'source_db_sha256':'NOT_COMPUTED_READ_ONLY_LIVE_SOURCE',
                 'output':'UNTRUSTED_CANDIDATE_ONLY','automatic_approval':False})
    elif args.cmd=='reason':
        events=[]
        for n,line in enumerate(args.input.open('r',encoding='utf-8'),1):
            if n>5000 or len(line)>16384:raise ValueError('reason input limit exceeded')
            if line.strip():events.append(json.loads(line))
        out=correlate(events)
        out['input_sha256']=file_digest(args.input)
        display({'report_sha256':write_hashed(args.output,out),
                 'hypotheses':len(out['hypotheses']),'containment_authorized':False})
    elif args.cmd=='verify':
        if args.journal:
            n,head,_=verify(args.path)
            display({'valid':True,'rows':n,'journal_head_sha256':head})
        else:display({'valid':True,'file_sha256':verify_sidecar(args.path)})
    elif args.cmd=='demo':
        rng=random.Random(440)
        start=datetime.now(timezone.utc)-timedelta(days=10)
        rows=[]
        for i in range(120):
            values=dict.fromkeys(FEATURES,0)
            values.update({'process_count':210+rng.randrange(20),'listener_count':24+rng.randrange(5),
                'outbound_count':4+rng.randrange(4),'inbound_count':rng.randrange(3),
                'remote_unique_count':3+rng.randrange(4),'public_listener_count':1,
                'rx_kib_per_second':50+rng.random()*10,'tx_kib_per_second':30+rng.random()*10})
            rows.append(window('synthetic-demo', (start+timedelta(hours=2*i)).isoformat(timespec='seconds'),
                values,'synthetic_demo',{'network','listener','process','storage'},[], 'generated_synthetic'))
        m=train(rows,'synthetic-demo','SYNTHETIC_DEMO_NO_OPERATOR_APPROVAL',epochs=75)
        m['training_classification']='SYNTHETIC_DEMO_NOT_HOST_TRAINED'
        m['warning']='SYNTHETIC TEST MODEL ONLY. Not a host-specific detection baseline.'
        display({'demo_model_sha256':write_hashed(args.output,m),
                 'train_windows':m['train_windows'],'validation_windows':m['validation_windows'],
                 'status':'SYNTHETIC_DEMO_ONLY','containment_authorized':False})
    return 0


def main():
    try:return cli()
    except (ValueError,FileNotFoundError,FileExistsError,PermissionError,OSError,json.JSONDecodeError) as e:
        print('HOLD:',str(e),file=sys.stderr)
        return HOLD

if __name__=='__main__':sys.exit(main())
