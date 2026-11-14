<!-- BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026 -->
# ADR-0001: Independent Repository and Evidence-first Scope

**BEACON COMPUTING INITIATIVE** | **Developer Seal: CJB-DEV-2026**  
**ORBIT11 / BCI Orbital Cyber Defense AI** | **Status: Accepted design decision**

- **Decision:** ORBIT11 is a new standalone design with no implicit migration from any installed Orbital product.
- **Context:** Existing systems may contain running services, mixed versions, private telemetry and live evidence. Blind reuse risks changing production behavior or leaking sensitive artifacts.
- **Consequences:** Initial work is documentation, synthetic fixtures and read-only components. Any legacy import requires its own explicitly reviewed change and qualified source inventory.
- **Alternatives:** Rename an older repo (rejected: loses isolation); copy an entire local installation (rejected: unresolved provenance and data sensitivity).
- **Review trigger:** Decision to migrate or interoperate with another BCI system.
