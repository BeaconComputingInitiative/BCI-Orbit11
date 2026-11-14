#!/usr/bin/env bash
# BEACON COMPUTING INITIATIVE | Orbital Cyber Defense
# Developer Seal: CJB-DEV-2026
# File SHA-256: see SHA256SUMS
# Installation succeeds IF AND ONLY IF all payload digests match and no existing
# version/service files would be overwritten. Evidence is never deleted.
set -euo pipefail
umask 077
usage(){ echo 'Usage: bash scripts/install.sh --user|--system [--activate]'; }
MODE=''; ACTIVATE=0
for arg in "$@"; do
  case "$arg" in
    --user) [[ -z "$MODE" ]] || { usage; exit 2; }; MODE=user ;;
    --system) [[ -z "$MODE" ]] || { usage; exit 2; }; MODE=system ;;
    --activate) ACTIVATE=1 ;;
    *) usage; exit 2 ;;
  esac
done
[[ -n "$MODE" ]] || { usage; exit 2; }
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
command -v sha256sum >/dev/null || { echo 'HOLD: sha256sum unavailable' >&2; exit 3; }
command -v python3 >/dev/null || { echo 'HOLD: python3 unavailable' >&2; exit 3; }
(cd "$SRC" && sha256sum -c SHA256SUMS) || { echo 'HOLD: release integrity check failed' >&2; exit 3; }
[[ $MODE != user || $EUID -ne 0 ]] || { echo 'HOLD: use --system under sudo; --user must run as target non-root account' >&2; exit 3; }
[[ $MODE != system || $EUID -eq 0 ]] || { echo 'HOLD: --system requires root' >&2; exit 3; }
if [[ $MODE == user ]]; then
  DEST="$HOME/.local/opt/bci-orbital-v2/0.1.0"
  LAUNCHER="$HOME/.local/bin/bci-orbital-v2"
  UNIT="$HOME/.config/systemd/user/bci-orbital-v2.service"
  UNIT_SRC="$SRC/systemd/bci-orbital-v2.user.service"
  STATE="$HOME/.local/state/bci-orbital-v2"
else
  DEST='/opt/bci-orbital-v2/releases/0.1.0'
  LAUNCHER='/usr/local/bin/bci-orbital-v2-system'
  UNIT='/etc/systemd/system/bci-orbital-v2.service'
  UNIT_SRC="$SRC/systemd/bci-orbital-v2.system.service"
  STATE='/var/lib/bci-orbital-v2'
fi
# Never overwrite an older or independently maintained component.
for path in "$DEST" "$LAUNCHER" "$UNIT"; do
  [[ ! -e "$path" && ! -L "$path" ]] || { echo "HOLD: path already exists: $path" >&2; exit 3; }
done
[[ ! -L "$STATE" ]] || { echo "HOLD: refusing symlink state directory: $STATE" >&2; exit 3; }
mkdir -p "$(dirname "$DEST")" "$(dirname "$LAUNCHER")" "$(dirname "$UNIT")" "$STATE"
chmod 700 "$STATE"
STAGE="$(mktemp -d "$(dirname "$DEST")/.bci-orbital-stage.XXXXXX")"
cleanup(){ if [[ -n "${STAGE:-}" && -d "$STAGE" ]]; then rm -rf -- "$STAGE"; fi; }
trap cleanup EXIT
cp -a "$SRC/." "$STAGE/"
(cd "$STAGE" && sha256sum -c SHA256SUMS >/dev/null) || {
  echo 'HOLD: staged release verification failed' >&2; exit 3;
}
# Validate code before installation; no network downloads or pip invocation.
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$STAGE/src" python3 -B -m bci_orbital --help >/dev/null
# Atomic promotion of the versioned directory.
mv -- "$STAGE" "$DEST"
STAGE=''
if [[ $MODE == user ]]; then
  cat > "$LAUNCHER" <<WRAPPER
#!/usr/bin/env bash
# BEACON COMPUTING INITIATIVE | Orbital Cyber Defense
# Developer Seal: CJB-DEV-2026
# File SHA-256: recorded in INSTALL-SHA256SUMS
export PYTHONPATH='$DEST/src'
exec /usr/bin/python3 -m bci_orbital "\$@"
WRAPPER
else
  cat > "$LAUNCHER" <<'WRAPPER'
#!/usr/bin/env bash
# BEACON COMPUTING INITIATIVE | Orbital Cyber Defense
# Developer Seal: CJB-DEV-2026
# File SHA-256: recorded in INSTALL-SHA256SUMS
export PYTHONPATH=/opt/bci-orbital-v2/releases/0.1.0/src
export BCI_ORBITAL_HOME=/var/lib/bci-orbital-v2
exec /usr/bin/python3 -m bci_orbital "$@"
WRAPPER
fi
chmod 700 "$LAUNCHER"
cp -- "$UNIT_SRC" "$UNIT"
chmod 644 "$UNIT"
( cd "$(dirname "$LAUNCHER")" && sha256sum "$(basename "$LAUNCHER")" ) > "$STATE/INSTALL-SHA256SUMS"
(cd "$(dirname "$UNIT")" && sha256sum "$(basename "$UNIT")") >> "$STATE/INSTALL-SHA256SUMS"
chmod 600 "$STATE/INSTALL-SHA256SUMS"
if [[ $MODE == user ]]; then
  systemctl --user daemon-reload 2>/dev/null || echo 'NOTICE: user systemd unavailable; use launcher directly'
else
  systemctl daemon-reload
fi
echo "STAGED: $MODE installation at $DEST"
echo "EVIDENCE: $STATE (never cleared by installer)"
if (( ACTIVATE )); then
  if systemctl is-active --quiet bci-orbital.service 2>/dev/null; then
    echo 'HOLD: legacy bci-orbital.service is active; new service NOT activated' >&2
    exit 3
  fi
  if [[ $MODE == user ]]; then
    systemctl --user enable --now bci-orbital-v2.service
  else
    systemctl enable --now bci-orbital-v2.service
  fi
  echo 'ACTIVATED: isolated bci-orbital-v2.service'
else
  echo 'INACTIVE: explicitly add --activate only after reviewing the service.'
fi
