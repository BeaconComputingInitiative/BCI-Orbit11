<!-- BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026 -->
# Security Policy

**BEACON COMPUTING INITIATIVE** | **Developer Seal: CJB-DEV-2026**  
**ORBIT11 / BCI Orbital Cyber Defense AI** | **Status: Security policy / no release supported**

## Reporting

Please report vulnerabilities privately through GitHub's private vulnerability reporting option if enabled. If unavailable, contact a trusted project maintainer through a previously verified private channel; do not post exploit details, credentials, production host identifiers or personal evidence in public issues. This document does not claim a dedicated security mailbox.

Provide affected commit/version, reproduction using synthetic data, impact, required privileges, and a suggested fix if known. Avoid probing systems you are not authorized to test.

## Supported versions

| Branch / version | Support |
|:--|:--|
| `main` (documentation) | Review of documentation and design flaws |
| Runtime releases | None currently exist |
| Legacy Orbital installs | Separate project; not covered by this repo |

## Mandatory safeguards

- No secrets or production evidence in pull requests, fixtures or GitHub Actions output.
- Deny unapproved model promotion, containment and destructive retention.
- Use scoped credentials, peer identity verification and least-privilege collectors.
- Reproduce security issues in isolated, authorized environments.
- Treat hashes as tamper indicators only when their reference is trusted.
- Preserve affected evidence before mitigation, subject to legal and privacy constraints.

This project is defensive and must not be used for unauthorized surveillance, interception or disruption.
