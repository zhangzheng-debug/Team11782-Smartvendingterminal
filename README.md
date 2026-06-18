# Team11782 Smart Vending Terminal

QSM368ZP-WF 智能零售终端项目开源包。

本仓库整理了比赛项目的核心代码、Qt/QML HDMI 前端、Flask/SQLite 后端、扫码枪输入、摄像头拍照、10-SKU RKNN/NPU 视觉校验、中文语音播报、云支付回写、部署脚本、测试脚本和关键证据材料。

## 项目简介

本项目运行在 QSM368ZP-WF / RK3568 类 Linux 板端，目标是实现一个可现场演示的智能零售终端：

- HDMI 显示 Qt/QML 全屏收银台
- Flask 提供 `/api/*` JSON 接口
- SQLite 保存商品、购物车、订单与状态
- USB HID 扫码枪作为主收银输入
- 摄像头拍照并进行 10 类商品视觉校验
- RKNN C runtime 接入板端 NPU 推理路径
- 中文语音识别、纠错和全操作人声播报
- 云支付订单创建和 paid 状态回写
- 一键启动 QML 收银台和一键恢复默认 Weston 桌面

重要设计边界：

- 条码/扫码是稳定收银主通道。
- 视觉模型用于扫码后的辅助校验和未知条码候选，不做连续视觉自动加购，避免误识别导致重复计费。
- 当前 10-SKU 数据集是低样本 baseline，适合比赛原型展示；商用需要继续扩充数据集。

## 仓库内容

| 路径 | 说明 |
| --- | --- |
| `app.py` | Flask 主后端，包含商品、购物车、订单、支付、音频、视觉等 API |
| `qt_kiosk/` | Qt/QML HDMI 收银台前端 |
| `static/` | 音频播报、CSS、商品图片等静态资源 |
| `templates/` | Web 调试页面模板 |
| `tools/` | API 回归、视觉测试、音频测试、部署辅助脚本 |
| `models/` | 板端运行使用的 ONNX/RKNN 模型入口文件 |
| `model_artifacts/` | 10-SKU ONNX/RKNN 模型产物和元数据 |
| `bin/vision_rknn_cli_v263/` | 板端 RKNN C CLI 和 runtime 依赖 |
| `cloud_payment_service/` | 云支付服务示例代码 |
| `data/10sku_manifest/` | 10-SKU 商品清单、数据集摘要和 contact sheet |
| `evidence/screenshots/` | 开源包内保留的关键截图证据 |
| `docs/` | 开源说明、部署说明、测试说明、证据说明和限制说明 |

没有上传的内容：

- 原始训练图片全集，体积较大，仓库只保留 manifest 和 contact sheet。
- 板端实时数据库文件，避免泄露现场运行数据。
- 私钥、云服务器凭据、Windows/ADB 私有环境文件。
- Buildroot/Qt SDK 和交叉编译缓存。

## 快速开始

本地开发调试：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

打开：

```text
http://127.0.0.1:5000
http://127.0.0.1:5000/api/state
```

板端 QML 演示：

```sh
sh /userdata/start_retail_hdmi_qml.sh
```

恢复默认 Weston 桌面：

```sh
sh /userdata/restore_default_weston.sh
```

更完整步骤见：

- [QUICK_START.md](QUICK_START.md)
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- [docs/TESTING.md](docs/TESTING.md)

## 常用测试

在板端 `/userdata/smart_retail` 下运行：

```sh
python3 tools/scan_api_matrix_test.py
python3 tools/qml_business_api_test.py
python3 tools/input_arbitration_api_test.py
python3 tools/capture_stress_test.py
python3 tools/audio_event_matrix_test.py
python3 tools/rknn_cli_smoke_test.py
wget -qO- http://127.0.0.1:5000/api/state | head -c 1500
```

## 关键能力状态

| 模块 | 当前状态 |
| --- | --- |
| HDMI QML 收银台 | 已完成 |
| Flask `/api/*` | 已完成 |
| SQLite 商品/购物车/订单 | 已完成 |
| 扫码枪 HID 输入 | 已完成 |
| 拍照采集与冷却保护 | 已完成 |
| 10-SKU ONNX baseline | 已完成 |
| RKNN/NPU C runtime 后端 | 已完成 |
| 中文语音播报 | 已完成 |
| 云支付 paid 回写 | 已完成 |
| 开机自启动 | 未启用，保留手动一键启动 |

## 评审说明

本仓库重点满足“项目代码开源、说明清晰、可验证”的要求。评审建议先阅读：

1. [docs/EVIDENCE.md](docs/EVIDENCE.md)
2. [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)
3. [docs/TESTING.md](docs/TESTING.md)
4. [docs/LIMITATIONS.md](docs/LIMITATIONS.md)

## License

本开源包使用 MIT License。第三方 SDK、RKNN runtime、Qt runtime、系统镜像和硬件厂商组件仍遵循各自原始许可。

