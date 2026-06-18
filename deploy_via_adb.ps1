$ADB="C:\Users\MR\Downloads\tool\tool\RKDevTool_Release_v2.92\RKDevTool_Release_v2.92\bin\adb.exe"
Write-Host "ADB: $ADB"
& $ADB devices
& $ADB shell "rm -rf /userdata/smart_retail; mkdir -p /userdata/smart_retail"
& $ADB push "$PSScriptRoot\." /userdata/smart_retail/
& $ADB shell "cd /userdata/smart_retail && python3 test_env.py"
Write-Host "Deploy done."
