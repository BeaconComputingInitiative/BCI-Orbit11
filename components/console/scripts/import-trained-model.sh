#!/usr/bin/env bash
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# File SHA-256: SHA256SUMS
# Import existing trained neural artifacts IF AND ONLY IF all pinned hashes verify.
# Does NOT train, rewrite, promote, or change the old model or the monitoring system.
set -euo pipefail
umask 077
[[ "$(id -un)" == bci && "$HOME" == /home/bci ]] || {
  echo 'HOLD: Run as the bci user only.' >&2;exit 3;
}
R="/home/chance/BCI-Orbital-Neural-Bridge-v0.2.0"
B='group4-20261113T102207Z'
MODEL="$B-candidate-model.json"
SCORES="$B-shadow-scores.json"
MD='493ba54a8edb0fed347994dc41f5ee682156527f13e717a3d366ae80bc3cf4b0'
SD='79e1675118844c3da4c18958f5d29d7a4543fc21c945b6bac75dd8fc9716882f'
DST="$HOME/.local/state/bci-orbital-ai-v0.8.0"
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$HERE"; sha256sum -c SHA256SUMS >/dev/null
printf 'BEACON COMPUTING INITIATIVE\nDeveloper Seal: CJB-DEV-2026\n'
echo '=== 1/4 VERIFY ORIGINAL ARTIFACTS — READ ONLY ==='
sudo -u chance test -f "$R/$MODEL"
sudo -u chance test ! -L "$R/$MODEL"
sudo -u chance test -f "$R/$SCORES"
sudo -u chance test ! -L "$R/$SCORES"
sudo -u chance bash -c 'cd "$1" && sha256sum -c -- "$2.sha256" "$3.sha256"' bash "$R" "$MODEL" "$SCORES"
read -r ACTUAL_MODEL _ < <(sudo sha256sum "$R/$MODEL")
read -r ACTUAL_SCORE _ < <(sudo sha256sum "$R/$SCORES")
[[ "$ACTUAL_MODEL" == "$MD" && "$ACTUAL_SCORE" == "$SD" ]] || {
  echo 'HOLD: Artifacts are not the original model and score report.' >&2;exit 3;
}
echo '=== 2/4 CREATE PRIVATE USER MODEL STORE ==='
if [[ -e "$DST" && ( -L "$DST" || ! -d "$DST" ) ]]; then echo 'HOLD: unsafe model path';exit 3;fi
install -d -m 700 "$DST"
[[ "$(stat -c %a "$DST")" == 700 && "$(stat -c %u "$DST")" == "$(id -u)" ]] || {
  echo 'HOLD: model store ownership/permissions invalid' >&2;exit 3;
}
[[ ! -e "$DST/artifacts" && ! -L "$DST/artifacts" ]] || {
  echo 'HOLD: existing imported model set is protected; do not overwrite' >&2;exit 3;
}
echo '=== 3/4 COPY VERIFIED DATA, NEVER REWRITE THE ORIGINAL ==='
TMP="$(mktemp -d "$DST/.stage-XXXXXXXX")"
trap 'rm -rf -- "$TMP"' EXIT
sudo install -o bci -g bci -m 600 "$R/$MODEL" "$TMP/legacy-model.json"
sudo install -o bci -g bci -m 600 "$R/$SCORES" "$TMP/legacy-shadow-scores.json"
[[ "$(sha256sum "$TMP/legacy-model.json" | awk '{print $1}')" == "$MD" && \
   "$(sha256sum "$TMP/legacy-shadow-scores.json" | awk '{print $1}')" == "$SD" ]] || {
  echo 'HOLD: copied data differ from original' >&2;exit 3;
}
echo '=== 4/4 VALIDATE MODEL LINKAGE AND ATOMICALLY PUBLISH ==='
PYTHONPATH="$HERE/src" python3 -B - "$TMP" <<'PY'
from pathlib import Path
import json,sys
from orbital_ai import CONTEXT,MODEL_SHA,SCORES_SHA,SEAL
r=Path(sys.argv[1]);m=json.loads((r/'legacy-model.json').read_text());s=json.loads((r/'legacy-shadow-scores.json').read_text())
assert m['context']==CONTEXT and m['model_state']=='candidate_unpromoted'
assert m['architecture']==[12,8,3,8,12] and m['developer_seal']==SEAL
assert s['model_sha256']==MODEL_SHA and len(s['outputs'])==610 and s['containment_authorized'] is False
print('PASS: Original neural model and 610-score report linkage')
PY
(
 cd "$TMP"
 sha256sum legacy-model.json > legacy-model.json.sha256
 sha256sum legacy-shadow-scores.json > legacy-shadow-scores.json.sha256
 sha256sum -c legacy-model.json.sha256
 sha256sum -c legacy-shadow-scores.json.sha256
 sha256sum legacy-model.json legacy-shadow-scores.json > SHA256SUMS
 sha256sum -c SHA256SUMS
 sha256sum SHA256SUMS > SHA256SUMS.sha256
)
# Publish the complete validated pair in one directory rename.
mv -- "$TMP" "$DST/artifacts"
echo 'PASS: Original Orbital neural checkpoint imported; no retraining or promotion.'
echo "Private model directory: $DST"
