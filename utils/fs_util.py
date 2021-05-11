import os
import shutil


def cleanup_dir(dir_path):
    """
    清空文件夹
    """
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.makedirs(dir_path)
