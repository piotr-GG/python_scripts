import datetime
import os.path
import pathlib
import subprocess
import re
import shutil


def split_data_into_folders(data):
    data_dict = dict()
    for el in data:
        if el:
            split_data = el.split(r"/")
            if len(split_data) == 2:
                folder, file = split_data
                file_list = data_dict.get(folder, [])
                file_list.append(file)
                data_dict[folder] = file_list
            else:
                print(f"Couldn't process {el}")
    return data_dict


PATH_TO_COPY = pathlib.Path(r"C:\Desktop\recycle_bin")
PATH = pathlib.Path(r"D:\Pool\Environment")

proc = subprocess.Popen(["git.exe", "-C", str(PATH), "pull"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
p = "".join([el.decode() for el in proc.stdout.readlines()])

local_dict = dict()
untracked_dict = dict()

current_timestamp = datetime.datetime.now().strftime("%d_%m_%y__%H_%M_%S")
regex_local_changes = (r"(?<=error: Your local changes to the following files would be overwritten by merge:\n)(("
                       r"?:.*\n)*)(?=Please commit)")
regex_untracked = (r"(?<=error: The following untracked working tree files would be overwritten by merge:\n)(("
                   r"?:.*\n)*)(?=Please move or remove them before you merge.)")

local_changes = re.findall(regex_local_changes, p, flags=re.M)
untracked = re.findall(regex_untracked, p, flags=re.M)

if local_changes:
    local_changes = local_changes[0]
    local_changes = [el.strip() for el in local_changes.split("\n")]

    print("-" * 50, "LOCAL CHANGES", "-" * 50)
    local_dict = split_data_into_folders(local_changes)

if untracked:
    untracked = untracked[0]
    untracked = [el.strip() for el in untracked.split("\n")]

    print("-" * 50, "UNTRACKED FILES", "-" * 50)
    untracked_dict = split_data_into_folders(untracked)

proc = subprocess.check_output(["git.exe", "-C", str(PATH), "rev-parse", "--show-toplevel"])
git_root_dir = proc.decode().strip()
git_root_dir = pathlib.Path(git_root_dir)

print("Path".ljust(30), PATH)
print("Path to copy".ljust(30), PATH_TO_COPY)
print("Git root dir:".ljust(30), git_root_dir)
print("Local changes count:".ljust(30), len(local_changes))
print("Untracked changes count:".ljust(30), len(untracked))

if local_dict or untracked_dict:
    COPY_FOLDER = pathlib.Path(PATH_TO_COPY, current_timestamp)
    COPY_FOLDER.mkdir()

    # Merging the two dicts
    local_untracked_dict = {**local_dict, **untracked_dict}

    for folder in local_untracked_dict:
        source_folder_path = pathlib.Path(git_root_dir, folder)
        copy_folder_path = pathlib.Path(COPY_FOLDER, folder)

        if not os.path.exists(copy_folder_path):
            os.mkdir(copy_folder_path)

        files = local_untracked_dict[folder]
        for file in files:
            source_file_path = source_folder_path / file
            if source_file_path.exists():
                target_file_path = copy_folder_path / file

                print("Copying", source_file_path, "-->", target_file_path)
                shutil.copy(source_file_path, target_file_path)
                source_file_path.unlink()
            else:
                print(f"Source file path {source_file_path} does not exist - copying aborted.")

    if local_changes:
        # Restoring the file version for local files
        print("Restoring the files...")
        print(f"git -C {git_root_dir} restore {' '.join(local_changes).strip()}")
        subprocess.call(["git.exe", "-C", str(git_root_dir), "restore", *local_changes])

else:
    print("Didn't find any conflicts. Exiting.")