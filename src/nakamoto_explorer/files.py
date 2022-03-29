from os import walk
from typing import List, Union

from pandas import DataFrame
from yaml import safe_load


def ensure_folder_format(folder: str, use_backslashes: bool = False) -> str:
    """ Ensure that the path returned does NOT end in `/`. """
    folder = normalize_path(folder)
    if folder[-1] == '/':
        folder = folder[:-1]
    return normalize_path(folder, use_backslashes=use_backslashes)


def get_folders_inside_folder(folder: str) -> List[str]:
    folder = ensure_folder_format(folder)
    folders_inside = [folders for root, folders, files in walk(folder)]
    if len(folders_inside) > 0:
        return folders_inside[0]
    return []


def load_csv(file_path: str) -> DataFrame:
    from pandas import read_csv
    return read_csv(file_path)


def load_yaml(yaml_file: str) -> Union[dict, list]:
    with open(yaml_file, 'r') as file:
        return safe_load(file)


def normalize_path(path: str, use_backslashes: bool = False) -> str:
    if use_backslashes:
        path = path.replace('/', '\\')
    else:
        path = path.replace('\\', '/')
    return path
