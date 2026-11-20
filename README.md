# BCI-Orbit11

## Kubuntu migration preparation — November 19, 2026

**BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026**

A source-only, account-portable Kubuntu bootstrap and private migration tooling
are now staged for review: [Kubuntu migration guide](docs/KUBUNTU-MIGRATION.md),
`scripts/install-kubuntu.sh`, `scripts/export-migration.sh`, and
`scripts/restore-migration.sh`. A synthetic-only CI workflow checks their
scripts and export/restore round trip.

**Important:** The public GitHub tree does not contain the complete newer
local-only ORBIT11 research workspaces, model checkpoints, or canonical
datasets. No private datasets or secrets were uploaded by this update.
The migration is complete **if and only if** the local artifacts are separately
backed up, restored, reviewed and independently verified on the target machine.
**Operational and production status remain HOLD.** No monitoring, training,
containment or offensive capabilities are activated by the bootstrap.

---


**BEACON COMPUTING INITIATIVE**  
**Developer Seal:** `CJB-DEV-2026`  
**Project:** BCI Orbital Cyber Defense AI  
**Reporting order:** Most recent first  
**Current qualification:** **HOLD — research-only; production disabled**  
**README content integrity:** SHA-256 manifest should be generated from the exported README bytes; GitHub blob SHA is not a SHA-256 digest.


## Latest research update — November 17, 2026

**Status:** **RESEARCH_ONLY · Operational qualification HOLD · PRODUCTION HOLD**  
**Evidence boundary:** The results below are **reported outcomes from local Kali/ORBIT11 workspaces**, supplied by the project operator. They are not GitHub CI results, not independently reproduced by this repository update, and do not mean the newer v0.6–v1.4 research workspaces or private checkpoints have been committed here.

### ORBIT11's four orbital divisions

The approved astronomical names are canonical for design and documentation. Previous functional names remain aliases while code is migrated.

| Division | Legacy functional alias | Responsibility | Operational boundary |
|---|---|---|---|
| **APOGEE** | Sentinel | Host/network observation, sensor visibility, detection and monitoring | Collect within existing authorization; no unsupported attribution |
| **PARALLAX** | Investigator | Evidence normalization, lineage, timeline reconstruction, correlation, missing-information analysis | Preserve original evidence; abstain when context is insufficient |
| **LAGRANGE** | Guardian | Defensive assessment, reversible response proposals and recovery verification | **Shadow-only**; no automatic containment authorization |
| **PERIGEE** | Adversary Lab | Authorized attack-surface assessment, finding verification and adversarial-activity investigation | Explicit targets, scope, method and operator approval; no unrestricted exploitation |

These names do **not** imply that the four agents, native model, or operational execution pathways have been integrated and qualified for deployment.

### Latest measured research outcomes (newest first)

#### November 17 — v1.4 neural-value qualification: engineering PASS; operational HOLD

- A read-only synthetic comparison examined **72 evidence-qualified cases**, representing **six distinct model-facing tensor patterns**.
- Deterministic-only, neural-only and evidence-gated hybrid decisions agreed on all 72; each reported **100% positive recall, negative recall and balanced accuracy** within this narrow synthetic subset.
- **Neural improvements over the deterministic decision rule: 0.** The native checkpoint was advisory and did not change an outcome.
- The v1.3 evidence gate prevented **12 false relationship assertions** that the original per-handoff rule would have made. Its explicit adjacent parent-child corroboration requirement explains the improvement; it is **not** a neural-learning gain.
- All **36 positive cosine distances** were within **1.2 × 10⁻⁷** of a zero cutoff; negative distances ranged from **0.04566 to 0.32920**. Cosine distances are **not calibrated probabilities** and cannot override sufficiency rules.
- Read-only local integration covered sealed audit metadata for **6,940 APOGEE host-event records** and **318 aggregate observation windows**, plus PARALLAX-compatible chain-integrity reports. **13 timestamp reversals** were recorded, with no chain mismatch and **zero approved native training targets**.
- **LAGRANGE** remained shadow-only; **PERIGEE** was not invoked. No additional model calls, optimizer steps, deployment or containment occurred in the reported v1.4 work.
- Local audit references (not necessarily present in GitHub): `workspaces/orbit11-neural-value-qualification-v1.4/reports/NEURAL-VALUE.json`, `NATIVE-DISTANCE-ANALYSIS.json`, `READ-ONLY-OBSERVATION-INTEGRATION.json` and `QUALIFICATION.json`. A reported eight-entry SHA-256 manifest and 141 protected-file checks passed locally.

