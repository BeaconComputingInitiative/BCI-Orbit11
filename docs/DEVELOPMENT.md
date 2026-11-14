<!-- BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026 -->
# Development Guide

**BEACON COMPUTING INITIATIVE** | **Developer Seal: CJB-DEV-2026**  
**ORBIT11 / BCI Orbital Cyber Defense AI** | **Status: Design specification**

## Current layout

ORBIT11 is currently a documentation-first repository. Treat described runtime modules as proposals; there is no deployable application.

## Proposed implementation layout (not yet present)

```text
orbit11/
  collectors/          # independent least-privilege sensors
  schema/              # typed versioned event records
  evidence/            # canonical audit and storage APIs
  baseline/            # network-context profiles and promotion
  detection/           # rules, features, local models
  correlation/         # incident hypotheses and provenance
  policy/              # authorized decisions and safety gates
  response/            # dry-run first, rollback-capable actions
  training/            # isolated candidates, validation and cleanup
  operator/            # CLI/API and later native desktop UI
tests/
docs/
```

A future implementation language/framework decision requires an ADR before code is introduced. Prefer Python for orchestration, and narrowly scoped native components only where measured performance or operating-system APIs justify them.

## Engineering workflow

1. Open an issue with scope, observable acceptance criterion, expected privileges, privacy impact and rollback.
2. Write a failing fixture/test proving the behavior or control.
3. Implement the smallest isolated component and schema migration.
4. Run unit, integration, negative, corruption and fail-safe tests.
5. Update affected README/docs, evidence schemas, hashes and changelog.
6. Submit review; never merge privileged/retention/response changes without separate safety review.

## Coding rules

- Deterministic code paths for authorization. A safety-critical action executes if and only if the complete predicate succeeds.
- Avoid broad exception swallowing and "success by silence".
- Use monotonic time for ordering and UTC for human-readable evidence. Preserve clock skew indications.
- Validate content lengths and formats at every trust boundary.
- Keep test fixtures synthetic; never commit production logs.
- No model, policy or baseline hot-swap without atomic versioning and rollback.
- Code comments and generated metadata should carry "BEACON COMPUTING INITIATIVE" and "Developer Seal: CJB-DEV-2026" where practical.
- Generate SHA-256 manifests for release artifacts; verify against a trusted recorded digest. A self-authored manifest is not a security boundary.

## Build and packaging

No dependency lockfile, API server, Python package or service exists yet. Do not invent setup instructions. Proposed milestones should add reproducible environment setup, pinned dependencies, SBOM, offline compatibility and versioned migration tooling.

## Local documentation integrity

Run `sha256sum -c SHA256SUMS` on Linux. If documentation changes, regenerate the list intentionally and review changed bytes. See [Verify](VERIFY.md) and [Release](RELEASE.md).

## Architecture decisions

Material decisions belong in [decisions](decisions/ADR-0001-scope.md). Prefer explicit alternatives and tradeoffs over implicit architectural drift.
