import re
import time

from functools import wraps
from pathlib import Path

import cv2

import numpy as np

from PySide import QtCore
from PySide.QtGui import (QPixmap, QImage, QMainWindow, QDesktopServices,
                          QSplitter, QFileDialog, QMessageBox, QWidget)
from PySide.QtCore import QSettings, QEvent

from .controls import Controls
from .image_label import ImageLabel
from .move_and_rename import move_and_rename
from .new_file_watcher import NewFileWatcher


# Supported image formats
IMAGE_SUFFIXES = ('.bmp', '.jpeg', '.jpg', '.png', '.tif', '.tiff',)

# A case-insensitive regular expression that matches each suffix
IMAGE_SUFFIXES_RE = '|'.join('{0}'.format(p[1:]) for p in IMAGE_SUFFIXES)
IMAGE_SUFFIXES_RE = '^.*\\.({0})$'.format(IMAGE_SUFFIXES_RE)
IMAGE_SUFFIXES_RE = re.compile(IMAGE_SUFFIXES_RE, re.IGNORECASE)

# Regular expression for specimen and location numbers
VALUE_RE = re.compile('^[0-9]+$')

def qimage_of_bgr(bgr):
    """ A QImage representation of a BGR numpy array
    """
    bgr = cv2.cvtColor(bgr.astype('uint8'), cv2.COLOR_BGR2RGB)
    bgr = np.ascontiguousarray(bgr)
    qt_image = QImage(bgr.data,
                      bgr.shape[1], bgr.shape[0],
                      bgr.strides[0], QImage.Format_RGB888)

    # QImage does not take a deep copy of np_arr.data so hold a reference
    # to it
    assert(not hasattr(qt_image, 'bgr_array'))
    qt_image.bgr_array = bgr
    return qt_image


def report_to_user(f):
    """Decorator that reports exceptions to the user
    """
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        except Exception as e:
            parent = self if isinstance(self, QWidget) else None
            QMessageBox.critical(parent, u'An error occurred',
                u'An error occurred:\n{0}'.format(e))
            raise
    return wrapper


