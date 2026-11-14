# BEACON COMPUTING INITIATIVE | Orbital Cyber Defense
# Developer Seal: CJB-DEV-2026
# File SHA-256: see SHA256SUMS
"""Scoped nftables quarantine; strictly opt-in, TTL bounded, never whole-host cutoffs."""
import ipaddress
import os
import shutil
import subprocess
from datetime import datetime, timedelta, timezone

TABLE='bci_orbital_v2'

def safe_target(value, reference, protected_dynamic=()):
    try:
        addr = ipaddress.ip_address(value)
        if (not addr.is_global or addr.is_multicast or addr.is_unspecified or addr.is_loopback):
            return False
        if any(addr in ipaddress.ip_network(x) for x in reference['protected_networks']):
            return False
        if any(addr == ipaddress.ip_address(x) for x in protected_dynamic):
            return False
        return True
    except ValueError:
        return False

def nft(args):
    if os.geteuid() != 0:
        raise RuntimeError('root privileges required for live quarantine')
    if not shutil.which('nft'):
        raise RuntimeError('nft is missing: install nftables before arming')
    p = subprocess.run(['nft',*args],capture_output=True,text=True,timeout=8,check=False)
    if p.returncode:
        raise RuntimeError('nft failed: '+p.stderr[:300])

def check_capability():
    return os.geteuid() == 0 and shutil.which('nft') is not None

def setup_scoped_table():
    """Fail closed if table unexpectedly already exists; never modify other tables."""
    # All rules are confined to this uniquely named table. No input or forward hooks.
    if os.geteuid() != 0 or not shutil.which('nft'):
        raise RuntimeError('live firewall unavailable')
    probe = subprocess.run(['nft','list','table','inet',TABLE],capture_output=True,text=True,timeout=8)
    if probe.returncode == 0:
        # Existing table may be ours or a collision; do not silently take ownership.
        if 'bci_quarantine_v4' not in probe.stdout or 'bci_quarantine_v6' not in probe.stdout:
            raise RuntimeError('unexpected existing nft table: manual inspection required')
        return
    content = f'''table inet {TABLE} {{
      set bci_quarantine_v4 {{ type ipv4_addr; flags timeout; timeout 300s; }}
      set bci_quarantine_v6 {{ type ipv6_addr; flags timeout; timeout 300s; }}
      chain output_guard {{ type filter hook output priority 5; policy accept;
        ip daddr @bci_quarantine_v4 drop
        ip6 daddr @bci_quarantine_v6 drop
      }}
    }}'''
    p = subprocess.run(['nft','-f','-'],input=content,text=True,capture_output=True,timeout=8)
    if p.returncode:
        raise RuntimeError('scoped nft setup failed: '+p.stderr[:300])

def quarantine(address, ttl=300):
    addr = ipaddress.ip_address(address)
    if ttl != 300:
        raise ValueError('v0.1.0 only supports a fixed 300-second TTL')
    setup_scoped_table()
    setname='bci_quarantine_v4' if addr.version == 4 else 'bci_quarantine_v6'
    nft(['add','element','inet',TABLE,setname,'{',str(addr),'timeout','300s','}'])
    return (datetime.now(timezone.utc)+timedelta(seconds=ttl)).isoformat()

def release(address):
    addr=ipaddress.ip_address(address)
    setname='bci_quarantine_v4' if addr.version == 4 else 'bci_quarantine_v6'
    nft(['delete','element','inet',TABLE,setname,'{',str(addr),'}'])

def remove_own_table():
    nft(['delete','table','inet',TABLE])
