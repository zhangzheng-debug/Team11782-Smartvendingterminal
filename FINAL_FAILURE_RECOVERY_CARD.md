# Final Failure Recovery Card / 现场故障兜底卡

## QML 没显示

```sh
sh /userdata/start_retail_hdmi_qml.sh
tail -120 /userdata/qt5/kiosk_launcher_logs/start_hdmi_qml_latest.log
pgrep -af 'app.py|weston|qmlscene'
```

## 回默认桌面

```sh
sh /userdata/restore_default_weston.sh
```

## QML 卡住

```sh
pkill -f qmlscene
sh /userdata/start_retail_hdmi_qml.sh
```

## API 不通

```sh
cd /userdata/smart_retail
nohup python3 -u app.py > /userdata/smart_retail/app.log 2>&1 &
wget -qO- http://127.0.0.1:5000/api/state | head -c 1200
```

## 扫码枪响但界面无反应

检查：

- 扫码枪是否插在已验证 USB Host 口
- `cat /proc/bus/input/devices | grep -iE 'Megahunt|ScanBox|Keyboard|HID' -A8`
- 不点击输入框，直接输入 `SKU001` + Enter 是否有效

## 拍照提示频繁或摄像头忙

处理：

- 等待冷却时间
- 不要连续快速点击
- 查看 `/api/capture` 返回

```sh
wget -qO- --header='Content-Type: application/json' --post-data='{}' http://127.0.0.1:5000/api/capture
```

## 音频无声音

```sh
cat /proc/asound/cards
aplay -l
arecord -l
python3 tools/audio_event_matrix_test.py
```

确认 HyperX Cloud III 或目标 USB 声卡存在。

## 云支付手机打不开

板端测试：

```sh
wget -S -O- http://139.59.102.178:8000/health 2>&1 | head -100
```

如果失败：

- 检查 Windows ICS/NAT 或真实路由器
- 确认板端默认路由
- 使用 local_debug 兜底，不影响扫码、购物车和本地订单演示

## 恢复稳定状态

```sh
sh /userdata/restore_default_weston.sh
sh /userdata/start_retail_hdmi_qml.sh
```

