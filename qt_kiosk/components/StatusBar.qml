import QtQuick 2.12
import QtQuick.Controls 2.5
import QtQuick.Layouts 1.12

Rectangle {
    id: root
    property bool online: false
    property string paymentStatus: "idle"
    property string audioStatus: ""
    property string message: ""
    property bool compact: false
    height: compact ? 46 : 58
    color: "#0F172A"

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: compact ? 14 : 26
        anchors.rightMargin: compact ? 14 : 26
        spacing: compact ? 12 : 20

        Text {
            text: online ? "后端已连接" : "后端断开"
            color: online ? "#86EFAC" : "#FCA5A5"
            font.pixelSize: compact ? 14 : 19
            font.family: "Noto Sans SC"
        }
        Text {
            text: "支付：" + paymentStatus
            color: "#E5E7EB"
            font.pixelSize: compact ? 14 : 19
            font.family: "Noto Sans SC"
        }
        Text {
            text: "音频：" + (audioStatus || "默认")
            color: "#E5E7EB"
            font.pixelSize: compact ? 14 : 19
            font.family: "Noto Sans SC"
            elide: Text.ElideMiddle
            Layout.preferredWidth: compact ? 230 : 340
        }
        Text {
            text: "最近动作：" + message
            color: "#FDE68A"
            font.pixelSize: compact ? 15 : 20
            font.bold: true
            font.family: "Noto Sans SC"
            elide: Text.ElideRight
            Layout.fillWidth: true
        }
    }
}
