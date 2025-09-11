import sys
from getopt import getopt
from pathlib import Path
from typing import Never


class Arguments:

    def __init__(self, argv: list[str]):
        def fatal(msg: str) -> Never:
            print(f"{argv[0]}: {msg}", file=sys.stderr)
            exit(1)

        options, parameters = getopt(argv[1:], "h", [
            "name=",
            "no-keep",
            "keep",
            "help",
        ])

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
                case "-h" | "--help":
                    print(f"""\
usage: {argv[0]} [options] [directory]

Sort files with Exif dates from a directory in chronological order. If
unspecified, this directory defaults to the working directory.

Files with no Exif metadata or no date in their metadata will be ignored.

Options:
 -h,--help      Display this help message.
 --keep         Keep the name part of files whose filename matches
                "<number> - <name>" (this is the default). Such files are still
                renumbered. This is useful when files were each given a
                different name and need renumbering because other files were
                added or removed from the directory. This option allows
                overwriting a previous --no-keep option.
 --name <arg>   Set a name to give files in addition of their index.
 --no-keep      Always discard existing filenames. See the --keep option.""")
                    exit(0)

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
