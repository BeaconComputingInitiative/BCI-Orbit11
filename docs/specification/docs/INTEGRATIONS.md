<!-- BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026 -->
# Integrations and Deployment Boundaries

**BEACON COMPUTING INITIATIVE** | **Developer Seal: CJB-DEV-2026**  
**ORBIT11 / BCI Orbital Cyber Defense AI** | **Status: Design specification**

## Independent first

ORBIT11 is a new repository, not a replacement name for an installed BCI Orbital service. Any import of existing source code or production artifacts requires scope review, license/provenance validation, secrets scanning, integrity verification and a rollback plan. Preserve the legacy deployment without concurrent unreviewed changes.

## Planned integrations

| Integration | Purpose | Initial boundary |
|:--|:--|:--|
| Linux / systemd | Supervision and startup | No unit yet; harden capabilities before install |
| Packet hashing | Optional evidence fingerprinting | Authorized raw capture only; metadata-first |
| Native desktop GUI | Operator review and approvals | Non-privileged process via authenticated local API |
| Desktop notifications | Explainable alerts and health | Must not imply conviction or automatically act |
| Email evidence | Operator-requested reports | Off until destination/encryption approval |
| Local model runtime | CPU-native training/scoring | Process isolation, quota, immutable candidate registry |
| Existing BCI components | Optional event/version exchange | Explicit opt-in schema and migration |
| Android/ADB | Future endpoint extension | Separate authorization, privacy and device permissions |

## Interface rules

Every integration must state its threat model, data sensitivity, consent, authentication, failure semantics, supported versions, event schema, observability and uninstall path. No default external egress. Treat user-supplied destinations and connected devices as untrusted until verified.

## Anti-goals

Do not merge with a phone backup cleaner or another product simply because they share BCI branding. Do not grant a model shell access or management credentials. Do not claim parity with installed tools absent source inspection and independent qualification.
