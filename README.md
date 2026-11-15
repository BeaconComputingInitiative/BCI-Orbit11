# BCI-Orbit11

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
| See latest separate Q1.7/Q1.8 research gate | [Qualification HOLD record](docs/research/ORBIT11-Q1.8-QUALIFICATION-2026-11-15.md) |
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
