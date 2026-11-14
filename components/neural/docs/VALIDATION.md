# BEACON COMPUTING INITIATIVE — ENGINEERING VALIDATION
**Developer Seal:** `CJB-DEV-2026`  
**Version:** `0.2.0`  
**SHA-256:** See `SHA256SUMS`

Execute from the release directory:

```bash
sha256sum -c SHA256SUMS
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m bci_neural demo --output /tmp/BCI-Neural-demo-unique.json
PYTHONPATH=src python3 -m bci_neural verify /tmp/BCI-Neural-demo-unique.json
```

The sample demonstration is synthetic and does not attest the installed host. For actual operational qualification, confirm the native v0.1.0 service remains active, input datasets have correct provenance, and the sidecar remains unable to request containment. Verify checksums externally and retain a copy of trust anchors outside the user account.
