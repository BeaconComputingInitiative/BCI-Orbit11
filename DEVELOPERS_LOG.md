<!-- BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026 -->
# Developers Log

**BEACON COMPUTING INITIATIVE**  
**Developer Seal:** CJB-DEV-2026  
**Repository:** BeaconComputingInitiative/BCI-Orbit11  
**Document type:** Maintainer's play-by-play, engineering audit, and release checklist  
**SHA-256:** See repository-root SHA256SUMS for the final file digest.

> Observe accurately. Preserve faithfully. Analyze transparently. Communicate securely. Act deliberately.

This document tracks HOW ORBIT11 should be developed, and WHAT was actually completed. A documented procedure is not evidence that an operation was performed. Record a PASS only when the exact artifact and test report prove that the stated gates passed.

## 1. Confirm the current engineering baseline

The source integration contains five experimental component families: host (0.1.0), neural (0.2.0), expansion (0.3.0), rate-aware (0.5.1), and console (0.8.3). The source integration reported 107 passing tests and an 11-page PyQt6 offscreen smoke test. Those are historical engineering results, not production certification. No live service, personal evidence store, private model checkpoint, or host-data corpus was imported by that commit.

Read README.md, docs/ARCHITECTURE.md, docs/MODEL-CARD.md, docs/GETTING-STARTED.md, docs/VALIDATION.md and docs/SOURCE-PROVENANCE.json before modifying code.

## 2. Start an authorized development session

~~~bash
# BEACON COMPUTING INITIATIVE | CJB-DEV-2026
git clone git@github.com:BeaconComputingInitiative/BCI-Orbit11.git
cd BCI-Orbit11
git fetch origin
git status --short --branch
git log -5 --format='%h %s'
~~~

If already cloned, omit clone. Confirm no unexplained changes. Record UTC time, project issue, branch, HEAD commit, environment, component, source authorization, expected behavior and currently known limitations.

## 3. Create a bounded feature branch

~~~bash
git switch main
git pull --ff-only origin main
git switch -c feature/issue-123-scoped-work
~~~

Define the trust boundary, scope, permissions, privacy impact, test fixtures and recovery plan. Do not make a running Orbital installation part of ordinary repository edits.

## 4. Develop and verify each small change

Use synthetic test data, not private forensic evidence or production credentials. Review source behavior instead of treating AI scores as proof of malicious intent.

~~~bash
python3 -B scripts/check.py
git diff --check
git status --short
git add -- <reviewed-files>
git diff --cached --stat
git commit -m "feat: bounded improvement"
~~~

The source-integrity manifests are not authority to activate services. If an imported source file changes, distinguish the new digest from the historical import recorded in the source-provenance record.

## 5. Five development commits for one reviewed commit

**ORBIT11 5:1 policy:** After five LOCAL, UNPUBLISHED commits on a feature branch, consolidate them into one logical commit before opening a pull request. Preserve main history and all source bytes. Never force-push main or rewrite other developers' published commits.

~~~bash
git fetch origin
git log --oneline origin/main..HEAD
git status --short
bash scripts/squash-five.sh "feat: describe the completed improvement"
~~~

The guarded script may rewrite the local branch if and only if the branch is not main/master, working tree is clean, there are exactly five linear commits directly based on origin/main, no candidate is already in a known remote-tracking branch, and the operator types the explicit approval token. It stores the original HEAD in a backup ref and uses the same Git tree for the consolidated commit.

The optional post-commit hook only reminds developers about five commits; it never changes history:

~~~bash
git config --local core.hooksPath .githooks
~~~

Disable with: git config --local --unset core.hooksPath

Check after grouping:

~~~bash
git log --oneline origin/main..HEAD
git status --short
git show -s --format='%H%n%B' HEAD
~~~

If the branch diverged or was published, stop and choose a new reviewed branch rather than bypassing the gate. The strict script supports one five-commit batch directly based on origin/main.

## 6. Verify artifacts and safety

~~~bash
python3 -B scripts/check.py
git diff --check
sha256sum -c SHA256SUMS
sha256sum -c SOURCE-SHA256SUMS
~~~

Update applicable manifests only after reviewing the actual content changes. SHA-256 identifies file bytes, not the author or authorization. New source and reports should carry the Beacon Computing Initiative header and CJB-DEV-2026 Developer Seal. Record digests externally in SHA256SUMS; a file cannot contain its own stable SHA-256 checksum without circularity.

