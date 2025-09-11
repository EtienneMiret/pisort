from pathlib import Path

from PIL import UnidentifiedImageError

from pisort.Picture import Picture


def list_pictures(directory: Path) -> list[Picture]:
    result = []
    for file in directory.iterdir():
        if not file.is_file():
            continue
        try:
            pic = Picture(file)
            if pic.date() is not None:
                result.append(pic)
        except UnidentifiedImageError:
            pass
    return result
