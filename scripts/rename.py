""""""

# Standard library modules.
import os
import glob
import argparse
import shutil

# Third party modules.

# Local modules.
from musictools.song import Song

# Globals and constants variables.

def main():
    parser = argparse.ArgumentParser(description='Rename mp3/ogg files')
    parser.add_argument('-o', '--output', required=True,
                        help='Output directory')
    parser.add_argument('dir', nargs='+', help='Directory containing mp3/ogg files')

    args = parser.parse_args()

    outdirpath = args.output

    for dirpath in args.dir:
        filepaths = glob.glob(os.path.join(dirpath, '**', '*.mp3'), recursive=True)
        filepaths += glob.glob(os.path.join(dirpath, '**', '*.ogg'), recursive=True)

        for filepath in filepaths:
            song = Song(filepath)

            newdirpath = os.path.join(outdirpath, song.formatted_dirname)
            os.makedirs(newdirpath, exist_ok=True)

            newfilepath = os.path.join(newdirpath, song.formatted_filename)
            shutil.move(filepath, newfilepath)
            print('{} -> {}'.format(filepath, newfilepath))

if __name__ == '__main__':
    main()
