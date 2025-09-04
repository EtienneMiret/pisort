import datetime
import unittest

from src.pisort.pisort import parse_offset


class ParseOffsetTest(unittest.TestCase):

    def test_parse_zero(self) -> None:
        tz = parse_offset("+00:00")

        self.assertEqual(0, tz.utcoffset(None).total_seconds())

    def test_parse_positive(self) -> None:
        tz = parse_offset("+02:00")

        self.assertEqual(7200, tz.utcoffset(None).total_seconds())

    def test_parse_negative(self) -> None:
        tz = parse_offset("-00:30")

        self.assertEqual(-1800, tz.utcoffset(None).total_seconds())

    def test_parse_invalid(self) -> None:
        now = datetime.datetime.now().astimezone()

        tz = parse_offset("")

        self.assertEqual(now.utcoffset(), tz.utcoffset(now))

    def test_parse_blank(self) -> None:
        now = datetime.datetime.now().astimezone()

        tz = parse_offset("   :  ")  # Unknown offset, as specified in Exif 3.0

        self.assertEqual(now.utcoffset(), tz.utcoffset(now))
