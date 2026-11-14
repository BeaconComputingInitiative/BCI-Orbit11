# Repository import validation

BEACON COMPUTING INITIATIVE · Developer Seal: CJB-DEV-2026

## Executed checks

Validated on 2026-11-14 UTC with Python 3.14 on this Kali environment.

| Suite | Tests | Result |
|---|---:|---|
| Host v0.1.0 | 9 | PASS |
| Neural v0.2.0 | 27 | PASS |
| Expansion v0.3.0 | 16 | PASS |
| Console v0.8.3 | 46 | PASS |
| Rate-aware v0.5.1 self-tests | 9 | PASS |
| **Total** | **107** | **PASS** |

`python3 -B scripts/check.py` also parsed all component Python files and checked
all component shell scripts with `bash -n`. Full output: [unit-tests.txt](../reports/unit-tests.txt).
Suites run in separate processes with component-specific import paths. Synthetic
neural training inside tests uses temporary fixtures, never local host evidence.

The original console suite requires both original PNG assets. An initial import
omitting the design mockup failed three asset checks. Restoring the original
mockup resolved all three; no test or imported source code was weakened or edited.
The mockup is a design fixture and does not claim current live service health.

## GUI smoke check

The offscreen PyQt6 smoke test passed: **11 pages rendered**, all visible controls
mapped, original globe loaded, and the supported baseline question routed. The
first invocation inherited a desktop theme that attempted a restricted DBus/display
connection. Explicitly disabling that theme and display produced a successful
isolated offscreen run:

```bash
env -u DISPLAY QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME= QT_STYLE_OVERRIDE=Fusion python3 -B components/console/scripts/gui_smoke.py
```

Details: [gui-smoke.json](../reports/gui-smoke.json). Live refresh is disabled and
UI state is synthetic. This does not prove live collector access, every dialog's
operational effect, or interactive desktop behavior under real load.

## Source preservation and upload scope

All 65 imported source/doc/asset files match their recorded original SHA-256 values
in SOURCE-PROVENANCE.json. Component manifests were regenerated for the selected
inventory. The root SOURCE-SHA256SUMS covers all committed project files except
itself. Runtime data, installed launchers and services were left untouched.

Only source, original assets, synthetic fixtures, documentation and these test
results are included. Credential-pattern and inventory review found no private key
or credential files in the selected upload. This is a scoped review, not a certified
secret audit. No private weights, approval files, host event stores, captures or
runtime telemetry were imported.

## Pending operational acceptance

No installer, service activation, privileged packet/kernel collection, host-data
training, model promotion, historical checkpoint import or firewall action was run.
No live acquisition completeness, independent model detection benchmark, production
accuracy or security incident conclusion is claimed. Existing packet service status
is an external runtime dependency; its installed collector is not bundled here.

Fresh-machine deployment, current-version compatibility outside this environment,
continuous service recovery, quota/retention recovery and privileged access need
separately authorized host acceptance. See ROADMAP.md for further engineering.
