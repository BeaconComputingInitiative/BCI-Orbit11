<!-- BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026 -->
# ADR-0003: Verified Disposal of Disposable Training Data

**BEACON COMPUTING INITIATIVE** | **Developer Seal: CJB-DEV-2026**  
**ORBIT11 / BCI Orbital Cyber Defense AI** | **Status: Accepted design decision**

- **Decision:** Post-training cleanup targets eligible transient copies only; forensic evidence and legal holds always take precedence.
- **Rationale:** Indefinite accumulation raises privacy and storage risk, while deleting authoritative evidence destroys investigative value.
- **Gate:** Purge occurs if and only if training outcome and lineage verify, retention classification allows disposal, and the operation generates a durable deletion receipt.
- **Failure behavior:** HOLD without deletion; never infer that a filename is disposable.
- **Review trigger:** Changes to legal-hold treatment, training source inventory or recovery/backup semantics.
