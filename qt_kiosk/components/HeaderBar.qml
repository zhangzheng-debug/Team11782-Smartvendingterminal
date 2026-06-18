import QtQuick 2.12
import QtQuick.Controls 2.5
import QtQuick.Layouts 1.12

Rectangle {
    id: root
    property string terminalId: "QSM368ZP-WF-001"
    property string clockText: "--"
    property string paymentStatus: "idle"
    property bool online: false
    property bool compact: false
    height: compact ? 78 : 92
    color: "#111827"

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: compact ? 18 : 30
        anchors.rightMargin: compact ? 18 : 30
        spacing: compact ? 14 : 22

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 2
            Text {
                text: "QSM368ZP-WF 智能零售终端"
                color: "#F9FAFB"
                font.pixelSize: compact ? 26 : 34
                font.bold: true
                font.family: "Noto Sans SC"
                elide: Text.ElideRight
            }
            Text {
                text: terminalId
                color: "#A7F3D0"
                font.pixelSize: compact ? 14 : 18
                font.family: "Noto Sans SC"
                elide: Text.ElideRight
            }
        }

        Rectangle {
            width: compact ? 14 : 18
            height: compact ? 14 : 18
            radius: width / 2
            color: online ? "#22C55E" : "#EF4444"
        }

        ColumnLayout {
            spacing: 2
            Text {
                text: online ? "API 在线" : "API 离线"
                color: online ? "#BBF7D0" : "#FECACA"
                font.pixelSize: compact ? 16 : 20
                font.bold: true
                font.family: "Noto Sans SC"
            }
            Text {
                text: "支付状态：" + paymentStatus
                color: "#E5E7EB"
                font.pixelSize: compact ? 13 : 16
                font.family: "Noto Sans SC"
            }
        }

        Text {
            text: clockText
            color: "#E5E7EB"
            font.pixelSize: compact ? 17 : 22
            font.family: "Noto Sans SC"
            horizontalAlignment: Text.AlignRight
        }
    }
}
