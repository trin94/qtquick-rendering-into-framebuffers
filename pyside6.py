import os
import sys

from PySide6.QtCore import QSize, QUrl, Slot, Signal
from PySide6.QtGui import QOpenGLContext, QGuiApplication
from PySide6.QtOpenGL import QOpenGLFramebufferObject
from PySide6.QtQml import qmlRegisterType, QQmlApplicationEngine
from PySide6.QtQuick import QQuickFramebufferObject, QSGRendererInterface, QQuickWindow
from mpv import MPV, MpvGlGetProcAddressFn, MpvRenderContext


def get_process_address(_, name):
    print("get_process_address", name.decode('utf-8'))
    glctx = QOpenGLContext.currentContext()
    if glctx is None:
        return 0
    return int(glctx.getProcAddress(name))


class MpvObject(QQuickFramebufferObject):
    onUpdate = Signal()

    def __init__(self, parent=None):
        print("MpvObject.init")
        super(MpvObject, self).__init__(parent)
        self.mpv = MPV(ytdl=True, vo='libmpv', terminal="yes", msg_level="all=v")
        self.onUpdate.connect(self.doUpdate)

    def on_update(self):
        self.onUpdate.emit()

    @Slot()
    def doUpdate(self):
        self.update()

    def createRenderer(self) -> 'QQuickFramebufferObject.Renderer':
        return MpvRenderer(self)

    @Slot()
    def toggle_play_pause(self):
        url = "resources/test1.mkv"  # 24 fps
        # url = ""  # (absolute) path to any other source with e.g. 30 or 60 fps

        if not bool(self.mpv.path):
            self.mpv.play(url)
        else:
            self.mpv.pause = not self.mpv.pause


class MpvRenderer(QQuickFramebufferObject.Renderer):

    def __init__(self, parent):
        super(MpvRenderer, self).__init__()
        self._parent = parent
        self._get_proc_address_resolver = MpvGlGetProcAddressFn(get_process_address)
        self._ctx = None

    def createFramebufferObject(self, size: QSize) -> QOpenGLFramebufferObject:
        if self._ctx is None:
            self._ctx = MpvRenderContext(
                self._parent.mpv,
                api_type='opengl',
                opengl_init_params={'get_proc_address': self._get_proc_address_resolver}
            )
            self._ctx.update_cb = self._parent.onUpdate.emit

        return QQuickFramebufferObject.Renderer.createFramebufferObject(self, size)

    def render(self):
        if self._ctx:
            factor = self._parent.scale()
            rect = self._parent.size()

            width = int(rect.width() * factor)
            height = int(rect.height() * factor)
            fbo = int(self.framebufferObject().handle())

            self._ctx.render(flip_y=False, opengl_fbo={'w': width, 'h': height, 'fbo': fbo})


if __name__ == '__main__':
    os.environ['LC_NUMERIC'] = 'C'  # Required for libmpv

    QQuickWindow.setGraphicsApi(QSGRendererInterface.GraphicsApi.OpenGL)

    app = QGuiApplication([])
    engine = QQmlApplicationEngine()

    qmlRegisterType(MpvObject, 'mpvtest', 1, 0, "MpvObject")

    engine.load(QUrl.fromLocalFile('window.qml'))

    if not engine.rootObjects():
        sys.exit(-1)

    app.exec()
