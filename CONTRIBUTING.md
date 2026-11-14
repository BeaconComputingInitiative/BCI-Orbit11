# Contributing to BCI-Orbit11

BEACON COMPUTING INITIATIVE · Developer Seal: CJB-DEV-2026

## Development workflow

1. Identify the component and read its README and trust boundaries.
2. Keep runtime state outside the checkout. Use synthetic fixtures and temporary
   directories for tests.
3. Make the smallest reviewable source change; preserve unrelated installed projects.
4. Run `python3 -B scripts/check.py`. If GUI behavior changes, run the offscreen
   smoke check with PyQt6 and perform appropriate interactive acceptance.
5. Refresh affected component manifests and the root source manifest. Hashes are
   evidence of the final bytes, not permission to change operational policy.
6. Explain behavior, test evidence, remaining limits and any required migration.

Preserved imported bytes are recorded in `docs/SOURCE-PROVENANCE.json`. When changing
an imported file, update its provenance description to distinguish the original
import digest from the new version. Do not silently claim modified source is still
byte-identical to its release.

## Review requirements

Keep the BCI identity and `CJB-DEV-2026` seal in new project source and reports.
Define explicit success/failure and authorization gates. Never replace failed sensor
reads with normal-looking zero/empty baselines. Do not label heuristic novelty as
confirmed malicious activity. Keep host baseline approval, candidate training,
model promotion and response authorization distinct.

Schema, feature semantics, context mapping and integrity pins are compatibility
contracts. Changes need migration notes and negative tests. Authentication,
privileged deployment, service activation and retention policy need concrete
reviewed behavior before operational use.

## Tests and dependencies

The standard test runner spawns each component suite in a separate process with
its own source path, preventing cross-component import collisions. Python/Bash
static checks run before suites. Core tests use the standard library; the optional
GUI smoke check requires PyQt6. Unit tests must not start live collectors, contact
external inference APIs, train on local evidence or activate services.

No package download, dependency upgrade, new license grant, runtime model import
or persistent installation is part of routine test execution.

## Pull request content

Describe the concrete trigger and resulting behavior, relevant validation and
material limits. Use synthetic reproductions. Include recovery steps for changes
that affect stored schemas, operational service wiring or model compatibility.