For models: record feature schema, training qualification, candidate/model digest, holdout evaluation, promotion approval and rollback. For containment: prove explicit identity/policy, corroboration, safe action scope and recovery before enabling anything. The current host source contains opt-in nftables logic; importing source alone does not authorize arming it.

## 7. Publish the single logical commit for review

~~~bash
git push -u origin HEAD
gh pr create --base main --fill
~~~

The repository's PR check expects one consolidated commit. Review includes security impact, tests, context and legal-hold protections, secret scans, scope, rollback and documentation. Use a reviewed squash merge when approved. Branch protections should separately prevent unreviewed direct main pushes.

## 8. Close the work session and log results

~~~bash
git status --short --branch
git log -3 --oneline
git show --stat --oneline HEAD
~~~

Record actual outcomes, not expectations. A PASS means a specific revision passed its required tests with evidence. A PARTIAL or HOLD is not a production release.

### Developers Log entry template

~~~text
BEACON COMPUTING INITIATIVE
Developer Seal: CJB-DEV-2026
UTC date and time:
Developer / reviewer:
Task, issue, branch, starting commit:
Affected components:
Data authorization and sensitivity:
Before-state evidence:
What changed and why:
Commands actually run:
Expected results:
Observed results:
Unit, integration, negative and safety tests:
Final artifact SHA-256:
Known issues / skipped checks:
Decision: PASS | PARTIAL | HOLD | FAIL
Rollback location:
Next authorized step:
~~~

## 9. Recovery and incident boundaries

- **Squash interrupted:** Inspect HEAD, status, and the backup under refs/bci-backups; restore to a NEW recovery branch for review. Do not force-update main.
- **Integrity failure:** Preserve the mismatched file and compare with trusted source provenance before altering manifest hashes.
- **Test failure:** Preserve fixtures and output; record HOLD until the cause is diagnosed.
- **Operational concern:** Use the separate operator incident playbook. Git history edits do not recover a running sensor or firewall.
- **Training-data cleanup:** Purge eligible transient copies only after verified training, retention approval and legal-hold checks. Original forensic evidence must remain protected.

## Migration execution journal (newest entries appended chronologically)

### Entry 001 — 2026-11-20 UTC — Recovery inventory and scope

**BEACON COMPUTING INITIATIVE** | **Developer Seal: CJB-DEV-2026**

- **Task:** Begin source-preserving migration from Kali to Kubuntu; inspect the public GitHub repository before changing the old computer.
- **Repository / branch:** `BeaconComputingInitiative/BCI-Orbit11` / `kubuntu-recovery-20261119`.
- **Observed source inventory:** Public `main` tree contained 183 entries, including the existing host, neural, expansion, rate-aware, and console source families. Latest v0.6–v1.8 research workspaces, local canonical datasets, private operational evidence, and local checkpoints were **not found in this GitHub tree**.
- **Privacy boundary:** No local machine or private dataset access is available through the GitHub connector. Do not assert that private research data was backed up, reproduced, or published. Use a separate encrypted or otherwise access-controlled backup.
- **Observed action:** Inspected repository metadata, tree, README, development guide, component installation scripts, integrity workflow, and existing developer log. Created a migration work branch.
- **Checks:** Repository contents and permissions inspected remotely; full checkout SHA-256 verification, build, GUI launch, and Kubuntu acceptance **NOT RUN**.
- **Decision:** **INVENTORY PASS / LOCAL ARTIFACT PRESERVATION HOLD / PRODUCTION HOLD**.
- **Next:** Add account-portable Kubuntu installer, export/restore procedure, and reproducible verification workflow; update the log after each completed action.

## Repository development history

| UTC date | Activity | Recorded state |
| --- | --- | --- |
| 2026-11-14 | README and architecture baseline authored | Documentation-only stage |
| 2026-11-14 | Five versioned Orbital component families imported | Experimental source; historical tests reported |
| 2026-11-14 | Developers Log and 5:1 development workflow introduced | Validate exact commit and CI before declaring PASS |

**Beacon Computing Initiative | CJB-DEV-2026**  
**Digest:** Managed through SHA256SUMS in the repository root. Never mark unexecuted work complete.
