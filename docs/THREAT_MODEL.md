<!-- BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026 -->
# Security Threat Model

**BEACON COMPUTING INITIATIVE** | **Developer Seal: CJB-DEV-2026**  
**ORBIT11 / BCI Orbital Cyber Defense AI** | **Status: Design specification**

## System and adversaries

The defended assets are the host's confidentiality, integrity, availability, administrative control, sensitive records, verified evidence and approved detection policies. Relevant adversaries may include opportunistic network attackers, local unprivileged malware, compromised accounts, malicious peripherals and insiders with elevated privileges. A fully compromised root/kernel is outside the guarantee of a local sensor alone.

## Trust boundaries

| Boundary | Threats | Required mitigations |
|:--|:--|:--|
| Host OS -> sensor | Forged events, blind spots, privilege escalation | Narrow capabilities, source health, event validation |
| Sensor -> event bus | Injection, replay, oversized payloads | Typed schemas, rate limits, origin identity, sequence tracking |
| Event bus -> evidence store | Deletion, tampering, rollback | Immutable logical history, protected checkpoint, recovery tests |
| Evidence -> model | Poisoning, label contamination, secret leakage | Training qualification, provenance, holdouts, isolation |
| Model -> interpretation | Overconfidence, misleading explanation | Confidence semantics, counterexamples, provenance |
| Detection -> policy | Unsafe autonomous action | No direct enforcement path, signed approvals |
| Policy -> executor | Confused deputy, stale targets, escalation | Short-lived authorization, narrow actions, dry-run and rollback |
| GUI/API -> daemon | CSRF/replay/insecure local IPC | Local bind, peer credential checks, authz, auditing |
| Repo -> runtime | Dependency compromise, secret exposure | Reviewable changes, pinned builds, secret scanning |
| Export -> external party | Sensitive information exfiltration | Explicit opt-in, encryption and destination review |

## Required abuse cases

Test benign USB backup incorrectly labeled exfiltration; VPN or Wi-Fi context changes; user-installed developer services; package updates changing listeners; a single high-volume outbound upload; rogue process reenacting a known PID; forged sensor events; model weights overwritten after approval; accidental data purge across a symlink; an expired policy; an interrupted containment rollback; and a privileged attacker replacing an entire hash chain.

## Security properties and limitations

- A cryptographic hash is an integrity primitive, **not** a source of authorization.
- Anomaly detection is uncertain and must support benign alternatives.
- The host may be compromised before the collector starts; no baseline can retroactively guarantee a trusted past.
- Without an independent log anchor, root can often rewrite both evidence and hashes.
- Blocking traffic can destroy legitimate connectivity and evidence; availability is part of security.

## Privacy and acceptable use

Collect only from owned or administratively authorized systems. Follow consent, retention and local legal requirements. Do not infer human identity, intent or criminality from network metadata. Require explicit review before third-party disclosure.

## Review cadence

Revisit this threat model before adding any privileged collector, remote endpoint, autonomous action, new model type or new evidence export channel.
