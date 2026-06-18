# Limitations / 限制与诚实说明

## 视觉模型

- 当前 10-SKU 数据集样本量较小，属于 baseline。
- 部分类别低于建议的 40 到 60 张多角度图片。
- 视觉结果用于辅助校验和未知条码候选，不作为自动连续加购依据。

## 硬件依赖

- 扫码枪必须插在已验证 USB Host 口，否则可能出现“扫码枪响但 QML 没反应”。
- HyperX Cloud III 或 USB 声卡需要被 ALSA 枚举，推荐设备名为 `plughw:CARD=III,DEV=0`。
- 云支付演示依赖板端公网出口，Windows ICS/NAT 不稳定时建议使用真实路由器。

## 运行时依赖

- QML 前端依赖 `/userdata/qt5` 中的 Qt Quick/QML runtime。
- RKNN 后端依赖板端 RKNN runtime 和 `vision_rknn_cli`。
- 本仓库不包含完整 Buildroot SDK、Qt SDK、系统镜像或刷机文件。

## 未启用内容

- 未做系统级开机自启动。
- 不修改 `/etc/init.d/S03weston`。
- 不刷写 boot/rootfs/oem/uboot。

