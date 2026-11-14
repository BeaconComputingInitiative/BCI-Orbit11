# BEACON COMPUTING INITIATIVE

**Developer Seal:** `CJB-DEV-2026`  
**Project:** Orbital Cyber Defense — Adaptive Neural Core  
**Release:** `v0.2.0` (isolated engineering preview)  
**SHA-256:** See `SHA256SUMS` and release ZIP `.sha256` sidecar.

## What this *actually* builds

This is a **working, standard-library-only Python neural autoencoder** plus a separate auditable rule-based evidence-correlator. It learns statistical regularities in qualified numeric telemetry windows, then scores deviations within the **same network context**. The deterministic correlation layer links time-ordered events with the same stable process identity *only when two different reported sensors support the sequence*.

**Neural novelty is NOT a maliciousness probability.** The model does not autonomously understand intent, attack paths, file contents, or causality. The reasoning layer produces reviewable hypotheses, not proof of compromise.

It is an isolated sidecar: **it does not replace or modify the running `bci-orbital-v2.service`**, alter the v0.1.0 SQLite database, or connect to nftables. There is deliberately **no containment implementation** in this release.

### Components

- `src/bci_neural/model.py`: 12 → 8 → 3 → 8 → 12 CPU autoencoder, backprop, temporal hold-out calibration, per-feature reconstruction deviation.
- `src/bci_neural/sources.py`: hash-verifies the installed Orbital sensor, samples a feature vector without writing raw remote addresses; read-only, bounded Chance-era SQLite converter that preserves **legacy profile IDs**.
- `src/bci_neural/journal.py`: append-only SHA-256 chained candidate observations; freeze to a separately hashed JSONL file.
- `src/bci_neural/reason.py`: deterministic file/process/outbound evidence sequence hypotheses; distinguishes time co-occurrence from attributable activity.
- `src/bci_neural/cli.py`: telemetry capture, review, approval gate, train, score, report, verification, synthetic demo.
- `systemd/`: optional **disabled-by-default** user timer. Five-minute read-only sensor sampling.
- `tests/`: positive, negative and tamper tests.

## Minimum requirements

- Kali Linux with Python 3.10+ standard library, `sha256sum`, `systemctl --user` for optional timer.
- Existing Orbital `~/.local/opt/bci-orbital-v2/0.1.0` sensor release **intact** for host capture. The new sidecar verifies the installed sensor source file against that release's `SHA256SUMS`.
- BCI account for installation; **no root** and **no pip downloads**.

## Verify, install, and sample

Save ZIP and its matching `.sha256` in `/home/bci/Downloads`. The installer runs **IF AND ONLY IF** release integrity, a functional CLI, and no target collisions satisfy all gates.

```bash
cd /home/bci/Downloads || exit 1
sha256sum -c BCI-Orbital-NeuralCore-v0.2.0.zip.sha256 || exit 1
unzip -n BCI-Orbital-NeuralCore-v0.2.0.zip || exit 1
cd BCI-Orbital-NeuralCore-v0.2.0 || exit 1
sha256sum -c SHA256SUMS || exit 1
PYTHONPATH=src python3 -m unittest discover -s tests -v || exit 1
bash scripts/install.sh --user || exit 1
~/.local/bin/bci-orbital-neural capture
~/.local/bin/bci-orbital-neural status
```

The capture writes its **own** append-only candidate journal:

`/home/bci/.local/state/bci-orbital-neural-v0.2.0/candidate-journal.jsonl`

It does not write to the Orbital v0.1.0 evidence database. Its `rx_kib_per_second` and `tx_kib_per_second` values remain zero because the existing sensor does not collect per-interval traffic byte rates; this missing coverage is explicitly recorded.

### Optional scheduled collection (only after checking one manual capture)

```bash
systemctl --user enable --now bci-orbital-neural.timer
systemctl --user list-timers --all | grep bci-orbital-neural
journalctl --user -u bci-orbital-neural.service -n 25 --no-pager
```

This timer samples every five minutes. It **never trains automatically**. Disable with:

```bash
systemctl --user disable --now bci-orbital-neural.timer
```

## Freeze and review the BCI account's live data

The following creates a **new** immutable candidate snapshot, never overwriting a previous file. Use the context obtained from `bci-orbital-neural status`.

```bash
NEURAL="$HOME/.local/bin/bci-orbital-neural"
"$NEURAL" freeze --context ctx-REPLACE-WITH-YOUR-EXACT-CONTEXT \
  --output "$HOME/BCI-Neural-Candidate.jsonl"
"$NEURAL" review --context ctx-REPLACE-WITH-YOUR-EXACT-CONTEXT \
  --input "$HOME/BCI-Neural-Candidate.jsonl"
```

