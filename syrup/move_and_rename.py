import shutil

from pathlib import Path


def move_and_rename(src, destination):
    """Moves the file src to destination, appending a numerical suffix to avoid
    overwritting existing files
    """
    if src != destination:
        suffix_n = 1

        # A string format to avoid collisions
        template = destination.stem + '_({0})' + destination.suffix
        while destination.is_file():
            print('Destination file [{0}] exists'.format(destination))
            destination = destination.parent / template.format(suffix_n)
            suffix_n += 1

        print('Moving [{0}] to [{1}]'.format(src, destination))
        shutil.move(str(src), str(destination))
