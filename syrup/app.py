import argparse
import sys

from PySide.QtGui import QApplication
from PySide.QtCore import QCoreApplication

import syrup
from syrup.main_window import MainWindow


# The QSettings default constructor uses the application's organizationName
# and applicationName properties.
QCoreApplication.setOrganizationName('NHM')
QCoreApplication.setApplicationName('syrup')

# No obvious benefit to also setting these but neither is there any obvious harm
QCoreApplication.setApplicationVersion(syrup.__version__)
QCoreApplication.setOrganizationDomain('nhm.ac.uk')


def main(args):
    parser = argparse.ArgumentParser(description=syrup.__doc__)
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + syrup.__version__)
    parsed = parser.parse_args(args[1:])

    app = QApplication(args)
    window = MainWindow(app)
    window.show_from_geometry_settings()
    sys.exit(app.exec_())
