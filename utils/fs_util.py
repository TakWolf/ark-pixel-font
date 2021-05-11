import os
import shutil


def cleanup_dir(dir_path):
    """
    清空文件夹
    """
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.makedirs(dir_path)


def make_dirs_if_not_exists(dir_path):
    """
    如果文件夹不存在，则创建文件夹
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
