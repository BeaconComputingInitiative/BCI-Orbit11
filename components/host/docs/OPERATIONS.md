# BEACON COMPUTING INITIATIVE — ORBITAL CYBER DEFENSE
**Developer Seal:** `CJB-DEV-2026`  
**Artifact SHA-256:** Recorded in top-level `SHA256SUMS`.

## Runbook and fail-closed gates

A production containment action runs **IF AND ONLY IF** all conditions are true:

1. The current, identifiable network-context profile is operator-approved after at least seven elapsed days and 24 distinct scan hours (or a configured additional 14 days).
2. The operator has confirmed authorization at a local interactive terminal.
3. A scoped nftables recovery drill has passed, and the daemon has root/CAP_NET_ADMIN and `nft` functionality.
4. The response mode is `armed`.
5. A process has a suspect executable location or browser mapping **and** the same process has a socket to an operator-registered external IOC address.
6. The target is globally routable, is not protected (local/reserved/gateway/DNS), and does not exceed the rate limit of three targets/hour.

If any gate fails, Orbital records an alert and does not change firewall state. Each live quarantine is a temporary address-specific nftables rule expiring in 300 seconds. There are no automatic process kills, reboots, account locks, device unmounts, or broad network shutdowns.

## User-mode install (BCI account)

Run this **as the account that will own the installation**; do not run `--user` through sudo:

```bash
cd BCI-Orbital-CyberDefense-v0.1.0
sha256sum -c SHA256SUMS
bash scripts/install.sh --user
~/.local/bin/bci-orbital-v2 scan
~/.local/bin/bci-orbital-v2 status
systemctl --user enable --now bci-orbital-v2.service
```

User mode monitors only processes and sockets visible to that account; `nft` live response is unavailable. It does not modify the old `bci-orbital.service`.

## System-mode install (host visibility and optional scoped response)

Run only after confirming legacy Orbital monitoring and evidence have been preserved; a second monitor may duplicate alerts:

```bash
cd BCI-Orbital-CyberDefense-v0.1.0
sha256sum -c SHA256SUMS
sudo bash scripts/install.sh --system
sudo /usr/local/bin/bci-orbital-v2-system scan
sudo /usr/local/bin/bci-orbital-v2-system status
sudo systemctl enable --now bci-orbital-v2.service
```

Activation is **not automatic**. `--activate` is provided for a deliberate one-step install-and-start and refuses activation when the existing `bci-orbital.service` is active.

## Baseline lifecycle

The included `reference.json` is a **curated generic seed**, not a trained weight file and not observed from this host. Its heuristics enable immediate alerts, but it does not classify any host as clean and does not authorize enforcement.

Each network context is identified by an opaque hash of default-route metadata. A profile starts in learning mode. The first seven days establish local observations. Set `baseline extend --days 14` to require 21 days for extra validation. No new observations are automatically incorporated into an approved baseline.

```bash
bci-orbital-v2 baseline status
bci-orbital-v2 baseline extend --days 14
bci-orbital-v2 baseline approve
```

`baseline approve` asks for an interactive confirmation phrase and fails unless the time and sample gates pass. When live-response authorization and recovery drill are already complete, approval automatically sets the response mode to `armed`, satisfying the after-approval behavior requirement.

### Optional historical import (30-day target)

Create an **operator-reviewed** UTF-8 JSONL with one object per line:

```json
{"ts":"2026-11-01T20:00:00+00:00","context":"ctx-1234567890abcdef","category":"listener","value":"tcp:0.0.0.0:22"}
```

Allowed categories are `exe`, `listener`, `remote`, and `usb`. The `context` must match `baseline status`, and the SHA-256 must match exactly:

```bash
sha256sum history.jsonl
bci-orbital-v2 baseline import-history history.jsonl --sha256 <digest>
```

Imported records remain in a separate **untrusted historical** table. They do not shorten the seven-day live requirement and do not suppress anomaly alerts. An inventory of 30 days is recommended where available, but it must not silently become the host's trusted baseline. The importer accepts up to 200,000 observations.

## Response qualification and activation

System mode only, with active host visibility and source verification:

```bash
sudo bci-orbital-v2-system response drill
sudo bci-orbital-v2-system response authorize
sudo bci-orbital-v2-system baseline approve
# After approval, if already qualified, response auto-arms.
sudo bci-orbital-v2-system response arm
sudo bci-orbital-v2-system response ioc-add 1.2.3.4 --note 'Operator-verified IOC and case reference'
```

Use the `response arm` command when authorization/drill occur after baseline approval. Never register an address solely because it is unfamiliar. `response disarm` switches to dry-run; existing rules automatically expire within five minutes. `response release <ip>` deletes a specific owned rule after local confirmation.

## Evidence, notifications, and limitations

- User state: `~/.local/state/bci-orbital-v2/`. Root service state: `/var/lib/bci-orbital-v2/`.
- Each alert is appended to SQLite WAL with a SHA-256 hash-chain. Keep trusted periodic copies of the chain head or exported digest off-host; an attacker with database write access could rewrite the entire chain.
- `bci-orbital-v2 integrity verify` verifies the internal chain. `bci-orbital-v2 export <newpath>.jsonl` creates an independent file plus `<newpath>.jsonl.sha256`.
- Desktop notifications are best-effort, typically only in graphical user mode. Email integration is disabled.
- Browser mapping anomalies are indicators, not proof of hooking; socket observations are not packet capture, and this version does not parse live DNS queries, perform kernel/eBPF instrumentation, correlate process bytes with outbound traffic, or assert exfiltration from temporal coincidence.
- No existing BCI Orbital source, databases, config, or service are overwritten by this installer. If such paths conflict, installation fails closed.

## Release validation

```bash
sha256sum -c SHA256SUMS
PYTHONPATH=src python3 -m unittest discover -s tests -v
bash -n scripts/install.sh
PYTHONPATH=src python3 -m bci_orbital --state-dir /tmp/bci-orbital-smoketest scan
```

Production acceptance is **HOLD** until tests are repeated on the target Kali host, baseline source provenance is reviewed, coverage is qualified, and the response/recovery drill is completed. Developer seal identifies project ownership; it is not a digital signature or code-signing certificate.
