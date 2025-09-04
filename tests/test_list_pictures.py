import tempfile
import unittest
from pathlib import Path

from src.pisort.pisort import list_pictures

src = Path(__file__).parent


class ListPicturesTest(unittest.TestCase):

    def test_list_pictures_in_directory(self):
        actual = list_pictures(src)

        paths = {pic.path for pic in actual}
        self.assertIn(src / "original_2020-01-01T00:00:00+00:00.png", paths)
        self.assertIn(src / "modified_2023-08-13T21:47:50+02:00.png", paths)
        self.assertIn(src / "digitized_2023-08-01T20:00:00-07:00.png", paths)

    def test_ignore_dateless_pictures(self):
        actual = list_pictures(src)

        paths = {pic.path for pic in actual}
        self.assertNotIn(src / "no-date.png", paths)

    def test_ignore_non_pictures(self):
        actual = list_pictures(src)

        paths = {pic.path for pic in actual}
        self.assertNotIn(src / "test_list_pictures.py", paths)

    def test_ignore_directories(self):
        with tempfile.TemporaryDirectory() as tempdir:
            directory = Path(tempdir)
            subdir = directory / "foo"
            subdir.mkdir()

            actual = list_pictures(directory)

            paths = {pic.path for pic in actual}
            self.assertNotIn(subdir, paths)
