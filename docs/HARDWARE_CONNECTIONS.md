# Hardware Connections / 硬件接线说明

## 推荐固定连接

| 设备 | 建议 |
| --- | --- |
| HDMI 显示器 | 接板端 HDMI，显示器切到正确输入源 |
| ADB/调试线 | 接板端 ADB/OTG 调试口 |
| 扫码枪 | 接已验证可作为 HID Keyboard 的 USB Host 口 |
| 摄像头 | 接固定 USB 口，确认 `/dev/video*` 存在 |
| HyperX/USB 声卡 | 接固定 USB 口，确认 `aplay -l` 和 `arecord -l` 均可见 |
| 以太网 | 需要云支付时接路由器或 Windows ICS/NAT |

## 现场规则

- 不要临场乱换扫码枪、摄像头、音频口。
- 扫码枪响但界面无反应时，优先检查 USB Host 口是否正确。
- 如果使用 USB Hub，建议使用带外接供电的 Hub，并提前完整彩排。
- ADB 调试口不要占用扫码枪/音频/摄像头已验证的口。

## 网络

云支付需要板端能访问：

```text
http://139.59.102.178:8000/health
```

Windows ICS/NAT 不稳定时，优先换真实路由器 LAN 口给板端上网。

