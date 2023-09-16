import QtQuick
import QtQuick.Controls

import mpvtest 1.0

Window {
    width: 1280
    height: 720
    visible: true

    property var timeOnRenderStart: 0
    property int timeItTookToRenderFrame: 0
    property double estimatedFps: 0

    onBeforeRendering: timeOnRenderStart = Date.now()

    onAfterRendering: {
        timeItTookToRenderFrame = Date.now() - timeOnRenderStart

        if (timeItTookToRenderFrame > 0) {
            estimatedFps = (1000 / timeItTookToRenderFrame).toFixed(2)
        }
    }

    MpvObject {
        id: renderer
        anchors.fill: parent

        MouseArea {
            anchors.fill: parent
            onClicked: renderer.toggle_play_pause()
        }
    }

    Label {

        width: 210
        padding: 15
        horizontalAlignment: Text.AlignLeft
        color: "white"
        text: "Frame rendered in ms: " + timeItTookToRenderFrame + "\nEstimated FPS: " + estimatedFps

        anchors.bottom: renderer.bottom
        anchors.right: renderer.right
        anchors.margins: 100

        background: Rectangle {
            color: "black"
            border.color: "red"
            border.width: 5
        }
    }

}
