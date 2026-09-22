# Quick Start / 快速启动

## 1. 本地 Web 调试

适用于在 Windows 或 Linux PC 上查看 Flask API 和调试页面。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

访问：

```text
http://127.0.0.1:5000
http://127.0.0.1:5000/api/state
```

说明：

- 本地 PC 调试不等价于板端 RKNN/NPU 演示。
- 若没有摄像头、音频设备或 RKNN runtime，相关接口会降级或返回诊断信息。

## 2. 板端启动 QML 收银台

板端目录约定：

```text
/userdata/smart_retail
/userdata/qt5
```

启动：

```sh
sh /userdata/start_retail_hdmi_qml.sh
```

恢复默认 Weston：

```sh
sh /userdata/restore_default_weston.sh
```

确认状态：

```sh
pgrep -af 'app.py|weston|qmlscene'
wget -qO- http://127.0.0.1:5000/api/state | head -c 1200
```

## 3. 现场硬件检查

- HDMI 显示器已连接并选择正确输入源
- 扫码枪插在已验证 USB Host 口
- HyperX Cloud III 或 USB 声卡在 `aplay -l` 和 `arecord -l` 中可见
- 摄像头在 `/dev/video*` 中可见
- 如需云支付，板端必须能访问 `http://<payment-host>:8000/health`

## 4. 演示流程

1. 启动 QML 收银台
2. 扫 SKU001 到 SKU010 中任一商品
3. 查看购物车、总价和视觉辅助校验
4. 扫未知条码，确认显示“未录入商品”
5. 点击拍照，查看图像预览和视觉候选
6. 使用语音/文本命令查询总价、删除上一件或结账
7. 点击结账，展示支付弹窗和订单状态

