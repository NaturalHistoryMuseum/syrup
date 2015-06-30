from PySide import QtCore, QtGui

class ImageLabel(QtGui.QWidget):
    """Displays a pixmap scaled to fit available within the available space
    with aspect ratio maintained.
    """

    # http://stackoverflow.com/a/14107727/1773758

    def __init__(self, parent=None):
        super(ImageLabel, self).__init__(parent)
        self._label = QtGui.QLabel(self)
        self._label.setScaledContents(True)
        self._label.setFixedSize(0,0)
        self._label.setStyleSheet('QLabel { background-color: darkgrey;}')

    def set_pixmap(self, pixmap):
        self._label.setPixmap(pixmap)
        self.resize_image();

    def resizeEvent(self, event):
        super(ImageLabel, self).resizeEvent(event)
        self.resize_image()
        self.setStyleSheet('background-color: darkgrey;')

    def resize_image(self):
        pixmap = self._label.pixmap()
        if pixmap:
            pixSize = self._label.pixmap().size()
            pixSize.scale(self.size(), QtCore.Qt.KeepAspectRatio)
            self._label.setFixedSize(pixSize)
        else:
            self._label.setFixedSize(self.size())
