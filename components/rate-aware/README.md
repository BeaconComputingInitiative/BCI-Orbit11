# BEACON COMPUTING INITIATIVE
**Developer Seal:** CJB-DEV-2026  
**Project:** Orbital Group 15 — Rate-Aware Neural Collection  
**Version:** 0.5.1

This release is a **single four-stage Python runner**. Run the script once as the
unprivileged `bci` user; after an explicit confirmation it updates the existing
`bci-orbital-neural.service` while reusing `bci-orbital-neural.timer`.

It fixes an important dataset gap: the earlier v0.2.0 neural timer encoded
unavailable throughput as `0`. The v0.3.0 expansion has a verified live
feature bridge that measures interface rates. The upgrade collects to a **new**
`rate-aware-journal.jsonl` so these feature definitions are never silently mixed.

## Four stages
1. Verify own SHA-256, installed Orbital source manifest hashes, host service,
   and existing neural timer.
2. Capture an actual measured-rate feature window and verify the host+route
   fingerprint, window hash, and precise feature schema.
3. Append the new window to a separate SHA-256-chained, unapproved candidate
   journal; verify the chain after append.
4. Only upon entering `ACTIVATE-RATE-AWARE`, copy the pinned runner into a
   versioned unprivileged location, back up the original neural service unit,
   swap its command, test a run, and resume the same timer. A failure attempts
   rollback of the service unit and timer.

## Run on Kali `bci` account
Download this release ZIP to `/home/bci/Downloads`, and run:

```bash
cd ~/Downloads
unzip -n BCI-Orbital-Group15-RateAware-v0.5.1.zip
cd BCI-Orbital-Group15-RateAware-v0.5.1
sha256sum -c SHA256SUMS
python3 BCI-Orbital-Group15-v0.5.1.py --self-test
python3 BCI-Orbital-Group15-v0.5.1.py
```

No sudo is needed for this migration. The installed shell launcher already
hash-verifies the expansion's code before each capture. The script checks the
base source release manifests before using their code.

## After activation
`systemctl --user status bci-orbital-neural.timer --no-pager`  
`systemctl --user status bci-orbital-neural.service --no-pager`  
`python3 ~/.local/opt/bci-orbital-integration/0.5.1/BCI-Orbital-Group15-v0.5.1.py --status`

Journal location:
`~/.local/state/bci-orbital-integration-v0.5.1/rate-aware-journal.jsonl`

Reports, manifests, and original user service backup:
`~/.local/state/bci-orbital-integration-v0.5.1/runs/group15-*/`

This **does not** approve the neural baseline, train/promote a model, enable
live scoring, enable root packet capture, modify root-owned packet collectors,
or change containment. Existing v0.2.0 neural candidate journal and all other
Orbital evidence are preserved.

## Important limitations
- A 2-second interface sample every five minutes is not complete network
  visibility and is not a packet-to-process attribution mechanism.
- A SHA-256 chain does not independently prove provenance or defend against
  complete deletion/replacement without an independently retained anchor.
- New route/host fingerprints are not silently mapped to legacy contexts.
- Model training still requires qualified host data and operator review.
- If the service update fails, inspect service and timer state before retrying;
  rollback is best-effort and no evidence file is deleted.
