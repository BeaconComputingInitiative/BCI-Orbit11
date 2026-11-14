<!-- BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026 -->
# Releases and Change Control

**BEACON COMPUTING INITIATIVE** | **Developer Seal: CJB-DEV-2026**  
**ORBIT11 / BCI Orbital Cyber Defense AI** | **Status: Design specification**

## Versioning

Use semantic versioning once runtime code exists. Documentation-only revisions can be noted in CHANGELOG without implying a new tested runtime release. Each tagged release should include change scope, migration effects, tests, known limitations and a rollback plan.

## Release checklist

1. Freeze the candidate commit and scope.
2. Review dependencies, SBOM, secrets, licenses, API compatibility and threat-model changes.
3. Execute the exact required tests and store immutable qualification results.
4. Validate original artifacts and SHA-256 manifest against trusted publication metadata.
5. Confirm policy and model rollback; test restore on an isolated environment.
6. Obtain explicit release/promotion approval for the version being shipped.
7. Stage first; verify live sensor health and alert quality before broader deployment.
8. Keep containment disabled until separately approved for the target host/profile.

Production release may proceed if and only if all applicable test and policy gates pass, rollback and audit channels are healthy, and the accountable operator approves the specific artifact/version.

## SHA-256 conventions

`SHA256SUMS` hashes tracked repository files, excluding itself to avoid circularity. It is a change-detection convenience and not an authenticated signature. A future release should sign a manifest and publish digest metadata through a separately controlled channel.

## Rollback

Record previous approved binary, schema, baseline, policy and model. Never run an irreversible migration without tested backup/restore. If rollout health degrades, stop enforcement, preserve evidence and revert only through a documented, authorized transition.

## No releases yet

There is **no deployable ORBIT11 release** in this repository as of this documentation update.