#### November 17 — v1.3 evidence-aware contrastive reasoning: synthetic PASS

- Final frozen synthetic challenge: **36 positive, 36 hard-negative and 72 ambiguous** cases across **12 new lineages**.
- The sufficiency gate assessed `SUFFICIENT`, `INSUFFICIENT` or `CONFLICTING` **before** neural inference and returned abstention reason codes plus required missing evidence.
- Hybrid results: **100% positive recall, 100% negative recall, 100% balanced accuracy, 100% ambiguous-case abstention**, **zero false assertions** on 72 ambiguous cases, and **zero native calls** for those cases.
- Original deterministic rule: **83.3% abstention**, with **12 unsupported match assertions**. Neural-only: **0% abstention**, **72 unsupported assertions**.
- All 12 improvements came from deterministic adjacent-handoff lineage checking; neural advice changed **zero decisions**.
- A defective first frozen fixture incorrectly allowed self-parent process links. That run was preserved; a development regression repaired the fixture generator and a **separately frozen lineage** was used for the final qualification.
- Local audit: `workspaces/orbit11-contrastive-reasoning-v1.3/results/`. Reported manifest SHA-256: `d9de31b92b2dbd342088b5665e0d39ba181bebaf5b4657c747db55e2df892b01`.

#### November 17 — v1.2 challenge: narrow binary accuracy but abstention FAIL

- A frozen synthetic challenge comprised **360 cases**, six scenario families and 18 lineages. Full tensor fingerprints were unique, but preprocessing reduced them to **13 patterns**.
- Nine new reduced patterns included negatives and ambiguous cases **but no new positives**. Positive/negative generalization to novel patterns therefore remained unqualified.
- The repaired checkpoint classified evidence-sufficient positive/negative cases correctly in that challenge, but **abstained on 0% of ambiguous cases**; a deterministic evidence rule abstained on 100%.
- This failure motivated the v1.3 non-overridable evidence-sufficiency gate. The earlier failed challenge remains part of project history; it was not retroactively relabeled PASS.

#### November 17 — contrastive v1.1: native training and evaluation limitations

- Separate synthetic research curriculum: **112 episodes, 448 pairs**, comprised of **112 positive, 224 negative and 112 unresolved/loss-masked** relationships; 448 response alternatives and 448 conditional resolution paths.
- Family-isolated synthetic splits provided **48 positive / 96 negative** training pairs and **32 positive / 64 negative** pairs in each of validation and evaluation. All 112 unresolved pairs were masked. Synthetic lineage separation is not proof of independent real-world sources.
- An initial **96-update** native contrastive experiment selected a checkpoint at validation step 56; frozen evaluation yielded **50% positive recall and 75% balanced accuracy**, failing predeclared thresholds. Historical failed results remain preserved.
- A later repaired candidate achieved **100% on 288 newly frozen synthetic examples**, but those examples collapsed to just **four distinct model-facing patterns**, three already seen in development. The deterministic evidence rule matched that result. This was not evidence of broad generalization or incremental neural value.
- Earlier v1.0 contrastive material contained **2,016 synthetic pairs**. Native compatibility was established, but conflicting tensor representations, generator-identity shortcuts and cross-partition overlap caused quarantine; do not use the original v1.0 counts as qualified training counts.
- The v1.1 repair kept explicit execution/session corroboration, handoff receipts, reliable relative chronology, visibility masks, and label/answer isolation. Unresolved evidence is not a negative label.

#### November 17 — native v0.6 and the first research-corpus pilot

- A separate local native v0.6 four-objective candidate reportedly contains **183,209 full native parameters**; engineering/gradient and checkpoint recovery tests passed. This is **not** the historical 12-feature autoencoder imported into this repository.
- Synthetic optimizer smoke tests demonstrated real parameter updates for four objectives on small fixed fixtures; these tests did **not** demonstrate cybersecurity generalization.
- An operator-authorized, offline, **100-CPU-update train-only pilot** used a verified 50K source through its canonical event view. Its **796 linked candidates** remained one group and deduplicated to **98 effective cases**.
- Reported train-only losses: temporal **0.70241 → 0.31284** (1,734 valid targets); relationship **0.70442 → 0.00328** (5,488 targets); reconstruction **0.43357 → 0.05362** (3,136 targets). **Contrastive had zero justified negative components and was not trained in that pilot.**
- **133,087 parameter elements changed**, recovery matched exactly, and nine local checksums reportedly passed. The research-only checkpoint's reported SHA-256 is `6490e8d89883d3590311dea5b8ff675e2b89af2a906005c289c75b0a6be691b7`.
- The user designated existing source data for research use. **Operator authorization is not equivalent to authenticated independent source review.** Training-set loss reductions do not establish predictive performance on unseen operational evidence.
- The separate research checkpoint and source data are local artifacts and **are not uploaded by this README change**.

