import sys

from pathlib import Path

from PySide import QtCore, QtGui

class NewFileWatcher(QtCore.QObject):
    """Emits self.new_file(path) whenever a file name matches the given regular
    expression appears in the given directory
    """

    # Emitted when a file appears in the directory given in __init__
    new_file = QtCore.Signal(Path)

    def __init__(self, directory, regex, parent=None):
        super(NewFileWatcher, self).__init__(parent)

        print(u'Watching [{0}]'.format(directory))

        self._directory = Path(directory)
        self._regex = regex
        self._previous_files = self._matching_files()

        self._watch = QtCore.QFileSystemWatcher([unicode(directory)])
        self._watch.directoryChanged.connect(self.changed)

    def changed(self, path):
        print(u'NewFileWatcher.changed [{0}]'.format(path))
        current = self._matching_files()
        for new_file in sorted(current.difference(self._previous_files)):
            print(u'New matching file in [{0}]: [{1}]'.format(path, new_file))
            self.new_file.emit(new_file)
        self._previous_files = current

    def _matching_files(self):
        """Returns set of files in self._directory that match IMAGE_SUFFIXES_RE
        """
        files = self._directory.iterdir()
        return set(p for p in files if p.is_file() and self._regex.match(unicode(p)))
