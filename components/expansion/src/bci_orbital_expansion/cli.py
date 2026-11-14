# BEACON COMPUTING INITIATIVE | Orbital Expansion CLI
# Developer Seal: CJB-DEV-2026 | SHA-256: see SHA256SUMS
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import os
import sys
from .common import report,save_hashed,save_jsonl_hashed,verify_file,utcnow
from . import context,packets,throughput,kernel,intelligence,bridge


def _doctor():
    cap=None
    try:
        for line in Path('/proc/self/status').read_text().splitlines():
            if line.startswith('CapEff:'):
                cap=(int(line.split(':')[1].strip(),16)&(1<<13))!=0
    except (OSError,ValueError):pass
    return report('capability_doctor',checks={
        'packet_capture':{'available':bool(cap),'requirement':'CAP_NET_RAW + explicit interface and opt-in'},
        'dns_port53':{'available':bool(cap),'limitation':'No DoH/DoT decryption or TCP reassembly'},
        'kernel_ebpf':{'available':bool(shutil.which('bpftrace') and Path('/sys/kernel/tracing').exists()),
                       'requirement':'bpftrace installed, kernel tracing supported, sufficient privileges'},
        'netdev_throughput':{'available':Path('/proc/net/dev').is_file()},
        'neural_scoring':{'available':True,'requirement':'verified same-context, complete-coverage qualified dataset and model'},
        'automatic_containment':{'available':False,'note':'intentionally not connected in this release'},
        'human_attribution':{'available':False,'note':'telemetry cannot identify remote person or intent'}
        },operating_mode='ISOLATED_SHADOW',previous_services_touched=False)

def cli(argv=None):
    p=argparse.ArgumentParser(description='BCI Orbital Expansion v0.3.0 — separate read-only/shadow sensors; no containment')
    sub=p.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('doctor');a.add_argument('--output')
    a=sub.add_parser('context');a.add_argument('--output')
    a=sub.add_parser('legacy-context');a.add_argument('--source',required=True)
    a=sub.add_parser('throughput');a.add_argument('--seconds',type=int,default=2);a.add_argument('--output')
    a=sub.add_parser('packet-capture');a.add_argument('--interface',required=True);a.add_argument('--seconds',type=int,default=5)
    a.add_argument('--max-packets',type=int,default=1500);a.add_argument('--include-metadata',action='store_true')
    a.add_argument('--acknowledge-privileged-capture',action='store_true',required=True);a.add_argument('--output',required=True)
    a=sub.add_parser('kernel-trace');a.add_argument('--seconds',type=int,default=3);a.add_argument('--max-events',type=int,default=2000)
    a.add_argument('--acknowledge-kernel-tracing',action='store_true',required=True);a.add_argument('--output',required=True)
    a=sub.add_parser('capture-window');a.add_argument('--orbital-release',required=True);a.add_argument('--neural-release',required=True)
    a.add_argument('--seconds',type=int,default=2);a.add_argument('--interface');a.add_argument('--output',required=True)
    a=sub.add_parser('verify');a.add_argument('path')
    a=sub.add_parser('shadow-score');a.add_argument('--model',required=True);a.add_argument('--candidate',required=True)
    a.add_argument('--neural-release',required=True);a.add_argument('--output',required=True)
    a=sub.add_parser('reason');a.add_argument('--evidence',required=True);a.add_argument('--neural-release',required=True);a.add_argument('--output',required=True)
    a=sub.add_parser('propose-retraining');a.add_argument('--previous',required=True);a.add_argument('--current',required=True)
    a.add_argument('--neural-release',required=True);a.add_argument('--output',required=True)
    args=p.parse_args(argv)
    try:
        if args.cmd=='doctor':data=_doctor()
        elif args.cmd=='context':data=context.context_snapshot()
        elif args.cmd=='legacy-context':data=context.legacy_summary(args.source)
        elif args.cmd=='throughput':data=throughput.capture(args.seconds)
        elif args.cmd=='packet-capture':data=packets.capture(args.interface,args.seconds,args.max_packets,args.include_metadata)
        elif args.cmd=='kernel-trace':data=kernel.collect(args.seconds,args.max_events)
        elif args.cmd=='capture-window':
            if not 1<=args.seconds<=15:raise ValueError('HOLD: timing out of bounds')
            data=bridge.snapshot(args.orbital_release,args.neural_release,args.seconds,args.interface)
        elif args.cmd=='verify':data=report('verified_artifact',path=args.path,sha256=verify_file(args.path),valid=True)
        elif args.cmd=='shadow-score':data=intelligence.shadow_score(args.model,args.candidate,args.neural_release)
        elif args.cmd=='reason':data=intelligence.reason(args.evidence,args.neural_release)
        elif args.cmd=='propose-retraining':data=intelligence.proposal(args.previous,args.current,args.neural_release)
        else:raise ValueError('HOLD: unknown operation')
        if hasattr(args,'output') and args.output:
            hashval=(save_jsonl_hashed(args.output,[data]) if args.cmd=='capture-window' else save_hashed(args.output,data))
            print(json.dumps({'header':'BEACON COMPUTING INITIATIVE','developer_seal':'CJB-DEV-2026',
                              'output':args.output,'sha256':hashval,'status':'PASS'},indent=2))
        else:print(json.dumps(data,indent=2,sort_keys=True))
        return 0
    except (OSError,RuntimeError,ValueError,PermissionError,FileExistsError,KeyError,TypeError) as exc:
        print(json.dumps({'header':'BEACON COMPUTING INITIATIVE','developer_seal':'CJB-DEV-2026',
                          'status':'HOLD','reason':str(exc),'live_response_authorized':False}),file=sys.stderr)
        return 3
