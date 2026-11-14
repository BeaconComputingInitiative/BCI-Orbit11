# BEACON COMPUTING INITIATIVE | Orbital Cyber Defense
# Developer Seal: CJB-DEV-2026
# File SHA-256: see SHA256SUMS
"""Tamper-evident, append-only event chain and per-network observational baseline."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import sqlite3
from datetime import datetime, timezone

GENESIS = '0' * 64

def utcnow():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

class Store:
    def __init__(self, home: Path):
        self.home = Path(home)
        self.home.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(self.home, 0o700)
        db = self.home / 'orbital.sqlite3'
        self.con = sqlite3.connect(str(db), timeout=20)
        self.con.row_factory = sqlite3.Row
        self.con.execute('PRAGMA journal_mode=WAL')
        self.con.execute('PRAGMA synchronous=FULL')
        if db.exists():
            os.chmod(db, 0o600)
        self.con.executescript('''
        CREATE TABLE IF NOT EXISTS events(
          seq INTEGER PRIMARY KEY AUTOINCREMENT,
          ts TEXT NOT NULL, context TEXT NOT NULL,
          kind TEXT NOT NULL, severity TEXT NOT NULL,
          data TEXT NOT NULL, prev_hash TEXT NOT NULL, entry_hash TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS scans(ts TEXT NOT NULL, context TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS scans_ctx ON scans(context,ts);
        CREATE TABLE IF NOT EXISTS observations(
          context TEXT NOT NULL, category TEXT NOT NULL, value TEXT NOT NULL,
          first_seen TEXT NOT NULL, last_seen TEXT NOT NULL,
          PRIMARY KEY(context,category,value));
        CREATE TABLE IF NOT EXISTS deviations(
          context TEXT NOT NULL, category TEXT NOT NULL, value TEXT NOT NULL,
          first_seen TEXT NOT NULL, last_seen TEXT NOT NULL,
          PRIMARY KEY(context,category,value));
        CREATE TABLE IF NOT EXISTS historical_observations(
          ts TEXT NOT NULL, context TEXT NOT NULL, category TEXT NOT NULL,
          value TEXT NOT NULL, source_sha256 TEXT NOT NULL,
          PRIMARY KEY(ts,context,category,value,source_sha256));
        CREATE TABLE IF NOT EXISTS approvals(
          context TEXT PRIMARY KEY, approved_at TEXT NOT NULL,
          baseline_hash TEXT NOT NULL, method TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS controls(
          key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS pending_iocs(
          ip TEXT PRIMARY KEY, note TEXT NOT NULL, added_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS quarantines(
          ip TEXT PRIMARY KEY, applied_at TEXT NOT NULL, expires_at TEXT NOT NULL,
          method TEXT NOT NULL, event_seq INTEGER NOT NULL);
        ''')
        self.con.commit()

    def close(self):
        self.con.close()

    def event(self, context: str, kind: str, severity: str, data: dict, ts: str | None = None):
        ts = ts or utcnow()
        row = self.con.execute('SELECT entry_hash FROM events ORDER BY seq DESC LIMIT 1').fetchone()
        prev = row['entry_hash'] if row else GENESIS
        data_json = canonical(data)
        content = canonical([prev, ts, context, kind, severity, data_json])
        digest = hashlib.sha256(content.encode()).hexdigest()
        with self.con:
            cur = self.con.execute('''INSERT INTO events(ts,context,kind,severity,data,prev_hash,entry_hash)
            VALUES(?,?,?,?,?,?,?)''', (ts, context, kind, severity, data_json, prev, digest))
        return cur.lastrowid

    def verify_chain(self):
        previous = GENESIS
        count = 0
        for r in self.con.execute('SELECT * FROM events ORDER BY seq'):
            content = canonical([previous, r['ts'], r['context'], r['kind'], r['severity'], r['data']])
            digest = hashlib.sha256(content.encode()).hexdigest()
            if previous != r['prev_hash'] or digest != r['entry_hash']:
                return False, count, r['seq']
            previous = digest
            count += 1
        return True, count, None

    def add_scan(self, context: str, observations: dict[str, set[str]], ts: str | None = None):
        ts = ts or utcnow()
        newly_seen = []
        locked = bool(self.approved(context))
        with self.con:
            self.con.execute('INSERT INTO scans(ts,context) VALUES(?,?)', (ts, context))
            for category, values in observations.items():
                for value in sorted(set(values)):
                    row = self.con.execute('''SELECT 1 FROM observations
                         WHERE context=? AND category=? AND value=?''', (context, category, value)).fetchone()
                    if row is None:
                        if locked:
                            prior = self.con.execute('''SELECT 1 FROM deviations WHERE context=? AND category=? AND value=?''',
                                                     (context, category, value)).fetchone()
                            if prior is None:
                                newly_seen.append((category, value))
                                self.con.execute('''INSERT INTO deviations VALUES(?,?,?,?,?)''',
                                                 (context, category, value, ts, ts))
                            else:
                                self.con.execute('''UPDATE deviations SET last_seen=?
                                    WHERE context=? AND category=? AND value=?''', (ts, context, category, value))
                        else:
                            newly_seen.append((category, value))
                            self.con.execute('''INSERT INTO observations VALUES(?,?,?,?,?)''',
                                             (context, category, value, ts, ts))
                    else:
                        self.con.execute('''UPDATE observations SET last_seen=?
                            WHERE context=? AND category=? AND value=?''', (ts, context, category, value))
        return newly_seen

    def approved(self, context: str):
        return self.con.execute('SELECT * FROM approvals WHERE context=?', (context,)).fetchone()

    def baseline_stats(self, context: str):
        row = self.con.execute('''SELECT COUNT(*) AS n, MIN(ts) AS first, MAX(ts) AS last,
            COUNT(DISTINCT substr(ts,1,13)) AS hours FROM scans WHERE context=?''', (context,)).fetchone()
        categories = {r['category']:r['n'] for r in self.con.execute('''SELECT category, COUNT(*) AS n
            FROM observations WHERE context=? GROUP BY category''', (context,))}
        historical=self.con.execute('SELECT COUNT(*) FROM historical_observations WHERE context=?',(context,)).fetchone()[0]
        return {**dict(row), 'categories':categories, 'historical_observations_untrusted':historical, 'approved':bool(self.approved(context))}

    def baseline_digest(self, context: str):
        obs = [(r['category'], r['value']) for r in self.con.execute('''
          SELECT category,value FROM observations WHERE context=? ORDER BY category,value''', (context,))]
        return hashlib.sha256(canonical(obs).encode()).hexdigest()

    def approve(self, context: str, method: str):
        digest = self.baseline_digest(context)
        with self.con:
            self.con.execute('''INSERT INTO approvals VALUES(?,?,?,?)
                ON CONFLICT(context) DO UPDATE SET approved_at=excluded.approved_at,
                baseline_hash=excluded.baseline_hash,method=excluded.method''',
                (context, utcnow(), digest, method))
        self.event(context, 'baseline-approved', 'info', {'method':method, 'baseline_sha256':digest})
        return digest

    def set_control(self, key: str, val: str):
        with self.con:
            self.con.execute('''INSERT INTO controls VALUES(?,?) ON CONFLICT(key)
                DO UPDATE SET value=excluded.value''', (key,val))

    def control(self, key: str, default=None):
        r = self.con.execute('SELECT value FROM controls WHERE key=?', (key,)).fetchone()
        return r['value'] if r else default

    def recent(self, limit=20):
        return [dict(x) for x in self.con.execute('SELECT * FROM events ORDER BY seq DESC LIMIT ?', (limit,))]

    def add_ioc(self, address: str, note: str):
        with self.con:
            self.con.execute('''INSERT INTO pending_iocs VALUES(?,?,?) ON CONFLICT(ip)
                    DO UPDATE SET note=excluded.note,added_at=excluded.added_at''', (address,note,utcnow()))
        self.event('operator','ioc-registered','info',{'ip':address,'note':note})

    def has_ioc(self, address: str):
        return self.con.execute('SELECT 1 FROM pending_iocs WHERE ip=?', (address,)).fetchone() is not None
