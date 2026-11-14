# BCI-Orbit11 roadmap

BEACON COMPUTING INITIATIVE · Developer Seal: CJB-DEV-2026

These are planned milestones, not claims that the functionality already exists.

## 1. Reproducible integration foundation

- Keep imported sources traceable and independently testable.
- Establish a unified package/launcher without breaking existing installation paths.
- Add repeatable environment setup and fixture-based cross-component contracts.
- Test current Python versions and PyQt6 rendering on intended Kali installations.

Acceptance: fresh checkout can run all tests and documented safe CLI entry points;
installed-stack acceptance records exact versions, access and missing components.

## 2. Data quality and sensor contracts

- Version feature semantics separately from the display release.
- Replace placeholder rates with explicit availability/missingness where needed.
- Validate rate intervals, resets, interface changes, host/route drift and clock jumps.
- Add stable process identity at sensor origin and authenticated source provenance.

Acceptance: old and new datasets cannot be mixed silently; gaps and context changes
produce explicit review states with fixture-backed compatibility tests.

## 3. Model evaluation and registry

- Curate reviewed benign and relevant adversarial evaluation datasets with provenance.
- Measure alert volume, false positive behavior, missed deviations and drift.
- Introduce independent holdout runs and documented threshold selection.
- Build authenticated, versioned, create-only model registration, promotion and rollback.
- Keep legacy data, synthetic demos and live approved candidates distinguishable.

Acceptance: model card links reproducible independent evaluation; promotion and
rollback are implemented and recovery-tested before either is operationally offered.

## 4. Evidence durability and retention

- Review journal crash consistency and chain anchoring.
- Define bounded rotation, archival receipts, storage reserve and explicit recovery.
- Anchor manifests externally or use independently controlled signing credentials.
- Test interrupted writes, full disks, damaged sidecars and restoration from backups.

Acceptance: recovery preserves original evidence, surfaces acquisition gaps and
never turns a corrupted/unavailable source into a normal observation.

## 5. Operator experience

- Add end-to-end mocked workflows and worker cancellation/shutdown acceptance.
- Make every unavailable sensor, context mismatch and quota condition actionable.
- Clearly separate eligibility, approval, training, evaluation and deployment states.
- Add safe export preview/redaction and discoverable evidence provenance.

Acceptance: displayed facts can be traced to successful reads or verified artifacts;
no decorative chart values or unsupported model predictions appear.

## 6. Optional privileged operations

- Design root-owned immutable deployments and minimum necessary capabilities.
- Benchmark packet drops, kernel probe coverage and resource overhead.
- Independently review legacy firewall response paths and scoped rollback.
- Require explicit authorization, tested recovery and auditable operator identity.

Acceptance: only separately approved, demonstrated-safe workflows are enabled.
Autonomous containment is not a prerequisite for delivering useful analysis.