class MainWindow(QMainWindow):
    """The application's main window
    """

    # Emitted when there are pending files to be processed
    new_pending_files = QtCore.Signal()

    def __init__(self, app):
        super(MainWindow, self).__init__()

        # Window layout - a splitter with the image on the left and controls
        # on the right
        self._image_widget = ImageLabel(self)
        self._controls = Controls(self)
        self._splitter = QSplitter()
        self._splitter.addWidget(self._image_widget)
        self._splitter.addWidget(self._controls)
        self._splitter.setSizes([1200, 600])

        # Main window layout
        self.setCentralWidget(self._splitter)

        # Connect controls to handlers
        self._controls.ok.clicked.connect(self.ok)
        self._controls.cancel.clicked.connect(self.cancel)
        self._controls.inbox.choose_directory.clicked.connect(self.choose_inbox)
        self._controls.processed.choose_directory.clicked.connect(self.choose_processed)

        # Directories
        mydocuments = QDesktopServices.storageLocation(
            QDesktopServices.DocumentsLocation)
        self._inbox = Path(QSettings().value('inbox',
            str(Path(mydocuments) / 'inbox')))
        self._processed = Path(QSettings().value('processed',
            str(Path(mydocuments) / 'processed')))

        self._controls.inbox.set_link(str(self._inbox.as_uri()), self._inbox.name)
        self._controls.processed.set_link(str(self._processed.as_uri()), self._processed.name)

        # A stack of Path objects to be processed
        self._pending_files = []

        # The Path currently shown in the UI
        self._under_review = None

        # Watch the inbox directory, if it exists
        self.new_pending_files.connect(self.process_next_pending,
            QtCore.Qt.QueuedConnection)

        if self._inbox.is_dir():
            self._watcher = NewFileWatcher(self._inbox, IMAGE_SUFFIXES_RE)
            self._watcher.new_file.connect(self.new_image_file)
        else:
            self._watcher = None

        self.empty_controls()

        # Setup drag-drop handling
        self.setAcceptDrops(True)
        self._controls.installEventFilter(self)
        self._splitter.installEventFilter(self)

    def new_inbox_directory(self):
        """Watch the inbox directory
        """
        print('MainWindow.new_inbox_directory [{0}]'.format(self._inbox))
        if self._watcher:
            self._watcher.new_file.disconnect()

        self._watcher = NewFileWatcher(self._inbox, IMAGE_SUFFIXES_RE)
        self._watcher.new_file.connect(self.new_image_file)

    def new_image_file(self, path):
        """Slot for self._watcher.new_file
        """
        print('MainWindow.new_image_file [{0}]'.format(path))
        self._pending_files.append(path)
        self.new_pending_files.emit()

    @report_to_user
    def process_next_pending(self):
        """Loads the next pending image for review
        """
        print('MainWindow.process_next_pending: [{0}] files'.format(
            len(self._pending_files)))
        if not self._under_review:
            if self._pending_files:
                self.review_image(self._pending_files.pop())
            else:
                self.empty_controls()

    def review_image(self, path):
        """Loads path for review
        """
        print('MainWindow.review_image [{0}]'.format(path))

        # Arbitrary delay to give the capture software time to finish writing
        # the image.
        time.sleep(1)
        image = cv2.imread(str(path))
        if image is None:
            raise ValueError('Unable to read [{0}]'.format(path))
        else:
            self._under_review = path
            self.setWindowTitle('')
            self.setWindowFilePath(str(path))
            self._controls.specimen.setText(QSettings().value('specimen'))
            self._controls.location.setText(QSettings().value('location'))
            self._image_widget.set_pixmap(QPixmap.fromImage(qimage_of_bgr(image)))
            self._controls.image_handling.setEnabled(True)

    def empty_controls(self):
        """Clears controls
        """
        print('MainWindow.empty_controls')
        self._under_review = None
        self.setWindowTitle('Syrup')
        self.setWindowFilePath(None)
        self._image_widget.set_pixmap(None)
        self._controls.clear()
        self._controls.image_handling.setEnabled(False)

    @report_to_user
    def ok(self):
        print('MainWindow.ok')
        specimen = self._controls.specimen.text()
        location = self._controls.location.text()
        if VALUE_RE.match(specimen) and VALUE_RE.match(location):
            if not self._processed.is_dir():
                self._processed.mkdir(parents=True)
            destination = self._processed / '{0}_{1}'.format(specimen, location)
            destination = destination.with_suffix(self._under_review.suffix)
            move_and_rename(self._under_review, destination)
            QSettings().setValue('specimen', specimen)
            QSettings().setValue('location', location)
            self._under_review = None
            self.process_next_pending()
        else:
            raise ValueError('Please enter one or more digits for both value '
                             'and location')

    @report_to_user
    def cancel(self):
        """Closes the image under review without moving the image file
        """
        print('MainWindow.cancel')
        self._under_review = None
        self.process_next_pending()

    @report_to_user
    def choose_inbox(self):
        """Prompts the user to choose the inbox directory
        """
        directory = QFileDialog.getExistingDirectory(self,
            "Choose the inbox directory", str(self._inbox))
        if directory:
            directory = Path(directory)
            if directory == self._processed:
                raise ValueError('The inbox directory cannot be the same as '
                                 'the processed directory')
            else:
                self._inbox = directory
                print('New inbox directory [{0}]'.format(self._inbox))
                self._controls.inbox.set_link(str(self._inbox.as_uri()),
                    self._inbox.name)
                QSettings().setValue('inbox', str(self._inbox))
                self.new_inbox_directory()

    @report_to_user
    def choose_processed(self):
        """Prompts the user to choose the processed directory
        """
        directory = QFileDialog.getExistingDirectory(self,
            "Choose the processed directory", str(self._processed))
        if directory:
            directory = Path(directory)
            if directory == self._inbox:
                raise ValueError('The inbox directory cannot be the same as '
                                 'the processed directory')
            else:
                self._processed = directory
                print('New processed directory [{0}]'.format(self._processed))
                self._controls.processed.set_link(str(self._processed.as_uri()),
                    self._processed.name)
                QSettings().setValue('processed', str(self._processed))

    def write_geometry_settings(self):
        "Writes geometry to settings"
        print('MainWindow.write_geometry_settings')

        # Taken from http://stackoverflow.com/a/8736705
        # TODO LH Test on multiple display system
        s = QSettings()

        s.setValue("mainwindow/geometry", self.saveGeometry())
        s.setValue("mainwindow/pos", self.pos())
        s.setValue("mainwindow/size", self.size())

    def show_from_geometry_settings(self):
        print('MainWindow.show_from_geometry_settings')

        # TODO LH What if screen resolution, desktop config change or roaming
        # profile means that restored state is outside desktop?
        s = QSettings()

        self.restoreGeometry(s.value("mainwindow/geometry", self.saveGeometry()))
        if not (self.isMaximized() or self.isFullScreen()):
            self.move(s.value("mainwindow/pos", self.pos()))
            self.resize(s.value("mainwindow/size", self.size()))
        self.show()

    def closeEvent(self, event):
        """QWidget virtual
        """
        print('MainWindow.closeEvent')
        self.write_geometry_settings()
        event.accept()

    def eventFilter(self, obj, event):
        "Event filter that accepts drag-drop events"
        if event.type() in (QEvent.DragEnter, QEvent.Drop):
            return True
        else:
            return super(MainWindow, self).eventFilter(obj, event)

    def _accept_drag_drop(self, event):
        """If no image is under review and event refers to a single image file,
        returns the path. Returns None otherwise.
        """
        if self._under_review:
            return None
        else:
            urls = event.mimeData().urls() if event.mimeData() else None
            path = Path(urls[0].toLocalFile()) if urls and 1 == len(urls) else None
            print(path, IMAGE_SUFFIXES_RE.match(path.suffix))
            if path and IMAGE_SUFFIXES_RE.match(path.suffix):
                return urls[0].toLocalFile()
            else:
                return None

    def dragEnterEvent(self, event):
        """QWidget virtual
        """
        print('MainWindow.dragEnterEvent')
        if self._accept_drag_drop(event):
            event.acceptProposedAction()
        else:
            super(MainWindow, self).dragEnterEvent(event)

    def dropEvent(self, event):
        """QWidget virtual
        """
        print('MainWindow.dropEvent')
        res = self._accept_drag_drop(event)
        if res:
            event.acceptProposedAction()
            self.review_image(Path(res))
        else:
            super(MainWindow, self).dropEvent(event)

