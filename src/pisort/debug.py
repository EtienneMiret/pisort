import sys
from pathlib import Path

from pisort.Picture import Picture

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        try:
            Picture(Path(arg)).print()
        except Exception as e:
            print(f'{arg}: {e}', file=sys.stderr)