A candidate can be approved for **experimental neural training** only after **at least seven elapsed days, 24 distinct scan hours and 80 samples**, source-integrity verification, single-context enforcement, and an interactive local confirmation. The CLI refuses unqualified data. An approval authorizes **only model training**: it does not approve Orbital's baseline or authorize automatic response.

```bash
"$NEURAL" approve-training --input "$HOME/BCI-Neural-Candidate.jsonl" \
  --context ctx-REPLACE-WITH-YOUR-EXACT-CONTEXT \
  --output "$HOME/BCI-Neural-Candidate-approval.json"
"$NEURAL" train --input "$HOME/BCI-Neural-Candidate.jsonl" \
  --approval "$HOME/BCI-Neural-Candidate-approval.json" \
  --context ctx-REPLACE-WITH-YOUR-EXACT-CONTEXT \
  --output "$HOME/BCI-Neural-Candidate-model.json"
"$NEURAL" score --model "$HOME/BCI-Neural-Candidate-model.json" \
  --input "$HOME/BCI-Neural-Candidate.jsonl" \
  --output "$HOME/BCI-Neural-Score-report.json"
```

The local interactive confirmation is **not** high-assurance operator authentication. An attacker with write access to the account could forge the approval and replace its checksum; production use requires independently held signing keys, authenticated review, and write-protected model registries.

## Convert the legacy Chance database into an *untrusted* candidate

The old database is approximately **3.69 GB**, and older `baseline_approvals`/`baseline_versions` contained **zero records in the supplied diagnostic**. The previous sampled observation span was under one day. Do **not** claim that archive is an approved, clean, trained baseline.

1. Copy this verified source package to the Chance account only through an authorized, separately verified path, or run the installed script with read-only access granted to Chance. Do not `chmod` the old evidence database to make it world-readable.
2. As `chance`, run a bounded sample that writes aggregate numeric features, **not raw IPs**:

```bash
PYTHONPATH=/path/to/verified/BCI-Orbital-NeuralCore-v0.2.0/src \
  python3 -m bci_neural legacy-export \
  --source /home/chance/BCI-Orbital-CyberDefense/state/operator/evidence.sqlite \
  --limit 50000 \
  --output /home/chance/BCI-Neural-Legacy-Candidate.jsonl
```

The output uses contexts like `legacy:network-...`. These are **not** interchangeable with the BCI account's `ctx-...`. The sidecar never maps them automatically, never imports legacy alerts as normal behavior, and never approves any baseline. For large databases, use `--profile` to select one legacy network profile, or a bounded `--limit` up to 200000. A live WAL database is read in SQLite `mode=ro` under snapshot isolation for that query; the output is **not** an attested forensic backup.

3. Review the source's date range, sensor gaps, context and benignness before deciding whether to approve *experimental* model training. `approve-training` explicitly requires `--allow-untrusted-legacy` and the additional `REVIEW-UNTRUSTED-LEGACY` typed confirmation. Historical learning is not automatically qualified.

## Test the neural core immediately without trusting machine data

```bash
~/.local/bin/bci-orbital-neural demo --output "$HOME/BCI-Neural-SYNTHETIC-DEMO.json"
~/.local/bin/bci-orbital-neural verify "$HOME/BCI-Neural-SYNTHETIC-DEMO.json"
```

The demo uses synthetic observations and labels the model accordingly; it must **never** be presented as trained on the BCI or Chance machines.

## Reasoning engine

`reason --input example-events.jsonl --output reason-report.json` consumes explicit event evidence with `kind`, `ts`, `host`, `context`, `source`, `event_id`, and optional stable `process_key` (e.g. PID plus process start time). It only creates a process-associated hypothesis if the evidence refers to the same process identity and two reported sensor sources. Mere USB/network co-occurrence remains an informational notice.

For validation examples see `examples/events.jsonl`. The source tags are provided by the input and are **not cryptographically authenticated**.

## Security limitations / not implemented

This v0.2.0 release **does not** include continuous online retraining, cryptographic signer authentication, a production-safe model registry, sensor-level stable process identity collection, file read/write hooks, on-host DNS capture, packet payload inspection, model-based prevention, human-equivalent reasoning, or proof of compromise. Its current live sensor captures only the subset exported by Orbital v0.1.0. It is a working experimental neural foundation, not a production-ready EDR platform.

See `docs/ARCHITECTURE.md` for feature meanings and qualification gates.
