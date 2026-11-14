# BEACON COMPUTING INITIATIVE
**Developer Seal:** `CJB-DEV-2026`  
**Release:** BCI Orbital Expansion `v0.3.0` — isolated evidence & capability foundation  
**Integrity:** SHA-256 manifest `SHA256SUMS` (every shipped non-manifest file)

## Four-step Group 6

1. **Context:** `context`, `legacy-context` inspect local host/routing context and legacy context descriptions, without conflating IDs.
2. **Packets + DNS + throughput:** `packet-capture` (requires explicit privileged opt-in and `CAP_NET_RAW`) records SHA-256 of full captured Ethernet frames and protocol/DNS metadata (HMAC by default). Raw packet contents are never persisted. `throughput` measures `/proc/net/dev` interface counter deltas, replacing misleading placeholder zeros.
3. **Kernel file evidence:** `kernel-trace` (requires explicit privileged opt-in and bpftrace) records bounded `openat` and `execve` syscall entry attempts, NOT verified successful file reads/writes. Sensitive paths are HMACed. No kernel/host settings are changed.
4. **Reasoning, model gating and adaptation:** `reason` invokes hash-verified Orbital Neural v0.2.0 correlation logic. `shadow-score` enforces exact context, model integrity and complete qualified sensor coverage; `propose-retraining` creates a review-only drift report and does not retrain or promote anything.

## Preconditions / install (as bci, NO sudo)

Verify outer ZIP SHA-256 first; extract and run:

```bash
cd ~/Downloads/BCI-Orbital-Expansion-v0.3.0
sha256sum -c SHA256SUMS
PYTHONPATH=src python3 -B -m unittest discover -s tests -v
bash scripts/install.sh --user
bash scripts/group6.sh
~/.local/bin/bci-orbital-expansion doctor
~/.local/bin/bci-orbital-expansion context
~/.local/bin/bci-orbital-expansion throughput --seconds 2
```

### v0.3 corrected neural feature window (run without sudo)

This connects the existing *hash-verified* process/network sensors to measured
interface RX/TX counter deltas. It produces a new unreviewed, per-context feature
window. It does **not** silently rewrite or reinterpret v0.2.0 zero-rate records.

```bash
~/.local/bin/bci-orbital-expansion capture-window \
  --orbital-release ~/.local/opt/bci-orbital-v2/0.1.0 \
  --neural-release ~/.local/opt/bci-orbital-neural/0.2.0 \
  --seconds 2 --output ~/BCI-Orbital-Neural-Window-NEW.jsonl
```

Verify the actual installed `--orbital-release` location first; the documented
path is illustrative and may differ from the installed release layout. The
output is create-only. Files and hashes should be retained as evidence. The
window is **unreviewed_live**, not automatically normal or training-approved.

The four-step `scripts/group6.sh` verifies both installed legacy releases,
records context/capability and actual throughput reports, writes a hashed
`unreviewed_live` neural feature window, and independently verifies outputs.
It runs as `bci` and never enables privileged sensors or changes systemd.

The installer does NOT alter existing `bci-orbital-v2.service` or `bci-orbital-neural.timer`. It does NOT register or start background services and has no response capability. Privileged capture/trace commands intentionally are not automatically configured. **Do not run Python from `/home/bci` as root:** prepare a separate root-owned, immutable deployment with an independently verified release digest before scheduling privileged collectors. This release does not provide that hardened system deployment.

## Additional CLI

```
~/.local/bin/bci-orbital-expansion legacy-context --source /home/chance/BCI-Orbital-CyberDefense/state/operator/evidence.sqlite
~/.local/bin/bci-orbital-expansion verify /path/to/report.json
~/.local/bin/bci-orbital-expansion shadow-score --model /path/to/verified-model.json --candidate /path/to/qualified-window.jsonl --neural-release /home/bci/.local/opt/bci-orbital-neural/0.2.0 --output /path/to/new-shadow-report.json
~/.local/bin/bci-orbital-expansion reason --evidence /path/to/verified-event-set.json --neural-release /home/bci/.local/opt/bci-orbital-neural/0.2.0 --output /path/to/new-reasoning-report.json
~/.local/bin/bci-orbital-expansion propose-retraining --previous /path/to/qualified-a.jsonl --current /path/to/qualified-b.jsonl --neural-release /home/bci/.local/opt/bci-orbital-neural/0.2.0 --output /path/to/new-proposal.json
```

The explicit privileged commands `packet-capture` and `kernel-trace` require their respective `--acknowledge-*` flags and must be run ONLY from a separately hardened root-owned deployment. Neither command implements containment.

## Coverage and limitations

| User goal | v0.3.0 capability | Limits |
|---|---|---|
| Every-packet SHA-256 | opt-in bounded AF_PACKET capture | captures only packets visible to that interface; drops, offload, jumbo and encryption gaps; no wire completeness guarantee |
| DNS intelligence | parser for unencrypted UDP/TCP port 53 DNS queries | no TLS/DoH/DoT decryption; no TCP reassembly; labels hashed by default |
| File accesses | bpftrace openat/execve syscall-entry probes | ATTEMPTS only; not full filesystem modification/read tracing |
| Kernel security | bpftrace optional Linux tracepoints | requires privileges, availability and overhead qualification; no anti-rootkit claim |
| Traffic throughput | interface `/proc/net/dev` deltas | not process-level, doesn't prove exfiltration |
| Neural model reasoning | verified v0.2.0 deterministic correlation | no generative reasoning or attribution of attacker intent |
| Adaptive learning | review-only drift proposal + existing manual training path | no autonomous training, baseline promotion, or unsafe online learning |
| Neural prevention | deliberately disabled | requires independent recovery testing, safeguards and explicit approval |
| Threat attribution | stable-process association when data supports it | remote human identity, intent and ownership cannot be proved by this telemetry |

**Privacy and evidence:** only local output, create-only hashed files, no packet contents or raw file paths persisted by default. All findings are hypotheses and must be corroborated. SHA-256 proves post-hoc consistency with a trusted checksum, not independent acquisition authenticity.

**Release integrity footer:** Obtain archive digest from adjacent `.zip.sha256`. All source files have `Developer Seal: CJB-DEV-2026` headers; manifest enumerates file hashes. If either manifest fails, do not install.
