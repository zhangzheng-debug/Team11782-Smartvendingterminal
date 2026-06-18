import QtQuick 2.12
import QtQuick.Controls 2.5
import QtQuick.Layouts 1.12

Rectangle {
    id: root
    property var products: []
    property var productsModel: null
    property bool compact: width <= 1050 || height <= 280
    signal addProduct(string productId, string productName)

    color: "#FFFFFF"
    radius: 6
    border.color: "#CBD5E1"

    function shortProductName(name, sku) {
        var s = String(name || sku || "");
        if (s.indexOf("立顿乌龙茶") >= 0) return "立顿乌龙茶";
        if (s.indexOf("西红柿") >= 0) return "西红柿面";
        if (s.indexOf("纳美科学") >= 0) return "纳美牙膏";
        if (s.indexOf("上海硫磺") >= 0) return "硫磺皂";
        if (s.length > 7) return s.substring(0, 7);
        return s;
    }

    function barcodeTail(code) {
        var s = String(code || "");
        return s.length > 4 ? s.substring(s.length - 4) : s;
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: root.compact ? 8 : 12
        spacing: root.compact ? 5 : 8

        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: root.compact ? 26 : 34

            Text {
                text: "快捷商品：10"
                color: "#111827"
                font.pixelSize: root.compact ? 18 : 26
                font.bold: true
                font.family: "Noto Sans SC"
                Layout.fillWidth: true
                elide: Text.ElideRight
            }

            Text {
                text: "SKU001 - SKU010"
                color: "#64748B"
                font.pixelSize: root.compact ? 12 : 16
                font.family: "Noto Sans SC"
            }
        }

        GridView {
            id: grid
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            interactive: false
            boundsBehavior: Flickable.StopAtBounds
            cellWidth: Math.max(116, width / 5)
            cellHeight: Math.max(root.compact ? 82 : 104, height / 2)
            model: productsModel || products || []

            delegate: Rectangle {
                width: grid.cellWidth - (root.compact ? 6 : 8)
                height: grid.cellHeight - (root.compact ? 6 : 8)
                radius: 6
                color: mouse.pressed ? "#DBEAFE" : "#F8FAFC"
                border.color: "#CBD5E1"

                MouseArea {
                    id: mouse
                    anchors.fill: parent
                    onClicked: root.addProduct(product_id, product_name)
                }

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: root.compact ? 5 : 8
                    spacing: root.compact ? 2 : 3

                    Text {
                        text: (product_id || "-") + " / " + root.shortProductName(short_name || product_name, product_id)
                        color: "#111827"
                        font.pixelSize: root.compact ? 13 : 18
                        font.bold: true
                        font.family: "Noto Sans SC"
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 4

                        Text {
                            text: price_text || ""
                            color: "#DC2626"
                            font.pixelSize: root.compact ? 17 : 24
                            font.bold: true
                            font.family: "Noto Sans SC"
                            Layout.fillWidth: true
                            elide: Text.ElideRight
                        }

                        Text {
                            text: barcode ? ("码" + root.barcodeTail(barcode)) : ""
                            color: "#64748B"
                            font.pixelSize: root.compact ? 10 : 13
                            font.family: "Noto Sans SC"
                            elide: Text.ElideRight
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: root.compact ? 22 : 30
                        radius: 5
                        color: "#2563EB"

                        Text {
                            anchors.centerIn: parent
                            text: "加入"
                            color: "#FFFFFF"
                            font.pixelSize: root.compact ? 13 : 18
                            font.bold: true
                            font.family: "Noto Sans SC"
                        }
                    }
                }
            }

            Text {
                anchors.centerIn: parent
                visible: grid.count === 0
                text: "暂无快捷商品"
                color: "#94A3B8"
                font.pixelSize: root.compact ? 20 : 28
                font.family: "Noto Sans SC"
            }
        }
    }
}
