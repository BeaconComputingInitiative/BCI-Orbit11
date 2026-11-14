# BEACON COMPUTING INITIATIVE — VALIDATION RECORD

**Developer Seal:** `CJB-DEV-2026`  
**Release:** `0.1.0` engineering preview  
**File SHA-256:** See `SHA256SUMS` and `SHA256SUMS.sha256`.

## Verified in this packaging environment

| Test | Result |
|---|---|
| Python standard-library unit tests | 9 passed, 0 failed |
| Initial hash manifest verification | PASS: all tracked release payloads |
| Shell script syntax (`bash -n`) | PASS |
| Fresh `--user` install under isolated unprivileged test account | PASS |
| Installed CLI launcher, one sensor scan | PASS |
| Status and evidence chain after test scan | PASS |
| Existing service untouched by installer | By design; not exercised against user's actual legacy service |
| Kali host system-mode deployment | NOT RUN |
| Systemd live unit and reboot persistence | NOT RUN |
| nftables recovery drill and quarantine TTL on Kali host | NOT RUN |
| Baseline 7-day learning and manual approval on Kali host | NOT RUN |
| Live DNS / eBPF / exfiltration correlation | NOT IMPLEMENTED |

**Release qualification: ENGINEERING PASS / OPERATIONAL HOLD.**

A successful sandbox scan is not a test of your particular Kali installation or your existing Orbital service. Do not arm automatic enforcement until the live system's sensor coverage, approvals, firewall rollback, and baseline provenance have been independently verified.
