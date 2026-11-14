<!-- BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026 -->
# Contributing to ORBIT11

**BEACON COMPUTING INITIATIVE** | **Developer Seal: CJB-DEV-2026**  
**ORBIT11 / BCI Orbital Cyber Defense AI** | **Status: Contributor guide**

ORBIT11 is currently a **private documentation-first** project. Contributions should improve a bounded engineering outcome, not imply that undeveloped capabilities already work.

## Before a change

Read [Architecture](docs/ARCHITECTURE.md), [Requirements](docs/REQUIREMENTS.md), [Threat model](docs/THREAT_MODEL.md), and [Governance](GOVERNANCE.md). For security-sensitive changes, include failure modes, permissions, evidence classification, approval rules and rollback.

## Pull request expectations

- Reference an issue or describe the design/bug in reproducible terms.
- State what changed, why, how it was tested and what remains unimplemented.
- Include deterministic tests for code changes and negative/safety tests for elevated privileges, retention or containment.
- Update documentation, relevant ADR and CHANGELOG when behavior or policy changes.
- Preserve developer seal and regenerate SHA-256 manifest intentionally.
- Use only synthetic or explicitly approved sanitized fixtures.

## Commit guidance

Prefer small, self-contained changes. Recommended subjects: `docs:`, `feat:`, `fix:`, `test:`, `security:`, `build:`. Never commit passwords, API keys, real PCAPs, private messages, personal case records, model training dumps or unreviewed machine inventories.

## Review and merging

Safety-critical changes require explicit review by the accountable maintainer, plus independently reproducible tests. A PR is merge-ready if and only if it satisfies its declared scope, the corresponding safety gates are demonstrated, required documentation is updated, and it does not alter active systems implicitly.

## Development readiness

No runtime build commands exist yet. Do not fabricate install instructions or claim a documentation change qualifies production code.
