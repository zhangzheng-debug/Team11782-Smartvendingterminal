$ADB="C:\Users\MR\Downloads\tool\tool\RKDevTool_Release_v2.92\RKDevTool_Release_v2.92\bin\adb.exe"
& $ADB shell "pkill -f 'python3 app.py' || true"
& $ADB shell "sh -c 'cd /userdata/smart_retail && nohup python3 app.py > /userdata/smart_retail/app.log 2>&1 &'"
Start-Sleep 2
& $ADB shell "tail -30 /userdata/smart_retail/app.log"
