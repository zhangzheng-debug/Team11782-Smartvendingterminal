param(
    [string]$PublicAdapterName = "WLAN",
    [string]$PrivateAdapterDescriptionPattern = "Realtek PCIe GbE"
)

$ErrorActionPreference = "Stop"
$LogPath = Join-Path (Split-Path -Parent $PSScriptRoot) "WINDOWS_ICS_ENABLE_LOG.txt"

function Write-Log {
    param([string]$Message)
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $Message"
    $line | Tee-Object -FilePath $LogPath -Append
}

function Assert-Admin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw "This script must run elevated as Administrator."
    }
}

function Get-IcsRows {
    param($HNet)
    $rows = @()
    foreach ($conn in @($HNet.EnumEveryConnection())) {
        $props = $HNet.NetConnectionProps($conn)
        $cfg = $HNet.INetSharingConfigurationForINetConnection($conn)
        $rows += [PSCustomObject]@{
            Conn = $conn
            Name = $props.Name
            DeviceName = $props.DeviceName
            Status = $props.Status
            SharingEnabled = [bool]$cfg.SharingEnabled
            SharingConnectionType = $cfg.SharingConnectionType
            Config = $cfg
        }
    }
    return $rows
}

Write-Log "=== V2.5.20f Windows ICS enable start ==="
Assert-Admin

Write-Log "Public adapter name target: $PublicAdapterName"
Write-Log "Private adapter description target: $PrivateAdapterDescriptionPattern"

$publicNet = Get-NetAdapter -Name $PublicAdapterName -ErrorAction Stop
$privateNet = Get-NetAdapter | Where-Object {
    $_.InterfaceDescription -like "*$PrivateAdapterDescriptionPattern*"
} | Select-Object -First 1

if (-not $privateNet) {
    throw "Could not find private adapter matching description: $PrivateAdapterDescriptionPattern"
}

Write-Log "Public adapter: $($publicNet.Name) / $($publicNet.InterfaceDescription) / $($publicNet.Status)"
Write-Log "Private adapter: $($privateNet.Name) / $($privateNet.InterfaceDescription) / $($privateNet.Status)"

$hnet = New-Object -ComObject HNetCfg.HNetShare
$rows = Get-IcsRows -HNet $hnet

foreach ($row in $rows) {
    Write-Log "Before ICS: name=$($row.Name), device=$($row.DeviceName), enabled=$($row.SharingEnabled), type=$($row.SharingConnectionType)"
}

$publicRow = $rows | Where-Object { $_.Name -eq $publicNet.Name -or $_.DeviceName -eq $publicNet.InterfaceDescription } | Select-Object -First 1
$privateRow = $rows | Where-Object { $_.Name -eq $privateNet.Name -or $_.DeviceName -eq $privateNet.InterfaceDescription } | Select-Object -First 1

if (-not $publicRow) {
    throw "Could not locate ICS connection for public adapter: $($publicNet.Name)"
}
if (-not $privateRow) {
    throw "Could not locate ICS connection for private adapter: $($privateNet.Name)"
}

# ICS supports one public/private pair. Disable existing sharing first so the requested pair is explicit.
foreach ($row in $rows) {
    if ($row.SharingEnabled) {
        Write-Log "Disabling existing sharing on $($row.Name) / $($row.DeviceName)"
        $row.Config.DisableSharing()
    }
}

Write-Log "Enabling public sharing on $($publicRow.Name) / $($publicRow.DeviceName)"
$publicRow.Config.EnableSharing(0)

Start-Sleep -Milliseconds 500

Write-Log "Enabling private sharing on $($privateRow.Name) / $($privateRow.DeviceName)"
$privateRow.Config.EnableSharing(1)

Start-Sleep -Seconds 2

Write-Log "Refreshing IP configuration after ICS enable"
Get-NetIPConfiguration | ForEach-Object {
    $ipv4 = ($_.IPv4Address | ForEach-Object { $_.IPAddress }) -join ","
    $gw = ($_.IPv4DefaultGateway | ForEach-Object { $_.NextHop }) -join ","
    Write-Log "IPConfig: alias=$($_.InterfaceAlias), desc=$($_.InterfaceDescription), ipv4=$ipv4, gateway=$gw"
}

$rowsAfter = Get-IcsRows -HNet $hnet
foreach ($row in $rowsAfter) {
    Write-Log "After ICS: name=$($row.Name), device=$($row.DeviceName), enabled=$($row.SharingEnabled), type=$($row.SharingConnectionType)"
}

Write-Log "=== V2.5.20f Windows ICS enable done ==="
