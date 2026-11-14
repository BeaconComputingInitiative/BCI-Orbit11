# BEACON COMPUTING INITIATIVE
**Developer Seal:** `CJB-DEV-2026`  
**Artifact:** Orbital Comprehensive Capabilities — implementation and acceptance matrix v0.3.0  
**SHA-256:** `SHA256SUMS`

## Target (not a claim of full completion)

| Capability | v0.3 status | Safe acceptance criterion |
|---|---|---|
| Packet hashing | Bounded AF_PACKET source and unit tests | Root-owned deployment, CAP_NET_RAW, interface coverage, packet-loss measurement, audit |
| DNS visibility | Plain DNS parser for visible UDP/TCP port 53 frames | Test DNS transports, privacy handling, enterprise DoH/DoT integration; decryption not assumed |
| File read/write telemetry | bpftrace `openat` and `execve` ATTEMPT-only source | Add qualified file operation auditing/fanotify/eBPF with reliable fd/process identity and syscall success |
| Kernel telemetry | Optional tracepoint source, not deployed | Kernel compatibility, privilege and performance benchmark, event-drop rate |
| Throughput | `/proc/net/dev` real delta, group6 test | Per-interface consistency, route changes and interface offload caveats |
| Neural context | Fingerprints host/route; produces measured v0.2 schema windows | Review approved context mapping; qualify trusted live training; untouched prospective testing |
| Reasoning | v0.2 verified independent-source correlation | Link captured process-event evidence using stable PID+starttime; distinguish strong proof vs co-occurrence |
| Adaptive learning | Manual-reviewed v0.2 training, drift proposal API | Explicit retraining gates, versioned evidence, independent evaluation & rollback |
| Neural prevention | Not armed | Corroborated event chain, deterministic policy, identity/recovery tests, rollback, explicit operator approval |
| Threat attribution | Process/source provenance only when supported | No unsupported claims about who operated a remote device or intent |

## Work batches (four checks per batch)

**Group 6 — Shipped now:** (1) Context, (2) network-rate collection, (3) corrected neural feature windows, (4) hashes + verification. Privileged sensor source available but disabled.

**Group 7 — Not yet operational:** (1) root-owned isolated packet collection, (2) DNS coverage validation + packet-drop accounting, (3) kernel file activity with success/failure and PID/FD correlation, (4) hardened service and evidence retention validation.

**Group 8 — Not yet operational:** (1) event graph linked by stable process identity, (2) source provenance & cross-account context review, (3) independent neural evaluation, (4) shadow inference linked to evidence (no response).

**Group 9 — Not yet operational:** (1) supervised adaptive retraining with rollback, (2) privileged recovery and policy checks, (3) safe deterministic containment dry-run/rehearsal, (4) explicit operator acceptance before live response.

**Non-negotiable:** A network packet or anomaly score alone never establishes malware, exfiltration, attacker identity, or a justification to block traffic. The existing Orbital services and forensic evidence must not be overwritten during expansion.
