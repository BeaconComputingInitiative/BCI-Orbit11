#!/usr/bin/env bash
# BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026
# SHA-256: see repository SHA256SUMS
# Restore IF AND ONLY IF the private backup manifest and path gates pass.
# Never overwrite live ORBIT11 data, promote models, or enable services.
set -Eeuo pipefail
umask 077
MODE=preview
BACKUP=''
DEST="$HOME/BCI/Restored-ORBIT11"
ANCHOR=''
usage(){
  echo 'Usage: bash scripts/restore-migration.sh --backup DIR [--destination DIR] [--expected-manifest-sha256 HEX] [--apply]'
}
while (( $# )); do
  case "$1" in
    --backup) shift; (( $# )) || { usage; exit 2; }; BACKUP="$1" ;;
    --destination) shift; (( $# )) || { usage; exit 2; }; DEST="$1" ;;
    --expected-manifest-sha256) shift; (( $# )) || { usage; exit 2; }; ANCHOR="$1" ;;
    --apply) MODE=apply ;;
    -h|--help) usage; exit 0 ;;
    *) usage; exit 2 ;;
  esac
  shift
done
echo 'BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026'
echo "ORBIT11 private migration restore: $MODE"
[[ "$EUID" -ne 0 && -n "$BACKUP" ]] || { usage; exit 3; }
command -v rsync >/dev/null && command -v python3 >/dev/null || {
  echo 'HOLD: rsync and python3 required'; exit 3;
}
BACKUP="$(realpath -e -- "$BACKUP")"
DEST="$(realpath -m -- "$DEST")"
[[ -d "$BACKUP/roots" && -f "$BACKUP/SHA256SUMS" ]] || {
  echo 'HOLD: incomplete backup directory'; exit 3;
}
[[ "$DEST" != / && "$DEST" != "$HOME" && "$DEST" != "$BACKUP" &&
  "$DEST/" != "$BACKUP/"* && "$BACKUP/" != "$DEST/"* ]] || {
  echo 'HOLD: unsafe destination / overlap'; exit 3;
}
[[ ! -e "$DEST" && ! -L "$DEST" ]] || {
  echo 'HOLD: restore destination must not exist'; exit 3;
}
python3 - "$BACKUP" "$ANCHOR" <<'PYVERIFY'
# BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026
import hashlib
import pathlib
import re
import stat
import sys

root = pathlib.Path(sys.argv[1])
anchor = sys.argv[2]
manifest = root / 'SHA256SUMS'
raw = manifest.read_bytes()
if anchor:
    if re.fullmatch(r'[0-9a-fA-F]{64}', anchor) is None:
        raise SystemExit('HOLD: invalid anchor SHA-256')
    if hashlib.sha256(raw).hexdigest() != anchor.lower():
        raise SystemExit('HOLD: external manifest anchor mismatch')
expected = {}
for line in raw.decode('utf-8').splitlines():
    if not line:
        continue
    match = re.fullmatch(r'([0-9a-f]{64})  (roots/.+)', line)
    if not match:
        raise SystemExit('HOLD: invalid backup manifest row')
    digest, relative = match.groups()
    path = pathlib.PurePosixPath(relative)
    if any(part in ('.', '..') for part in path.parts) or relative in expected:
        raise SystemExit('HOLD: unsafe or duplicate backup path')
    expected[relative] = digest
actual = set()
for path in (root / 'roots').rglob('*'):
    if path.is_symlink():
        raise SystemExit('HOLD: symlink in backup')
    if path.is_file():
        rel = path.relative_to(root).as_posix()
        actual.add(rel)
        if rel not in expected:
            raise SystemExit('HOLD: file absent from manifest: ' + rel)
        h = hashlib.sha256()
        with path.open('rb') as fh:
            for chunk in iter(lambda: fh.read(4 * 1024 * 1024), b''):
                h.update(chunk)
        if h.hexdigest() != expected[rel]:
            raise SystemExit('HOLD: bad payload checksum: ' + rel)
if actual != set(expected):
    raise SystemExit('HOLD: manifest contains unavailable files')
print('PASS: all ' + str(len(expected)) + ' regular backup files verified')
print('Manifest SHA-256: ' + hashlib.sha256(raw).hexdigest())
if not anchor:
    print('NOTICE: no independent anchor supplied; self-consistency verified only')
PYVERIFY
if [[ "$MODE" == preview ]]; then
  rsync -aHn --no-links --stats -- "$BACKUP/roots/" "$DEST/roots/"
  echo 'PREVIEW PASS: nothing restored or activated.'
  exit 0
fi
mkdir -p -- "$DEST/roots"
rsync -aH --no-links -- "$BACKUP/roots/" "$DEST/roots/"
DIFF="$(rsync -aHnc --no-links --out-format='%n' -- "$BACKUP/roots/" "$DEST/roots/")"
[[ -z "$DIFF" ]] || {
  printf 'HOLD: copied restore mismatch:\n%s\n' "$DIFF"; exit 3;
}
( cd "$DEST" && find roots -type f -print0 | sort -z | xargs -0 -r sha256sum > RESTORE-SHA256SUMS )
( cd "$DEST" && sha256sum --check --strict RESTORE-SHA256SUMS >/dev/null )
echo "RESTORE VERIFIED: $DEST/roots"
echo 'No live source paths overwritten; research assets require separate compatibility review.'
echo 'No monitoring, training, containment, or production service was activated.'
