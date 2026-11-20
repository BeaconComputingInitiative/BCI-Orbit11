# ORBIT11 — Kubuntu Recovery and Reproducibility

**BEACON COMPUTING INITIATIVE** | **Developer Seal: CJB-DEV-2026**

**Status (2026-11-19 Pacific):** Repository bootstrap source committed; local
research data and current trained model recovery **NOT YET PERFORMED**;
operational acceptance and production **HOLD**.

## What this repository actually restores

This public repository contains source for five historical component families:
host v0.1.0, neural v0.2.0, expansion v0.3.0, rate-aware v0.5.1 and the
PyQt6 console v0.8.3. These are not an independently verified installation
of the latest local ORBIT11 native research track. Newer research workspaces,
canonical datasets, model weights, qualified training history and enterprise
Docker lab must be preserved separately from the old machine.

**No private source data, personal telemetry, packet captures, secrets or
unreviewed model weights are included in the public GitHub migration.**
Git LFS is not an encryption or authorization boundary.

## First: back up the old computer, before erasing anything

Use an adequately sized mounted backup volume. If the data includes evidence,
credentials or personally sensitive information, make it an encrypted volume.
The script does not mount, format, partition or erase devices.

Clone the repository on the old system if necessary:

```bash
# BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026
git clone https://github.com/BeaconComputingInitiative/BCI-Orbit11.git
cd BCI-Orbit11
bash scripts/export-migration.sh --destination /media/bci/SAFE-BACKUP/ORBIT11-20261119
bash scripts/export-migration.sh --destination /media/bci/SAFE-BACKUP/ORBIT11-20261119 --apply
```

**Critical:** Replace the sample `/media/bci/SAFE-BACKUP` path with your
actual mounted backup disk. The export detects up to three historical roots
under the current home directory; pass any additional location with
`--source /actual/path`, repeating as needed. These defaults do not mean
every training dataset is included. Audit the complete inventory.

Preserve, where available: Git source and uncommitted code; canonical raw,
filtered and reviewed dataset files; data provenance and licenses; train,
validation, and test partition definitions; tokenizer/feature schemas; labels
and leakage decisions; training scripts, parameters and seeds; checkpoints
(including the actual tensor files, not just JSON reports); frozen evaluation
cases; API contracts; Docker Compose/config files and local images/build
recipes; GUI source/assets; systemd customizations; forensic chains;
SHA-256 manifests and external trusted digest anchors.

The exporter copies data without publishing it, verifies copied content, and
prints a SHA-256 digest of its manifest. Keep that manifest digest somewhere
independent of the backup. **Do not wipe Kali unless you have inspected the
backup contents and can verify that every required root and checkpoint exists.**

## Next: install on freshly installed Kubuntu

```bash
# BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026
sudo apt-get update
sudo apt-get install -y git
git clone https://github.com/BeaconComputingInitiative/BCI-Orbit11.git ~/BCI/Projects/ORBIT11
cd ~/BCI/Projects/ORBIT11
bash scripts/install-kubuntu.sh --install
bash scripts/install-kubuntu.sh --audit
```

The install mode sets up Ubuntu Python 3 and PyQt6 through the package manager,
runs the committed integrity/test gates, and installs regular-user entrypoints:

- `~/.local/bin/orbit11` — research GUI
- `~/.local/bin/orbit11-host` — historical host CLI
- `~/.local/bin/orbit11-neural` — historical neural CLI
- `~/.local/bin/orbit11-expansion` — historical expansion CLI

A Plasma launcher is created. Existing launcher conflicts cause **HOLD**,
rather than silent replacement. The setup does not enable privileged collectors,
timers, network containment, new training, model promotion or offensive tasks.

**Note:** `--audit` expects Python 3, PyQt6 and the other test prerequisites
already installed; if they are absent, start with `--install` instead.
No target-Kubuntu execution results are claimed here.

## Then: verify and stage the private restore

```bash
# BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026
cd ~/BCI/Projects/ORBIT11
bash scripts/restore-migration.sh --backup /media/bci/SAFE-BACKUP/ORBIT11-20261119
bash scripts/restore-migration.sh --backup /media/bci/SAFE-BACKUP/ORBIT11-20261119 --apply
```

An optional `--expected-manifest-sha256` value protects the restore against
a replaced manifest when its trusted digest was recorded separately.
Files are staged into `~/BCI/Restored-ORBIT11/roots` and **not** merged
into live runtime paths. This protects evidence, schema compatibility,
earlier services and current installation state. Local model weights need
separate compatibility and approval checks before any inference or training.

## Acceptance criteria

**Full reconstruction is PASS if and only if** the local-only source and dataset
inventory is complete, immutable hashes and external anchors verify, package
dependencies and GUI tests pass on Kubuntu, schemas and training configurations
are compatible, reference and frozen evaluation results reproduce, and all
backend routes are independently tested. Any monitoring activation, trained
model promotion, automated remediation or lab target execution requires its
own review and authorization.

Until then: **SOURCE PREPARATION PASS / LOCAL MIGRATION HOLD / PRODUCTION HOLD**.
