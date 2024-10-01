import argparse
import datetime
import os
import pathlib
from typing import List

########################################################################################################################
DAY_COUNT = 45
ALLOWED_EXTS = [
    "BLF",
    "DLT",
    "PCAP",
    "MF4",
    "MDF",
    "PCAPNG",
]
# #######################################################################################################################

ALLOWED_EXTS = ["." + ext.replace(".", "").upper() for ext in ALLOWED_EXTS]
count = 0
file_size = 0


def move_file_if_date_modified_greater_than(file: pathlib.Path, **kwargs):
    to_be_deleted_path = kwargs.get("to_be_deleted_path", None)
    if to_be_deleted_path is None:
        raise SystemExit("TO_BE_DELETED path is set to None!")

    if file.suffix.upper() in ALLOWED_EXTS:
        converted_date = datetime.date.fromtimestamp(os.path.getmtime(file))
        date_diff = datetime.datetime.now().date() - converted_date
        if date_diff.days > DAY_COUNT:
            print("TO BE DELETED", file)
            new_path = pathlib.Path.joinpath(to_be_deleted_path, file.name)
            file.replace(target=new_path)
            global count
            global file_size
            count += 1
            file_size += os.path.getsize(new_path)


def _clean_dir(path):
    path = pathlib.Path(path)
    for file in path.iterdir():
        if not file.is_dir():
            file.unlink()


def _traverse_dir(path, function, ignored_dirs: List[pathlib.Path], **kwargs):
    path = pathlib.Path(path)
    if path not in ignored_dirs:
        if path.is_dir():
            for file in path.iterdir():
                _traverse_dir(file, function, ignored_dirs, **kwargs)
        else:
            return function(path, **kwargs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="delete_logs",
        description="Deletes logs older than a given amount of time"
    )
    parser.add_argument("-path", type=str, nargs="?", default=pathlib.Path(os.getcwd()))
    parser.add_argument("-tbd", type=str, nargs="?", default=None)
    parser.add_argument("-m", "--manual", action="store_true")
    args = parser.parse_args()

    if args.path is not None and os.path.exists(args.path):
        path_to_be_traversed = args.path
    else:
        raise SystemExit("The path provided does not exist!")

    if args.tbd is not None:
        TO_BE_DELETED_PATH = args.tbd
    else:
        TO_BE_DELETED_PATH = pathlib.Path(path_to_be_traversed).joinpath("TO_BE_DELETED")

    if not os.path.exists(TO_BE_DELETED_PATH):
        try:
            os.mkdir(TO_BE_DELETED_PATH)
        except:
            raise SystemExit(f"Couldn't create a new directory for TO_BE_DELETED path: {TO_BE_DELETED_PATH}")

    print("*" * 50)
    print("PATH:", path_to_be_traversed)
    print("TO_BE_DELETED_PATH:", TO_BE_DELETED_PATH)
    print("*" * 50)

    _traverse_dir(path_to_be_traversed, move_file_if_date_modified_greater_than,
                  ignored_dirs=[TO_BE_DELETED_PATH],
                  to_be_deleted_path=TO_BE_DELETED_PATH)
    if count:
        response = input(
            f"Do you want to clean the TO_BE_DELETED directory. This operation would clear "
            f"{(file_size / (1024 * 1024 * 1024)):.3} GB of memory.\nY - Yes / N - No: ")
        if response.upper().strip() == "Y":
            _clean_dir(TO_BE_DELETED_PATH)
            print("TO_BE_DELETED directory has been cleaned!")
    else:
        print(f"No file older than {DAY_COUNT} days has been found. Exiting.")
