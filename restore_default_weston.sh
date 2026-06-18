#!/bin/sh
set +e

QT_ROOT="${QT_ROOT:-/userdata/qt5}"
LOG_DIR="$QT_ROOT/kiosk_launcher_logs"
RUN_ID="$(date '+%Y%m%d_%H%M%S')"
LOG_FILE="$LOG_DIR/restore_default_weston_$RUN_ID.log"
LATEST_LOG="$LOG_DIR/restore_default_weston_latest.log"

mkdir -p "$LOG_DIR"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

snapshot_procs() {
  label="$1"
  log "$label"
  for proc in /proc/[0-9]*; do
    comm="$(cat "$proc/comm" 2>/dev/null)"
    case "$comm" in
      weston|qmlscene|weston-terminal|python3|adbd)
        echo "${proc#/proc/}:$comm" | tee -a "$LOG_FILE"
        tr '\0' ' ' < "$proc/cmdline" 2>/dev/null | tee -a "$LOG_FILE"
        echo | tee -a "$LOG_FILE"
        ;;
    esac
  done
}

kill_by_comm() {
  name="$1"
  for proc in /proc/[0-9]*; do
    [ -r "$proc/comm" ] || continue
    pid="${proc#/proc/}"
    [ "$pid" = "$$" ] && continue
    [ "$(cat "$proc/comm" 2>/dev/null)" = "$name" ] && kill "$pid" 2>/dev/null
  done
}

kill_python_target() {
  target="$1"
  for proc in /proc/[0-9]*; do
    [ -r "$proc/comm" ] || continue
    pid="${proc#/proc/}"
    [ "$pid" = "$$" ] && continue
    [ "$(cat "$proc/comm" 2>/dev/null)" = "python3" ] || continue
    cmdline="$(tr '\0' ' ' < "$proc/cmdline" 2>/dev/null)"
    echo "$cmdline" | grep -q "$target" && kill "$pid" 2>/dev/null
  done
}

drm_status() {
  log "DRM status"
  for status in /sys/class/drm/card*-*/status; do
    echo "=== $status ===" | tee -a "$LOG_FILE"
    cat "$status" 2>/dev/null | tee -a "$LOG_FILE"
  done
}

log "V2.5.15 restore_default_weston begin"
snapshot_procs "processes before restore"

log "Stopping QML and terminal clients"
kill_by_comm qmlscene
kill_python_target "terminal_kiosk.py"
kill_by_comm weston-terminal
sleep 2

log "Stopping userdata Weston"
cp /tmp/weston.log "$LOG_DIR/weston_before_restore_$RUN_ID.log" 2>/dev/null || true
pids="$(pidof weston 2>/dev/null || true)"
[ -n "$pids" ] && kill $pids 2>/dev/null
sleep 2
pids="$(pidof weston 2>/dev/null || true)"
[ -n "$pids" ] && kill -9 $pids 2>/dev/null
rm -f /run/wayland-0 /run/wayland-0.lock

log "Starting default Weston through /etc/init.d/S03weston"
/etc/init.d/S03weston start >> "$LOG_FILE" 2>&1
sleep 6

snapshot_procs "processes after restore"
drm_status
log "tail /tmp/weston.log"
tail -160 /tmp/weston.log 2>/dev/null | tee -a "$LOG_FILE"

if command -v weston-info >/dev/null 2>&1; then
  XDG_RUNTIME_DIR=/run WAYLAND_DISPLAY=wayland-0 timeout 8 weston-info > "$LOG_DIR/weston_info_default_$RUN_ID.txt" 2>&1
fi

cp "$LOG_FILE" "$LATEST_LOG" 2>/dev/null || true
log "V2.5.15 restore_default_weston complete"
exit 0
