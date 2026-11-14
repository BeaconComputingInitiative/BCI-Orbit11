#!/usr/bin/env bash
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Group 6 sensor integration: proceed IF AND ONLY IF prior gates pass.
set -euo pipefail
umask 077
[[ "$(id -un)" == 'bci' ]] || { echo 'HOLD: must run as bci user'; exit 3; }
EXE="$HOME/.local/bin/bci-orbital-expansion"
OLD="$HOME/.local/opt/bci-orbital-v2/0.1.0"
NEURAL="$HOME/.local/opt/bci-orbital-neural/0.2.0"
[[ -x "$EXE" && -f "$OLD/SHA256SUMS" && -f "$NEURAL/SHA256SUMS" ]] || {
  echo 'HOLD: required installed source missing'; exit 3;
}
(cd "$OLD" && sha256sum -c SHA256SUMS >/dev/null) || { echo 'HOLD: Orbital integrity'; exit 3; }
(cd "$NEURAL" && sha256sum -c SHA256SUMS >/dev/null) || { echo 'HOLD: Neural integrity'; exit 3; }
STATE="$HOME/.local/state/bci-orbital-expansion-v0.3.0"
mkdir -p "$STATE"; chmod 700 "$STATE"
RUN=$(mktemp -d "$STATE/group6-XXXXXXXX")
chmod 700 "$RUN"
echo "=== GROUP 6 / STEP 1: CONTEXT + CAPABILITIES ==="
"$EXE" doctor --output "$RUN/capabilities.json"
"$EXE" context --output "$RUN/context.json"
echo "=== GROUP 6 / STEP 2: REAL INTERFACE RATE ==="
"$EXE" throughput --seconds 2 --output "$RUN/throughput.json"
echo "=== GROUP 6 / STEP 3: VERIFIED FULL FEATURE WINDOW ==="
"$EXE" capture-window --orbital-release "$OLD" --neural-release "$NEURAL" --seconds 2 \
    --output "$RUN/live-window.jsonl"
echo "=== GROUP 6 / STEP 4: VERIFY + RECORD MANIFEST ==="
for NAME in capabilities.json context.json throughput.json live-window.jsonl; do
  "$EXE" verify "$RUN/$NAME" >/dev/null || { echo 'HOLD: failed verification'; exit 3; }
done
(cd "$RUN" && sha256sum *.json *.jsonl > BCI-GROUP6-SHA256SUMS)
(cd "$RUN" && sha256sum -c BCI-GROUP6-SHA256SUMS)
sha256sum "$RUN/BCI-GROUP6-SHA256SUMS"
printf 'BEACON COMPUTING INITIATIVE\nDeveloper Seal: CJB-DEV-2026\n'
echo "PASS: GROUP 6 VERIFIED — $RUN"
echo 'No privileged collectors, model promotion, or containment enabled.'
