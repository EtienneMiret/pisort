from pathlib import Path
from typing import Optional, TextIO

from PIL import Image, UnidentifiedImageError, ExifTags


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
    for image in list_pictures(Path(".")):
        image.print()
