import QtQuick 2.12
import QtQuick.Controls 2.5
import QtQuick.Layouts 1.12
import "../retail_api.js" as RetailApi

Dialog {
    id: root

    property var order: ({})
    property bool qrLoadError: false
    property string qrStatusText: ""
    property string cloudStatusText: ""
    property bool paidSuccessState: false
    property bool syncBusy: false
    property string syncStatusText: ""

    signal paidConfirmed(var order)

    modal: true
    focus: true
    title: "支付订单"
    standardButtons: Dialog.Close
    property bool compact: parent ? (parent.width <= 2000 || parent.height <= 1150) : false
    width: Math.min(parent ? parent.width * (compact ? 0.82 : 0.72) : 1040, compact ? 980 : 1120)
    height: Math.min(parent ? parent.height * 0.90 : 860, compact ? 900 : 920)

    onVisibleChanged: {
        if (visible) {
            paidSuccessState = isPaid();
            syncStatusText = paidSuccessState ? "支付成功" : "正在等待支付确认...";
            if (paidSuccessState) {
                pollingTimer.stop();
            } else {
                pollingTimer.restart();
            }
        } else {
            pollingTimer.stop();
            closeAfterPaidTimer.stop();
            syncBusy = false;
        }
    }

    function mode() {
        return order.payment_mode || order.payment_url_type || (order.cloud_pay_url ? "cloud" : (order.local_debug_only ? "local_debug" : "lan"));
    }

    function accessibility() {
        return order.payment_accessibility || (mode() === "cloud" ? "phone_accessible" : (mode() === "lan" ? "same_lan_required" : "local_debug_only"));
    }

    function isPaid() {
        return order && (order.payment_status === "paid" || order.cloud_status === "paid" || order.order_status === "paid");
    }

    function paymentModeText() {
        if (paidSuccessState) return "支付成功";
        if (mode() === "cloud") return "云端支付：手机可扫码";
        if (mode() === "lan") return "局域网支付：手机需同一网络";
        return "本地调试：手机不可访问";
    }

    function paymentModeDetail() {
        if (paidSuccessState) return "订单已 paid，正在返回收银台。";
        if (mode() === "cloud") return "当前二维码内容是 cloud_pay_url，手机可打开云端支付页。";
        if (mode() === "lan") return "当前二维码内容是板端局域网地址，手机必须和板子在同一 LAN。";
        return "当前二维码是 127.0.0.1 或本机调试地址，手机扫码无法访问。";
    }

    function modeColor() {
        if (paidSuccessState || mode() === "cloud") return "#166534";
        if (mode() === "lan") return "#B45309";
        return "#B91C1C";
    }

    function modeBg() {
        if (paidSuccessState || mode() === "cloud") return "#DCFCE7";
        if (mode() === "lan") return "#FEF3C7";
        return "#FEE2E2";
    }

    function paymentLinkText() {
        return order.cloud_pay_url || order.payment_qr_content || order.preferred_payment_url || order.local_pay_url || "";
    }

    function qrSource() {
        return order.payment_qr_file_url || order.payment_qr_url || order.qr_image_url || "";
    }

    function applySyncedOrder(nextOrder, message) {
        if (nextOrder) order = nextOrder;
        paidSuccessState = isPaid();
        syncStatusText = message || (paidSuccessState ? "支付成功" : "正在等待支付确认...");
        if (paidSuccessState) {
            pollingTimer.stop();
            paidConfirmed(order);
            closeAfterPaidTimer.restart();
        }
    }

    function syncPaymentStatus() {
        if (!visible || syncBusy || isPaid()) return;
        var orderId = order.order_id || "";
        if (!orderId) {
            syncStatusText = "缺少订单号，无法同步支付状态";
            return;
        }
        syncBusy = true;
        syncStatusText = "正在等待支付确认...";
        RetailApi.syncOrderCloud(orderId, function(ok, data) {
            syncBusy = false;
            if (ok && data && data.order) {
                applySyncedOrder(data.order, data.message || "");
            } else if (data && data.error_reason === "cloud_unreachable") {
                syncStatusText = "云端暂不可达，稍后自动重试";
            } else {
                syncStatusText = (data && (data.message || data.error || data.error_reason)) || "支付状态同步失败，稍后重试";
            }
        });
    }

    Timer {
        id: pollingTimer
        interval: 1200
        repeat: true
        running: false
        onTriggered: syncPaymentStatus()
    }

    Timer {
        id: closeAfterPaidTimer
        interval: 1800
        repeat: false
        onTriggered: root.close()
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: root.compact ? 12 : 16
        spacing: root.compact ? 7 : 10

        Text {
            text: "订单号：" + (order.order_id || "")
            color: "#111827"
            font.pixelSize: root.compact ? 22 : 28
            font.bold: true
            font.family: "Noto Sans SC"
            horizontalAlignment: Text.AlignHCenter
            Layout.fillWidth: true
        }

        Text {
            text: order.total_text || ""
            color: paidSuccessState ? "#166534" : "#DC2626"
            font.pixelSize: root.compact ? 42 : 54
            font.bold: true
            font.family: "Noto Sans SC"
            horizontalAlignment: Text.AlignHCenter
            Layout.fillWidth: true
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: root.compact ? 72 : 88
            radius: 8
            color: modeBg()
            border.color: modeColor()
            Column {
                anchors.centerIn: parent
                width: parent.width - 28
                spacing: 4
                Text {
                    text: paymentModeText()
                    color: modeColor()
                    font.pixelSize: root.compact ? 22 : 30
                    font.bold: true
                    font.family: "Noto Sans SC"
                    horizontalAlignment: Text.AlignHCenter
                    width: parent.width
                }
                Text {
                    text: paidSuccessState ? "支付成功，正在返回收银台" : (order.qr_user_message || paymentModeDetail())
                    color: modeColor()
                    font.pixelSize: root.compact ? 15 : 20
                    font.bold: true
                    font.family: "Noto Sans SC"
                    horizontalAlignment: Text.AlignHCenter
                    wrapMode: Text.WordWrap
                    width: parent.width
                }
            }
        }

        Rectangle {
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: Math.min(root.compact ? 300 : 390, root.width * 0.42, root.height * 0.36)
            Layout.preferredHeight: Layout.preferredWidth
            radius: 8
            border.color: paidSuccessState ? "#22C55E" : "#CBD5E1"
            color: "#FFFFFF"

            Image {
                id: qrImage
                anchors.fill: parent
                anchors.margins: 14
                fillMode: Image.PreserveAspectFit
                cache: false
                opacity: paidSuccessState ? 0.16 : (accessibility() === "local_debug_only" ? 0.38 : 1.0)
                source: qrSource()
                onStatusChanged: {
                    if (status === Image.Error) {
                        root.qrLoadError = true;
                        root.qrStatusText = "二维码加载失败";
                    } else if (status === Image.Ready) {
                        root.qrLoadError = false;
                        root.qrStatusText = "二维码已加载";
                    } else if (status === Image.Loading) {
                        root.qrStatusText = "二维码加载中";
                    }
                }
            }

            Rectangle {
                anchors.fill: parent
                anchors.margins: 12
                visible: paidSuccessState || accessibility() === "local_debug_only" || !qrImage.source || root.qrLoadError || order.qr_exists === false
                color: paidSuccessState ? "#166534" : (accessibility() === "local_debug_only" ? "#7F1D1D" : "#FEF2F2")
                opacity: paidSuccessState ? 0.94 : (accessibility() === "local_debug_only" ? 0.88 : 0.96)
                border.color: paidSuccessState ? "#22C55E" : "#FCA5A5"
                radius: 6
                Text {
                    anchors.centerIn: parent
                    width: parent.width - 28
                    text: paidSuccessState
                          ? "支付成功\n即将自动返回收银台"
                          : accessibility() === "local_debug_only"
                            ? "仅本地调试\n手机扫码无法访问\n请恢复云端网络后升级云支付"
                            : ((root.qrLoadError ? "二维码加载失败" : (order.qr_error || "等待二维码")) +
                               "\n原因：" + (order.qr_error || root.qrStatusText || "-") +
                               "\n支付链接：" + paymentLinkText())
                    color: paidSuccessState || accessibility() === "local_debug_only" ? "#FFFFFF" : "#7F1D1D"
                    font.pixelSize: root.compact ? 18 : 24
                    font.bold: true
                    font.family: "Noto Sans SC"
                    wrapMode: Text.WrapAnywhere
                    horizontalAlignment: Text.AlignHCenter
                }
            }
        }

        Text {
            text: "当前二维码内容：" + paymentLinkText()
            color: modeColor()
            font.pixelSize: root.compact ? 15 : 19
            font.bold: true
            font.family: "Noto Sans SC"
            wrapMode: Text.WrapAnywhere
            horizontalAlignment: Text.AlignHCenter
            Layout.fillWidth: true
        }

        Text {
            text: "手机可访问性：" + accessibility() + " / " + paymentModeDetail()
            color: "#334155"
            font.pixelSize: root.compact ? 14 : 18
            font.family: "Noto Sans SC"
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }

        Text {
            text: syncStatusText.length > 0 ? syncStatusText : cloudStatusText
            visible: syncStatusText.length > 0 || cloudStatusText.length > 0
            color: paidSuccessState ? "#166534" : "#B45309"
            font.pixelSize: root.compact ? 14 : 18
            font.bold: true
            font.family: "Noto Sans SC"
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }

        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 12

            Button {
                text: "刷新支付状态"
                Layout.preferredWidth: root.compact ? 150 : 190
                Layout.preferredHeight: root.compact ? 44 : 54
                font.pixelSize: root.compact ? 14 : 18
                enabled: !paidSuccessState && !syncBusy
                onClicked: syncPaymentStatus()
            }

            Button {
                text: "重新生成二维码"
                Layout.preferredWidth: root.compact ? 170 : 210
                Layout.preferredHeight: root.compact ? 44 : 54
                font.pixelSize: root.compact ? 14 : 18
                enabled: !paidSuccessState
                onClicked: {
                    RetailApi.regeneratePaymentQr(order.order_id || "", function(ok, data) {
                        if (data && data.order) {
                            root.order = data.order;
                            root.qrLoadError = false;
                            root.qrStatusText = ok ? "二维码已重新生成" : (data.qr_error || "二维码生成失败");
                        } else {
                            root.qrLoadError = true;
                            root.qrStatusText = "二维码生成失败";
                        }
                    });
                }
            }

            Button {
                text: "检查云端网络"
                Layout.preferredWidth: root.compact ? 170 : 210
                Layout.preferredHeight: root.compact ? 44 : 54
                font.pixelSize: root.compact ? 14 : 18
                enabled: !paidSuccessState
                onClicked: {
                    cloudStatusText = "正在检查云支付";
                    RetailApi.cloudStatus(function(ok, data) {
                        if (ok && data && data.cloud_health_ok) {
                            cloudStatusText = "云端在线：" + (data.cloud_base_url || "");
                        } else {
                            cloudStatusText = "云端不可用：" + ((data && (data.error || data.message)) || "unknown");
                        }
                    });
                }
            }

            Button {
                text: "升级云端二维码"
                visible: mode() !== "cloud"
                Layout.preferredWidth: root.compact ? 180 : 220
                Layout.preferredHeight: root.compact ? 44 : 54
                font.pixelSize: root.compact ? 14 : 18
                enabled: !paidSuccessState
                onClicked: {
                    cloudStatusText = "正在尝试升级云端订单";
                    RetailApi.promoteOrderCloud(order.order_id || "", function(ok, data) {
                        if (ok && data && data.order) {
                            root.order = data.order;
                            root.qrLoadError = false;
                            cloudStatusText = "云端二维码已生成，手机可扫码";
                        } else {
                            cloudStatusText = "升级失败：" + ((data && (data.message || data.error_reason)) || "云端不可用");
                        }
                    });
                }
            }

            Button {
                text: "关闭"
                Layout.preferredWidth: root.compact ? 100 : 130
                Layout.preferredHeight: root.compact ? 44 : 54
                font.pixelSize: root.compact ? 14 : 18
                onClicked: root.close()
            }
        }
    }
}
