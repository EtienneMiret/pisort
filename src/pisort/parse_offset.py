import datetime
import re

import tzlocal


exif_offset_re = re.compile("([+-])(\\d\\d):(\\d\\d)", re.ASCII)

def parse_offset(string: str) -> datetime.tzinfo:
    match = exif_offset_re.fullmatch(string)
    if not match:
        return tzlocal.get_localzone()
    delta = datetime.timedelta(
        hours=int(match.group(2)),
        minutes=int(match.group(3)),
    )
    if match.group(1) == "-":
        delta = -delta
    return datetime.timezone(delta, string)
