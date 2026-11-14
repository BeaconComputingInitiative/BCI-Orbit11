<!-- BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026 -->
# ADR-0002: Human Authority Over Baselines and Containment

**BEACON COMPUTING INITIATIVE** | **Developer Seal: CJB-DEV-2026**  
**ORBIT11 / BCI Orbital Cyber Defense AI** | **Status: Accepted design decision**

- **Decision:** Training and anomaly scoring are advisory. Active baseline/model promotion and containment are separate authenticated, audited policy transitions.
- **Rule:** A mutating response executes if and only if an approved policy, valid identity, sufficient corroboration, healthy evidence and tested recovery are all present.
- **Rationale:** Adaptive models can absorb attacker behavior and false positives can interrupt legitimate activity.
- **Consequence:** Unknown network context or failed authentication defaults to observe-only/HOLD. A future management GUI cannot bypass the same central authorization path.
- **Review trigger:** A proposal for unattended policy or model updates.
