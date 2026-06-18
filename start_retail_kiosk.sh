#!/bin/sh
set -u

APP_DIR="${APP_DIR:-/userdata/smart_retail}"
APP_LOG="$APP_DIR/app.log"
KIOSK_LOG="$APP_DIR/kiosk.log"
APP_PID="$APP_DIR/app.pid"
KIOSK_PID="$APP_DIR/kiosk.pid"
QML_FILE="$APP_DIR/qt_kiosk/Main.qml"
TERMINAL_KIOSK="$APP_DIR/terminal_kiosk.py"
QT_USERDATA_ROOT="${QT_USERDATA_ROOT:-/userdata/qt5}"
QT_USERDATA_ENV="$QT_USERDATA_ROOT/qt5-env.sh"
HDMI_QML_LAUNCHER="${HDMI_QML_LAUNCHER:-/userdata/start_retail_hdmi_qml.sh}"

mkdir -p "$APP_DIR"
cd "$APP_DIR" || exit 1

export PYTHONUNBUFFERED=1
if [ -r "$QT_USERDATA_ENV" ]; then
  . "$QT_USERDATA_ENV"
fi
export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-wayland}"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run}"
export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}"

echo "==== start_retail_kiosk $(date '+%Y-%m-%d %H:%M:%S') ====" >> "$KIOSK_LOG"
echo "APP_DIR=$APP_DIR" >> "$KIOSK_LOG"
echo "QT_USERDATA_ROOT=$QT_USERDATA_ROOT" >> "$KIOSK_LOG"

if [ -x "$QT_USERDATA_ROOT/bin/qmlscene" ] && [ -x "$HDMI_QML_LAUNCHER" ]; then
  echo "delegating to HDMI QML launcher: $HDMI_QML_LAUNCHER" >> "$KIOSK_LOG"
  exec sh "$HDMI_QML_LAUNCHER"
fi

flask_running() {
  for proc in /proc/[0-9]*; do
    [ -r "$proc/comm" ] || continue
    [ "$(cat "$proc/comm" 2>/dev/null)" = "python3" ] || continue
    if grep -q 'app.py' "$proc/cmdline" 2>/dev/null; then
      return 0
    fi
  done
  return 1
}

if ! flask_running; then
  echo "starting Flask app.py" >> "$KIOSK_LOG"
  if command -v start-stop-daemon >/dev/null 2>&1; then
    start-stop-daemon -S -b -m -p "$APP_PID" -x /usr/bin/python3 -- -u app.py >> "$APP_LOG" 2>&1
  else
    nohup python3 -u app.py >> "$APP_LOG" 2>&1 &
    echo "$!" > "$APP_PID"
  fi
else
  echo "Flask already running" >> "$KIOSK_LOG"
fi

i=0
while [ "$i" -lt 30 ]; do
  if wget -qO- http://127.0.0.1:5000/health >/dev/null 2>&1 || wget -qO- http://127.0.0.1:5000/api/state >/dev/null 2>&1; then
    echo "Flask API ready" >> "$KIOSK_LOG"
    break
  fi
  i=$((i + 1))
  sleep 1
done

if [ "$i" -ge 30 ]; then
  echo "warning: Flask API did not become ready within 30 seconds" >> "$KIOSK_LOG"
fi

pkill -f 'qmlscene.*/qt_kiosk/Main.qml' 2>/dev/null || true
pkill -f 'qml.*/qt_kiosk/Main.qml' 2>/dev/null || true
pkill -f 'terminal_kiosk.py' 2>/dev/null || true
pkill -f 'weston-terminal.*kiosk_console.sh' 2>/dev/null || true
rm -f "$KIOSK_PID"

launch_qml() {
  runner="$1"
  echo "launching Qt/QML with $runner" >> "$KIOSK_LOG"
  if command -v start-stop-daemon >/dev/null 2>&1; then
    start-stop-daemon -S -b -m -p "$KIOSK_PID" -x /bin/sh -- -c "cd '$APP_DIR' && exec $runner '$QML_FILE' >> '$KIOSK_LOG' 2>&1"
  else
    sh -c "cd '$APP_DIR' && exec $runner '$QML_FILE' >> '$KIOSK_LOG' 2>&1" &
    echo "$!" > "$KIOSK_PID"
  fi
}

if [ -x "$QT_USERDATA_ROOT/bin/qmlscene" ]; then
  launch_qml "$QT_USERDATA_ROOT/bin/qmlscene"
  exit 0
fi

if [ -x "$QT_USERDATA_ROOT/bin/qml" ]; then
  launch_qml "$QT_USERDATA_ROOT/bin/qml"
  exit 0
fi

if command -v qmlscene >/dev/null 2>&1; then
  launch_qml "$(command -v qmlscene)"
  exit 0
fi

if command -v qml >/dev/null 2>&1; then
  launch_qml "$(command -v qml)"
  exit 0
fi

echo "missing Qt/QML runtime; keeping Flask running" >> "$KIOSK_LOG"

cat > "$APP_DIR/kiosk_console.sh" <<'EOF'
#!/bin/sh
clear
echo "Smart Retail Flask backend is running."
echo ""
echo "Qt/QML runtime was not found on this Buildroot image:"
echo "  missing qmlscene/qml"
echo ""
echo "Starting V2.5.6 Terminal Kiosk fallback..."
echo ""
cd /userdata/smart_retail || exit 1
if [ -f ./terminal_kiosk.py ]; then
  exec python3 -u ./terminal_kiosk.py
fi
echo ""
echo "terminal_kiosk.py is missing. Flask remains available at http://127.0.0.1:5000"
exec /bin/sh
EOF
chmod +x "$APP_DIR/kiosk_console.sh"

if command -v weston-terminal >/dev/null 2>&1; then
  if command -v start-stop-daemon >/dev/null 2>&1; then
    start-stop-daemon -S -b -m -p "$KIOSK_PID" -x weston-terminal -- --fullscreen --shell="$APP_DIR/kiosk_console.sh" >> "$KIOSK_LOG" 2>&1
  else
    weston-terminal --fullscreen --shell="$APP_DIR/kiosk_console.sh" >> "$KIOSK_LOG" 2>&1 &
    echo "$!" > "$KIOSK_PID"
  fi
else
  echo "weston-terminal also missing; see $KIOSK_LOG via adb shell" >> "$KIOSK_LOG"
fi

exit 0
