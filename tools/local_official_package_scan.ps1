$ErrorActionPreference = "Stop"

$Roots = @(
    "C:\Users\MR\Desktop\Vibecoder\QSM368ZP-WF-master",
    "C:\Users\MR\Downloads"
)
$OutFile = Join-Path $PSScriptRoot "local_official_package_scan_result.txt"
$Patterns = @(
    "qt5base",
    "qt5declarative",
    "qt5quick",
    "qtquick",
    "qt5wayland",
    "qmlscene",
    "BR2_PACKAGE_QT5",
    "QtWebEngine",
    "simplebrowser",
    "chromium",
    "buildroot",
    "defconfig",
    "rootfs",
    "sdk"
)
$NameRegex = "qt|qml|buildroot|rootfs|sdk|defconfig|weston|wayland|chromium|simplebrowser"
$ContentExt = @(".txt", ".md", ".config", ".cfg", ".conf", ".mk", ".cmake", ".sh", ".ps1", ".bat", ".cmd", ".ini", ".log", ".json")

function Add-Line {
    param([string]$Text)
    $Text | Tee-Object -FilePath $OutFile -Append
}

if (Test-Path -LiteralPath $OutFile) {
    Remove-Item -LiteralPath $OutFile -Force
}

Add-Line "QSM368ZP-WF local official package scan"
Add-Line "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Add-Line "Roots:"
$Roots | ForEach-Object { Add-Line "  $_" }
Add-Line ""

foreach ($root in $Roots) {
    Add-Line "===== ROOT: $root ====="
    if (!(Test-Path -LiteralPath $root)) {
        Add-Line "MISSING"
        continue
    }

    Add-Line ""
    Add-Line "--- Candidate file names ---"
    Get-ChildItem -LiteralPath $root -Recurse -Force -File -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -match $NameRegex -or $_.Name -match $NameRegex } |
        Select-Object -First 500 FullName, Length, LastWriteTime |
        Format-Table -AutoSize | Out-String -Width 240 |
        Tee-Object -FilePath $OutFile -Append | Out-Null

    Add-Line ""
    Add-Line "--- Archive/image candidates ---"
    Get-ChildItem -LiteralPath $root -Recurse -Force -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Extension -match "(\.zip|\.7z|\.rar|\.tar|\.gz|\.xz|\.img|\.bin|\.iso)$" -or $_.Name -match $NameRegex } |
        Select-Object -First 500 FullName, Length, LastWriteTime |
        Format-Table -AutoSize | Out-String -Width 240 |
        Tee-Object -FilePath $OutFile -Append | Out-Null

    Add-Line ""
    Add-Line "--- Content matches ---"
    $files = Get-ChildItem -LiteralPath $root -Recurse -Force -File -ErrorAction SilentlyContinue |
        Where-Object { $ContentExt -contains $_.Extension -or $_.Name -in @("Config.in", "Makefile", ".config") } |
        Select-Object -First 8000

    foreach ($pattern in $Patterns) {
        Add-Line ""
        Add-Line "Pattern: $pattern"
        $matches = $files | Select-String -Pattern $pattern -SimpleMatch -ErrorAction SilentlyContinue | Select-Object -First 120
        if ($matches) {
            $matches | Select-Object Path, LineNumber, Line |
                Format-List | Out-String -Width 240 |
                Tee-Object -FilePath $OutFile -Append | Out-Null
        } else {
            Add-Line "  no matches"
        }
    }
}

Add-Line ""
Add-Line "Scan complete: $OutFile"
Write-Host "Scan complete: $OutFile"

