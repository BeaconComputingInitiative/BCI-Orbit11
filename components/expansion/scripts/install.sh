#!/usr/bin/env bash
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Installer IF AND ONLY IF release hashes and source tests pass.
set -euo pipefail
umask 077
[[ "${1:-}" == '--user' ]] || { echo 'HOLD: use --user'; exit 3; }
[[ $(id -un) == 'bci' ]] || { echo 'HOLD: run under bci account'; exit 3; }
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
cd "$ROOT"
sha256sum -c SHA256SUMS >/dev/null
PYTHONPATH=src python3 -B -m unittest discover -s tests -v
DEST="$HOME/.local/opt/bci-orbital-expansion/0.3.0"
[[ ! -e "$DEST" && ! -L "$DEST" ]] || { echo 'HOLD: version already installed; no overwrite'; exit 3; }
mkdir -p "$(dirname "$DEST")" "$HOME/.local/bin"
cp -a "$ROOT" "$DEST"
# Post-copy manifest verification; preserve the original version independent of working tree.
(cd "$DEST" && sha256sum -c SHA256SUMS >/dev/null)
LAUNCH="$HOME/.local/bin/bci-orbital-expansion"
[[ ! -e "$LAUNCH" && ! -L "$LAUNCH" ]] || { echo 'HOLD: launcher already exists; release is still staged'; exit 3; }
cat > "$LAUNCH" <<'SCRIPT'
#!/usr/bin/env bash
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Execute IF AND ONLY IF the installed source manifest verifies.
set -euo pipefail
RELEASE="$HOME/.local/opt/bci-orbital-expansion/0.3.0"
(cd "$RELEASE" && sha256sum -c SHA256SUMS >/dev/null) || { echo 'HOLD: source integrity check failed' >&2; exit 3; }
exec env PYTHONPATH="$RELEASE/src" /usr/bin/python3 -B -m bci_orbital_expansion "$@"
SCRIPT
chmod 700 "$LAUNCH"
sha256sum "$LAUNCH"
echo 'PASS: Isolated expansion installed; no systemd changes, no privileged sensors started.'
