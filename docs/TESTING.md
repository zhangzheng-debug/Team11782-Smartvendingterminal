# Testing / 测试说明

## 基础 API

```sh
python3 tools/api_smoke_test.py
wget -qO- http://127.0.0.1:5000/api/state | head -c 1500
```

## 收银业务

```sh
python3 tools/scan_api_matrix_test.py
python3 tools/qml_business_api_test.py
python3 tools/input_arbitration_api_test.py
```

覆盖点：

- SKU001 到 SKU010 可扫码加购
- 未知条码有明确反馈
- 语音输入框中输入 SKU/条码时优先走扫码
- 购物车、总价、删除、清空、结账状态正确

## 拍照与视觉

```sh
python3 tools/capture_stress_test.py
python3 tools/vision_model_status_test.py
python3 tools/vision_predict_smoke_test.py
python3 tools/vision_scan_verify_test.py
python3 tools/vision_no_repeat_add_test.py
python3 tools/rknn_cli_smoke_test.py
python3 tools/vision_rknn_cli_backend_test.py
```

覆盖点：

- 拍照互斥、冷却、超时和清理策略稳定
- `active_backend=rknn_cli`
- 视觉结果只做辅助校验，不重复加购

## 音频与语音播报

```sh
python3 tools/audio_asset_audit.py
python3 tools/audio_event_matrix_test.py
```

人工确认：

- 扫码成功有播报
- 未知商品有播报
- 拍照开始/成功/失败有播报
- 结账和支付成功有播报
- 音频设备异常时主业务不崩溃

## 云支付

```sh
python3 tools/cloud_payment_probe.py --base http://127.0.0.1:5000 --create-test-order
python3 tools/payment_phone_first_cloud_test.py
```

验收点：

- checkout 生成 `cloud_pay_url`
- 手机可打开云端支付页
- 模拟支付后云端订单 paid
- 板端订单同步 paid
- QML 显示 paid
- 触发 `payment_success` 播报

## 最小提交前检查

```powershell
python -m py_compile app.py terminal_kiosk.py tools/api_smoke_test.py tools/scan_api_matrix_test.py tools/qml_business_api_test.py
git status --short
```