### Current release and qualification gates

| Gate | Current reported decision |
|---|---|
| Native v0.6 engineering and research optimization | PASS on controlled fixtures; local code/checkpoints not confirmed present in this repository |
| Three native objectives trained on an operator-authorized local corpus pilot | Research completed, **train-only** |
| Contrastive native optimization | Research completed; broad neural contribution **not demonstrated** |
| Evidence-sufficiency and abstention | v1.3 synthetic PASS; enforce fail-closed behavior |
| Independent operational labels / authenticated provenance | **HOLD** |
| Independent, frozen, real-observation evaluation | **HOLD / not measured** |
| Production neural promotion | **BLOCKED** |
| LAGRANGE active response / containment | **DISABLED / shadow-only** |
| PERIGEE active assessment execution | **NOT INVOKED / requires explicit scope approval** |
| Deployment and operational acceptance | **PRODUCTION HOLD** |

### Next milestone — v1.5 operational evidence qualification

1. Reuse existing APOGEE/PARALLAX read-only source inventories rather than repeating mass scans. Inspect raw-event provenance and the **13 timestamp reversals** without silently rewriting timestamps.
2. Distinguish event time, ingest time, clock synchronization, source visibility and aggregate metadata. Missing execution/session evidence must remain unknown, not invented.
3. Document evidence-supported positive, negative and unresolved relationships, with non-overridable abstention for invalid ancestry, contradictory receipts or degraded visibility.
4. Obtain authenticated source/label review and **independent frozen operational evidence**. Maintain isolation from local synthetic curricula and earlier development fixtures.
5. Compare deterministic-only, neural advisory and hybrid decisions on qualified new evidence; require a **measurable incremental neural benefit** before any promotion claim.
6. Keep the four orbital divisions isolated from live offensive execution, containment, and automatic production changes without separate explicit authorization.

**Qualification is PASS if and only if** applicable provenance, integrity, source authorization, objective/feature compatibility, leakage isolation, independent review and frozen evaluation criteria all pass. Otherwise record the precise HOLD or FAIL state. **Research PASS does not imply production approval.**

**Publication boundary:** This README update contains a status digest and references to locally reported paths and hashes only. It does not upload private telemetry, raw capture files, credentials, source datasets, research checkpoints, or local evidence. The source files already committed in this repository remain the previously imported experimental components; the latest local v0.6–v1.4 workspaces must be separately reviewed and committed if publication is later authorized.

---

## Historical qualification — November 15, 2026

**Unified qualification: HOLD.** These are reported qualification outcomes from the project review, not independently re-executed tests on GitHub.

| Area | Latest reported result | Interpretation |
|---|---|---|
| Original checkpoints and canonical v1.0.1 | PASS | Historical artifact checks passed; no production authorization |
| Frozen evaluations and 24 historical regressions | PASS | Existing reference checks passed |
| Software tests | 29 PASS | Reported test result, not a fresh CI run |
| Generated SHA-256 manifests | PASS | Manifest generation reported; validate against local artifacts |
| Research training eligibility | BLOCKED | Zero eligible records; zero runs started |
| Label-compatible targets | HOLD | Approval, supervision, leakage and runtime clearance missing |
| Frozen capability-constrained planning diagnostic | FAIL (0/1) | Untrained candidate; synthetic diagnostic |
| Frozen staged hypothesis checks | FAIL (0/3) | Untrained candidate; synthetic diagnostic |
| Production integration | BLOCKED | No deployment, containment or promotion authorized |

**Referenced local reports:** `audits/orbit11-unified-qualification-v0.1.0/UNIFIED-RUN-REPORT.json` and its capability comparison. These paths are local report references, not assertions that the files are committed to this repository.

### November 15 — Q1.8 offline review gate

