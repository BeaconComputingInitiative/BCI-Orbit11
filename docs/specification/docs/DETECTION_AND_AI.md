<!-- BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026 -->
# Detection and Native AI Strategy

**BEACON COMPUTING INITIATIVE** | **Developer Seal: CJB-DEV-2026**  
**ORBIT11 / BCI Orbital Cyber Defense AI** | **Status: Design specification**

## What "AI" means in ORBIT11

The objective is a **locally evaluated, adaptive and inspectable detection system**, not an unbounded language agent controlling a firewall. Start with deterministic rules and statistical models; introduce learned models only when they can improve verified performance under an explicit safety budget.

A detector output should be a claim of the form: *This observation differs from the approved context profile, these corroborating observations exist, and these alternative benign explanations remain plausible.* It must never claim certainty about attacker identity or intent.

## Four layers

1. **Sensors:** authoritative raw facts such as process ID, socket metadata, mount events, I/O deltas and timestamps.
2. **Deterministic detectors:** rate/change rules, disallowed listeners, new service launches, suspicious execution lineage, known policy breaks.
3. **Anomaly models:** per-context drift/rate/sequence and multivariate feature scoring, with confidence and missing-data flags.
4. **Correlation:** groups related findings into a bounded incident hypothesis using time, host, process and destination relationships.

AI can propose prioritization and explain detected patterns; it does not bypass the policy engine or establish causality on its own.

## Model interfaces (proposed)

- `extract_features(events, schema_version) -> features + missingness`
- `score(features, approved_profile, model_version) -> scored_finding`
- `explain(scored_finding, referenced_events) -> provenance + alternatives`
- `train(qualified_dataset, fixed_config) -> candidate + manifest`
- `evaluate(candidate, locked_test_corpus) -> metrics + failure_cases`
- `promote(candidate, authenticated_approval) -> immutable_registry_entry`

Actual callable functions will be specified when runtime code exists; these are interface descriptions.

## Evaluation protocol

Split by time, host/network context and incident family to reduce leakage. Compare against a rule-only baseline. Report precision, recall, false positives per host-day, mean detection delay, and out-of-distribution behavior; include uncertainty bounds and class imbalance assumptions. Evaluate benign context switches, offline hosts, noisy desktop activity and unavailable sensors. Never optimize solely for a headline accuracy percentage.

## Learning and promotion

- Capture eligible samples only with provenance and purpose.
- Train in an isolated, resource-bounded process; candidates cannot mutate live profiles.
- Reproduce metrics; reject unsafe regressions and data leakage.
- Require an identified operator to approve exact candidate digest, test report and intended profile.
- Retain the prior approved model for rollback.
- Purge only eligible disposable rows *after* successful validation, approval/retention checks, and a verifiable receipt; never purge incident evidence or legal holds.
- If any step fails, remain on the last approved candidate and record HOLD.

## Explainability record

Each finding needs input IDs, detector name/version, profile version, model hash (if used), feature window, threshold, confidence semantics, missing sensors and alternative interpretations. An LLM-generated narrative, if later added, must be visibly labeled as interpretation, grounded in cited records and excluded from policy-authorization logic.

## Prohibited shortcuts

No retraining directly on unreviewed alerts as new truth; no model weights changed merely because the network changes; no hidden prompt-based firewall changes; no assumption that one suspicious signal equals compromise.
