<!-- BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026 -->
# Project Governance and Authority

**BEACON COMPUTING INITIATIVE** | **Developer Seal: CJB-DEV-2026**  
**ORBIT11 / BCI Orbital Cyber Defense AI** | **Status: Design specification**

## Stewardship

ORBIT11 is maintained under **Beacon Computing Initiative**, Developer Seal **CJB-DEV-2026**. Project changes use named reviewers, versioned records and explicit decisions. The developer seal identifies project convention; it does not authenticate GitHub accounts or sign binaries.

## Decision classes

| Class | Approval requirement |
|:--|:--|
| Editorial documentation | Maintainer review |
| API/schema change | Maintainer + migration/testing review |
| Sensor privilege expansion | Security review + least-privilege demonstration |
| Model or baseline promotion | Authenticated operator approval of exact candidate |
| Retention or evidence handling | Security/forensic review with legal-hold safeguards |
| Response/containment change | Independent fail-safe review, dry-run, rollback proof |
| Production deployment | Environment-specific operational acceptance |

## Separation of duties

Model authors may propose changes; they must not grant their own runtime privileges. The system should distinguish contributor, reviewer, operator and emergency-recovery roles. Production authorization must derive from a validated identity, not an in-code string or a public GitHub username.

## Documentation truthfulness

Status labels must reflect evidence. Historical results from a different BCI project cannot establish ORBIT11 qualification. Record known limitations, partial results, missing tests and HOLD states plainly.

## Disputes and exceptions

Exceptions require an issue or controlled record specifying risk, duration, owner and rollback. There is no permanent unreviewed bypass for containment, data deletion or baseline publication.
