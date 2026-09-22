# AWS 支付演示节点部署记录

更新时间：2026-09-22

## 当前节点

| 项目 | 值 |
| --- | --- |
| 区域 | `ap-northeast-2` |
| 实例 | `i-0da0fa1d09386cf7a` |
| 系统 | Ubuntu Server 24.04 LTS x86_64 |
| 类型 | `t3.micro` |
| 磁盘 | 20 GiB 加密 gp3，随实例终止删除 |
| 服务 | `qsm-payment`，systemd + Gunicorn |
| 端口 | TCP 8000，比赛迁移/演示用途 |
| 状态 | `/health`、订单创建、支付页、模拟 `paid` 回写已验证 |

公网地址和 SSH 私钥不写入公开材料。板端通过 `/userdata` 状态配置注入实际云服务地址。

## 已完成验证

- `GET /health` 返回 `ok=true`。
- `POST /api/orders` 返回 `cloud_pay_url`。
- 手机支付页可打开，页面包含“模拟支付成功”。
- 点击模拟支付后显示“支付成功”，云端订单状态变为 `paid`。
- systemd 服务已启用，应用不使用 Flask 开发服务器对外提供服务。
- 初始无法维护的临时实例已终止；旧 Windows/MT5 实例已按用户确认终止。

## 当前板端状态

板端支付地址已切换到新节点，但本次采集时 `eth0` carrier 为 `0`、没有默认路由，因此 `/api/cloud/status` 仍报告 `Network is unreachable`。这不是云服务故障；接通板端网线并配置路由后需要重新执行：

```sh
wget -qO- http://<payment-host>:8000/health
wget -qO- http://127.0.0.1:5000/api/cloud/status
```

只有板端 `/health` 成功并完成一次手机支付/paid 回写，才能把板端云支付现场证据标为 PASS。

## 后续安全动作

1. 给节点绑定 Elastic IP 或域名，避免自动公网 IP 变化。
2. 使用 HTTPS 反向代理，关闭长期公开的 8000 管理入口。
3. 把 SSH 入站限制为当前操作 IP，定期轮换密钥。
4. 真实商户支付必须另行完成商户审核、签名验签、回调幂等和退款/关单。
