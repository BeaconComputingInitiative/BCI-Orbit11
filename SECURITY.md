# Security and privacy

BEACON COMPUTING INITIATIVE · Developer Seal: CJB-DEV-2026

## Intended boundary

BCI-Orbit11 is an experimental local defensive analysis system. Its neural output
supports human review. It is not a certified EDR, a network-authenticity oracle,
a forensic acquisition appliance or an autonomous response authority.

## Threats and current controls

| Threat | Current control | Residual risk |
|---|---|---|
| Accidental artifact modification | Source/sidecar digests and event chains | Account owner can replace data and hashes |
| Baseline poisoning | Review gates, immutable candidate outputs, separate trust classes | Review quality and source trust remain external |
| Context confusion | Exact contexts and host/route provenance | Vendor/environment semantics still need acceptance |
| Missing sensors | Gaps and explicit HOLD/unavailable states | Blind spots remain; status is not a clean-host verdict |
| Malformed inputs | Schema, numeric, size and chronology validation | Not a comprehensive hostile-input audit |
| Arbitrary prompt execution | Deterministic intent routing; no prompt-to-shell path | Legacy administrative commands remain separate tools |
| Excess privilege | No privilege escalation in tests or source import | Optional capture and legacy firewall features require care |
| Privacy exposure | Aggregate features and HMAC options | Host monitor evidence can still contain sensitive identifiers |
| Disk exhaustion | Quota diagnostics and explicit stops in existing collectors | Retention/archival automation remains incomplete |
| False inference | Separate novelty, hypothesis and confirmed findings | No labeled independent detection benchmark supplied |

## Sensitive functions retained

The legacy host `response.py` includes nftables setup, quarantine, release and table
removal functions. Expansion has opt-in AF_PACKET capture and bpftrace probes.
Installers and migration scripts can write versioned launchers or service units.
The console can request training and privileged evidence verification through
explicit operator workflows. Their inclusion is source preservation, not approval
to execute them. This repository was populated without running those workflows.

Never run mutable user-owned Python as root in a scheduled collector. A hardened,
root-owned deployment, reviewed capabilities, independently verified source and
recovery testing are prerequisites to future privileged operation.

## Repository hygiene

Commit source, synthetic fixtures and reviewed documentation. Keep secrets,
credentials, evidence databases, captures, journals, private checkpoints and approval
files outside Git. `.gitignore` is a convenience, not a security boundary; inspect
the staged file list and contents before each push. A private repository also does
not justify uploading unrelated or unnecessary sensitive records.

The included model hash and legacy context pins are source-level compatibility
metadata, not live evidence or distributable weights. Renaming them would break
verification and requires an explicit artifact migration.

## Reporting a vulnerability

Send the repository owner a private report through an established private channel
or GitHub private vulnerability reporting if the owner enables it. No dedicated
security mailbox or response SLA has been configured by this import. Do not post
credentials, personal telemetry, exploit targets or private evidence in public
issues. Include affected component/version, minimal synthetic reproduction,
expected behavior, actual behavior and proposed mitigation where available.

## Assurance limits

No penetration test, privileged deployment validation, packet completeness claim,
model robustness guarantee, malicious-intent classifier or authenticated registry
is supplied. Read the model card, per-component limitations and latest validation
report before deciding what conclusion a finding can support.
