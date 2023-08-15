import tempfile
import unittest
from pathlib import Path

from pisort import Picture, sort_pictures

src = Path(__file__).parent
digitized = src / "digitized_2023-08-01T20:00:00-07:00.png"
modified = src / "modified_2023-08-13T21:47:50+02:00.png"
no_date = src / "no-date.png"
original = src / "original_2020-01-01T00:00:00+00:00.png"
sample = src / "sample.jpg"


class SortPicturesTest(unittest.TestCase):

    def setUp(self) -> None:
        self.dir = tempfile.TemporaryDirectory()
        self.dst = Path(self.dir.name)

    def tearDown(self) -> None:
        self.dir.cleanup()

    def test_order_by_date_asc(self) -> None:
        (self.dst / "digitized.png").hardlink_to(digitized)
        (self.dst / "modified.png").hardlink_to(modified)
        (self.dst / "original.png").hardlink_to(original)
        (self.dst / "no-date.png").hardlink_to(no_date)
        (self.dst / "sample.jpg").hardlink_to(sample)
        pictures = [Picture(self.dst / name) for name in [
            "digitized.png",
            "modified.png",
            "original.png",
            "no-date.png",
            "sample.jpg",
        ]]

        sort_pictures(pictures)

        self.assertSameFile(sample, "0.jpg")
        self.assertSameFile(original, "1.png")
        self.assertSameFile(digitized, "2.png")
        self.assertSameFile(modified, "3.png")
        self.assertSameFile(no_date, "4.png")

    def test_add_specified_name(self) -> None:
        (self.dst / "digitized.png").hardlink_to(digitized)
        (self.dst / "modified.png").hardlink_to(modified)
        (self.dst / "original.png").hardlink_to(original)
        pictures = [Picture(self.dst / name) for name in [
            "digitized.png",
            "modified.png",
            "original.png",
        ]]

        sort_pictures(pictures, "Summer 2023")

        self.assertSameFile(original, "0 - Summer 2023.png")
        self.assertSameFile(digitized, "1 - Summer 2023.png")
        self.assertSameFile(modified, "2 - Summer 2023.png")

    def test_already_numbered_files_are_not_deleted(self) -> None:
        (self.dst / "0.png").hardlink_to(original)
        (self.dst / "1.png").hardlink_to(modified)
        (self.dst / "new.png").hardlink_to(digitized)
        pictures = [Picture(self.dst / name) for name in ["0.png", "1.png", "new.png"]]

        sort_pictures(pictures)

        self.assertSameFile(original, "0.png")
        self.assertSameFile(digitized, "1.png")
        self.assertSameFile(modified, "2.png")

    def test_do_nothing_when_would_overwrite_directory(self) -> None:
        (self.dst / "original.png").hardlink_to(original)
        (self.dst / "digitized.png").hardlink_to(digitized)
        (self.dst / "1.png").mkdir()
        pictures = [Picture(self.dst / name) for name in ["original.png", "digitized.png"]]

        self.assertRaises(FileExistsError, sort_pictures, pictures)

        self.assertSameFile(original, "original.png")
        self.assertSameFile(digitized, "digitized.png")

    def test_do_nothing_when_would_overwrite_non_picture_file(self) -> None:
        (self.dst / "original.png").hardlink_to(original)
        (self.dst / "digitized.png").hardlink_to(digitized)
        (self.dst / "1.png").touch()
        pictures = [Picture(self.dst / name) for name in ["original.png", "digitized.png"]]

        self.assertRaises(FileExistsError, sort_pictures, pictures)

        self.assertSameFile(original, "original.png")
        self.assertSameFile(digitized, "digitized.png")

    def test_pad_numer_with_zeros(self) -> None:
        pictures = self.mk_samples(25)

        sort_pictures(pictures)

        self.assertTrue((self.dst / "00.jpg").exists())
        self.assertFalse((self.dst / "0.jpg").exists())

    def test_use_no_more_padding_than_needed(self) -> None:
        pictures = self.mk_samples(100)

        sort_pictures(pictures)

        self.assertTrue((self.dst / "00.jpg").exists())
        self.assertTrue((self.dst / "99.jpg").exists())
        self.assertFalse((self.dst / "100.jpg").exists())
        self.assertFalse((self.dst / "000.jpg").exists())

    def mk_samples(self, count: int) -> list[Picture]:
        for i in range(count):
            (self.dst / f"xxx-{i}.jpg").hardlink_to(sample)
        return [Picture(self.dst / f"xxx-{i}.jpg") for i in range(count)]

    def assertSameFile(self, reference: Path, filename: str):
        if not (self.dst / filename).exists():
            existing = [p.name for p in self.dst.iterdir()]
            existing.sort()
            self.fail(f"File '{filename}' doesn’t exist. There are: {existing}.")
        if not reference.samefile(self.dst / filename):
            self.fail(f"File '{filename}' isn’t the same as '{reference.name}'.")