- Status: `HOLD_ONLY_STRUCTURAL_INSPECTION`.
- Input reports: 1.
- Production integration: **BLOCKED**.
- Local report: `/home/bci/ORBIT11-Q18-reports/q18-20261115T024416Z-7effa0b2/qualification_report.json`.
- Local review: `/home/bci/ORBIT11-Q18-reports/q18-20261115T024416Z-7effa0b2/review.html`.
- Reported report SHA-256: `d99a3907548ecb896b39dc2bb1dd207f4626fee504a326a118b1534c08c3` (not independently verified here).

### November 15 — Q1.7 leakage gate

- Smoke test reported **HOLD** due to possible label leakage in native input: `['target']`.
- Any `target` field used as a supervision label must be excluded from inference features unless an explicit, independently validated feature specification allows it.
- Training remains blocked until label separation, provenance, leakage controls and review gates pass.

### November 14 — checkpoint and dataset review

- Two 100-epoch multicorpus checkpoint files were reported byte-identical, with SHA-256 `88116790044ce300fd3caaa6452f4f254770d021e1ab0b635ee9ffc3aa00f99f`.
- Byte identity is **not** evidence of two independent training outcomes or model effectiveness.
- Dataset directory structure was reported PASS, but structural validity alone does not establish eligible supervised records.
- Offline research examples of incorrect or anomalous behavior are a proposed dataset direction; they must be explicitly labeled, evidence-grounded, provenance-tracked and leakage-tested before training.
- No operational attack execution, unreviewed model promotion or production integration is authorized by these historical results.

### Next qualification steps

1. Inventory candidate research records and document provenance, permissions and label semantics.
2. Add independently reviewed negative/incorrect examples alongside valid controls, without exposing labels in model input features.
3. Re-run leakage checks, staged hypothesis tests and capability-constrained planning diagnostics.
4. Require explicit approval before any training, model promotion or production integration.
5. Publish reproducible evaluation reports and an informational SHA-256 manifest for committed documentation.

## Detailed engineering interpretation (November 15, 2026)

### What Orbit11 is—and is not

Orbit11 is an experimental, locally operated security-monitoring and research stack. The repository integrates host observations, a small anomaly autoencoder, evidence handling, measured-rate telemetry, and an operator console. The source import is not evidence that all subsystems are running together, that model training has succeeded on eligible research records, or that an automated defensive response is approved.

The current learning architecture documented in the imported source is a 12-feature reconstruction autoencoder with topology `12 → 8 → 3 → 8 → 12`. Reconstruction error can flag unfamiliar observations; it does **not** prove intrusion, intent, identity, or attribution. A separate research qualification track evaluates constrained planning and staged hypotheses. Its frozen untrained-candidate diagnostic failures must not be conflated with the autoencoder's statistical reconstruction behavior.

### Evidence and dataset lifecycle

| Stage | Required evidence | Failure behavior |
|---|---|---|
| 1. Source intake | Dataset identifier, origin, collection authority, collection time, immutable source reference | Quarantine unknown or unauthorized sources |
| 2. Schema and chronology | Feature schema, timestamps, event ordering, source context | HOLD on malformed or temporally inconsistent records |
| 3. Supervision | Clear definition of expected/incorrect behavior, reviewer identity, labeling rationale | HOLD ambiguous or unsupported labels |
| 4. Leakage prevention | Disjoint feature/target fields, train/validation/test isolation, duplicate and near-duplicate review | HOLD if target or evaluation answers enter input features |
| 5. Coverage | Positive and negative controls across relevant host/network contexts and representative failure modes | HOLD if coverage is inadequate |
| 6. Training approval | Eligible records, reproducible configuration, explicit operator authorization | No training when authorization is absent |
| 7. Qualification | Frozen test set, historical regressions, calibration, failure analysis, evidence-backed metrics | No promotion on failed diagnostics |
| 8. Operational promotion | Approved model identity, rollback plan, bounded permissions, operator acceptance | Research-only if any gate remains unresolved |

**Negative examples** should include independently reviewed *incorrect* or suspicious patterns with benign counterexamples: unexpected service exposure, anomalous process/network correlations, unauthorized storage transfer indicators, stale baselines, mismatched network context, contradictory telemetry, and deliberately malformed evidence. These are proposed evaluation categories—not claims of detected attacks. Keep ground-truth labels separate from model-visible features and avoid representing synthetic fixtures as real incidents.

### Trust boundaries and safeguards

