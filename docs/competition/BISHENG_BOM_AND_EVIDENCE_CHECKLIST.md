# 毕昇杯硬件清单与证据交接

## BOM 待填表

| 项目 | 数量 | 型号/规格 | 单价 | 小计 | 证据/备注 |
|---|---:|---|---:|---:|---|
| QSM368ZP-WF 开发板 | 1 | 现场铭牌填写 | 待填 | 待填 | 板卡照片、供电方式 |
| HDMI 显示器 | 1 | 分辨率填写 | 待填 | 待填 | HDMI connected 与画面 |
| USB HID 扫码枪 | 1 | 型号填写 | 待填 | 待填 | 已验证 USB Host 端口 |
| USB 摄像头 | 1 | 型号填写 | 待填 | 待填 | `/dev/video*` 与拍照日志 |
| USB 音频/耳机 | 1 | HyperX Cloud III 或现场型号 | 待填 | 待填 | `aplay -l`、`arecord -l` |
| 网线、电源、转接线 | 1 批 | 现场填写 | 待填 | 待填 | 接线图与功耗记录 |
| 合计 |  |  |  | 待填 | 采购凭证或估算依据 |

不得用估算价格证明“低成本”；没有发票或采购记录时，标注“待补”。

## 证据文件命名

```text
YYYYMMDD_version_hdmi_qml.jpg
YYYYMMDD_version_usb_ports.jpg
YYYYMMDD_version_scanner_input.jpg
YYYYMMDD_version_camera_capture.jpg
YYYYMMDD_version_vision_candidates.jpg
YYYYMMDD_version_payment_demo.jpg
YYYYMMDD_version_audio_devices.txt
YYYYMMDD_version_regression.log
```

所有截图/日志旁边写清楚版本、设备日期和是否为历史证据。历史照片可以展示项目形态，但不能代替本次现场验收。

## 提交包安全检查

- [ ] 无 SSH 私钥、云 API key、token、真实支付凭据。
- [ ] 无运行中 SQLite 数据库、订单二维码缓存和私人音频录音。
- [ ] 无旧公网地址的误导性“当前可用”描述。
- [ ] `rg` 扫描个人手机号、邮箱、内部绝对路径和访问令牌。
- [ ] 给提交包生成 SHA-256 和文件清单。
- [ ] 公开仓库仅保留可复现源码、脱敏文档和小型测试夹具。
