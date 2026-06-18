import QtQuick 2.12
import QtQuick.Controls 2.5
import QtQuick.Layouts 1.12

Rectangle {
    id: root
    property var cart: ({ items: [], count: 0, total_cent: 0, total_text: "¥0.00" })
    property var cartItemsModel: null
    property bool compact: width <= 680 || height <= 760
    signal removeProduct(string productId)

    color: "#FFFFFF"
    radius: 6
    border.color: "#CBD5E1"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: root.compact ? 10 : 18
        spacing: root.compact ? 7 : 12

        RowLayout {
            Layout.fillWidth: true

            Text {
                text: "购物车"
                color: "#111827"
                font.pixelSize: root.compact ? 25 : 34
                font.bold: true
                font.family: "Noto Sans SC"
                Layout.fillWidth: true
            }

            Text {
                text: (cart.count || 0) + " 件"
                color: "#475569"
                font.pixelSize: root.compact ? 16 : 22
                font.family: "Noto Sans SC"
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: root.compact ? 32 : 42
            radius: 5
            color: "#F1F5F9"

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: root.compact ? 8 : 14
                anchors.rightMargin: root.compact ? 8 : 14

                Text { text: "商品"; color: "#475569"; font.pixelSize: root.compact ? 13 : 17; font.family: "Noto Sans SC"; Layout.fillWidth: true }
                Text { text: "数量"; color: "#475569"; font.pixelSize: root.compact ? 13 : 17; font.family: "Noto Sans SC"; Layout.preferredWidth: root.compact ? 46 : 70; horizontalAlignment: Text.AlignHCenter }
                Text { text: "小计"; color: "#475569"; font.pixelSize: root.compact ? 13 : 17; font.family: "Noto Sans SC"; Layout.preferredWidth: root.compact ? 82 : 110; horizontalAlignment: Text.AlignRight }
                Item { Layout.preferredWidth: root.compact ? 44 : 58 }
            }
        }

        ListView {
            id: cartList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: cartItemsModel || cart.items || []
            spacing: root.compact ? 6 : 10

            delegate: Rectangle {
                width: cartList.width
                height: root.compact ? 66 : 88
                radius: 5
                color: index % 2 === 0 ? "#F8FAFC" : "#EEF2F7"

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: root.compact ? 8 : 14
                    anchors.rightMargin: root.compact ? 8 : 12
                    spacing: root.compact ? 6 : 10

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        Text {
                            text: product_name || product_id
                            color: "#111827"
                            font.pixelSize: root.compact ? 17 : 24
                            font.bold: true
                            font.family: "Noto Sans SC"
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }

                        Text {
                            text: product_id + "  " + (unit_price_text || "")
                            color: "#64748B"
                            font.pixelSize: root.compact ? 12 : 16
                            font.family: "Noto Sans SC"
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }
                    }

                    Text {
                        text: "x" + (quantity || 0)
                        color: "#0F172A"
                        font.pixelSize: root.compact ? 17 : 24
                        font.bold: true
                        font.family: "Noto Sans SC"
                        Layout.preferredWidth: root.compact ? 46 : 70
                        horizontalAlignment: Text.AlignHCenter
                    }

                    Text {
                        text: subtotal_text || ""
                        color: "#0F172A"
                        font.pixelSize: root.compact ? 18 : 25
                        font.bold: true
                        font.family: "Noto Sans SC"
                        Layout.preferredWidth: root.compact ? 82 : 110
                        horizontalAlignment: Text.AlignRight
                    }

                    Button {
                        text: "-"
                        Layout.preferredWidth: root.compact ? 44 : 58
                        Layout.preferredHeight: root.compact ? 40 : 52
                        font.pixelSize: root.compact ? 18 : 24
                        onClicked: root.removeProduct(product_id)
                    }
                }
            }

            Text {
                anchors.centerIn: parent
                visible: cartList.count === 0
                text: "购物车为空"
                color: "#94A3B8"
                font.pixelSize: root.compact ? 28 : 38
                font.bold: true
                font.family: "Noto Sans SC"
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: root.compact ? 96 : 124
            radius: 6
            color: "#111827"

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: root.compact ? 14 : 22
                anchors.rightMargin: root.compact ? 14 : 22

                Text {
                    text: "总计"
                    color: "#E5E7EB"
                    font.pixelSize: root.compact ? 24 : 34
                    font.family: "Noto Sans SC"
                    Layout.fillWidth: true
                }

                Text {
                    text: cart.total_text || "¥0.00"
                    color: "#FDE68A"
                    font.pixelSize: root.compact ? 40 : 56
                    font.bold: true
                    font.family: "Noto Sans SC"
                    elide: Text.ElideNone
                }
            }
        }
    }
}