- **Observation is not conclusion:** raw telemetry, model scores, analyst findings, and enforcement decisions must remain separately identified.
- **Context matters:** network and host profiles must not be silently pooled; baseline changes require review.
- **Evidence integrity:** preserve provenance and relevant forensic/legal-hold material. A hash is an integrity comparison, not proof of origin or authenticity.
- **Containment:** legacy opt-in host response code exists, but no containment is authorized by the present research qualification. Fail closed on missing approval.
- **Privacy:** do not publish personal machine logs, raw captures, credentials, host identifiers, or private training material as part of documentation updates.
- **Reproducibility:** record exact source revision, dataset manifest, environment, seed, evaluation definition and artifact hashes for each qualifying experiment.
- **Retention:** cleanup of disposable training inputs may occur only after verified successful qualification and subject to evidence preservation and legal holds; no deletion is implied by this README.

### Interpretation of current failures

**Q1.7: possible target leakage.** The native input included a field named `target`. This is a structural warning, not proof of malicious manipulation. The feature builder must demonstrate that supervised labels and evaluation answers cannot leak into predictors.

**Q1.8: structural-only review.** One report was ingested; the review did not grant runtime or production clearance. Its local JSON/HTML report paths are operator artifacts, not automatically public repository assets.

**Unified frozen diagnostics:** 0/1 constrained planning and 0/3 staged hypotheses on an untrained candidate. These small synthetic controls expose missing capabilities under those fixtures; they do not establish a real-world attack-detection rate, false-positive rate or production efficacy.

**Checkpoint identity:** two checkpoint files sharing the same reported SHA-256 establish byte identity if verified locally. They do not establish independent experiments, successful learning or generalization.

### Acceptance criteria for the next milestone

A research milestone is **PASS if and only if** all mandatory eligibility, provenance, separation, supervision, reproducibility and frozen evaluation gates pass and an authorized reviewer records approval. Otherwise it remains **HOLD/FAIL**, with the blocking reason retained in the report. A production milestone requires a *separate* explicit operational authorization and safety review; a research PASS never automatically enables production.

The immediate priorities are: curate eligible reviewed examples; correct label/feature separation; build a reproducible qualification harness; re-run historical and frozen diagnostics; inspect failure cases; and only then consider a separately approved training run.

### Public-release readiness

This documentation may describe a public research project, but repository visibility is managed separately in GitHub Settings. Before making the repository public, review **all commits and branches**, GitHub Actions logs/artifacts, committed configuration, tokens, internal paths, machine evidence, personal data, licenses, and dependencies. Git history may expose previously removed material. No security audit or visibility change is asserted by this README update.

### Reporting and verification convention

The latest status appears first. Each reported result must identify whether it is **reported**, **reproduced**, or **independently verified**. Use informational SHA-256 manifests for distributed artifacts, and retain the developer seal `CJB-DEV-2026`. Git commit SHA and Git blob SHA are not SHA-256 file digests.

---

## Preserved repository documentation


**BEACON COMPUTING INITIATIVE**  
**Developer Seal:** `CJB-DEV-2026`  
**Project:** BCI Orbital Cyber Defense AI  
**Repository/model-family identity:** BCI-Orbit11  
**Stage:** Experimental engineering integration; analyst review required

BCI-Orbit11 brings the existing Orbital host monitor, native neural anomaly detector,
evidence tools, measured-rate telemetry bridge, and PyQt6 operator console into one
source repository. It is intended for Kali Linux and local operation. The learned
component is a small CPU autoencoder; the conversational interface routes supported
questions deterministically. No external LLM or cloud inference is required.

The Orbit11 name identifies this project. It does not imply an 11-billion-parameter
model, a newly trained checkpoint, or a production security certification. This import
preserves existing component versions and source bytes. No private checkpoint,
training dataset, machine evidence database, or runtime journal is distributed here.

## Specification and implementation status

The earlier documentation-first design is preserved as a complete snapshot in
[docs/specification/README.md](docs/specification/README.md). Its targets are not
claims of delivered or validated behavior. The current experimental import is
scoped by [ADR-0004](docs/decisions/ADR-0004-source-import.md). Existing governance,
legal terms, issue templates, release requirements and broader target specifications
remain in this repository. Imported source does not imply a production migration.

The implemented components described below are independently tested experimental
building blocks. They do not satisfy all requirements in the target specification.

## Start here

