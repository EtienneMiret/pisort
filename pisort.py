import datetime
import errno
import re
import sys
import uuid
from getopt import getopt
from pathlib import Path
from typing import Optional, TextIO, Never

from PIL import Image, UnidentifiedImageError, ExifTags

exif_offset_re = re.compile("([+-])(\\d\\d):(\\d\\d)", re.ASCII)
exif_datetime_format = "%Y:%m:%d %H:%M:%S"
max_date = datetime.datetime(
    datetime.MAXYEAR, 12, 31,
    tzinfo=datetime.timezone.utc,
)
new_stem_re = re.compile("\\d+ - (.*)")


class Arguments:

    def __init__(self, argv: list[str]):
        def fatal(msg: str) -> Never:
            print(f"{argv[0]}: {msg}", file=sys.stderr)
            exit(1)

        options, parameters = getopt(argv[1:], "", ["name=", "no-keep", "keep"])

        self.name = None
        self.keep_good_names = True
        for k, v in options:
            match k:
                case "--name":
                    self.name = v
                case "--no-keep":
                    self.keep_good_names = False
                case "--keep":
                    self.keep_good_names = True

        if len(parameters) > 1:
            fatal("Too many arguments")

        directory = "."
        if len(parameters) > 0:
            directory = parameters[0]

        self.directory = Path(directory)
        if not self.directory.exists():
            fatal(f"No such directory: {directory}")
        if not self.directory.is_dir():
            fatal(f"Not a directory: {directory}")


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


def parse_offset(string: str) -> datetime.tzinfo:
    match = exif_offset_re.fullmatch(string)
    if not match:
        return datetime.datetime.now().astimezone().tzinfo
    delta = datetime.timedelta(
        hours=int(match.group(2)),
        minutes=int(match.group(3)),
    )
    if match.group(1) == "-":
        delta = -delta
    return datetime.timezone(delta, string)


def list_pictures(directory: Path) -> list[Picture]:
    result = []
    for file in directory.iterdir():
        if not file.is_file():
            continue
        try:
            result.append(Picture(file))
        except UnidentifiedImageError:
            pass
    return result


def sort_pictures(
        pictures: list[Picture],
        name: Optional[str] = None,
        keep_good_names: bool = True,
) -> None:
    index_format = f"{{:0{len(str(len(pictures) - 1))}}}"

    def compute_new_stem(picture: Picture, index: int):
        new_name = name
        if keep_good_names and (match := new_stem_re.fullmatch(picture.path.stem)):
            new_name = match.group(1)
        if new_name is None:
            return index_format.format(index)
        else:
            return index_format.format(index) + " - " + new_name

    pictures = sorted(pictures, key=lambda p: p.path.name)
    pictures = sorted(pictures, key=lambda p: p.date() or max_date)
    new_stems = [compute_new_stem(pictures[i], i) for i in range(len(pictures))]

    # Check we won’t overwrite anything
    current_paths = {picture.path for picture in pictures}
    for i in range(len(pictures)):
        new_path = pictures[i].path.with_stem(new_stems[i])
        if new_path not in current_paths and new_path.exists():
            raise FileExistsError(errno.EEXIST, "Target file already exists", str(new_path))

    # Rename in two steps:
    # We can have file foo and bar with foo.new_name == bar.old_name
    for picture in pictures:
        picture.rename_to(str(uuid.uuid4()))
    for i in range(len(pictures)):
        pictures[i].rename_to(new_stems[i])


if __name__ == "__main__":
    args = Arguments(sys.argv)
    pics = list_pictures(args.directory)
    try:
        sort_pictures(pics, args.name, keep_good_names=args.keep_good_names)
    except FileExistsError as error:
        print(f"File already exist, will not overwrite: {error.filename}", file=sys.stderr)
        exit(2)
