from PySide.QtGui import (QFrame, QWidget, QLineEdit, QFormLayout, QPushButton,
                          QHBoxLayout, QVBoxLayout, QLabel, QIcon, QSizePolicy,
                          QStyle)
from PySide.QtCore import Qt, QSize

import syrup


class _HorizontalLine(QFrame):
    """A horizontal line
    """
    def __init__(self, parent=None):
        super(_HorizontalLine, self).__init__(parent)
        self.setFrameShape(QFrame.HLine)


class LinkLabel(QLabel):
    """A label that displays a clickable link in black.
    """

    HTML = '''<html><head><style type=text/css>
    a:link {{ color: black; text-decoration: underline;}}
    </style></head>
    <body>{prefix}<a href="{link}">{label}</a></body>
    </html>
    '''

    def __init__(self, link, label=None, prefix='', parent=None, f=0):
        super(LinkLabel, self).__init__('', parent, f)
        self.prefix = prefix
        self.set_link(link, label)
        self.setOpenExternalLinks(True)

    def set_link(self, link, label=None):
        html = self.HTML.format(**{
            'link': link,
            'label': label if label else link,
            'prefix': self.prefix})
        self.setText(html)


class SelectedDirectoryWidget(QWidget):
    """A widget that shows a currently selected directory as a LinkLabel with a
    'choose new directory' button to the right.
    """
    def __init__(self, prefix, parent=None):
        super(SelectedDirectoryWidget, self).__init__(parent)
        self.directory = LinkLabel('', prefix=prefix)
        self.directory.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored);
        icon = self.style().standardIcon(QStyle.SP_DirOpenIcon)
        self.choose_directory = QPushButton(icon, '')
        self.choose_directory.setIconSize(QSize(16, 16))

        l = QHBoxLayout()
        l.addWidget(self.directory)
        l.addWidget(self.choose_directory, 0, Qt.AlignRight)
        self.setLayout(l)

    def set_link(self, link, label=None):
        # Delegate to link
        self.directory.set_link(link, label)

class Controls(QWidget):
    """Container for controls
    """
    def __init__(self, parent=None):
        super(Controls, self).__init__(parent)

        # Specimen number and location edit boxes
        self.specimen = QLineEdit()
        self.location = QLineEdit()
        l = QFormLayout()
        l.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        l.addRow('Specimen number', self.specimen)
        l.addRow('Location', self.location)
        form = QWidget()
        form.setLayout(l)

        # OK and cancel buttons
        self.ok = QPushButton('Move to processed')
        self.cancel = QPushButton('Ignore file')
        l = QHBoxLayout()
        l.addWidget(self.ok)
        l.addWidget(self.cancel)
        buttons = QWidget()
        buttons.setLayout(l)

        # A container for the image handling controls
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(form)
        layout.addWidget(buttons)
        self.image_handling = QWidget()
        self.image_handling.setLayout(layout)

        # Buttons to choose the inbox and processed directories
        self.inbox = SelectedDirectoryWidget(prefix='Watch for new images in ')
        self.processed = SelectedDirectoryWidget(prefix='Move processed images to ')
        l = QVBoxLayout()
        l.addWidget(QLabel('Directories'))
        l.addWidget(self.inbox)
        l.addWidget(self.processed)
        directories = QWidget()
        directories.setLayout(l)

        # Layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(LinkLabel(
            link='https://github.com/NaturalHistoryMuseum/syrup/',
            label='Syrup {0}'.format(syrup.__version__)))
        layout.addWidget(QLabel(syrup.__doc__.strip()))
        layout.addWidget(_HorizontalLine())
        layout.addWidget(self.image_handling)
        layout.addWidget(_HorizontalLine())
        layout.addWidget(directories)
        self.setLayout(layout)

    def clear(self):
        "Clears the line edit controls"
        for control in (self.specimen, self.location):
            control.setText('')
