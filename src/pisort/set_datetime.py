import datetime
import getopt
import sys
from pathlib import Path
from typing import Any

import piexif
import tzlocal

from pisort.fmt_offset import fmt_offset


ImageIFD = "0th"
ExifIFD = "Exif"

tz = tzlocal.get_localzone()

def has_datetime(exif: dict[str, dict[int, Any]]) -> bool:
    for key in [
        (ExifIFD, piexif.ExifIFD.DateTimeOriginal),
        (ExifIFD, piexif.ExifIFD.DateTimeDigitized),
        (ImageIFD, piexif.ImageIFD.DateTime),
    ]:
        if key[0] in exif and key[1] in exif[key[0]]:
            return True
    return False

def process(path: Path, force: bool) -> None:
    try:
        exif = piexif.load(str(path))
    except Exception as e:
        print(f"Failed to load {path}: {e}", file=sys.stderr)
        return
    if (not force) and has_datetime(exif):
        return
    date = datetime.datetime.fromtimestamp(path.lstat().st_mtime, tz=tz)
    if ExifIFD not in exif:
        exif[ExifIFD] = {}
    exif[ExifIFD][piexif.ExifIFD.DateTimeOriginal] = date.strftime("%Y:%m:%d %H:%M:%S")
    exif[ExifIFD][piexif.ExifIFD.OffsetTimeOriginal] = fmt_offset(date)
    binary = piexif.dump(exif)
    piexif.insert(binary, str(path))
    print(f"Wrote {date} to {path}")

if __name__ == "__main__":
    options, _ = getopt.getopt(sys.argv[1:], "fh", [
        "force",
        "help",
    ])

    f = False
    for k, v in options:
        match k:
            case "-f" | "--force":
                f = True
            case "-h" | "--help":
                print(f"""
usage: {sys.argv[0]} [options] paths...

Set the Exif dates of the files specified in `paths...` to their filesystem
last modification time. Unless the `-f` option is specified, the date will
not be set on files that already have one in their Exif metadata.

Options:
 -h,--help      Display this help message and exit.
 -f,--force     Set the Exif date even if there is already one.
""")
                exit(0)

    for filename in sys.argv[1:]:
        process(Path(filename), f)
