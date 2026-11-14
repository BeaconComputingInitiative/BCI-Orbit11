# BEACON COMPUTING INITIATIVE
**Developer Seal:** `CJB-DEV-2026`  
**Release:** Orbital PyQt6 Native AI v0.8.3 — P0/P1 Remediation  
**Installation policy:** No mandatory hash verification

## What was actually patched

The proposed terminal-CAT code discussed earlier **was not executed by the operator**. This release is based on the existing original **v0.8.2 ZIP source**, not that proposed sample. No rollback of an unrun script is needed.

1. **Packet collector diagnostics (P0):** the GUI reads `systemctl show` for `ActiveState`, `SubState`, `Result`, `ExecMainStatus`, and `NRestarts`. It reports `QUOTA HOLD` only if the running service has stopped, the recorded exit code is 3, and the packet service journal contains the explicit evidence-quota HOLD message. Otherwise it shows the actual failed, restart-limit, starting, or unknown condition. `orbital storage` provides a read-only diagnostic.
2. **Restart-loop safeguard (P0, separate authorization):** `scripts/packet-quota-guard.sh` can, with explicit root approval, install a new systemd drop-in with `RestartPreventExitStatus=3`. This prevents the v0.4.1 collector from repeatedly restarting after its exit-code-3 HOLD. **It does not solve the full quota, resume packet capture, modify collector source, or delete/move/archive evidence.** Run `--diagnose` first.
3. **Qt worker lifecycle (P0):** keeps the existing persistent, window-owned `Poller` and `Operation` threads rather than replacing them with self-deleting threads. Closing waits asynchronously for both threads to finish, without blocking the Qt GUI event loop or deleting a running QThread.
4. **Training readiness (P1):** verifies all windows in the real rate-aware JSONL journal and requires valid hash chain, matching host/route provenance, chronological timestamps, no past sensor gaps, no future samples, sufficient observation span, 80 windows, 24 unique *date-hour* buckets, current interface, and a fresh final observation. This means *eligible for review*, not authorized to train.
5. **Orbital AI (P1):** retains the original neural model and its baseline distinctions. New packet/quota questions report grounded service facts, not invented packet baselines or model predictions. No external LLM.
6. **Chart correctness (P1):** the built-in Qt graph uses actual sysfs network counters. Absent/invalid readings are displayed as unavailable instead of synthetic zero-traffic points; missing samples break chart lines.
7. **Visual identity:** original pixel-accurate globe and original approved mockup remain unchanged. The sidebar shows current release `v0.8.3` rather than stale `v0.8.0`.

## Install (does not require SHA-256)

Save `BCI-Orbital-PyQt6-P0P1-Patch-v0.8.3.zip` to `/home/bci/Downloads`. Then as the **bci user**:

```bash
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Install IF AND ONLY IF source checks and built-in tests succeed.
cd /home/bci/Downloads || exit 1
unzip -n BCI-Orbital-PyQt6-P0P1-Patch-v0.8.3.zip
cd BCI-Orbital-PyQt6-v0.8.3 || exit 1
bash scripts/install.sh
orbital storage
orbital
```

The installer runs all unit tests and an offscreen PyQt6 smoke test **on Kali before installing**. It preserves the previous launcher and installs into a **new** `~/.local/opt/bci-orbital-gui/0.8.3` directory. It does not modify any systemd services or forensic evidence. `SHA256SUMS` is provided only for optional review; integrity verification remains required for security evidence and for importing the original trained model.

## Separate root-only optional safeguard

These two actions are distinct; `--diagnose` is read-only and works without root (though root may see more logs):

```bash
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
bash scripts/packet-quota-guard.sh --diagnose
# Only if you explicitly wish to stop the EXIT 3 restart loop:
sudo bash scripts/packet-quota-guard.sh --install
```

`--install` requires typing `INSTALL-QUOTA-GUARD` directly in a terminal. It creates `/etc/systemd/system/bci-orbital-dynamic.service.d/90-bci-quota-hold.conf` **IF AND ONLY IF** the installed unit matches the known v0.4.1 collector and the drop-in does not already exist. It then reloads systemd but **does not start or restart the service**. It does not solve the ~512 MiB storage limit; that needs a separately reviewed archival/segment/retention strategy. Do not clear the restart limit or restart until quota is resolved.

## Verification and limitations

- Local static Python compile and 46 unit tests: PASS.
- Shell syntax tests: PASS.
- Original globe asset matches v0.8.2 byte-for-byte.
- PyQt6 not available in the artifact build environment; **graphical rendering must pass the included on-host smoke test**. No claim of live Kali integration is made until you run the installer.
- Privileged systemd drop-in installation has not been executed on your machine; optional approval is required.
- Original unpromoted model is **not** automatically imported or activated.
- No model training, live inference, baseline approval or containment is authorized.

## Review artifacts

`PATCH-v0.8.2-to-v0.8.3.diff` is a human-reviewable unified text diff. `SHA256SUMS` contains optional hashes for supplied files. The release ZIP checksum is provided separately and is *not* required to install.

**Developer Seal:** `CJB-DEV-2026`
