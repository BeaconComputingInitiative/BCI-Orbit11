# BEACON COMPUTING INITIATIVE | Orbital Network Rate Collector
# Developer Seal: CJB-DEV-2026 | SHA-256: see SHA256SUMS
"""Measure Linux interface counters using monotonic time and report resets."""
import time
from pathlib import Path
from .common import report

def parse_netdev(text):
    counters={}
    for line in text.splitlines()[2:]:
        if ':' not in line:continue
        name,values=line.rsplit(':',1)
        vals=values.split()
        if len(vals)>=16:
            try:counters[name.strip()]={'rx_bytes':int(vals[0]),'tx_bytes':int(vals[8])}
            except ValueError:pass
    return counters

def rate(first,second,elapsed):
    if elapsed <=0:raise ValueError('invalid elapsed seconds')
    out={}; gaps=[]
    for iface,ends in second.items():
        if iface not in first:
            gaps.append('new-interface:'+iface);continue
        start=first[iface]
        if ends['rx_bytes']<start['rx_bytes'] or ends['tx_bytes']<start['tx_bytes']:
            gaps.append('counter-reset:'+iface);continue
        out[iface]={'rx_bytes_per_second':round((ends['rx_bytes']-start['rx_bytes'])/elapsed,3),
                    'tx_bytes_per_second':round((ends['tx_bytes']-start['tx_bytes'])/elapsed,3)}
    return out,gaps

def capture(seconds=2):
    if not 1<=seconds<=15:raise ValueError('seconds must be 1..15')
    before=parse_netdev(Path('/proc/net/dev').read_text())
    start=time.monotonic();time.sleep(seconds)
    after=parse_netdev(Path('/proc/net/dev').read_text())
    rates,gaps=rate(before,after,time.monotonic()-start)
    return report('network_throughput',interfaces=rates,gaps=gaps,
                  scope='interface-wide, not per-process, not packet loss proof',
                  throughput_available=bool(rates))
