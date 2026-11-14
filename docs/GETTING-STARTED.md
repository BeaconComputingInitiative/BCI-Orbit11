# Getting started with BCI-Orbit11

BEACON COMPUTING INITIATIVE · Developer Seal: CJB-DEV-2026

## Prerequisites

Use Python 3.10+ and Bash for development checks. Kali/Linux is the intended live
platform. Core neural, host and expansion code uses the Python standard library;
GUI rendering additionally requires PyQt6. Live collection depends on Linux procfs,
sysfs, networking tools, permissions and existing component installations.

Clone the private repository using your own GitHub authentication:

```bash
git clone https://github.com/BeaconComputingInitiative/BCI-Orbit11.git
cd BCI-Orbit11
python3 -B scripts/check.py
```

No credential belongs in a repository file or command committed to Git.

## Console from source

```bash
python3 -B components/console/src/orbital_cli.py --help
python3 -B components/console/src/orbital_cli.py status
python3 -B components/console/src/orbital_cli.py storage
python3 -B components/console/src/orbital_cli.py baselines
python3 -B components/console/src/orbital_cli.py ai 'what are your baselines?'
```

Status commands inspect the existing local stack. They may report missing launchers,
unavailable systemd or unverified sources on a fresh checkout. Those are coverage
gaps; a successful CLI invocation alone is not live acceptance of every sensor.
Do not upload their host-specific outputs unless reviewed and sanitized.

With PyQt6 available, launch `python3 -B components/console/src/orbital_cli.py gui`.
An optional isolated rendering check uses synthetic GUI data and disables live refresh:

```bash
env -u DISPLAY QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME= QT_STYLE_OVERRIDE=Fusion python3 -B components/console/scripts/gui_smoke.py
```

The smoke check verifies rendering/routing, not live collection or every button's
operational effect. It is separate from standard-library unit tests.

## Neural CLI and synthetic demonstration

```bash
PYTHONPATH=components/neural/src python3 -B -m bci_neural --help
```

To deliberately run a synthetic demonstration, choose a new output path outside
Git. This trains on generated data only and writes a hashed demo report:

```bash
PYTHONPATH=components/neural/src python3 -B -m bci_neural demo --output /tmp/BCI-Orbit11-SYNTHETIC-DEMO.json
PYTHONPATH=components/neural/src python3 -B -m bci_neural verify /tmp/BCI-Orbit11-SYNTHETIC-DEMO.json
```

The output must not be described as a model trained on the local host. Create-only
artifact writers refuse an existing path. Do not delete prior evidence to retry.
The root test runner already covers synthetic learning; the demo is optional.

## Installation boundaries

This repository has no new combined installer. Preserved component installers
retain versioned release paths and collision checks. Read their scripts and READMEs
before using them. Some historical instructions refer to ZIP names rather than the
new `components/<name>` directories. Adapt the working directory, not integrity or
approval gates. Component manifests are supplied for the imported inventory.

An existing installation may deliberately refuse reinstallation. Repository setup
does not authorize replacing it, updating service units, enabling timers, requesting
root access, importing historical model artifacts, or training on local data.
The rate-aware runner changes service wiring in its default workflow; run only
`--self-test` during ordinary development.

## Acceptance on the intended host

After a separately reviewed installation, verify source consistency, launcher
versions, each sensor's actual access, context identity, journal integrity, service
restart behavior, quota reporting and UI responsiveness. Record exact unavailable
sources. Obtain explicit approval for persistent activation and privileged sensors.
Training is a further, separate approval workflow. See OPERATIONS.md and VALIDATION.md.
