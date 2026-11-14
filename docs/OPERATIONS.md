# Operations and evidence

BEACON COMPUTING INITIATIVE · Developer Seal: CJB-DEV-2026

## Read-only triage

1. Read component status and identify every unavailable or denied sensor.
2. Read packet collector state and bounded diagnostic logs. QUOTA HOLD requires
   both the defined service condition and an explicit matching journal message.
3. Verify evidence consistency before relying on a journal, frozen candidate,
   model or score report. Preserve originals and record retained chain heads.
4. Compare context, timestamps and measurement provenance before correlating data.
5. Report observations and alternate explanations. Escalate a hypothesis only
   when independent evidence supports the stated conclusion.

An inactive service, quota failure, unusual port, listener change or statistical
outlier does not prove an attack. A failed collector also does not prove safety.

## Candidate-to-model lifecycle

| Stage | Required condition | Result |
|---|---|---|
| Capture | Authorized sources and validated measurement provenance | Unreviewed local journal |
| Freeze | Valid chain and chosen context | New hashed candidate snapshot |
| Review | Schema, digest, coverage, chronology, span and provenance | Eligibility assessment |
| Approve training | Operator review plus dataset/context binding | Training-only approval artifact |
| Train | Matching approval and revalidated input | New unpromoted model |
| Evaluate | Verified same-context independent evaluation data | Shadow scores and contributor report |
| Promote/rollback | Future authenticated registry and tested recovery | Currently HOLD in console |

Do not concatenate legacy and live datasets to satisfy minimum window counts.
Do not treat measured and zero-filled throughput windows as semantically identical.
Do not use a high training-window count as a substitute for a valid chain or benign
label review. The original core and console have different readiness layers;
inspect the actual reports rather than assuming one checklist covers both.

## Execution gates

- Inspect host state IF AND ONLY IF the command is authorized and its dependencies
  are available; record missing visibility explicitly.
- Issue a model-derived finding IF AND ONLY IF the artifact and input satisfy the
  schema, integrity and exact-context checks. Label it statistical novelty.
- Record an event-sequence hypothesis IF AND ONLY IF the correlator's temporal,
  host/context, stable-process and independent-source criteria are satisfied.
- Train on host data IF AND ONLY IF qualification, review and explicit training
  authorization all pass. A source-code upload is not training authorization.
- Activate a service or privileged sensor IF AND ONLY IF that operation is separately
  approved and its deployment/rollback requirements are reviewed.
- Apply a live response IF AND ONLY IF separately approved, supported, scoped and
  recovery-tested. Neural scores alone never supply that approval.
- Remove temporary data IF AND ONLY IF it is classified disposable and required
  evidence has been preserved. The repository's test fixtures live in temporary
  directories; runtime forensic stores do not belong to that class.

## Runtime locations retained for compatibility

| Component | Existing state path |
|---|---|
| Host | `~/.local/state/bci-orbital-v2` |
| Original neural | `~/.local/state/bci-orbital-neural-v0.2.0` |
| Rate-aware integration | `~/.local/state/bci-orbital-integration-v0.5.1` |
| Imported historical AI artifacts | `~/.local/state/bci-orbital-ai-v0.8.0` |
| Console reports/models | `~/.local/state/bci-orbital-gui` |

The existing application expects versioned launchers under `~/.local/bin` and
release sources under `~/.local/opt`. Some preserved scripts explicitly assume the
`bci` account at `/home/bci`; they are not general multiuser installers.

## Quota and retention

A storage limit is an acquisition gap. Preserve existing evidence and establish a
reviewed archival/retention strategy before restarting a quota-stopped collector.
The console quota guard only prevents a known exit-code-3 restart loop; it does
not create storage capacity or resume acquisition. No automatic purge is added.
The dynamic packet service referenced by the console is an external installed
component, not a bundled, newly validated system service.

## Evidence assurance

Keep hashes/chain heads in an independent trusted location when stronger provenance
is needed. Local SHA-256 cannot authenticate the original sensor or prevent a
privileged adversary from replacing both data and digests. Report receipt timestamps,
acquisition context, access failures and transformations. Preserve original rows;
work on verified copies. HMAC redaction protects identifier disclosure but not all
linkability or inference risk. Do not upload packet captures, raw event databases,
private model files or operator approval artifacts to this repository.
