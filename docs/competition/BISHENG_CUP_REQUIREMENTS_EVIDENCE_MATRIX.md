# 初赛要求与证据矩阵

状态含义：`已有材料` 不等于本次现场通过；`待现场` 必须在初赛提交包中放入照片、视频或带日期的日志。

| 要求/评审关注 | 作品响应 | 代码/文档入口 | 当前状态 | 提交前动作 |
| --- | --- | --- | --- | --- |
| 真实应用问题 | 小型无人值守零售收银 | `docs/competition/BISHENG_CUP_DESIGN_REPORT_DRAFT.md` | 已有材料 | 补场景照片和成本表 |
| 电子系统完整性 | 板端、HDMI、扫码枪、摄像头、音频 | `docs/HARDWARE_CONNECTIONS.md` | 待现场 | 拍一张全连接图 |
| 可靠计费 | barcode/HID 主通道、购物车/订单 | `app.py`、`tools/scan_api_matrix_test.py` | 有自动化材料 | 现场扫 2 个 SKU |
| 视觉创新 | RKNN/NPU Top-3 校验和未知候选 | `VISION_API_CONTRACT.md`、`V263_*` | 有历史材料 | 采本次 status/predict |
| 防误计费 | 视觉不连续自动加购 | `VISION_TRIGGER_POLICY.md` | 已有设计 | 视频中明确演示 |
| 本机交互 | Qt/QML Weston HDMI | `qt_kiosk/`、启动脚本 | 待现场 | 拍 HDMI 可见画面 |
| 语音/可访问性 | 中文固定播报、短语命令 | `AUDIO_BROADCAST_POLICY.md` | 有自动化材料 | 戴 HyperX 录短视频 |
| 支付闭环 | 本地订单 + 仿真云支付 paid 回写 | `CLOUD_PAYMENT_*`、支付服务 | 部分待现场 | 标注“仿真”，补手机访问证据 |
| 经济性 | 板端 + USB 外设 + 开源软件 | 设计报告第 6 节 | 待补 | 填 BOM 和估算价 |
| 可复现性 | README、依赖、测试脚本 | `README.md`、`requirements*.txt` | 已改善 | 干净环境跑 smoke |
| 公开安全 | 无私钥、现场 DB、真实凭据 | `.gitignore`、公开仓库 | 需复核 | 提交前做 secrets scan |
| 诚实限制 | 小样本、支付仿真、网络依赖 | `V263_LIMITATIONS_HONEST_LIST.md` | 已有材料 | 统一到最终报告 |
