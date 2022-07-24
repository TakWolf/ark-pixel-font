import os
import shutil


def delete_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)


def make_dirs_if_not_exists(path):
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise Exception(f"Path exists but not a directory: '{path}'")
    else:
        os.makedirs(path)
