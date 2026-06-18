$ErrorActionPreference = "Stop"

$ADB = "C:\Users\MR\Downloads\tool\tool\RKDevTool_Release_v2.92\RKDevTool_Release_v2.92\bin\adb.exe"
$OutFile = Join-Path $PSScriptRoot "qt_runtime_probe_full_result.txt"

function Add-Line {
    param([string]$Text)
    $Text | Tee-Object -FilePath $OutFile -Append
}

function Run-Host {
    param(
        [string]$Title,
        [scriptblock]$Command
    )
    Add-Line ""
    Add-Line "===== HOST: $Title ====="
    try {
        $result = & $Command 2>&1
        if ($result) {
            $result | Tee-Object -FilePath $OutFile -Append
        }
    } catch {
        Add-Line "ERROR: $($_.Exception.Message)"
    }
}

function Run-Adb {
    param(
        [string]$Title,
        [string]$Command
    )
    Add-Line ""
    Add-Line "===== BOARD: $Title ====="
    Add-Line "`$ $Command"
    try {
        $result = & $ADB shell $Command 2>&1
        if ($LASTEXITCODE -ne 0) {
            Add-Line "exit_code=$LASTEXITCODE"
        }
        if ($result) {
            $result | Tee-Object -FilePath $OutFile -Append
        }
    } catch {
        Add-Line "ERROR: $($_.Exception.Message)"
    }
}

if (Test-Path -LiteralPath $OutFile) {
    Remove-Item -LiteralPath $OutFile -Force
}

Add-Line "QSM368ZP-WF V2.5.7 Qt Runtime Gate - Full Probe"
Add-Line "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Add-Line "ADB: $ADB"
Add-Line "Safety: read-only probe. No RKDevTool Upgrade, no EraseFlash, no boot/rootfs/oem/uboot writes."

Run-Host "adb devices" { & $ADB devices -l }

Run-Adb "identity" "id; pwd; whoami 2>/dev/null || true"
Run-Adb "kernel and architecture" "uname -a; uname -m; cat /proc/cpuinfo 2>/dev/null | head -80"
Run-Adb "os release" "cat /etc/os-release 2>/dev/null || cat /etc/issue 2>/dev/null || true"
Run-Adb "busybox version" "busybox 2>&1 | head -5 || true"
Run-Adb "libc and ldd" "ldd --version 2>&1 || /lib/ld-linux-aarch64.so.1 --help 2>&1 | head -40 || /lib/ld-musl-aarch64.so.1 2>&1 | head -40 || true"
Run-Adb "glibc version direct" "/lib/libc.so.6 2>&1 | head -20 || true; /lib/ld-linux-aarch64.so.1 --version 2>&1 | head -8 || true"
Run-Adb "tool availability" "for c in file readelf ldd; do printf '%-12s ' `$c; command -v `$c || true; done"
Run-Adb "key binary file types" "file /bin/busybox /usr/bin/python3 /usr/bin/weston /usr/bin/weston-terminal 2>/dev/null || true"
Run-Adb "dynamic loader" "readelf -l /bin/busybox 2>/dev/null | head -60 || true"
Run-Adb "python linkage" "readelf -d /usr/bin/python3 2>/dev/null | head -80 || true"
Run-Adb "mounts" "mount"
Run-Adb "disk space" "df -h; echo '--- userdata stat ---'; df -h /userdata /usr / 2>/dev/null || true"
Run-Adb "library dirs" "ls -la /lib /usr/lib /usr/local/lib /opt 2>/dev/null | head -240"
Run-Adb "qt commands" "for c in qmlscene qml qmake qtpaths simplebrowser qtlauncher; do printf '%-16s ' `$c; command -v `$c || true; done"
Run-Adb "qt files" "find / -maxdepth 6 \( -name '*Qt5*' -o -name 'qmlscene' -o -name 'qml' -o -name 'qt.conf' \) 2>/dev/null | sort | head -300"
Run-Adb "wayland egl gles files" "find / -maxdepth 6 \( -name '*wayland*' -o -name '*Wayland*' -o -name '*EGL*' -o -name '*GLES*' -o -name '*gbm*' \) 2>/dev/null | sort | head -300"
Run-Adb "weston version and process" "weston --version 2>&1 || true; echo '--- ps ---'; ps -ef 2>/dev/null | grep -E '[w]eston|[w]ayland|[t]erminal_kiosk' || ps | grep -E '[w]eston|[w]ayland|[t]erminal_kiosk' || true"
Run-Adb "wayland socket" "ls -la /run/wayland-0 /var/run/wayland-0 2>/dev/null || true; echo XDG_RUNTIME_DIR=`$XDG_RUNTIME_DIR WAYLAND_DISPLAY=`$WAYLAND_DISPLAY"
Run-Adb "drm gpu devices" "ls -la /dev/dri /sys/class/drm 2>/dev/null || true; echo '--- drm names ---'; for p in /sys/class/drm/*/status /sys/class/drm/*/modes; do [ -e `$p ] && echo ===`$p=== && cat `$p; done"
Run-Adb "gpu kernel modules" "lsmod 2>/dev/null | head -120 || cat /proc/modules 2>/dev/null | head -120 || true"
Run-Adb "input devices" "ls -la /dev/input 2>/dev/null || true; echo '--- proc input ---'; cat /proc/bus/input/devices 2>/dev/null || true"
Run-Adb "fonts" "find /usr /lib /opt /userdata -maxdepth 7 \( -name '*.ttf' -o -name '*.otf' -o -name '*.ttc' \) 2>/dev/null | sort | head -240"
Run-Adb "pkg config and buildroot hints" "find /etc /usr /lib /opt /userdata -maxdepth 5 \( -name '*defconfig*' -o -name '.config' -o -name '*buildroot*' -o -name '*qt5*' -o -name '*.pc' \) 2>/dev/null | sort | head -240"
Run-Adb "environment" "env | sort"

Add-Line ""
Add-Line "Probe complete: $OutFile"
Write-Host "Probe complete: $OutFile"
