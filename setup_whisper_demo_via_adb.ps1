
$ADB="C:\Users\MR\Downloads\tool\tool\RKDevTool_Release_v2.92\RKDevTool_Release_v2.92\bin\adb.exe"
$DEMO="C:\Users\MR\Desktop\Vibecoder\QSM368ZP-WF-master\examples\rknn\rknn_whisper_demo"

& $ADB shell "rm -rf /userdata/rknn_whisper_demo; mkdir -p /userdata/rknn_whisper_demo"
& $ADB push "$DEMO\." /userdata/rknn_whisper_demo/
& $ADB shell "cd /userdata/rknn_whisper_demo && find . -maxdepth 3 -type f | sort"
