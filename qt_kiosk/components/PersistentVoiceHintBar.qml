import QtQuick 2.12
import QtQuick.Layouts 1.12

Rectangle {
    id: root
    property bool compact: false
    height: compact ? 64 : 88
    color: "#0F172A"
    border.color: "#38BDF8"
    border.width: 1

    ColumnLayout {
        anchors.fill: parent
        anchors.leftMargin: compact ? 16 : 26
        anchors.rightMargin: compact ? 16 : 26
        anchors.topMargin: compact ? 6 : 10
        anchors.bottomMargin: compact ? 6 : 10
        spacing: compact ? 2 : 4

        Text {
            Layout.fillWidth: true
            text: "语音指令：先说“小售小售”，再说编号短语"
            color: "#F8FAFC"
            font.family: "Noto Sans SC"
            font.pixelSize: compact ? 20 : 30
            font.bold: true
            elide: Text.ElideRight
        }

        Text {
            Layout.fillWidth: true
            text: "1号查询总价 / 2号删除上一件 / 3号清空购物车 / 4号结账 / 5号拍照识别 / 0号取消    示例：小售小售四号结账"
            color: "#BAE6FD"
            font.family: "Noto Sans SC"
            font.pixelSize: compact ? 16 : 24
            font.bold: true
            elide: Text.ElideRight
        }
    }
}
