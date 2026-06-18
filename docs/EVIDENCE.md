# Evidence / 证据材料说明

本仓库保留了适合公开上传的关键证据，完整现场照片和视频可在答辩材料中补充。

## 已随仓库上传

- `evidence/screenshots/board_current_screen.png`
- `evidence/screenshots/dataset_contact_sheet_v260.jpg`
- `data/10sku_manifest/contact_sheet.jpg`
- `data/10sku_manifest/manifest.csv`
- `model_artifacts/onnx/`
- `model_artifacts/rknn/`

## 建议答辩展示证据

1. HDMI QML 收银台主界面
2. 扫码枪加购商品
3. 未知条码提示
4. 拍照预览与视觉 Top-3
5. `active_backend=rknn_cli` 状态
6. 云支付 paid 回写
7. HyperX 或 USB 声卡枚举
8. 中文人声播报现场视频
9. 扫码枪、摄像头、HDMI、音频接口接线照片
10. 回归测试 PASS 输出

## 关键答辩表述

- 系统是板端 HDMI QML 收银台，不依赖电脑浏览器作为主界面。
- 条码是稳定收银主通道，视觉用于端侧 AI 辅助校验。
- RKNN/NPU 后端已经接入，ONNX fallback 保留。
- 云端支付完成 paid 回写，本地订单状态可同步。
- 当前 10-SKU 模型是低样本 baseline，需要更多商品图片提升泛化能力。

