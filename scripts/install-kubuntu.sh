#!/usr/bin/env bash
# BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026
# SHA-256: repository SHA256SUMS
# Install IF AND ONLY IF source, dependencies, tests and collision gates pass.
set -Eeuo pipefail
umask 077
MODE=audit
ROOT="$HOME/BCI/Projects/ORBIT11"
usage(){ echo 'Usage: bash scripts/install-kubuntu.sh --audit|--install [--source DIR]'; }
while (( $# )); do
  case "$1" in
    --audit) MODE=audit ;;
    --install) MODE=install ;;
    --source) shift; (( $# )) || { usage; exit 2; }; ROOT="$1" ;;
    -h|--help) usage; exit 0 ;;
    *) usage; exit 2 ;;
  esac
  shift
done
echo 'BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026'
echo "Kubuntu bootstrap: $MODE"
[[ "$EUID" -ne 0 ]] || { echo 'HOLD: do not run as root'; exit 3; }
# shellcheck disable=SC1091
source /etc/os-release
case " $ID $ID_LIKE " in *ubuntu*) : ;; *) echo 'HOLD: Ubuntu/Kubuntu required';exit 3;; esac
echo '=== 1/4: Source and prerequisites ==='
if [[ "$MODE" == install ]]; then
  sudo apt-get update
  sudo apt-get install -y --no-install-recommends git ca-certificates \
    python3 python3-venv python3-pyqt6 python3-pyqt6.qtsvg \
    rsync iproute2 util-linux nftables libgl1
  if [[ ! -e "$ROOT" ]]; then
    mkdir -p -- "$(dirname -- "$ROOT")"
    git clone --depth 1 https://github.com/BeaconComputingInitiative/BCI-Orbit11.git "$ROOT"
  fi
fi
[[ -d "$ROOT/.git" && -f "$ROOT/SHA256SUMS" ]] || {
  echo "HOLD: checkout absent: $ROOT"; exit 3;
}
ORIGIN="$(git -C "$ROOT" remote get-url origin)"
case "$ORIGIN" in
  https://github.com/BeaconComputingInitiative/BCI-Orbit11.git|git@github.com:BeaconComputingInitiative/BCI-Orbit11.git) : ;;
  *) echo "HOLD: unexpected origin: $ORIGIN"; exit 3 ;;
esac
COMMIT="$(git -C "$ROOT" rev-parse HEAD)"
echo '=== 2/4: Manifest, tests and offscreen GUI smoke ==='
(cd "$ROOT" && sha256sum -c --strict SHA256SUMS >/dev/null) || {
  echo 'HOLD: source SHA-256 mismatch'; exit 3;
}
if [[ "$MODE" == install ]]; then
  VENV="$HOME/.local/share/bci-orbit11/venv"
  [[ -x "$VENV/bin/python3" ]] || python3 -m venv --system-site-packages "$VENV"
  PY="$VENV/bin/python3"
else
  PY=python3
fi
(cd "$ROOT" && "$PY" -B scripts/check.py)
(cd "$ROOT" && env -u DISPLAY QT_QPA_PLATFORM=offscreen \
  QT_QPA_PLATFORMTHEME= QT_STYLE_OVERRIDE=Fusion "$PY" -B \
  components/console/scripts/gui_smoke.py)
if [[ "$MODE" == audit ]]; then
  echo 'AUDIT PASS; no changes made.'
  exit 0
fi
echo '=== 3/4: Unprivileged launchers ==='
BIN="$HOME/.local/bin"
APP="$HOME/.local/share/applications/org.beaconcomputing.orbit11.desktop"
STATE="$HOME/.local/state/bci-orbit11-installer"
[[ "$HOME" != *' '* && "$ROOT" != *' '* ]] || { echo 'HOLD: paths with spaces'; exit 3; }
for name in orbit11 orbit11-host orbit11-neural orbit11-expansion; do
  [[ ! -e "$BIN/$name" && ! -L "$BIN/$name" ]] || {
    echo "HOLD: launcher already exists: $BIN/$name"; exit 3;
  }
