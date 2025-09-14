import datetime
import unittest
from zoneinfo import ZoneInfo

from pisort.fmt_offset import fmt_offset


class TestFormatOffset(unittest.TestCase):

    def test_fmt_zero(self) -> None:
        dt = datetime.datetime.fromtimestamp(0, tz=datetime.timezone.utc)

        fmt = fmt_offset(dt)

        self.assertEqual("+00:00", fmt)

    def test_fmt_positive(self):
        tz = ZoneInfo("Europe/Paris")
        dt = datetime.datetime.strptime("2025-09-14 17:08", "%Y-%m-%d %H:%M")
        dt = dt.replace(tzinfo=tz)

        fmt = fmt_offset(dt)

        self.assertEqual("+02:00", fmt)

    def test_fmt_negative(self):
        tz = ZoneInfo("America/Toronto")
        dt = datetime.datetime.strptime("2025-09-14 17:08", "%Y-%m-%d %H:%M")
        dt = dt.replace(tzinfo=tz)

        fmt = fmt_offset(dt)

        self.assertEqual("-04:00", fmt)

    def test_fmt_none(self):
        dt = datetime.datetime.strptime("2025-09-14 17:08", "%Y-%m-%d %H:%M")
        dt = dt.replace(tzinfo=None)

        fmt = fmt_offset(dt)

        self.assertEqual("   :  ", fmt)
