# BCI-Orbit11 model card

BEACON COMPUTING INITIATIVE · Developer Seal: CJB-DEV-2026

## Identity and intended use

BCI-Orbit11 is the project/model-family name. The included learned implementation is
Orbital Neural Core v0.2.0, an experimental self-supervised CPU autoencoder for local
telemetry novelty review. Source is included; private trained weights, historical
score reports, approvals and training datasets are not. No checkpoint was newly
trained or promoted during repository preparation.

Use it to prioritize analyst review of aggregate changes in a qualified network
context. Do not use scores as malware probabilities, attacker attribution, evidence
of interception, proof of a clean host, or authorization to block traffic.

## Architecture and learning

- Dense network dimensions: `12 → 8 → 3 → 8 → 12`.
- Hidden activations: tanh; output: linear.
- Learned parameters: 240 weights plus 31 biases, **271 parameters**.
- Input transformation: `log1p`, followed by training-subset means and standard
  deviations, with standard deviation floored at 0.15 and normalized inputs clipped
  to the range −8 to 8.
- Seed: 440 by default. Gradient-clipped stochastic updates, learning rate 0.012,
  small weight regularization, up to 90 default epochs and patience of 22 epochs.
- Chronological split: 80% training with a minimum 64 training windows; at least
  16 later validation windows. Normalization uses training rows only.
- Calibration: `max(0.015, 1.3 × held-out p99 reconstruction MSE)`.
- Output: mean squared reconstruction error, threshold comparison and four largest
  per-feature squared reconstruction errors.

The threshold is a candidate calibration heuristic. The recorded candidate false
positive fraction is calculated on candidate-normal calibration data; it is not an
independent field performance estimate. Temporal dependence can inflate apparent
generalization even with chronological holdout. Thresholds and dimensions are
verified in `components/neural/src/bci_neural/model.py`.

## Fixed feature order

| # | Feature | Interpretation / limitation |
|---|---|---|
| 1 | `process_count` | Visible process count; permission/namespace limits apply |
| 2 | `listener_count` | Observable listening/unconnected sockets |
| 3 | `outbound_count` | Observed public remote sockets |
| 4 | `inbound_count` | Heuristic based on known listener ports |
| 5 | `remote_unique_count` | Unique observed public remote endpoints |
| 6 | `usb_mount_count` | Visible USB block-storage mounts |
| 7 | `risky_process_count` | Rule-derived suspicious execution indicators |
| 8 | `public_listener_count` | Wildcard-bound listeners; not automatically unsafe |
| 9 | `unusual_remote_port_count` | Ports outside a small common set; not maliciousness |
| 10 | `rx_kib_per_second` | Measured interface rate in expansion; unavailable in original host-only capture |
| 11 | `tx_kib_per_second` | Same measurement limitation as RX |
| 12 | `visibility_issue_count` | Recorded collector limitations |

Exact order is part of the model contract. Counts/rates are nonnegative finite
numbers; booleans, unexpected dimensions and invalid timestamps are rejected.
Measurement gaps must remain visible. The original zero-filled rate data and new
rate-aware data are not interchangeable just because they share feature names.

## Qualification and approval

The training workflow requires dataset hashes, fixed schema, one exact context,
minimum sample/time span/coverage and a local interactive training approval tied
to that input. The original minimums are 80 samples, 24 distinct observation hours
and seven days. Console readiness adds checks for journal integrity, chronological
samples, no future samples, fresh final data, interface identity, consistent
host/route provenance and no historical sensor gaps.

Original sidecar review and newer console review are different layers; their
checks must not be assumed identical. Use the stricter rate-aware path for future
qualification work and inspect the actual review report. Legacy training additionally
requires explicit acknowledgment and never maps a legacy context to a live one.
A local approval file is not strong authentication against an attacker who controls
the same account.

## Evaluation status

Included tests cover numerical training/scoring on generated data, malformed model
rejection, context mismatch, tampering, coverage gaps, and approval logic. Tests
may train tiny synthetic models in temporary directories. They do not train on
host observations or create deployable production checkpoints.

No labeled malware benchmark, independent accuracy estimate, production false
positive rate, adversarial robustness assessment or comprehensive drift evaluation
is supplied. Historical checkpoint metrics referenced by the console are only
available if separately imported artifacts pass their pinned integrity checks.
Their existence in source code does not mean those artifacts ship in this repo.

## Failure modes and controls

- Poisoned candidate-normal data can normalize unwanted behavior: require provenance
  review, separate evaluation and independent benignness evidence.
- Context drift can raise or suppress novelty: preserve host/route and measurement
  semantics, reject silent cross-context scoring.
- Clipping and feature aggregation lose detail: corroborate with original authorized
  evidence; per-feature contributors are not causal explanations.
- Missing sensors reduce visibility: preserve gaps and HOLD states.
- Local hashes can be replaced with files: retain independent anchors and future
  authenticated model provenance.
- A small autoencoder can miss attacks resembling ordinary aggregate activity.

Live automatic inference, online self-training, production model promotion and
model-driven containment are not activated. Future changes require versioned
contracts, explicit evaluation and reviewed operational boundaries.
