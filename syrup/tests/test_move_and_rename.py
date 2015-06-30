import shutil
import tempfile
import unittest

from pathlib import Path

from syrup.move_and_rename import move_and_rename

class TestMoveAndRename(unittest.TestCase):
    def test_no_existing(self):
        tempdir = Path(tempfile.mkdtemp())
        try:
            src = tempdir / 'a'
            dest = tempdir / 'b'
            src.open('w')

            move_and_rename(src, dest)

            self.assertFalse(src.is_file())
            self.assertTrue(dest.is_file())
        finally:
            shutil.rmtree(str(tempdir))

    def test_existing(self):
        tempdir = Path(tempfile.mkdtemp())
        try:
            src = tempdir / 'a'
            dest = tempdir / 'b'
            expected = tempdir / 'b_(4)'

            src.open('w')
            dest.open('w')
            collision1 = tempdir / 'b_(1)'
            collision2 = tempdir / 'b_(2)'
            collision3 = tempdir / 'b_(3)'
            collision1.open('w')
            collision2.open('w')
            collision3.open('w')

            move_and_rename(src, dest)

            self.assertFalse(src.is_file())
            self.assertTrue(dest.is_file())
            self.assertTrue(collision1.is_file())
            self.assertTrue(collision2.is_file())
            self.assertTrue(collision3.is_file())
            self.assertTrue(expected.is_file())
        finally:
            shutil.rmtree(str(tempdir))


if __name__=='__main__':
    unittest.main()
