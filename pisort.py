import sys
from getopt import getopt
from pathlib import Path
from typing import Optional, TextIO, Never

from PIL import Image, UnidentifiedImageError, ExifTags


class Arguments:

    def __init__(self, argv: list[str]):
        def fatal(msg: str) -> Never:
            print(f"{argv[0]}: {msg}", file=sys.stderr)
            exit(1)

        options, parameters = getopt(argv[1:], "")

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


if __name__ == "__main__":
    args = Arguments(sys.argv)
    for image in list_pictures(args.directory):
        image.print()