| Goal | Read |
|---|---|
| Understand components and trust boundaries | [Architecture](docs/ARCHITECTURE.md) |
| Understand the actual neural model | [Model card](docs/MODEL-CARD.md) |
| Run tests and launch from source | [Getting started](docs/GETTING-STARTED.md) |
| Review evidence and operational workflows | [Operations](docs/OPERATIONS.md) |
| Review attack surface, privacy and gaps | [Security](SECURITY.md) |
| See what was checked for this import | [Validation](docs/VALIDATION.md) |
| Plan further development | [Roadmap](docs/ROADMAP.md) |
| Trace each imported file | [Source provenance](docs/SOURCE-PROVENANCE.json) |

## Components

| Directory | Preserved version | Responsibility |
|---|---|---|
| `components/host` | 0.1.0 | Linux process/socket/storage observations, context-separated behavioral profiles, SQLite evidence chain |
| `components/neural` | 0.2.0 | Standard-library neural autoencoder, candidate journals, review/training/scoring gates, deterministic correlation |
| `components/expansion` | 0.3.0 | Measured throughput, context provenance, optional packet/DNS metadata and kernel probes |
| `components/rate-aware` | 0.5.1 | Separate measured-rate candidate journal and explicitly gated timer migration |
| `components/console` | 0.8.3 | Native PyQt6 GUI, CLI, evidence-bound AI questions, readiness and collector diagnostics |

Component READMEs preserve release history and historical installation instructions.
Use the root documentation for the current repository layout and tested commands.
The console's runtime globe image and original design mockup fixture are included.
The mockup is a design reference, not a current host status report. ZIPs and the
old patch diff are omitted. Component manifests were regenerated for this
inventory; imported source code remains unchanged.

## Quick validation

From a checkout, using Python 3.10 or later:

```bash
python3 -B scripts/check.py
```

This checks Python syntax, shell syntax, four independent component test suites,
and the rate-aware runner's self-tests. It does not install software, start a
collector, change a service, import machine evidence, or approve a model. Bash is
needed for shell syntax checks. PyQt6 is optional for this test command.

Read-only CLI entry points from source:

```bash
python3 -B components/console/src/orbital_cli.py --help
PYTHONPATH=components/neural/src python3 -B -m bci_neural --help
PYTHONPATH=components/host/src python3 -B -m bci_orbital --help
PYTHONPATH=components/expansion/src python3 -B -m bci_orbital_expansion --help
```

Launch the GUI on a machine with PyQt6 and a graphical session:

```bash
python3 -B components/console/src/orbital_cli.py gui
```

The console expects existing versioned Orbital launchers and state directories for
live component status. A fresh checkout supplies source, not an installed and
active monitoring stack. Missing dependencies must remain unavailable/HOLD; they
must not be interpreted as a clean host or confirmed attack.

## Learning and interpretation

The autoencoder reconstructs 12 aggregate features through a `12 → 8 → 3 → 8 → 12`
network. High reconstruction error means statistical novelty relative to the
candidate training context. It does not identify a person, establish malicious
intent, or prove compromise. Training and inference enforce context matching;
legacy and live observations are separate trust domains.

Training eligibility includes at least 80 observations, 24 distinct observation
hours and seven elapsed days, plus integrity, schema, coverage and operator-review
gates. The console applies additional provenance, chronology, freshness and
historical-gap checks. Passing numeric thresholds is eligibility for review, not
approval. See the model card for exact preprocessing and calibration.

## Execution policy

- Repository population does not authorize installation, persistent activation,
  privileged collection, training on host data, model import or promotion.
- The neural core has no containment implementation. The preserved **legacy host
  monitor does contain opt-in nftables response code**. Do not arm it as part of
  normal setup; inspect its explicit controls before any separately approved use.
- The expansion includes privileged capture/probe commands. Unit tests use fixtures;
  collecting real packet or kernel evidence requires separate authorization.
- Rate-aware migration and quota-guard scripts can change service definitions only
  through their explicit operator gates. They are not run by repository checks.
- Telephony Shield and BCI Flux are separate projects and are not included.

Source consistency can be checked optionally with `sha256sum -c SOURCE-SHA256SUMS`.
Local checksums are not signatures or independent proof of acquisition authenticity.
Some preserved component installers require their own manifests; the console's
installer does not require source hash verification for launch.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for tests, change boundaries and review
expectations. No new open-source license is assigned by this repository import;
redistribution and licensing terms remain for the owner to decide.
