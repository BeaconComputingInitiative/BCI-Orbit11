<!-- BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026 -->
# Requirements and Acceptance Criteria

**BEACON COMPUTING INITIATIVE** | **Developer Seal: CJB-DEV-2026**  
**ORBIT11 / BCI Orbital Cyber Defense AI** | **Status: Design specification**

All identifiers are proposed product acceptance requirements, not completed tests.

## Functional requirements

| ID | Requirement | Minimum acceptance evidence |
|:--|:--|:--|
| OBS-01 | Collect host, network and storage metadata only with an approved scope | Deterministic fixtures, privilege review, bounded failure tests |
| OBS-02 | Identify source, host, process and clock context where available | Schema tests and unknown-value coverage |
| NET-01 | Detect unexpected listeners and destination changes relative to profile | Positive/negative fixture evaluation |
| NET-02 | Correlate metadata-only outbound anomalies with other signals | Incident explanation includes source IDs |
| STO-01 | Identify removable storage/copy bursts without assuming malicious intent | Benign large-copy control cases |
| EVD-01 | Link findings to unmodified source evidence and audit changes | Tamper/reorder/gap verification tests |
| EVD-02 | Maintain protected legal-hold and incident-evidence classification | Deletion-denial tests |
| BAS-01 | Keep separate profiles for distinct network contexts | Context-switch regression tests |
| BAS-02 | Require authenticated approval before baseline publication | Unauthorized promotion denied |
| AI-01 | Record training data lineage, model identity and deterministic eval | Reproducible candidate evaluation |
| AI-02 | Reject candidates that breach declared false-positive or safety budgets | Holdout and regression gate reports |
| RET-01 | Delete eligible transient training data after validated use | Selective purge and audit receipt |
| RET-02 | Never delete legal holds, active evidence or unverified source inputs | Retention precedence and crash tests |
| POL-01 | Separate detection from response authorization | Direct model-to-response bypass denied |
| POL-02 | Containment requires approved policy and corroboration | All-denied permutations tested |
| RES-01 | Containment is reversible and externally observable | Rollback drills and recovery tests |
| OPS-01 | Provide explicit healthy/degraded/HOLD operational state | Failure-injection and operator UI tests |
| OPS-02 | Keep telemetry local by default | Network egress tests without export consent |
| SEC-01 | Ensure control actions have authenticated, audited principals | Forged identity and replay tests |
| SEC-02 | Isolate privileged collectors and protect keys | Least-privilege and secret-scan reports |

## Non-functional requirements

- **Reliability:** no silent gaps, no false PASS based only on absence of errors, and visible timestamps for the most recent successful sample per sensor.
- **Performance:** record CPU, memory, disk and event-throughput baselines for target machines before asserting budget numbers.
- **Safety:** no remote blocking, quarantine, firewall mutation or deletion during initial read-only milestones.
- **Portability:** Linux first; document specific kernel permissions and unsupported distributions. Android/ADB and Windows are separate optional integration proposals.
- **Confidentiality:** minimize captured personal data; retain sensitive local material outside source control.
- **Accessibility:** provide explanations in plain language alongside technical evidence and version identifiers.
- **Recovery:** operator can restore last approved profiles and policies without trusting an unverified model.
- **Observability:** audit every decision, missing sensor, model change, approval and response attempt.

## Evidence needed before labeling a milestone PASS

A milestone is PASS if and only if its specified tests run on version-pinned inputs, their artifacts and hashes are recorded, no required safety gate is bypassed, and acceptance is explicitly signed off by the responsible operator. A passing unit test count alone is not production acceptance.

## Scope exclusions at project start

No cloud-hosted inference dependency; no offensive exploitation features; no endpoint surveillance outside owned/authorized environments; no autonomous evidence deletion; no claims about identity, motive or criminal attribution based solely on anomaly scores.
