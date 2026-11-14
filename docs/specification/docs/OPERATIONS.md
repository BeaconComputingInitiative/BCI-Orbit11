<!-- BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026 -->
# Operations and Incident Runbook

**BEACON COMPUTING INITIATIVE** | **Developer Seal: CJB-DEV-2026**  
**ORBIT11 / BCI Orbital Cyber Defense AI** | **Status: Pre-deployment runbook**

## Status definitions

- **NOT_IMPLEMENTED:** design exists but binary/service does not.
- **HOLD:** required evidence, approvals or controls are missing; no promotion/containment.
- **OBSERVE_ONLY:** implemented sensor collects within approved scope, but makes no disruptive changes.
- **DRY_RUN:** records what a response policy *would* do without executing it.
- **ARMED:** published policy permits strictly gated automated actions.
- **DEGRADED:** one or more required collectors, clocks, stores or identity checks are unhealthy.
- **PASS:** a declared set of tests and acceptance criteria is satisfied for a specific version. It is not a blanket assertion that the host is secure.

Currently **NOT_IMPLEMENTED / HOLD** applies to this repository's runtime.

## Operator checklist (future runtime)

Before starting: confirm authorized host and approved sensor scope; verify version, binary and config provenance; check disk/time synchronization; validate keys and least privilege; confirm network context; check forensic hold requirements; and snapshot rollback material.

During monitoring: inspect collector heartbeat, ingestion lag, dropped-event counters, store integrity, alert rates, model/profile version, current response posture and incidents awaiting review. Do not promote a baseline solely to silence alerts.

## Incident handling

1. Confirm the observation's source, timestamp, context and sensor integrity.
2. Record the original evidence reference, not only a screenshot or AI summary.
3. Gather independent corroboration where available and list alternative benign explanations.
4. Classify severity and confidence independently; raise HOLD when data is insufficient.
5. Protect relevant originals from training cleanup and retention expiry.
6. Apply response only under an approved policy and recoverable execution path.
7. Validate outcome and rollback; preserve operator notes separately from raw data.
8. Close with false-positive labeling, test cases, audit review and any approved baseline change.

## System failure

**Ledger corruption:** freeze mutating responses, preserve the affected files, compare protected anchors, enter HOLD. **Unknown network:** observe-only until profile review. **Lost clock:** preserve monotonic ordering where possible and clearly mark uncertainty. **Disk nearly full:** stop nonessential collection before risking evidence integrity; do not silently purge evidence. **Model failure:** fall back to deterministic rules and last approved version; no automatic promotion. **Policy identity failure:** containment denied.

## Deployment constraints

No `systemctl`, `pip install`, firewall or database migration commands are specified here because ORBIT11 has no shipped runtime. Once added, installation documentation must include exact paths, sandboxing, privileges, reversible commands and checks for interaction with any existing BCI Orbital service.

## Recovery expectations

Maintain a separate, read-only recovery plan; verify restores using copies; record event gaps; and make restart decisions contingent on operator review. A restored baseline is usable if and only if its signature/digest and approval lineage verify.
