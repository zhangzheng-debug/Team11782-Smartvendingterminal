import QtQuick 2.12
import QtQuick.Controls 2.5
import QtQuick.Layouts 1.12

Rectangle {
    id: root
    signal refresh()
    signal capture()
    signal speech()
    signal removeLast()
    signal clearCart()
    signal checkout()
    property bool busy: false
    property bool captureBusy: false
    property bool speechBusy: false
    property bool compact: false
    height: compact ? 82 : 104
    color: "#E5E7EB"

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: compact ? 12 : 20
        anchors.rightMargin: compact ? 12 : 20
        spacing: compact ? 8 : 12

        Button {
            text: "刷新"
            enabled: true
            Layout.fillWidth: true
            Layout.preferredHeight: compact ? 58 : 76
            font.pixelSize: compact ? 18 : 24
            font.family: "Noto Sans SC"
            onClicked: root.refresh()
        }
        Button {
            text: root.captureBusy ? "拍照中" : "拍照"
            enabled: !root.captureBusy
            Layout.fillWidth: true
            Layout.preferredHeight: compact ? 58 : 76
            font.pixelSize: compact ? 18 : 24
            font.family: "Noto Sans SC"
            onClicked: root.capture()
        }
        Button {
            text: root.speechBusy ? "识别中" : "语音唤醒"
            enabled: !root.speechBusy
            Layout.fillWidth: true
            Layout.preferredHeight: compact ? 58 : 76
            font.pixelSize: compact ? 18 : 24
            font.family: "Noto Sans SC"
            onClicked: root.speech()
        }
        Button {
            text: "删除上一件"
            enabled: !root.busy
            Layout.fillWidth: true
            Layout.preferredHeight: compact ? 58 : 76
            font.pixelSize: compact ? 17 : 24
            font.family: "Noto Sans SC"
            onClicked: root.removeLast()
        }
        Button {
            text: "清空"
            enabled: !root.busy
            Layout.fillWidth: true
            Layout.preferredHeight: compact ? 58 : 76
            font.pixelSize: compact ? 18 : 24
            font.family: "Noto Sans SC"
            background: Rectangle {
                radius: 6
                color: root.busy ? "#CBD5E1" : "#F97316"
            }
            contentItem: Text {
                text: parent.text
                color: "#FFFFFF"
                font: parent.font
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            onClicked: root.clearCart()
        }
        Button {
            text: "结账"
            enabled: !root.busy
            Layout.fillWidth: true
            Layout.preferredHeight: compact ? 58 : 76
            font.pixelSize: compact ? 20 : 26
            font.bold: true
            font.family: "Noto Sans SC"
            background: Rectangle {
                radius: 6
                color: root.busy ? "#CBD5E1" : "#16A34A"
            }
            contentItem: Text {
                text: parent.text
                color: "#FFFFFF"
                font: parent.font
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            onClicked: root.checkout()
        }
    }
}
