# Project Structure / 项目结构

```text
.
├── app.py
├── qt_kiosk/
├── static/
├── templates/
├── tools/
├── models/
├── model_artifacts/
├── bin/
├── cloud_payment_service/
├── data/
├── evidence/
├── database/
└── docs/
```

## 核心文件

- `app.py`: 主后端。提供商品、购物车、扫码、拍照、视觉、语音、音频和支付 API。
- `qt_kiosk/Main.qml`: HDMI 收银台主界面。
- `qt_kiosk/retail_api.js`: QML 调用 Flask API 的封装。
- `start_retail_hdmi_qml.sh`: 板端一键启动 HDMI QML 收银台。
- `restore_default_weston.sh`: 恢复默认 Weston 桌面的回滚脚本。
- `terminal_kiosk.py`: Qt runtime 缺失时的终端兜底界面。

## 模型与视觉

- `models/vision_10sku_v260/model.onnx`: 10-SKU ONNX baseline。
- `models/vision_10sku_rknn_v263/vision_10sku_v263_default.rknn`: 板端 RKNN 模型。
- `bin/vision_rknn_cli_v263/vision_rknn_cli`: RKNN C CLI。
- `model_artifacts/`: ONNX/RKNN 转换、标签、metadata 和评估产物。
- `data/10sku_manifest/manifest.csv`: 10-SKU 商品清单。

## 工具脚本

常用工具集中在 `tools/`：

- `scan_api_matrix_test.py`: 扫码 API 矩阵测试。
- `qml_business_api_test.py`: 收银台业务 API 回归。
- `capture_stress_test.py`: 拍照互斥、冷却和超时压力测试。
- `audio_event_matrix_test.py`: 语音播报事件矩阵测试。
- `rknn_cli_smoke_test.py`: RKNN CLI 冒烟测试。
- `cloud_payment_probe.py`: 云支付创建和回写探测。

## 数据与安全

`database/` 只保留 `.gitkeep`，不上传运行时数据库。真实部署时由程序初始化或从板端备份恢复。

`data/10sku_manifest/` 只保留商品清单和 contact sheet，不上传完整原始训练图片。

