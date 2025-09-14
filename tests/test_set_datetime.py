import datetime
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from zoneinfo import ZoneInfo

from pisort.Picture import Picture
from pisort.set_datetime import process


class SetDatetimeTest(unittest.TestCase):

    def setUp(self) -> None:
        self.src_dir = Path(__file__).parent
        self.work_dir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.work_dir.cleanup()

    def test_set_datetime(self) -> None:
        path = Path(self.work_dir.name) / "picture.jpg"
        shutil.copy(self.src_dir / "sample.jpg", path)
        expected = datetime.datetime.strptime("2025-09-14 18:18", "%Y-%m-%d %H:%M")
        expected = expected.replace(tzinfo=ZoneInfo("Europe/Paris"))
        os.utime(path, (expected.timestamp(), expected.timestamp()))

        process(path, True)

        actual = Picture(path).date()
        self.assertEqual(expected.timestamp(), actual.timestamp())
        self.assertEqual(datetime.timedelta(hours=2), actual.tzinfo.utcoffset(actual))
