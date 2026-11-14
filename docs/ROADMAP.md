<!-- BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026 -->
# Development Roadmap and Exit Gates

**BEACON COMPUTING INITIATIVE** | **Developer Seal: CJB-DEV-2026**  
**ORBIT11 / BCI Orbital Cyber Defense AI** | **Status: Design specification**

This roadmap states **intent**, not completed work. Milestone status is deliberately conservative.

| Stage | Deliverables | Exit gate | Status |
|:--|:--|:--|:--|
| M0: Charter | README, specs, security boundaries, contribution rules | Reviewed design; no operational claims | Documentation authored |
| M1: Evidence core | Event schemas, local store, hash-chain verification, synthetic fixtures | Crash/tamper/replay tests pass | Not started |
| M2: Sensors | Process/socket/storage metadata, telemetry health | Least-privilege and negative tests | Not started |
| M3: Baselines | Context profiles, history/live import, approval ledger | Authorized versioned promotion; drift tests | Not started |
| M4: Detection | Rules, correlation, explainable incidents | Benign/malicious fixture and FP budget | Not started |
| M5: Local adaptive AI | Candidate training, evaluation, registry and rollback | Reproducible positive/negative performance | Not started |
| M6: Retention | Qualified post-training purge and legal holds | Deletion denial and recovery tests | Not started |
| M7: Operator surface | Authenticated CLI/API, GUI, notifications | Usability, identity and access tests | Not started |
| M8: Dry-run response | Policy reasoning, action simulation, audited review | No mutation in dry-run verified | Not started |
| M9: Guarded containment | Bounded executor, recovery, approval workflow | Independent rollback and fail-safe drills | Not started |
| M10: Deployment | systemd packaging, migration, health, observability | Full environment acceptance and sign-off | Not started |

## Delivery slices

- **First slice:** synthetic event ingestion and integrity verifier; no privileges and no network activity.
- **Second slice:** read-only process/socket metadata under minimum privileges, health and gap handling.
- **Third slice:** reviewed profiles and audited incident correlation.
- **Subsequent slices:** local learning, retention, operator UI and containment in that order.

## Definition of done

A milestone completes if and only if its actual code and docs are committed, its acceptance suite passes on the exact commit, artifacts are hashed, security risks are reviewed, and an operator signs off on the stated scope. Labels such as "AI-powered", "active protection" and "self-learning" are not permitted until corresponding functionality is demonstrated.
