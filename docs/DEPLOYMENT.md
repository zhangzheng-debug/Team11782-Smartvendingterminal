# 部署说明

## 板端应用层部署

1. 确认 ADB 输出中设备状态为 `device`。
2. 备份 `/userdata/smart_retail`。
3. 仅部署应用目录、QML 和 `/userdata` 启动脚本。
4. 运行 `start_retail_hdmi_qml.sh`。
5. 用 `/api/state`、HDMI、扫码枪和摄像头做验收。

本项目不需要刷写 boot、rootfs、oem、uboot，也不需要 RKDevTool Upgrade/EraseFlash。

## 云端演示服务

`cloud_hotfix_v2611a/` 是本工作区的独立 Flask/Gunicorn 演示支付服务，公开仓库整理为 `cloud_payment_service/`。生产化部署应使用 HTTPS 反向代理、域名、签名验签、回调幂等、鉴权和密钥管理。不要把真实支付凭据放入仓库。

## 板端切换云地址

板端已有状态配置接口，切换前先备份并确认新服务 `/health`：

```sh
cd /userdata/smart_retail
python3 - <<'PY'
from app import get_cloud_base_url, set_cloud_base_url
set_cloud_base_url("http://payment-host:8000")
print(get_cloud_base_url())
PY
wget -qO- http://127.0.0.1:5000/api/cloud/status
```

示例地址必须替换为现场实际的 HTTPS 或局域网地址。
