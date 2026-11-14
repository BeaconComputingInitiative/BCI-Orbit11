# BEACON COMPUTING INITIATIVE | Orbital Cyber Defense
# Developer Seal: CJB-DEV-2026
# File SHA-256: see SHA256SUMS
"""Detector, correlation, immutable-baseline rules and protected response gate."""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
import ipaddress
import json
import os
from pathlib import Path
import subprocess
from .sensors import collect
from .response import safe_target, quarantine, check_capability
from .store import utcnow

def reference_data():
    return json.loads((Path(__file__).parent / 'reference.json').read_text())

def public_remote(value):
    try:
        return ipaddress.ip_address(value).is_global
    except (ValueError, TypeError):
        return False

def notify(severity, kind):
    # Best effort only; privileged services will generally lack a desktop session.
    if not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
        return
    try:
        subprocess.Popen(['notify-send', '-a', 'BCI Orbital', f'Orbital: {severity}', kind],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        pass

def dynamic_protected(snapshot):
    """Protect the host's current default gateway plus interface/DNS addresses from quarantine."""
    from .sensors import command
    protected = set()
    data, err = command(['ip','-j','route','show','default'])
    if not err:
        try:
            for x in json.loads(data):
                if x.get('gateway'):
                    protected.add(x['gateway'])
        except ValueError:
            pass
    try:
        for line in Path('/etc/resolv.conf').read_text().splitlines():
            fields=line.split()
            if len(fields)>=2 and fields[0]=='nameserver':
                try:
                    protected.add(str(ipaddress.ip_address(fields[1])))
                except ValueError:
                    pass
    except OSError:
        pass
    data, err = command(['resolvectl','dns'])
    if not err:
        import re
        for item in re.findall(r'(?:\d{1,3}\.){3}\d{1,3}|(?:[0-9a-fA-F]*:){2,}[0-9a-fA-F:]+', data):
            try:
                protected.add(str(ipaddress.ip_address(item)))
            except ValueError:
                pass
    return protected

class Engine:
    def __init__(self, store):
        self.store = store
        self.ref = reference_data()

    def alert(self, ctx, kind, severity, evidence):
        seq = self.store.event(ctx, kind, severity, evidence)
        if severity in ('high','critical'):
            notify(severity,kind)
        return seq

    def scan(self, snapshot=None):
        snap = snapshot if snapshot is not None else collect()
        ctx = snap['context']
        if ctx == 'ctx-unknown':
            self.alert(ctx,'network-context-unknown','medium',
                       {'reason':'context identification unavailable; no baseline approval or containment'})
        process_by_pid = {p['pid']:p for p in snap['processes']}
        unusual_pids = set()
        listeners = set()
        remote_ips = set()
        mount_ids = set()
        observations = {'exe':set(),'listener':set(),'remote':set(),'usb':set()}
        for p in snap['processes']:
            exe = p.get('exe') or ''
            if exe:
                observations['exe'].add(exe)
            if any(exe.startswith(prefix) for prefix in self.ref['suspicious_execution_prefixes']) or exe.endswith(' (deleted)'):
                unusual_pids.add(p['pid'])
            if p.get('suspect_browser_mappings'):
                unusual_pids.add(p['pid'])
        for sock in snap['sockets']:
            if sock['state'] in ('LISTEN','UNCONN') and (not sock.get('peer_ip') or sock.get('peer_port') is None or sock.get('peer_ip') in ('0.0.0.0','::')):
                listeners.add(f"{sock['proto']}:{sock['local_ip']}:{sock['local_port']}")
            elif sock.get('peer_ip') and public_remote(sock['peer_ip']):
                remote_ips.add(sock['peer_ip'])
        observations['listener'] = listeners
        observations['remote'] = remote_ips
        for mount in snap['usb_mounts']:
            mount_ids.add(f"{mount['device']}:{mount['mountpoint']}")
        observations['usb'] = mount_ids
        approved = bool(self.store.approved(ctx))
        new = self.store.add_scan(ctx, observations)
        new_set = set(new)
        alerts = []
        for issue in snap['visibility_issues']:
            alerts.append(('sensor-visibility','medium',{'detail':issue}))
        for p in snap['processes']:
            if p['pid'] not in unusual_pids:
                continue
            # No unbounded command line or environmental secrets are logged.
            if ('exe',p.get('exe')) in new_set or p.get('suspect_browser_mappings'):
                alerts.append(('process-anomaly','high',{'pid':p['pid'],'process':p['name'],
                             'exe':p.get('exe'),'browser_mappings':p.get('suspect_browser_mappings',[]),
                             'interpretation':'suspicious indicator, not proof of compromise'}))
        for port in sorted(listeners):
            number = int(port.rsplit(':',1)[1])
            if ('listener',port) in new_set and number in self.ref['high_risk_listen_ports']:
                alerts.append(('high-risk-listener','high',{'socket':port,'interpretation':'investigate exposure'}))
            elif approved and ('listener',port) in new_set:
                alerts.append(('new-listener','medium',{'socket':port}))
        for category,val in new:
            if approved and category == 'remote':
                alerts.append(('new-remote-peer','medium',{'ip':val,'interpretation':'not independently malicious'}))
            elif category == 'usb':
                alerts.append(('usb-mounted','medium',{'device':val}))
        if approved and any(k == 'usb' for k,v in new) and remote_ips:
            alerts.append(('storage-network-cooccurrence','medium',
                           {'usb_mount_count':len(mount_ids),'public_remote_count':len(remote_ips),
                            'interpretation':'time coincidence only; not evidence of exfiltration'}))
        for kind,severity,evidence in alerts:
            self.alert(ctx, kind, severity, evidence)
        quarantined = []
        mode = self.store.control('response_mode','dry-run')
        # Biconditional gate: live quarantine occurs IF AND ONLY IF each verified
        # precondition is satisfied, including two independent indicators.
        gates = bool(approved and ctx != 'ctx-unknown' and mode == 'armed'
                     and self.store.control('recovery_verified') == 'yes'
                     and self.store.control('operator_authorized') == 'yes'
                     and check_capability())
        protected = dynamic_protected(snap) if gates else set()
        for sock in snap['sockets']:
            pid, ip = sock.get('pid'), sock.get('peer_ip')
            if (not pid or pid not in unusual_pids or not ip or not self.store.has_ioc(ip)):
                continue
            # Independent indicators: anomalous executable/browser mapping PLUS
            # an operator-vetted IOC on that same process socket.
            if not safe_target(ip,self.ref,protected):
                self.alert(ctx,'quarantine-denied','medium',{'ip':ip,'reason':'protected or invalid destination'})
                continue
            if not gates:
                self.alert(ctx,'quarantine-dry-run','high',{'ip':ip,'pid':pid,
                    'gates':{'approved':approved,'armed':mode=='armed',
                             'recovery_verified':self.store.control('recovery_verified')=='yes',
                             'operator_authorized':self.store.control('operator_authorized')=='yes',
                             'root_nft':check_capability()}})
                continue
            one_hour_ago=(datetime.now(timezone.utc)-timedelta(hours=1)).isoformat()
            count=self.store.con.execute('''SELECT COUNT(*) FROM quarantines WHERE applied_at>=?''',
                                         (one_hour_ago,)).fetchone()[0]
            if count >= self.ref['response']['maximum_targets_per_hour']:
                self.alert(ctx,'quarantine-rate-limited','high',{'ip':ip})
                continue
            existing=self.store.con.execute('SELECT expires_at FROM quarantines WHERE ip=?',(ip,)).fetchone()
            if existing:
                if datetime.fromisoformat(existing['expires_at']) > datetime.now(timezone.utc):
                    continue
                # Remove expired *bookkeeping* only; original audit event persists.
                with self.store.con:
                    self.store.con.execute('DELETE FROM quarantines WHERE ip=?',(ip,))
            try:
                expires=quarantine(ip,300)
                seq=self.alert(ctx,'quarantine-applied','critical',
                               {'ip':ip,'pid':pid,'expires':expires,'method':'scoped-nft-ttl'})
                with self.store.con:
                    self.store.con.execute('INSERT INTO quarantines VALUES(?,?,?,?,?)',
                                           (ip,utcnow(),expires,'nft',seq))
                quarantined.append(ip)
            except Exception as exc:
                self.alert(ctx,'quarantine-failed','high',{'ip':ip,'error':str(exc)[:250]})
        seq = self.store.event(ctx,'scan-complete','info',
                       {'processes':len(snap['processes']),'sockets':len(snap['sockets']),
                        'usb_mounts':len(snap['usb_mounts']),'alerts':len(alerts),
                        'approved':approved,'response_mode':mode,
                        'visibility_issues':len(snap['visibility_issues'])})
        return {'context':ctx,'scan_event_seq':seq,'alerts':len(alerts),
                'visibility_issues':snap['visibility_issues'],
                'quarantined':quarantined,'observations':{k:len(v) for k,v in observations.items()},
                'approved':approved,'response_mode':mode}
