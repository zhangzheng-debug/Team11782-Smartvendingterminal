$ErrorActionPreference = "Stop"

$ADB = "C:\Users\MR\Downloads\tool\tool\RKDevTool_Release_v2.92\RKDevTool_Release_v2.92\bin\adb.exe"
$OutFile = Join-Path $PSScriptRoot "qt_env_probe_result.txt"

function Add-Line {
    param([string]$Text)
    $Text | Tee-Object -FilePath $OutFile -Append
}

function Run-Probe {
    param(
        [string]$Title,
        [string]$Command
    )
    Add-Line ""
    Add-Line "===== $Title ====="
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

if (Test-Path $OutFile) {
    Remove-Item -LiteralPath $OutFile -Force
}

Add-Line "QSM368ZP-WF Qt/QML environment probe"
Add-Line "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Add-Line "ADB: $ADB"
Add-Line ""
Add-Line "This probe is read-only. It does not install packages or modify board files."

Run-Probe "adb devices" "echo connected && id"
Run-Probe "Qt commands" "for c in qmlscene qml qmake qtpaths simplebrowser qtlauncher; do printf '%-16s ' `$c; command -v `$c || true; done"
Run-Probe "Qt libraries" "find /usr /lib /userdata -name '*Qt5Core*' -o -name '*Qt5Quick*' -o -name '*Qt5Qml*' -o -name '*Qt5Widgets*' -o -name '*Qt5Network*' -o -name '*Qt5Wayland*' -o -name '*Qt5WebEngine*' 2>/dev/null | sort | head -200"
Run-Probe "QML and plugin directories" "find /usr /lib /userdata -type d \( -name qml -o -name plugins -o -name platforms -o -name wayland \) 2>/dev/null | sort | head -200"
Run-Probe "Fonts" "find /usr /lib /userdata -name '*.ttf' -o -name '*.otf' 2>/dev/null | sort | head -120"
Run-Probe "Wayland socket" "ls -l /run/wayland-0 /var/run/wayland-0 2>/dev/null || true"
Run-Probe "Weston process" "ps | grep -i '[w]eston' || true"
Run-Probe "Input devices" "ls -l /dev/input 2>/dev/null || true"
Run-Probe "Input capabilities" "cat /proc/bus/input/devices 2>/dev/null | grep -i -E 'touch|mouse|keyboard|hid|Handlers|Name' || true"

Add-Line ""
Add-Line "Probe complete: $OutFile"
Write-Host "Probe complete: $OutFile"

