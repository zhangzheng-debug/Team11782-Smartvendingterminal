#!/bin/sh
set -eu

APP_DIR="${APP_DIR:-/userdata/smart_retail}"
QML_FILE="$APP_DIR/qt_kiosk/Main.qml"
LOGFILE="$APP_DIR/kiosk.log"

export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-wayland}"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run}"
export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}"

cd "$APP_DIR"

if command -v qmlscene >/dev/null 2>&1; then
  exec qmlscene "$QML_FILE" > "$LOGFILE" 2>&1
fi

if command -v qml >/dev/null 2>&1; then
  exec qml "$QML_FILE" > "$LOGFILE" 2>&1
fi

echo "Missing Qt/QML runtime. Flask backend remains available at http://127.0.0.1:5000" >> "$LOGFILE"
exit 127

