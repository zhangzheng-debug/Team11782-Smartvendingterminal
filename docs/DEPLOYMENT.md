# Deployment / 部署说明

## 安全边界

本项目的板端部署只需要应用层文件和 `/userdata/qt5` runtime。不要执行以下操作：

- 不刷机
- 不执行 RKDevTool Upgrade 或 EraseFlash
- 不写 boot/rootfs/oem/uboot
- 不覆盖现场数据库
- 不修改 `/etc/init.d/S03weston`

## 板端目录

推荐目录：

```text
/userdata/smart_retail
/userdata/qt5
```

`/userdata/smart_retail` 放置本仓库应用代码。

`/userdata/qt5` 放置 Qt/QML runtime、字体、Weston HDMI primary 配置和启动日志。

## ADB 部署参考

Windows PowerShell：

```powershell
$ADB="C:\Users\MR\Downloads\tool\tool\RKDevTool_Release_v2.92\RKDevTool_Release_v2.92\bin\adb.exe"
& $ADB devices -l
```

部署前建议先备份：

```powershell
$TS=Get-Date -Format "yyyyMMdd_HHmmss"
$BACKUP="C:\Users\MR\Desktop\backup_smart_retail_$TS"
New-Item -ItemType Directory -Force $BACKUP | Out-Null
& $ADB pull /userdata/smart_retail "$BACKUP\smart_retail"
```

## 启动与回滚

启动 QML：

```sh
sh /userdata/start_retail_hdmi_qml.sh
```

恢复默认 Weston：

```sh
sh /userdata/restore_default_weston.sh
```

日志位置：

```text
/userdata/qt5/kiosk_launcher_logs/start_hdmi_qml_latest.log
/userdata/qt5/main_qml.log
/userdata/smart_retail/app.log
/tmp/weston.log
```

## 网络与云支付

若使用 Windows ICS/NAT：

- Windows 有线口建议为 `192.168.137.1`
- 板端 `eth0` 可设为 `192.168.137.191/24`
- 默认路由为 `192.168.137.1`

板端测试：

```sh
wget -S -O- http://139.59.102.178:8000/health 2>&1 | head -100
```

只有板端能访问云端 health 时，手机扫码云支付链路才适合做最终演示。

