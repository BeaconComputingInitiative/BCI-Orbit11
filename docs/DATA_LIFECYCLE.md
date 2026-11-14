<!-- BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026 -->
# Evidence, Training Data and Retention Lifecycle

**BEACON COMPUTING INITIATIVE** | **Developer Seal: CJB-DEV-2026**  
**ORBIT11 / BCI Orbital Cyber Defense AI** | **Status: Design specification**

## Classification precedes retention

ORBIT11 must never treat all collected bytes as interchangeable. Use explicit classes:

| Class | Purpose | Default protection |
|:--|:--|:--|
| Security evidence | Incidents, original observations, chain-of-custody | Retain under evidence policy |
| Legal hold | Records subject to preservation obligation | Never routine-purge |
| Audit/provenance | Approvals, lineage, digests, deletions and changes | Preserve for investigation/accountability |
| Qualified training inputs | Disposable working examples with lawful purpose | Eligible only after validation and policy checks |
| Transient cache | Reconstructable processing state | Bounded TTL |
| Secrets | Credentials, keys, bearer tokens | Never train; store securely and redact logs |

## Post-training cleanup contract

The user-facing goal is **not to accumulate unnecessary training data indefinitely**. The cleanup engine shall remove eligible *training copies* if and only if:

1. The completed training job is reproducible and artifact digests have been verified.
2. Validation and regression gates are PASS, and the intended model disposition has been recorded.
3. Each input is explicitly labeled disposable, has no active legal hold and is not required as original evidence.
4. An authorized retention policy permits deletion and a dry-run inventory has been reviewed.
5. The deletion operation can generate a durable receipt including source IDs, counts, byte totals, hashes where appropriate, policy, approver and outcome.

On failure, mark HOLD and do not guess which source to delete. After a crash, reconciliation must not silently retry a destructive batch. Delete only selected known paths/rows; defend against symlinks, path traversal and hardlink surprises.

**Deleting a training copy does not delete the authoritative forensic original.** If evidence is needed for a live incident or an active preservation duty, retention outranks minimization. Disposal may also be constrained by backups, snapshots and filesystem recovery; record these limits honestly.

## Suggested state model

`INGESTED -> CLASSIFIED -> QUALIFIED -> TRAINING -> VALIDATED -> (PROMOTED|REJECTED) -> RETENTION_REVIEW -> PURGE_ELIGIBLE -> PURGED`

Any state may become `HOLD` on legal-hold, corruption, lost provenance, conflicting approval or an unresolved incident. A model is not automatically deployable because training succeeded.

## Evidence integrity

For each evidence record capture capture source, event time, receipt time, collector version, host/context, chain predecessor and canonical-record SHA-256. Preserve the original and derived interpretations separately. Use protected anchoring or signatures to detect whole-chain replacement by a privileged attacker. SHA-256 verifies bytes against a trusted reference; it does not identify the author.

## Export and privacy

Encrypted evidence export requires explicit destination, purpose and minimum necessary disclosure. Do not ship packet payloads, private host names, device serials or personal records to GitHub issues or public logs. An outbound email evidence feature, if implemented, must remain off until the operator configures and approves it.
