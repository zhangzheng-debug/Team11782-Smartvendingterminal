# Team11782 Smart Vending Terminal

QSM368ZP-WF 智能零售终端，面向校园便利点、宿舍无人货柜和办公室零食柜等小型无人值守零售场景。项目运行在 RK3568 类嵌入式 Linux 板端，提供 HDMI 本机收银界面、扫码计费、端侧视觉辅助校验、语音交互和演示支付回写。

## 作品主线

```text
USB HID 扫码枪
        |
        v
板端 Flask/SQLite --> Qt/QML HDMI 收银台 --> 订单/支付状态
        |
        +--> 摄像头 --> RKNN/NPU Top-3 辅助校验
        +--> 音频输入/输出 --> 中文播报与短语命令
        +--> 云端演示支付 --> 手机页面 --> paid 回写
```

核心工程取舍：

- 条码是稳定计费主通道，视觉只做扫码后的双重校验和未知条码候选。
- 视觉结果不会连续自动加购，避免误识别造成重复计费。
- Qt/QML、Flask、SQLite 和设备输入都在板端运行，电脑仅用于调试、部署和证据采集。
- 云支付目录是比赛演示服务：验证订单创建、手机访问、模拟支付和 `paid` 回写，不等同于真实微信/支付宝商户结算。

## 目录导航

| 路径 | 作用 |
| --- | --- |
| `app.py` | 板端 Flask 后端、商品/购物车/订单/API、拍照、音频和视觉路由 |
| `qt_kiosk/` | Qt/QML HDMI 全屏收银台 |
| `templates/` | 本地调试后台和支付页模板 |
| `static/` | 小型静态资源与示例播报资产 |
| `tools/` | API 回归、设备诊断、视觉/音频验证脚本 |
| `cloud_payment_service/` | 独立云端演示支付服务 |
| `docs/` | 部署、测试、证据和限制说明 |
| `BISHENG_CUP_*.md` | 毕昇杯材料准备与项目升级建议 |

大文件、现场数据库、原始训练图片、运行日志、密钥、SDK 和板端运行时包不进入公开仓库。模型可按 `docs/MODEL_ARTIFACTS.md` 中的说明单独获取。

## 本地快速开始

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:SMART_RETAIL_CLOUD_BASE_URL = "http://127.0.0.1:8000"
python app.py
```

访问：

```text
http://127.0.0.1:5000/
http://127.0.0.1:5000/api/state
http://127.0.0.1:5000/health
```

本地只启动板端服务时，不需要配置云支付地址；支付流程会显示明确的本地/离线状态。

## 板端启动

前置条件：Qt runtime 已放在 `/userdata/qt5`，应用目录为 `/userdata/smart_retail`，Weston 已可用，扫码枪插入已验证的 USB Host 口。

```sh
sh /userdata/start_retail_hdmi_qml.sh
```

恢复默认 Weston 桌面：

```sh
sh /userdata/restore_default_weston.sh
```

ADB 部署脚本默认只用于应用层文件，不涉及 boot/rootfs/oem/uboot，也不执行 RKDevTool Upgrade/EraseFlash。部署前请先备份 `/userdata/smart_retail`。

## 云支付演示服务

云服务目录：`cloud_payment_service/`。Ubuntu 上建议使用 systemd + Gunicorn：

```bash
sudo APP_DIR=/opt/qsm-payment PORT=8000 bash tools/ubuntu_payment_server_bootstrap.sh
curl http://127.0.0.1:8000/health
```

服务提供：

- `GET /health`
- `POST /api/orders`
- `GET /api/orders/<cloud_order_id>`
- `/pay/<cloud_order_id>` 手机演示支付页
- `/dashboard` 订单和事件后台

真实支付接入还需要域名/HTTPS、平台商户审核、签名验签、回调幂等、退款/关单和管理员鉴权，本仓库不包含任何真实商户凭据。

## 回归测试

板端应用目录下可运行：

```sh
python3 tools/scan_api_matrix_test.py
python3 tools/qml_business_api_test.py
python3 tools/input_arbitration_api_test.py
python3 tools/capture_stress_test.py
python3 tools/audio_event_matrix_test.py
python3 tools/rknn_cli_smoke_test.py
wget -qO- http://127.0.0.1:5000/api/state | head -c 1500
```

测试脚本分清了三类证据：后端 API 自动测试、板端设备/运行时自检、HDMI/扫码枪/摄像头/耳机的现场人工验收。自动 PASS 不替代肉眼显示和真实 USB 设备验收。

## 毕昇杯评审建议

建议评审按以下顺序看：

1. `BISHENG_CUP_PROJECT_UPGRADE_PLAN.md`
2. `BISHENG_CUP_SUBMISSION_CHECKLIST.md`
3. `docs/DEPLOYMENT.md`
4. `docs/TESTING.md`
5. `docs/EVIDENCE.md`
6. `API_CONTRACT.md` 和 `VISION_API_CONTRACT.md`

演示时应明确说明：扫码负责可靠计价，RKNN/NPU 负责端侧辅助校验；当前 10-SKU 是低样本 baseline，报告必须同时给出样本规模、划分方式、Top-1/Top-3、延迟和失败样例。

## 安全与公开范围

- 不提交 SSH 私钥、AWS 密钥、支付 token、现场订单数据库或带凭据的日志。
- 不在代码中固化生产支付地址；板端通过状态配置或环境变量注入云端地址。
- 不公开 Buildroot SDK、完整 rootfs、训练原图和带个人信息的现场照片。
- 任何刷机、rootfs/boot 写入和系统级 autostart 都不属于本应用仓库的正常部署流程。

## 许可证

见 `LICENSE`。比赛提交前请再核对队员、指导教师、截止时间和赛区要求，以正式通知为准。
