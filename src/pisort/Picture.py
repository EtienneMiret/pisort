import datetime
from pathlib import Path
from typing import Optional, TextIO

from PIL import Image, ExifTags

from pisort.parse_offset import parse_offset

exif_datetime_format = "%Y:%m:%d %H:%M:%S"


class Picture:

    def __init__(self, path: Path):
        self.path = path
        with Image.open(path) as img:
            self.exif = img.getexif()

    def __str__(self) -> str:
        return self.path.name

    def print(self, file: Optional[TextIO] = None) -> None:
        print(f'{self.path.name}:')
        for k, v in self.exif.items():
            print(f'  {ExifTags.TAGS[k]}: {v}', file=file)
        for k, v in self.exif.get_ifd(ExifTags.IFD.Exif).items():
            print(f'  {ExifTags.TAGS[k]}: {v}', file=file)

    def date(self) -> Optional[datetime.datetime]:
        tz = datetime.datetime.now().astimezone().tzinfo
        tz_ifd = self.exif.get_ifd(ExifTags.IFD.Exif)
        for (date_tag, tz_tag) in [
            (ExifTags.Base.DateTimeOriginal, ExifTags.Base.OffsetTimeOriginal),
            (ExifTags.Base.DateTimeDigitized, ExifTags.Base.OffsetTimeDigitized),
            (ExifTags.Base.DateTime, ExifTags.Base.OffsetTime),
        ]:
            date_ifd = self.exif.get_ifd(ExifTags.IFD.Exif)
            if date_tag == ExifTags.Base.DateTime:
                date_ifd = self.exif
            if date_tag in date_ifd:
                date = datetime.datetime.strptime(
                    date_ifd[date_tag],
                    exif_datetime_format,
                )
                if tz_tag in tz_ifd:
                    tz = parse_offset(tz_ifd[tz_tag])
                return date.replace(tzinfo=tz)
        return None

    def rename_to(self, new_stem: str) -> None:
        self.path = self.path.rename(self.path.with_stem(new_stem))
