# ORBIT11 Q1.7-Q1.8 qualification record

**BEACON COMPUTING INITIATIVE**  
**Developer Seal:** `CJB-DEV-2026`  
**Project:** BCI-Orbit11 | Research qualification  
**Report period:** November 14, 2026 (Pacific) / November 15, 2026 (UTC)  
**Decision:** `HOLD_ONLY_STRUCTURAL_INSPECTION`  
**Operational scope:** `RESEARCH_ONLY / PROPOSE_ONLY`  
**Production integration:** `BLOCKED`  
**SHA-256:** Managed by the repository-root `SHA256SUMS` manifest.

> This is a documentation record of operator-provided terminal output, not an independent examination of the local report bytes, a checkpoint import, a production release, or an approval to run the model on live host telemetry.

## Verified repository baseline versus operator-reported research

The repository's earlier source integration consists of five experimental component families and recorded 107 passing component tests plus an 11-page offscreen GUI smoke test. Those checks do not validate the newer ORBIT11 research checkpoints or its Q1.7/Q1.8 qualification path.

Earlier operator-provided research summaries described 50,000 synthetic cases (five datasets of 10,000). A prior Q1 test stage reported 13/13 checks passing; four checkpoint files were recorded as PASS, while four reports were classified `OBSERVED_UNVERIFIED`. Independent model evaluation remained HOLD. These figures describe the separately operated research track, not tests executed on this GitHub revision or evidence of field performance.

## Most recent reported gates

| Stage | Operator-visible result | Significance |
| --- | --- | --- |
| Q1.7 smoke | `HOLD: possible label leakage in native input: ['target']` | A target/label field may have entered features; training/evaluation integrity cannot be assumed |
| Q1.8 offline review | `HOLD_ONLY_STRUCTURAL_INSPECTION` | Structural inspection only, not independent behavioral qualification |
| Q1.8 input reports | `1` | One input report, not a comprehensive validated corpus |
| Q1.8 production integration | `BLOCKED` | No model promotion, production inference or automatic containment authorized |

**Q1.8 operator-local report identifier:** `q18-20261115T024416Z-7effa0b2`  
**Files named by the operator:** `qualification_report.json`, `review.html`  
**Operator-reported SHA-256 for the JSON report:**  
`d99a3907548ecb896b39dc2bb1dd207f4626fee504a326a118b1534c08c3d489`

The report path, checksum and status were transcribed from terminal output. The report and HTML have **not** been downloaded, opened or independently rehashed as part of this repository update. No raw host evidence, private checkpoint, operator approvals, training ZIPs or runtime database is committed.

## Release and execution gates

- Accept a native research input **if and only if** schema validation, provenance, target/label exclusion and held-out split checks pass; fail closed when a target-like field is present.
- Record a model evaluation as independently qualified **if and only if** untouched test data, leakage-negative tests, temporal or cross-context holdouts and auditable metrics are reviewed.
- Promote a model **if and only if** candidate identity, dataset provenance, independent evaluation, human authorization, rollback and exact deployment context have all been verified.
- Enable active containment **if and only if** its own independently approved identity, corroboration, policy, reversible response and recovery gates pass. A model score alone is insufficient.
- Delete transient training inputs **if and only if** training validation and authorized retention review have succeeded, forensic evidence/legal holds remain protected, and minimal provenance receipts are retained.

## Next engineering work (not completed)

1. Inspect the Q1.7 native-input construction and eliminate label/target leakage at the feature-contract boundary; add a failing regression fixture for any future target field.
2. Independently read Q1.8 JSON/HTML and record exact file digests, checkpoint identities, source-data lineage, test commands and negative-case outcomes.
3. Execute isolated blind and temporal evaluations with fixed splits; prevent report reuse or circular evaluation.
4. Produce a reviewed model-registration proposal with immutable provenance, deployment OFF by default and rollback tests.
5. Publish source code only after a separate scoped source review excludes secrets, raw telemetry, host-local evidence, private weights and approvals.

**Current decision:** HOLD. The existing GitHub source and operator-local Q1.8 research must remain separate until the above evidence and authorization gates are met.
