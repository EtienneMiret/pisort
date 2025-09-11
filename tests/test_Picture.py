import datetime
import unittest
from pathlib import Path

from pisort.pisort import Picture


class PictureTest(unittest.TestCase):

    def setUp(self) -> None:
        self.dir = Path(__file__).parent

    def test_date_get_original(self) -> None:
        image = Picture(self.dir / "original_2020-01-01T00:00:00+00:00.png")

        actual = image.date()

        expected = datetime.datetime(
            2020, 1, 1,
            tzinfo=datetime.timezone.utc,
        )
        self.assertEqual(expected, actual)
        self.assertEqual(expected.tzinfo, actual.tzinfo)

    def test_date_get_digitized(self) -> None:
        image = Picture(self.dir / "digitized_2023-08-01T20:00:00-07:00.png")

        actual = image.date()

        expected = datetime.datetime(
            2023, 8, 1, 20,
            tzinfo=datetime.timezone(datetime.timedelta(hours=-7)),
        )
        self.assertEqual(expected, actual)
        self.assertEqual(expected.tzinfo, actual.tzinfo)

    def test_date_get_modified(self) -> None:
        image = Picture(self.dir / "modified_2023-08-13T21:47:50+02:00.png")

        actual = image.date()

        expected = datetime.datetime(
            2023, 8, 13, 21, 47, 50,
            tzinfo=datetime.timezone(datetime.timedelta(hours=2))
        )
        self.assertEqual(expected, actual)
        self.assertEqual(expected.tzinfo, actual.tzinfo)

    def test_date_get_None(self) -> None:
        image = Picture(self.dir / "no-date.png")

        actual = image.date()

        self.assertIsNone(actual)
