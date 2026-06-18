# API Contract / 接口说明

Base URL:

```text
http://127.0.0.1:5000
```

## Health and State

| Method | Path | 说明 |
| --- | --- | --- |
| GET | `/api/health` | API 健康检查 |
| GET | `/health` | 简化健康检查 |
| GET | `/api/state` | QML 主状态，包含购物车、订单、视觉、语音、音频等 |
| GET | `/api/metrics` | 系统指标 |
| GET | `/metrics` | 指标页面/文本 |

## Products, Scan and Cart

| Method | Path | 说明 |
| --- | --- | --- |
| GET | `/products` | 商品页面 |
| POST | `/api/scan` | 扫码或 SKU 输入，加购已知商品，未知条码返回明确错误 |
| POST | `/api/cart/add` | 加入商品 |
| POST | `/api/cart/remove_last` | 删除上一件 |
| POST | `/api/cart/remove_product` | 删除指定商品 |
| POST | `/api/cart/clear` | 清空购物车 |

`POST /api/scan` 示例：

```json
{
  "barcode": "SKU001"
}
```

成功响应包含：

```json
{
  "ok": true,
  "success": true,
  "product_id": "SKU001",
  "product_name": "三元酸奶",
  "cart": {},
  "total_price_cent": 350
}
```

未知条码响应包含：

```json
{
  "ok": false,
  "success": false,
  "error_reason": "unknown_barcode",
  "message": "未录入商品：UNKNOWN_TEST_001"
}
```

## Orders and Payment

| Method | Path | 说明 |
| --- | --- | --- |
| POST | `/api/checkout` | 生成订单 |
| GET | `/api/order/<order_id>` | 查询订单 |
| POST | `/api/order/<order_id>/sync_cloud` | 同步云端订单状态 |
| POST | `/api/payment/sync_latest` | 同步最近订单支付状态 |
| POST | `/api/payment/qr/regenerate` | 重新生成支付二维码 |
| POST | `/api/order/<order_id>/promote_cloud` | 将本地订单提升为云支付订单 |
| GET | `/api/cloud/status` | 云支付状态 |
| POST | `/api/cloud/test_order` | 创建云支付测试订单 |

## Capture and Vision

| Method | Path | 说明 |
| --- | --- | --- |
| POST | `/api/capture` | 拍照，返回图片路径、URL、耗时和状态 |
| POST | `/api/captures/cleanup` | 清理旧照片 |
| GET | `/api/vision/status` | 视觉后端状态，期望 `active_backend=rknn_cli` |
| POST | `/api/vision/predict` | 对图片进行视觉预测 |
| POST | `/api/vision/candidates` | 未知条码候选商品 |
| POST | `/api/vision/verify_scan` | 扫码后视觉辅助校验 |
| POST | `/api/vision/confirm` | 人工确认视觉候选 |

## Speech and Audio

| Method | Path | 说明 |
| --- | --- | --- |
| POST | `/api/speech/execute` | 执行文本语音命令 |
| POST | `/api/speech/auto_once` | 单次自动语音识别 |
| GET | `/api/speech/menu` | 数字语音菜单 |
| POST | `/api/speech/cancel` | 取消语音会话 |
| POST | `/api/speech/guard/start` | 启动语音守候 |
| POST | `/api/speech/guard/stop` | 停止语音守候 |
| GET | `/api/speech/guard/status` | 语音守候状态 |
| GET | `/api/audio/status` | 音频设备状态 |
| POST | `/api/audio/set` | 设置输入/输出音频设备 |
| POST | `/api/audio/test_output` | 播放测试音或事件音 |
| POST | `/api/audio/test_record` | 录音测试 |

## Web Pages

| Path | 说明 |
| --- | --- |
| `/` | Web 调试首页 |
| `/dashboard` | 订单/指标面板 |
| `/cloud` | 云支付调试页 |
| `/audio` | 音频调试页 |
| `/speech` | 语音调试页 |
| `/network` | 网络调试页 |

