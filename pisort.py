from pathlib import Path
from PIL import Image, UnidentifiedImageError, ExifTags


def list_pictures(directory: Path) -> None:
    for file in directory.iterdir():
        if not file.is_file():
            continue
        try:
            exif = Image.open(file).getexif()
            print(f'{file.name} has EXIF:')
            for k, v in exif.items():
                print(f'  {ExifTags.TAGS[k]}: {v}')
            for k, v in exif.get_ifd(ExifTags.IFD.Exif).items():
                print(f'  {ExifTags.TAGS[k]}: {v}')
        except UnidentifiedImageError:
            pass


if __name__ == "__main__":
    list_pictures(Path("."))
