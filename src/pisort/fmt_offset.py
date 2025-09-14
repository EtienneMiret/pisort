import datetime


def fmt_offset(dt: datetime.datetime) -> str:
    """
    Format the TZ offset from UTC of the given date time according to Exif
    specification.

    :return: a string that will be 7 bytes long in ASCII with a NULL terminator.
    """
    delta = dt.utcoffset()
    if delta is None:
        return "   :  "
    sgn = "-" if delta < datetime.timedelta()\
        else "+"
    hours = abs(delta.total_seconds()) // 3600
    minutes = (abs(delta.total_seconds()) // 60) % 60
    return f"{sgn}{hours:02.0f}:{minutes:02.0f}"
