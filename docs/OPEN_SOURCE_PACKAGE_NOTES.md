# Open Source Package Notes / 开源包说明

本仓库按照公开评审和技术复现需求进行整理，重点上传可阅读、可运行、可验证的核心材料。

## 已包含

- 应用层代码
- Qt/QML 前端
- 部署和恢复脚本
- 测试脚本
- 10-SKU 商品 manifest
- ONNX/RKNN 模型产物
- RKNN CLI runtime bridge
- 中文播报 WAV 资产
- 云支付服务示例代码
- 关键截图和 contact sheet

## 未包含

- 原始训练图片全集
- 现场运行数据库
- ADB 私有路径配置
- 云服务器私钥和凭据
- Buildroot SDK、Qt runtime 构建目录和系统镜像
- `pydeps` 这类板端临时 Python 依赖缓存

这些内容未上传的原因主要是体积、隐私、安全和第三方许可限制。

## 复现建议

1. 先本地运行 Flask 后端。
2. 再在板端部署 `/userdata/smart_retail`。
3. 确认 `/userdata/qt5` runtime 存在。
4. 用测试脚本逐项验证扫码、拍照、音频、视觉和支付。
5. 如果需要重新训练视觉模型，请按 `data/10sku_manifest/manifest.csv` 扩充图片数据。

