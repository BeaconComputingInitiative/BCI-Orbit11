#!/usr/bin/env bash
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# SHA-256: repository SHA256SUMS
# Export succeeds IF AND ONLY IF source, destination and copy checks all pass.
# PRIVATE OFFLINE BACKUP ONLY. Never publish unreviewed datasets or telemetry.
set -Eeuo pipefail
umask 077
MODE=preview
DEST=''
SOURCES=()
usage() {
  echo 'Usage: bash scripts/export-migration.sh --destination DIR [--source DIR ...] [--apply]'
  echo 'Default: dry-run preview. --apply copies to a new private destination.'
}
while (( $# )); do
  case "$1" in
    --destination) shift; (( $# )) || { usage; exit 2; }; DEST="$1" ;;
    --source) shift; (( $# )) || { usage; exit 2; }; SOURCES+=("$1") ;;
    --apply) MODE=apply ;;
    --help|-h) usage; exit 0 ;;
    *) usage; exit 2 ;;
  esac
  shift
done
echo 'BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026'
echo "ORBIT11 private migration export: $MODE"
[[ "$EUID" -ne 0 && -n "$DEST" ]] || { usage; exit 3; }
command -v rsync >/dev/null && command -v sha256sum >/dev/null || {
  echo 'HOLD: rsync and sha256sum must be installed'; exit 3;
}
if (( ${#SOURCES[@]} == 0 )); then
  for candidate in "$HOME/ORBIT11" "$HOME/BCI/Projects/ORBIT11" "$HOME/BCI-Orbital-CyberDefense"; do
    [[ -d "$candidate" ]] && SOURCES+=("$candidate")
  done
fi
(( ${#SOURCES[@]} > 0 )) || {
  echo 'HOLD: no local roots found; pass --source explicitly'; exit 3;
}
DEST="$(realpath -m -- "$DEST")"
[[ "$DEST" != / && "$DEST" != "$HOME" ]] || { echo 'HOLD: unsafe destination'; exit 3; }
[[ ! -e "$DEST" && ! -L "$DEST" ]] || {
  echo 'HOLD: destination already exists; provide a new versioned path'; exit 3;
}
IDX=0
for source in "${SOURCES[@]}"; do
  [[ -d "$source" && ! -L "$source" ]] || { echo "HOLD: invalid root $source"; exit 3; }
  SRC="$(realpath -e -- "$source")"
  [[ "$SRC" != "$DEST" && "$SRC/" != "$DEST/"* && "$DEST/" != "$SRC/"* ]] || {
    echo "HOLD: overlapping source/destination: $SRC"; exit 3;
  }
  printf -v SLOT '%02d-%s' "$IDX" "$(basename -- "$SRC")"
  TARGET="$DEST/roots/$SLOT"
  printf 'Source: %s\nTarget: %s\n' "$SRC" "$TARGET"
  if [[ "$MODE" == preview ]]; then
    rsync -aHn --no-links --stats -- "$SRC/" "$TARGET/"
  else
    mkdir -p -- "$TARGET"
    rsync -aH --no-links -- "$SRC/" "$TARGET/"
    DIFF="$(rsync -aHnc --no-links --out-format='%n' -- "$SRC/" "$TARGET/")"
    [[ -z "$DIFF" ]] || {
      printf 'HOLD: source changed during backup or mismatch:\n%s\n' "$DIFF"; exit 3;
    }
  fi
  IDX=$((IDX+1))
done
if [[ "$MODE" == preview ]]; then
  echo 'PREVIEW COMPLETE: no files were copied.'
  exit 0
fi
( cd "$DEST" && find roots -type f -print0 | sort -z | xargs -0 -r sha256sum > SHA256SUMS )
( cd "$DEST" && sha256sum --check --strict SHA256SUMS >/dev/null ) || {
  echo 'HOLD: copied payload did not match SHA-256 manifest'; exit 3;
}
printf '%s\n' 'BACKUP VERIFIED: no source files removed, modified or published.' \
  "Destination: $DEST" 'Record manifest checksum in a separate trusted location:'
sha256sum "$DEST/SHA256SUMS"
