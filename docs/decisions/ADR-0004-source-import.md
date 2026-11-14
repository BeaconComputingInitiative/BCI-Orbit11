# ADR-0004: Qualified experimental source import

BEACON COMPUTING INITIATIVE · Developer Seal: CJB-DEV-2026

**Status:** Recorded implementation decision for the requested repository population.

## Context

The owner requested that BCI-Orbit11 be populated in detail. During source preparation,
a documentation-first specification set was concurrently added to main at commit
`baa4d9b8c360f62ae338fa89167b31fa51e1c90e`. The first branch update did not apply.
That tree was inspected before preparing the integration against its new head.
ADR-0001 requires a reviewed inventory rather than blind migration of an installation.

## Decision

Import the explicitly inventoried source releases under separate `components/`
directories. Preserve source bytes, versions, assets and synthetic tests. Publish
the original file digests in SOURCE-PROVENANCE.json and current validation results.
Preserve the entire earlier documentation snapshot under `docs/specification/`,
retain nonconflicting current policy/target documents, and use the root README and
current implementation documents to describe what actually ships.

No private evidence, historical weights, approval files, running installation,
services or runtime configuration are imported. Tests run on temporary synthetic
fixtures. The existing private repository audience stays unchanged.

## Consequences

This is a source integration baseline, not a production migration or automatic
endorsement of legacy runtime behavior. Legacy host firewall code and optional
privileged expansion commands remain explicit review boundaries. Future governance,
authenticated promotion, deployment acceptance and independent model evaluation
requirements are unchanged. The code satisfies only a subset of the target design;
read current validation separately from target acceptance criteria.

## Validation

107 tests pass; all 11 GUI pages render with synthetic data offscreen. All imported
files match the selected release digests. Both current and preserved documentation
remain available for review in Git history and in the specification snapshot.
