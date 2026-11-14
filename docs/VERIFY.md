<!-- BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026 -->
# Documentation Integrity and SHA-256 Verification

**BEACON COMPUTING INITIATIVE** | **Developer Seal: CJB-DEV-2026**  
**ORBIT11 / BCI Orbital Cyber Defense AI** | **Status: Design specification**

The repository includes `SHA256SUMS`, a snapshot of SHA-256 checksums for tracked files. It excludes itself so regenerating it does not create an impossible self-reference.

## On Linux

```bash
# BEACON COMPUTING INITIATIVE | CJB-DEV-2026
# Verification succeeds if and only if every listed file matches its expected digest.
sha256sum -c SHA256SUMS
```

If a file has intentionally changed, regenerate the manifest in a dedicated reviewed change. An example that excludes Git metadata and the manifest itself:

```bash
git ls-files -z | grep -zv '^SHA256SUMS$' | xargs -0 -r sha256sum > SHA256SUMS
```

After adding *new* files, stage them first or they will not appear in `git ls-files`. Review the diff before committing; do not regenerate hashes to dismiss unexpected tampering. The manifest cannot authenticate itself, so verification against the same untrusted checkout only checks self-consistency. Trust requires an externally anchored digest or signed release.

The developer seal `CJB-DEV-2026` is an authorship label, not cryptographic proof.
