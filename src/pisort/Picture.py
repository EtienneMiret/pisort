import datetime
from pathlib import Path
from typing import Optional, TextIO

import exifread
from exifread.core.ifd_tag import IfdTag

from pisort.exceptions import NoExifDataException
from pisort.parse_offset import parse_offset

exif_datetime_format = "%Y:%m:%d %H:%M:%S"


class Picture:

    def __init__(self, path: Path):
        self.path = path
        with path.open("rb") as f:
            self.exif: dict[str, IfdTag] = exifread.process_file(f)
        if len(self.exif) == 0:
            raise NoExifDataException()

    def __str__(self) -> str:
        return self.path.name

    def print(self, file: Optional[TextIO] = None) -> None:
        print(f'{self.path.name}:')
        for k, v in self.exif.items():
            print(f'  {k}: {v}', file=file)

    def date(self) -> Optional[datetime.datetime]:
        tz = datetime.datetime.now().astimezone().tzinfo
        for (date_tag, tz_tag) in [
            ("EXIF DateTimeOriginal", "EXIF OffsetTimeOriginal"),
            ("EXIF DateTimeDigitized", "EXIF OffsetTimeDigitized"),
            ("Image DateTime", "EXIF OffsetTime"),
        ]:
            if date_tag in self.exif.keys():
                date = datetime.datetime.strptime(
                    self.exif[date_tag].values,
                    exif_datetime_format,
                )
                if tz_tag in self.exif.keys():
                    tz = parse_offset(self.exif[tz_tag].values)
                return date.replace(tzinfo=tz)
        return None

    def rename_to(self, new_stem: str) -> None:
        self.path = self.path.rename(self.path.with_stem(new_stem))
