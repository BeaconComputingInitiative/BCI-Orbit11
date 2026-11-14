# BEACON COMPUTING INITIATIVE

**Project:** Orbital Cyber Defense — clean-room source implementation  
**Version:** `0.1.0` — engineering preview  
**Developer Seal:** `CJB-DEV-2026`  
**Integrity:** SHA-256 per-file hashes in `SHA256SUMS`, distribution ZIP hash provided separately

## Source-complete, installable replacement prototype

This bundle contains **all source code** required to run its implemented monitoring and baseline capabilities. No earlier Orbital repository is required. It is deliberately deployed as `bci-orbital-v2` so the existing `bci-orbital.service`, forensic evidence, configuration and current installation are not overwritten.

### Delivered capabilities

- Read-only Linux `/proc` process examination and Chromium/Firefox mapping anomaly indicators.
- `ss`-based TCP/UDP socket/listener inventory with PID association when permissions allow.
- USB block storage mount observation through `lsblk`.
- Per-network-context baseline observations, seven-day approval gate, optional fourteen-day extension, 30-day historical evidence import path.
- Bundled curated reference profile for immediate alerts, explicitly **not** actual host-specific pretrained model weights.
- Locked approved baselines: novel observations are retained separately as deviations, without unauthorized learning.
- SQLite WAL, SHA-256 event chain, forensic export with sidecar hashes.
- Desktop notification attempts, email disabled.
- Guarded, 300-second, single-destination nftables containment when all explicit gates pass.
- Self-contained standard-library Python package, Kali/systemd user + system installation methods, tests, manifest.

### Known gaps before production-grade acceptance

This engineering preview has **no live DNS packet capture, browser-injection proof, kernel/eBPF telemetry, historical conversion from arbitrary prior DB schemas, packet/byte-based exfiltration attribution, signed threat-intelligence feed, secure operator authentication, or full rollback orchestrator**. It cannot certify a host clean. It should not be described as a fully qualified production cyber-defense replacement. Refer to [Operations and acceptance gates](docs/OPERATIONS.md).

### Files

- `src/bci_orbital/` — complete implementation, reference seed, CLI and safety gates
- `systemd/` — user and root system units (different service name from legacy)
- `scripts/install.sh` — digest-verified, collision-refusing installation
- `tests/test_orbital.py` — unit and negative tests
- `docs/OPERATIONS.md` — commands, baseline qualification, containment conditions
- `SHA256SUMS` — immutable payload inventory generated for this release

### Quick start on Kali

```bash
cd BCI-Orbital-CyberDefense-v0.1.0
sha256sum -c SHA256SUMS
PYTHONPATH=src python3 -m unittest discover -s tests -v
bash scripts/install.sh --user
~/.local/bin/bci-orbital-v2 scan
~/.local/bin/bci-orbital-v2 status
```

**IF AND ONLY IF** all manifest hashes validate, supported dependencies are present, and paths are unoccupied will the installer promote this isolated release. New service activation is opt-in. See the operations guide for host-scope deployment.
