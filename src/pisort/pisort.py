import sys

from pisort.Arguments import Arguments
from pisort.list_pictures import list_pictures
from pisort.sort_pictures import sort_pictures

if __name__ == "__main__":
    args = Arguments(sys.argv)
    pics = list_pictures(args.directory)
    try:
        sort_pictures(pics, args.name, keep_good_names=args.keep_good_names)
    except FileExistsError as error:
        print(f"File already exist, will not overwrite: {error.filename}", file=sys.stderr)
        exit(2)