done
[[ ! -e "$APP" && ! -L "$APP" ]] || { echo 'HOLD: desktop entry exists'; exit 3; }
mkdir -p -- "$BIN" "$(dirname -- "$APP")" "$STATE"
chmod 700 "$STATE"
STAGE="$(mktemp -d "$STATE/.stage.XXXXXXXX")"
trap 'rm -rf -- "$STAGE"' EXIT
printf -v ROOT_Q '%q' "$ROOT"
printf -v PY_Q '%q' "$PY"
for name in orbit11 orbit11-host orbit11-neural orbit11-expansion; do
  case "$name" in
    orbit11) TARGET=console ;;
    orbit11-host) TARGET=host ;;
    orbit11-neural) TARGET=neural ;;
    orbit11-expansion) TARGET=expansion ;;
  esac
  cat > "$STAGE/$name" <<EOF
#!/usr/bin/env bash
# BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026
# SHA-256: ~/.local/state/bci-orbit11-installer/INSTALL-SHA256SUMS
set -euo pipefail
ROOT=$ROOT_Q
PY=$PY_Q
[[ -x "\$PY" && -d "\$ROOT/components" ]] || { echo 'HOLD: missing runtime' >&2; exit 3; }
case "$TARGET" in
  console) exec "\$PY" -B "\$ROOT/components/console/src/orbital_cli.py" gui "\$@" ;;
  host) exec env PYTHONPATH="\$ROOT/components/host/src" "\$PY" -B -m bci_orbital "\$@" ;;
  neural) exec env PYTHONPATH="\$ROOT/components/neural/src" "\$PY" -B -m bci_neural "\$@" ;;
  expansion) exec env PYTHONPATH="\$ROOT/components/expansion/src" "\$PY" -B -m bci_orbital_expansion "\$@" ;;
esac
EOF
  bash -n "$STAGE/$name"
done
cat > "$STAGE/orbit11.desktop" <<EOF
[Desktop Entry]
Type=Application
Version=1.0
Name=ORBIT11 (Research)
Comment=Beacon Computing Initiative - approval-gated security console
Exec=$BIN/orbit11
Icon=$ROOT/components/console/assets/orbital-globe-exact.png
Terminal=false
Categories=Development;System;
StartupNotify=true
EOF
for name in orbit11 orbit11-host orbit11-neural orbit11-expansion; do
  install -m 700 "$STAGE/$name" "$BIN/$name"
done
install -m 644 "$STAGE/orbit11.desktop" "$APP"
install -d -m 700 "$HOME/BCI/Private/ORBIT11"/{datasets,checkpoints,evidence,workspaces}
(cd "$BIN" && sha256sum orbit11 orbit11-host orbit11-neural orbit11-expansion) > "$STATE/INSTALL-SHA256SUMS"
sha256sum "$APP" >> "$STATE/INSTALL-SHA256SUMS"
printf '%s\n' "$COMMIT" > "$STATE/INSTALLED-COMMIT"
sha256sum "$STATE/INSTALLED-COMMIT" > "$STATE/INSTALLED-COMMIT.sha256"
chmod 600 "$STATE/"*
echo '=== 4/4: Post-install verification ==='
"$BIN/orbit11-host" --help >/dev/null
"$BIN/orbit11-neural" --help >/dev/null
"$BIN/orbit11-expansion" --help >/dev/null
(cd "$BIN" && sha256sum -c --strict "$STATE/INSTALL-SHA256SUMS" >/dev/null)
echo 'INSTALL PASS: committed host, neural, expansion and GUI accessible.'
echo "GUI: $BIN/orbit11"
echo "Launcher SHA-256 manifest: $STATE/INSTALL-SHA256SUMS"
echo 'Local-only datasets/checkpoints: NOT RESTORED.'
echo 'Monitoring, training and containment: NOT ENABLED.'
