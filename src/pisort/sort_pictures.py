import datetime
import errno
import re
import uuid
from typing import Optional

from pisort.Picture import Picture

max_date = datetime.datetime(
    datetime.MAXYEAR, 12, 31,
    tzinfo=datetime.timezone.utc,
)
new_stem_re = re.compile("\\d+ - (.*)")


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
