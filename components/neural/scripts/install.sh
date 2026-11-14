#!/usr/bin/env bash
# BEACON COMPUTING INITIATIVE | Orbital Neural Core Installer
# Developer Seal: CJB-DEV-2026
# File SHA-256: SHA256SUMS
# Installation occurs IF AND ONLY IF release hash checks and all path gates pass.
set -euo pipefail
umask 077
[[ $# -eq 1 && "$1" == '--user' ]] || { echo 'Usage: bash scripts/install.sh --user' >&2; exit 2; }
[[ $EUID -ne 0 ]] || { echo 'HOLD: install as the BCI user, not root' >&2; exit 3; }
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
command -v sha256sum >/dev/null || { echo 'HOLD: sha256sum missing' >&2; exit 3; }
command -v python3 >/dev/null || { echo 'HOLD: python3 missing' >&2; exit 3; }
(cd "$SRC" && sha256sum -c SHA256SUMS) || { echo 'HOLD: invalid release manifest' >&2; exit 3; }
DEST="$HOME/.local/opt/bci-orbital-neural/0.2.0"
BIN="$HOME/.local/bin/bci-orbital-neural"
SERVICE="$HOME/.config/systemd/user/bci-orbital-neural.service"
TIMER="$HOME/.config/systemd/user/bci-orbital-neural.timer"
STATE="$HOME/.local/state/bci-orbital-neural-v0.2.0"
for p in "$DEST" "$BIN" "$SERVICE" "$TIMER"; do
  [[ ! -e "$p" && ! -L "$p" ]] || { echo "HOLD: refusing overwrite: $p" >&2; exit 3; }
done
[[ ! -L "$STATE" ]] || { echo 'HOLD: state directory is symlink' >&2; exit 3; }
mkdir -p "$(dirname "$DEST")" "$(dirname "$BIN")" "$(dirname "$SERVICE")" "$STATE"
chmod 700 "$STATE"
STAGE="$(mktemp -d "$(dirname "$DEST")/.neural-stage.XXXXXX")"
trap 'if [[ -n "${STAGE:-}" && -d "$STAGE" ]]; then rm -rf -- "$STAGE"; fi' EXIT
cp -a "$SRC/." "$STAGE/"
(cd "$STAGE" && sha256sum -c SHA256SUMS >/dev/null)
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$STAGE/src" python3 -B -m bci_neural --help >/dev/null
mv -- "$STAGE" "$DEST"
STAGE=''
cat > "$BIN" <<SCRIPT
#!/usr/bin/env bash
# BEACON COMPUTING INITIATIVE | Orbital Neural Core Launcher
# Developer Seal: CJB-DEV-2026
# File SHA-256: $STATE/INSTALL-SHA256SUMS
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH='$DEST/src'
exec /usr/bin/python3 -B -m bci_neural "\$@"
SCRIPT
chmod 700 "$BIN"
cp "$DEST/systemd/bci-orbital-neural.user.service" "$SERVICE"
cp "$DEST/systemd/bci-orbital-neural.user.timer" "$TIMER"
chmod 600 "$SERVICE" "$TIMER"
sha256sum "$BIN" "$SERVICE" "$TIMER" > "$STATE/INSTALL-SHA256SUMS"
chmod 600 "$STATE/INSTALL-SHA256SUMS"
systemctl --user daemon-reload 2>/dev/null || true
printf '%s\n' 'BEACON COMPUTING INITIATIVE' 'Developer Seal: CJB-DEV-2026' \
  "INSTALLED: $DEST" "SHA256 MANIFEST: $DEST/SHA256SUMS" \
  'NEURAL CORE: isolated shadow mode, no containment or baseline authority' \
  'TIMER: installed but NOT enabled (explicit opt-in required)'
