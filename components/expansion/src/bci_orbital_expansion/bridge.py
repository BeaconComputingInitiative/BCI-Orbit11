# BEACON COMPUTING INITIATIVE | Verified Orbital Neural v0.3 Feature Bridge
# Developer Seal: CJB-DEV-2026 | SHA-256: see SHA256SUMS
"""Combine verified v0.1.0 process/socket sensors and actual interface deltas.

Old v0.2.0 collector wrote throughput=0 when unavailable. This bridge refuses
missing rates, retains context and labels windows unreviewed_live.
"""
from __future__ import annotations
import importlib
from . import context,throughput,intelligence
from .common import report,utcnow


def snapshot(orbital_release,neural_release,seconds=2,interface=None):
    common,_,_=intelligence.verified_neural(neural_release)
    mod=importlib.import_module('bci_neural.sources')
    verified_sensor=mod.installed_sensor_module(orbital_release)
    first_routes,gaps=context.default_routes()
    if gaps or not first_routes:raise ValueError('HOLD: network route missing; context unsafe')
    devs={r['dev'] for r in first_routes if r.get('dev')}
    if interface is None:
        if len(devs)!=1:raise ValueError('HOLD: select interface explicitly for multi-route host')
        interface=next(iter(devs))
    if interface not in devs:raise ValueError('HOLD: interface does not match default route')
    from pathlib import Path
    before=throughput.parse_netdev(Path('/proc/net/dev').read_text())
    import time
    start=time.monotonic(); time.sleep(seconds)
    after=throughput.parse_netdev(Path('/proc/net/dev').read_text())
    interval=time.monotonic()-start
    rates,rate_gaps=throughput.rate(before,after,interval)
    if interface not in rates or rate_gaps:raise ValueError('HOLD: unavailable or reset throughput counters')
    snap=verified_sensor.collect()
    last_routes,last_gaps=context.default_routes()
    if last_gaps or first_routes!=last_routes or snap.get('context')=='ctx-unknown':
        raise ValueError('HOLD: network route changed or context unknown during capture')
    w=mod.snapshot_window(snap)
    # Replace intentionally-unavailable v0.2.0 placeholder with actual measured rates.
    measurements=rates[interface]
    w['features']['rx_kib_per_second']=measurements['rx_bytes_per_second']/1024
    w['features']['tx_kib_per_second']=measurements['tx_bytes_per_second']/1024
    w['gaps']=[g for g in w['gaps'] if g!='throughput_rates_not_available_in_v0.1.0_collector']
    ctx=context.fingerprint(routes=first_routes)
    w['measurement_provenance']={'throughput_source':'/proc/net/dev',
        'scope':'selected default-route interface, not per-socket throughput',
        'network_interface':interface,'elapsed_seconds':round(interval,3),
        'host_id':ctx['host_id'],'route_id':ctx['route_id'],
        'legacy_mapping_verified':False}
    w['source']='verified_orbital_v0.1.0_sensors+proc_net_dev'
    common.validate_window(w)
    return w
