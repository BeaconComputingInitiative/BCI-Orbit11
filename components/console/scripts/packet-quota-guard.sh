#!/usr/bin/env bash
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# P0 packet restart-loop safeguard for original v0.4.1 collector
# Install IF AND ONLY IF original unit and operator approval are verified.
# File digest: optional manifest in release; no hash prerequisite.
set -euo pipefail
umask 077
UNIT=bci-orbital-dynamic.service
DIR=/etc/systemd/system/bci-orbital-dynamic.service.d
FILE="$DIR/90-bci-quota-hold.conf"
case "${1:---diagnose}" in
  --diagnose)
    echo 'BEACON COMPUTING INITIATIVE'
    echo 'Developer Seal: CJB-DEV-2026'
    echo '=== PACKET COLLECTOR DIAGNOSTIC (READ ONLY) ==='
    SYSTEMD_PAGER=cat systemctl show "$UNIT" \
      -p FragmentPath -p ActiveState -p SubState -p Result \
      -p ExecMainStatus -p NRestarts -p Restart -p RestartPreventExitStatus \
      -p StateDirectory --no-pager || true
    echo '=== RECENT COLLECTOR LOGS ==='
    journalctl -u "$UNIT" -n 16 --no-pager -l || true
    echo '=== EVIDENCE USAGE (REAL STATE DIRECTORY) ==='
    if [[ $EUID -eq 0 ]]; then
      du -sh /var/lib/private/bci-orbital-dynamic-v0.4.0 2>/dev/null || true
    else
      echo 'Run sudo bash ... --diagnose for privileged state directory size.'
    fi
    df -h /var/lib || true
    exit 0
    ;;
  --install)
    [[ $EUID -eq 0 ]] || { echo 'HOLD: sudo/root required for systemd drop-in';exit 3; }
    echo 'BEACON COMPUTING INITIATIVE'
    echo 'Developer Seal: CJB-DEV-2026'
    [[ -c /dev/tty ]] || { echo 'HOLD: interactive TTY required';exit 3; }
    echo 'This only prevents systemd from restarting on collector exit code 3 (HOLD).'
    echo 'It does NOT resume collection, enlarge storage, or move/delete evidence.'
    printf 'Type INSTALL-QUOTA-GUARD to authorize: ' >/dev/tty
    IFS= read -r ANSWER </dev/tty
    [[ "$ANSWER" == 'INSTALL-QUOTA-GUARD' ]] || { echo 'HOLD: not approved';exit 3; }
    # Confirm unit identity before changing service manager policy.
    START="$(systemctl show "$UNIT" -p ExecStart --value --no-pager)"
    STATE="$(systemctl show "$UNIT" -p StateDirectory --value --no-pager)"
    [[ "$START" == *'/opt/bci-orbital-dynamic/0.4.1/scripts/runner.py run'* ]] || {
      echo 'HOLD: unknown collector executable; no changes';exit 3;
    }
    [[ "$STATE" == 'bci-orbital-dynamic-v0.4.0' ]] || {
      echo 'HOLD: unexpected evidence state directory; no changes';exit 3;
    }
    [[ ! -e "$FILE" && ! -L "$FILE" ]] || {
      echo 'HOLD: policy drop-in already exists; refusing replacement';exit 3;
    }
    [[ ! -L "$DIR" ]] || { echo 'HOLD: symlinked systemd directory';exit 3; }
    install -d -m 0755 -- "$DIR"
    TMP="$(mktemp "$DIR/.bci-quota-guard.XXXXXXXX")"
    cleanup(){ [[ -z "${TMP:-}" || ! -e "$TMP" ]] || rm -f -- "$TMP"; }
    trap cleanup EXIT
    cat >"$TMP" <<'DROPIN'
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# On an explicit security/storage HOLD (exit 3), prevent an endless restart loop.
# This does not alter evidence, and does not authorize capture restart.
[Service]
RestartPreventExitStatus=3
DROPIN
    chmod 0644 "$TMP"
    mv -n -- "$TMP" "$FILE"
    TMP=''
    systemctl daemon-reload
    echo 'PASS: HOLD exit code 3 is restart-inhibited for this collector.'
    echo 'Collector deliberately remains stopped/failed until storage lifecycle is repaired.'
    echo 'Verify: systemctl show bci-orbital-dynamic.service -p RestartPreventExitStatus'
    ;;
  *) echo 'Usage: bash packet-quota-guard.sh [--diagnose | --install]' >&2;exit 2;;
esac
