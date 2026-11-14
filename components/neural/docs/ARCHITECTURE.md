# BEACON COMPUTING INITIATIVE — ORBITAL NEURAL ARCHITECTURE
**Developer Seal:** `CJB-DEV-2026`  
**Version:** `0.2.0`  
**SHA-256:** See `SHA256SUMS`

```
        HISTORICAL CHANCE ACCOUNT                LIVE BCI ACCOUNT
     baseline_observations (read-only)       Orbital v0.1.0 sensors
              |                                         |
         legacy-export                             capture
              |                                         |
    per-legacy-profile windows              hashed append-only journal
              |                                         |
        UNTRUSTED CANDIDATE                   freeze per current context
              |                                         |
              +------- Review gates / SHA-256 ---------+
                                    |
                            LOCAL HUMAN REVIEW
                         (training-only approval)
                                    |
                  12→8→3→8→12 neural autoencoder
                       80% temporal train / 20% holdout
                                    |
                     Candidate anomaly score + features
                                    |
                  Evidence correlation (independent rules)
                                    |
                       EXPLAIN / INVESTIGATE ONLY
                         NOT A CONTAINMENT PATH
```

## Statistical learner

A self-supervised multi-layer perceptron reconstructs a vector representing a single sensor interval. Inputs are normalized with `log1p` and standardization fitted to the training subset only; the final layer is linear. The architecture has **12 input and output dimensions**, bottlenecked through a 3-unit latent representation. Seed `440` is deterministic; the model trains with clipped-gradient SGD and an epoch-patience stop.

MSE reconstruction error is used as an anomaly score. A threshold is calibrated to `1.3×p99` of held-out candidate-normal errors, with a minimum floor of `0.015`. It is **not a calibrated probability of malware**, and no adversarial robustness guarantee exists. Chronological holdout avoids training on later data in the same dataset, but correlated windows can still leak temporal structure; operator review of evaluation drift remains essential.

| Feature | Source/interpretation |
|---|---|
| process_count | Number of visible processes |
| listener_count | TCP/UDP sockets listening or unconnected |
| outbound_count | Public remote sockets observed |
| inbound_count | Established sockets corresponding to known listener ports; heuristic |
| remote_unique_count | Unique public remote endpoint count |
| usb_mount_count | USB block storage mounts observed |
| risky_process_count | Suspicious executable location/deleted executable/browser mappings |
| public_listener_count | Listeners bound to wildcard interfaces |
| unusual_remote_port_count | Public remotes not on a small common-port set; **not malicious by itself** |
| rx_kib_per_second | Inbound traffic rate, unavailable in v0.1.0 live sensors (zero + gap) |
| tx_kib_per_second | Outbound traffic rate, unavailable in v0.1.0 live sensors (zero + gap) |
| visibility_issue_count | Number of collector limitations in the current observation |

A numeric zero when rates are unavailable must **not** be understood as measured zero bytes. Missing-data masks and a real throughput collector are production milestones.

## Context and baseline qualification

- **IF AND ONLY IF** dataset SHA-256, schema, single-context identity, seven elapsed days, 24 scan hours, 80 observations, minimum network+listener coverage, and an interactive operator confirmation pass may the sidecar issue a **candidate-training-only approval**.
- **IF AND ONLY IF** the training request matches that approval file's source digest and context may it create a candidate model.
- Legacy contexts remain isolated in `legacy:*`. They are never assigned to current `ctx-*` without separately engineered, audited context mapping.
- A candidate neural model is immutable once written; training a new version must use a new filename. No online learning or silent self-approval.
- A model has **no write path** into Orbital v0.1.0 approvals, response controls or nftables.
- Anomaly review and verified benign labels must be separately curated before any future retrain. Otherwise self-learning can normalize attacker persistence.

## Reasoning / limitations

The reasoning engine is deterministic evidence-based **hypothesis generation**, not deliberative AI or formal causal inference. For sequence links it requires both temporal ordering and a shared host/context/stable process key, plus two declared sensor sources. It reports the event IDs and limitations; it neither proves data transfer nor independently confirms sensor identities. File-read and file-write records currently need trusted future collectors or external validated input. USB/network timing is explicitly categorized as weak coincidence.

## Integrity

Every release file is included in `SHA256SUMS`, and the ZIP has its own external checksum. Frozen candidate/model/score/reason files receive adjacent SHA-256 checksums. Live candidate observations use a SHA-256 hash chain. All these detect unexpected changes **only if a trusted prior hash is retained independently**; local hashes are not authentication, immutability, or a cryptographic signature.
