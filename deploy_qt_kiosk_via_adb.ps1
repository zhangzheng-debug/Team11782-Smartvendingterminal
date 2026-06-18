$ErrorActionPreference = "Stop"

$ADB = "C:\Users\MR\Downloads\tool\tool\RKDevTool_Release_v2.92\RKDevTool_Release_v2.92\bin\adb.exe"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RemoteApp = "/userdata/smart_retail"
$RemoteStart = "/userdata/start_retail_kiosk.sh"
$BackupRoot = "C:\Users\MR\Desktop\Vibecoder"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupDir = Join-Path $BackupRoot "backup_smart_retail_before_v256_$Timestamp"

Write-Host "ADB: $ADB"
Write-Host "Project: $ProjectRoot"
Write-Host "Remote app dir: $RemoteApp"
Write-Host "Safety: no RKDevTool Upgrade, no EraseFlash, no reboot, no partition image writes."

& $ADB devices
if ($LASTEXITCODE -ne 0) {
    throw "adb devices failed"
}

Write-Host "Backing up current board app before deploy: $BackupDir"
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
& $ADB pull $RemoteApp "$BackupDir\smart_retail"
if ($LASTEXITCODE -ne 0) {
    throw "backup failed; deploy stopped"
}

& $ADB shell "mkdir -p $RemoteApp $RemoteApp/qt_kiosk $RemoteApp/tools"
if ($LASTEXITCODE -ne 0) {
    throw "remote mkdir failed"
}

& $ADB shell "rm -rf $RemoteApp/templates/templates $RemoteApp/static/static $RemoteApp/database/database $RemoteApp/qt_kiosk/qt_kiosk $RemoteApp/tools/tools"
if ($LASTEXITCODE -ne 0) {
    throw "cleanup nested deploy directories failed"
}

& $ADB push "$ProjectRoot\app.py" "$RemoteApp/app.py"
& $ADB push "$ProjectRoot\terminal_kiosk.py" "$RemoteApp/terminal_kiosk.py"
& $ADB push "$ProjectRoot\templates\." "$RemoteApp/templates/"
& $ADB push "$ProjectRoot\static\." "$RemoteApp/static/"
& $ADB push "$ProjectRoot\qt_kiosk\." "$RemoteApp/qt_kiosk/"
& $ADB push "$ProjectRoot\tools\api_smoke_test.py" "$RemoteApp/tools/api_smoke_test.py"
& $ADB push "$ProjectRoot\tools\probe_qt_env.ps1" "$RemoteApp/tools/probe_qt_env.ps1"
& $ADB push "$ProjectRoot\tools\reparse_voice_eval_results.py" "$RemoteApp/tools/reparse_voice_eval_results.py"
& $ADB push "$ProjectRoot\README.md" "$RemoteApp/README.md"
& $ADB push "$ProjectRoot\README_QT_KIOSK.md" "$RemoteApp/README_QT_KIOSK.md"
& $ADB push "$ProjectRoot\README_TERMINAL_KIOSK.md" "$RemoteApp/README_TERMINAL_KIOSK.md"
& $ADB push "$ProjectRoot\API_CONTRACT.md" "$RemoteApp/API_CONTRACT.md"
& $ADB push "$ProjectRoot\CHANGELOG_QT_KIOSK.md" "$RemoteApp/CHANGELOG_QT_KIOSK.md"
& $ADB push "$ProjectRoot\start_retail_kiosk.sh" "$RemoteStart"
& $ADB push "$ProjectRoot\start_retail_kiosk.sh" "$RemoteApp/start_retail_kiosk.sh"

& $ADB shell "if [ ! -f $RemoteApp/database/retail_terminal.db ]; then mkdir -p $RemoteApp/database; fi"
if ($LASTEXITCODE -ne 0) {
    throw "database directory check failed"
}
& $ADB shell "test -f $RemoteApp/database/retail_terminal.db"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Remote database missing; pushing seed database."
    & $ADB push "$ProjectRoot\database\." "$RemoteApp/database/"
} else {
    Write-Host "Remote database exists; preserving board SQLite database."
}

& $ADB shell "chmod +x $RemoteStart $RemoteApp/start_retail_kiosk.sh $RemoteApp/terminal_kiosk.py $RemoteApp/qt_kiosk/start_qt_kiosk.sh 2>/dev/null || true"
if ($LASTEXITCODE -ne 0) {
    throw "chmod failed"
}

Write-Host "Deploy done."
Write-Host "Backup saved at: $BackupDir"
Write-Host "Start manually with:"
Write-Host "& `"$ADB`" shell `"sh $RemoteStart`""
