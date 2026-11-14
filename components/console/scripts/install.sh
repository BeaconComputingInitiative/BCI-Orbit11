#!/usr/bin/env bash
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Orbital Native AI v0.8.3 — checksum-optional installer.
# Install IF AND ONLY IF user, dependency, GUI-test, path, and launcher gates pass.
# Integrity metadata can be generated independently; no hash/sidecar required.
set -euo pipefail
umask 077

VER=0.8.3
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
BASE="$HOME/.local/opt/bci-orbital-gui"
DEST="$BASE/$VER"
BIN="$HOME/.local/bin/orbital"
SEAL=CJB-DEV-2026

printf '%s\n' 'BEACON COMPUTING INITIATIVE' "Developer Seal: $SEAL"
echo '=== 1/4 SOURCE AND TEST CHECKS (NO HASH REQUIRED) ==='
[[ "$(id -un)" == 'bci' && "$HOME" == '/home/bci' && "$(id -u)" -ne 0 ]] || {
  echo 'HOLD: Run as the normal bci account, never as root.' >&2;exit 3;
}
[[ -d "$ROOT/src" && -f "$ROOT/src/orbital_cli.py" && -f "$ROOT/assets/orbital-globe-exact.png" ]] || {
  echo 'HOLD: Incomplete release source/assets.' >&2;exit 3;
}
cd "$ROOT"
python3 -B -m unittest discover -s tests -v

echo '=== 2/4 PYQT6 DEPENDENCIES ==='
/usr/bin/python3 - <<'PYQT'
from PyQt6.QtCore import PYQT_VERSION_STR
from PyQt6.QtWidgets import QApplication
print('PASS: PyQt6 '+PYQT_VERSION_STR)
PYQT

echo '=== 3/4 GUI SMOKE TEST AND SAFE BACKUP ==='
QT_QPA_PLATFORM=offscreen /usr/bin/python3 -B "$ROOT/scripts/gui_smoke.py"
[[ ! -e "$DEST" && ! -L "$DEST" ]] || {
  echo 'HOLD: This version is already installed; refusing overwrite.' >&2;exit 3;
}
[[ ! -L "$HOME/.local" && ! -L "$HOME/.local/bin" && ! -L "$BASE" ]] || {
  echo 'HOLD: Symlinked installation directory is not allowed.' >&2;exit 3;
}
install -d -m 700 "$BASE" "$HOME/.local/bin"
if [[ -e "$BIN" || -L "$BIN" ]]; then
  [[ -f "$BIN" && ! -L "$BIN" ]] || {
    echo 'HOLD: Existing orbital launcher must be a regular file.' >&2;exit 3;
  }
  (grep -Fq 'bci-orbital-gui/0.7.0' "$BIN" ||
   grep -Fq 'bci-orbital-gui/0.7.1' "$BIN" ||
   grep -Fq 'bci-orbital-gui/0.8.0' "$BIN" ||
   grep -Fq 'bci-orbital-gui/0.8.1' "$BIN" ||
   grep -Fq 'bci-orbital-gui/0.8.2' "$BIN") || {
    echo 'HOLD: Existing launcher is not recognized as an Orbital GUI release.' >&2;exit 3;
  }
  BACKUP="$BIN.pre-v0.8.3.$(date -u +%Y%m%dT%H%M%SZ)"
  cp -p -- "$BIN" "$BACKUP"
  echo "Backup: $BACKUP"
fi

# Create the new release in a private, uniquely named staging directory.
STAGE="$(mktemp -d "$BASE/.stage-083-XXXXXXXX")"
TMP=""
cleanup() {
  if [[ -n "$TMP" && -e "$TMP" ]]; then rm -f -- "$TMP";fi
  if [[ -n "$STAGE" && -d "$STAGE" ]]; then rm -rf -- "$STAGE";fi
}
trap cleanup EXIT
cp -a -- README.md src scripts tests assets "$STAGE/"
if [[ -f SHA256SUMS ]]; then cp -a -- SHA256SUMS "$STAGE/";fi
[[ -f "$STAGE/src/orbital_gui.py" && -f "$STAGE/assets/orbital-globe-exact.png" ]] || {
  echo 'HOLD: Staged release incomplete.' >&2;exit 3;
}
mv -- "$STAGE" "$DEST"
STAGE=''

# Atomic launcher replacement; existing services, models and evidence untouched.
TMP="$(mktemp "$HOME/.local/bin/.orbital-083-XXXXXXXX")"
cat > "$TMP" <<'LAUNCH'
#!/usr/bin/env bash
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Orbital GUI native AI v0.8.3 — no launcher checksum prerequisite.
# Execute IF AND ONLY IF installed source is present.
set -euo pipefail
SRC="$HOME/.local/opt/bci-orbital-gui/0.8.3/src"
[[ -f "$SRC/orbital_cli.py" && -f "$SRC/orbital_backend.py" ]] || {
  echo 'HOLD: GUI source is missing.' >&2;exit 3;
}
exec /usr/bin/python3 -B "$SRC/orbital_cli.py" "$@"
LAUNCH
chmod 700 "$TMP"
[[ -s "$TMP" ]] || exit 3
mv -f -- "$TMP" "$BIN"
TMP=''

if [[ -f "$HOME/.zshrc" ]] && grep -Fxq 'alias orbital="$HOME/.local/bin/orbital"' "$HOME/.zshrc"; then
  echo 'PASS: zsh orbital alias unchanged'
else
  echo 'Note: launcher available as ~/.local/bin/orbital; optionally add it to PATH.'
fi

echo '=== 4/4 POST-INSTALL FUNCTIONAL ACCEPTANCE ==='
"$BIN" train status
"$BIN" ai 'what are your baselines?'
"$BIN" baselines
echo 'PASS: Orbital Native AI v0.8.3 installed without any hash requirement.'
echo 'Original GUI backups retained. No monitoring service or security policy changed.'
echo 'Training, model promotion and containment remain disabled without authorization.'
echo 'Existing learned model import remains separately authorization-gated.'
