#!/bin/sh
set +e

APP_DIR="${APP_DIR:-/userdata/smart_retail}"
QT_ROOT="${QT_ROOT:-/userdata/qt5}"
LOG_DIR="$QT_ROOT/kiosk_launcher_logs"
RUN_ID="$(date '+%Y%m%d_%H%M%S')"
LOG_FILE="$LOG_DIR/start_hdmi_qml_$RUN_ID.log"
LATEST_LOG="$LOG_DIR/start_hdmi_qml_latest.log"
WESTON_CONFIG="$QT_ROOT/weston-hdmi-primary.ini"
WESTON_LOG="/tmp/weston.log"
QML_LOG="$LOG_DIR/main_qml_$RUN_ID.log"
APP_LOG="$APP_DIR/app.log"

mkdir -p "$LOG_DIR"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

copy_latest_log() {
  cp "$LOG_FILE" "$LATEST_LOG" 2>/dev/null || true
}

proc_cmdline_has() {
  pattern="$1"
  for proc in /proc/[0-9]*; do
    [ -r "$proc/cmdline" ] || continue
    tr '\0' ' ' < "$proc/cmdline" 2>/dev/null | grep -q "$pattern" && return 0
  done
  return 1
}

first_pid_by_comm() {
  name="$1"
  for proc in /proc/[0-9]*; do
    [ -r "$proc/comm" ] || continue
    [ "$(cat "$proc/comm" 2>/dev/null)" = "$name" ] && {
      echo "${proc#/proc/}"
      return 0
    }
  done
  return 1
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

write_default_hdmi_config() {
  if [ -f "$WESTON_CONFIG" ]; then
    return 0
  fi
  cat > "$WESTON_CONFIG" <<'EOF'
[core]
backend=drm-backend.so
require-input=false
idle-time=0
repaint-window=-1

[shell]
panel-scale=3
locking=false

[keyboard]
vt-switching=false

[output]
name=HDMI-A-1
mode=preferred
position=0,0

[output]
name=LVDS-1
mode=off
EOF
}

drm_status() {
  log "DRM status"
  for status in /sys/class/drm/card*-*/status; do
    echo "=== $status ===" | tee -a "$LOG_FILE"
    cat "$status" 2>/dev/null | tee -a "$LOG_FILE"
  done
  hdmi_status="$(cat /sys/class/drm/*HDMI*/status 2>/dev/null | head -n 1)"
  lvds_status="$(cat /sys/class/drm/*LVDS*/status 2>/dev/null | head -n 1)"
  log "HDMI_STATUS=${hdmi_status:-unknown}"
  log "LVDS_STATUS=${lvds_status:-unknown}"
  if [ "$hdmi_status" = "connected" ]; then
    log "HDMI_FIELD_GATE=CONNECTED_QML_VISIBILITY_NEEDS_HUMAN_CONFIRM"
  else
    log "HDMI_FIELD_GATE=DISCONNECTED_CHECK_CABLE_POWER_INPUT_SOURCE"
  fi
}

wait_api() {
  i=0
  while [ "$i" -lt 20 ]; do
    if wget -qO- http://127.0.0.1:5000/api/state > "$LOG_DIR/api_state_latest.json" 2>/dev/null; then
      log "API_READY=1"
      return 0
    fi
    sleep 1
    i=$((i + 1))
  done
  log "API_READY=0"
  return 1
}

wait_wayland() {
  i=0
  while [ "$i" -lt 20 ]; do
    [ -S /run/wayland-0 ] && return 0
    sleep 1
    i=$((i + 1))
  done
  return 1
}

log "V2.5.15 start_retail_hdmi_qml begin"
log "APP_DIR=$APP_DIR"
log "QT_ROOT=$QT_ROOT"
log "WESTON_CONFIG=$WESTON_CONFIG"
df -h /userdata | tee -a "$LOG_FILE"
snapshot_procs "processes before"
drm_status

if [ ! -x "$QT_ROOT/bin/qmlscene" ]; then
  log "ERROR: qmlscene missing at $QT_ROOT/bin/qmlscene"
  copy_latest_log
  exit 10
fi

if [ ! -f "$QT_ROOT/qt5-env.sh" ]; then
  log "ERROR: qt5-env.sh missing at $QT_ROOT/qt5-env.sh"
  copy_latest_log
  exit 11
fi

if [ ! -f "$APP_DIR/app.py" ]; then
  log "ERROR: app.py missing at $APP_DIR/app.py"
  copy_latest_log
  exit 12
fi

write_default_hdmi_config

if proc_cmdline_has "python3 .*app.py"; then
  log "Flask already running"
else
  log "Starting Flask app.py"
  cd "$APP_DIR" || {
    log "ERROR: cannot cd $APP_DIR"
    copy_latest_log
    exit 13
  }
  nohup python3 -u app.py >> "$APP_LOG" 2>&1 &
  echo "$!" > "$APP_DIR/app.pid"
  sleep 3
fi

wait_api
API_RC=$?

log "Stopping old frontend clients"
kill_by_comm qmlscene
kill_python_target "terminal_kiosk.py"
kill_by_comm weston-terminal
sleep 2

log "Stopping current Weston"
cp /tmp/weston.log "$LOG_DIR/weston_before_$RUN_ID.log" 2>/dev/null || true
pids="$(pidof weston 2>/dev/null || true)"
[ -n "$pids" ] && kill $pids 2>/dev/null
sleep 2
pids="$(pidof weston 2>/dev/null || true)"
[ -n "$pids" ] && kill -9 $pids 2>/dev/null
rm -f /run/wayland-0 /run/wayland-0.lock

log "Starting HDMI-primary Weston"
export XDG_RUNTIME_DIR=/run
export WESTON_DISABLE_ATOMIC=1
export WESTON_DRM_PRIMARY=HDMI-A-1
export WESTON_DRM_HEAD_MODE=external
export WESTON_OUTPUT_FLOW=horizontal
export WESTON_DRM_KEEP_RATIO=1
nohup /usr/bin/weston --config="$WESTON_CONFIG" --log="$WESTON_LOG" > "$LOG_DIR/weston_nohup_$RUN_ID.log" 2>&1 &
WESTON_PID="$!"
echo "$WESTON_PID" > "$LOG_DIR/weston_latest.pid"
log "WESTON_PID=$WESTON_PID"

if ! wait_wayland; then
  log "ERROR: /run/wayland-0 did not appear"
  copy_latest_log
  exit 20
fi
ls -l /run/wayland-0 /run/wayland-0.lock 2>/dev/null | tee -a "$LOG_FILE"

if command -v weston-info >/dev/null 2>&1; then
  XDG_RUNTIME_DIR=/run WAYLAND_DISPLAY=wayland-0 timeout 8 weston-info > "$LOG_DIR/weston_info_$RUN_ID.txt" 2>&1
fi
cp "$WESTON_LOG" "$LOG_DIR/weston_hdmi_$RUN_ID.log" 2>/dev/null || true

log "Starting QML Main.qml"
. "$QT_ROOT/qt5-env.sh"
export QT_WAYLAND_DISABLE_WINDOWDECORATION=1
export QT_LOGGING_RULES="${QT_LOGGING_RULES:-qt.qpa.*=true;qt.scenegraph.*=true}"
nohup "$QT_ROOT/bin/qmlscene" "$APP_DIR/qt_kiosk/Main.qml" > "$QML_LOG" 2>&1 &
QML_PID="$!"
echo "$QML_PID" > "$LOG_DIR/qmlscene_latest.pid"
sleep 6

FLASK_PID="$(first_pid_by_comm python3)"
WESTON_PID_NOW="$(pidof weston 2>/dev/null || true)"
QML_PID_NOW="$(pidof qmlscene 2>/dev/null || true)"
log "FLASK_PID=$FLASK_PID"
log "WESTON_PID=$WESTON_PID_NOW"
log "QMLSCENE_PID=$QML_PID_NOW"
log "API_RC=$API_RC"

snapshot_procs "processes after"
drm_status
tail -120 "$QML_LOG" > "$LOG_DIR/main_qml_latest_tail.log" 2>/dev/null || true
tail -120 "$WESTON_LOG" > "$LOG_DIR/weston_latest_tail.log" 2>/dev/null || true

if [ -z "$WESTON_PID_NOW" ] || [ -z "$QML_PID_NOW" ]; then
  log "ERROR: expected weston/qmlscene process missing"
  copy_latest_log
  exit 30
fi

log "V2.5.15 start_retail_hdmi_qml complete"
copy_latest_log
exit 0
