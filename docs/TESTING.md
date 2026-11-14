<!-- BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026 -->
# Verification and Acceptance Test Strategy

**BEACON COMPUTING INITIATIVE** | **Developer Seal: CJB-DEV-2026**  
**ORBIT11 / BCI Orbital Cyber Defense AI** | **Status: Design specification**

## Test pyramid

| Level | Examples | Exit criterion |
|:--|:--|:--|
| Unit | Event canonicalization, threshold math, policies, hash chain | Deterministic expected outputs |
| Integration | Collector -> ledger -> detection, baseline versioning | No silent gap, clear error signals |
| Negative | Missing privileges, stale identity, broken sensor, symlink purge | Safe denial/HOLD |
| Safety | Containment expiry, rollback, watchdog, non-target isolation | Bounded action and recovery |
| ML | Holdout, time/context split, drift, poisoning, false positives | Predeclared metric thresholds |
| Reliability | Disk full, clock jump, power interruption, WAL replay | No false PASS or unexplained loss |
| Release | Reproducible artifacts, manifests, migration/restore, secret scan | Operator acceptance recorded |

## Required security cases

- Approval absent or stale => no baseline/model promotion.
- New network context => no unapproved containment.
- Single weak indicator => record finding, not forced intervention.
- Unverifiable evidence chain => deny mutating actions.
- Legal hold present => no training-data purge.
- Failed training/evaluation => keep previous model and input protection.
- Unavailable rollback => deny response, even for high anomaly scores.
- Malformed/oversized event => reject and audit without crashing.
- Hash-chain replacement => detect via trusted external anchor or document that detection is not guaranteed.

## Test data rules

Use synthetic, minimized fixtures. Separate normal cases from adversarial cases and avoid data leakage between train and test. Record exact source version, test commands, runtime, OS/kernel context, seed, outputs and artifact hashes. If a test suite is not committed and runnable, do not describe it as passing.

## Qualification gates

An acceptance claim is valid if and only if the version under review matches the tested artifact, required test families have executed successfully, evidence is preserved, safety/identity approvals are valid, and operational risks are recorded. A mocked "pass" or legacy-project result does not qualify this repository.

## CI progression

Milestone 0: documentation integrity and link checks. Milestone 1: deterministic read-only unit tests. Milestone 2: integration and fault injection. Milestone 3: model validation. Milestone 4: hardware-in-loop and rollback drills. Milestone 5: production qualification. Each promotion requires an acceptance report.
