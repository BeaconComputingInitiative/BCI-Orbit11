#!/usr/bin/env python3
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# File SHA-256: SHA256SUMS
# Orbital v0.8.3 terminal control plane.
# Operator actions execute IF AND ONLY IF their integrity and approval gates pass.
"""The `orbital` command used by both the GUI and operator scripts."""
from __future__ import annotations
import argparse
import json
from datetime import datetime
import sys
from pathlib import Path
from orbital_backend import HEADER,SEAL,VERSION,HOME,snapshot,write_operator_report
from orbital_ai import respond as ai_respond, model_state as ai_model_state, baseline_report
from orbital_actions import (Hold,host_evidence,neural_command,make_candidate,
    verified_preparation_status,review_candidate,service_logs)


def fail(reason):
    print('HOLD: '+str(reason),file=sys.stderr)
    return 3


def main(argv=None):
    parser=argparse.ArgumentParser(prog='orbital',description='BCI Orbital Control Plane (PyQt6)')
    commands=parser.add_subparsers(dest='command')
    commands.add_parser('gui',help='Launch PyQt6 control plane')
    ai=commands.add_parser('ai',help='Launch native Orbital AI or ask a supported question')
    ai.add_argument('prompt',nargs='*')
    commands.add_parser('status',help='Read current component status')
    commands.add_parser('storage',help='Read-only packet-collector health and quota diagnostic')
    commands.add_parser('baselines',help='Read verified baseline classifications and training state')
    commands.add_parser('neural',help='Read neural sidecar status')
    commands.add_parser('evidence',help='Verify nonprivileged host evidence chain')
    logs=commands.add_parser('logs',help='Read bounded monitoring logs')
    logs.add_argument('service',choices=['host','neural','packet'],nargs='?',default='host')
    commands.add_parser('report',help='Generate signed-by-hash local operator report (not cryptographic signature)')
    train=commands.add_parser('train',help='Gated native neural training workflow')
    train.add_argument('action',choices=['status','review','prepare','run','evaluate','promote','rollback'],nargs='?',default='status')
    train.add_argument('--input',type=Path)
    train.add_argument('--approval',type=Path)
    train.add_argument('--model',type=Path)
    train.add_argument('--confirm-train',action='store_true')
    args=parser.parse_args(argv)
    op=args.command or 'gui'
    if op in ('gui','ai') and not (op=='ai' and args.prompt):
        try:from orbital_gui import launch
        except ImportError as exc:return fail('PyQt6 unavailable: '+str(exc)+'; install python3-pyqt6')
        return launch('Orbital AI' if op=='ai' else 'Dashboard')
    try:
        if op=='ai':
            print(HEADER+'\nDeveloper Seal: '+SEAL)
            print(ai_respond(' '.join(args.prompt),snapshot()))
            return 0
        if op=='logs':print(service_logs(args.service));return 0
        if op=='evidence':print(host_evidence());return 0
        data=snapshot()
        if op=='status':print(json.dumps(data,indent=2,default=str));return 0
        if op=='storage':
            print(json.dumps({'header':HEADER,'developer_seal':SEAL,
                  'packet_condition':data.get('packet_condition'),
                  'service_details':(data.get('service_details') or {}).get('packet',{}),
                  'note':'Read-only; never deletes, archives, resumes, or changes the packet collector.'},indent=2))
            return 0
        if op=='baselines':print(json.dumps(baseline_report(data),indent=2,default=str));return 0
        if op=='neural':print(json.dumps(data.get('neural_status') or {},indent=2));return 0
        if op=='report':
            path,digest=write_operator_report(HOME/'.local/state/bci-orbital-gui/reports',data)
            print(json.dumps({'header':HEADER,'developer_seal':SEAL,'file':str(path),'file_sha256':digest},indent=2));return 0
        if op!='train':return fail('Unsupported operation')
        ready=verified_preparation_status(data)
        if args.action=='status':
            print(json.dumps({'header':HEADER,'developer_seal':SEAL,'version':VERSION,**ready},indent=2));return 0
        if args.action=='prepare':
            print(json.dumps(make_candidate(data),indent=2));return 0
        if args.action=='review':
            if args.input is None:return fail('Supply --input <verified-candidate.jsonl>')
            print(review_candidate(args.input,str(ready['context'])));return 0
        if args.action=='run':
            if not ready['qualified_for_review']:
                return fail('Live-context qualification gates not met')
            if not (args.input and args.approval and args.confirm_train):
                return fail('Supply --input DATA --approval APPROVAL --confirm-train; native CLI revalidates approval')
            directory=HOME/'.local/state/bci-orbital-gui/models'
            directory.mkdir(parents=True,exist_ok=True,mode=0o700)
            output=directory/('candidate-model-'+datetime.now().strftime('%Y%m%dT%H%M%S%f')+'.json')
            print(neural_command('train','--input',args.input,'--approval',args.approval,
                '--context',str(ready['context']),'--output',output,timeout=240));return 0
        if args.action=='evaluate':
            if not (args.model and args.input):return fail('Supply --model MODEL --input INDEPENDENT_TEST_DATA')
            directory=HOME/'.local/state/bci-orbital-gui/evaluations'
            directory.mkdir(parents=True,exist_ok=True,mode=0o700)
            output=directory/('shadow-scores-'+datetime.now().strftime('%Y%m%dT%H%M%S%f')+'.json')
            print(neural_command('score','--model',args.model,'--input',args.input,'--output',output,timeout=240));return 0
        return fail('Model promotion/rollback needs a separately qualified, implemented model registry')
    except (Hold,OSError,ValueError,KeyError) as exc:return fail(exc)

if __name__=='__main__':sys.exit(main())
