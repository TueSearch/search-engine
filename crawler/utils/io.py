"""
This module contains functions for reading and writing files.
"""
import _pickle as pickle
import json
import os
import shutil
from pathlib import Path
from crawler.utils.log import get_logger

LOG = get_logger(__file__)


def read_json_file(path: str) -> json:
    """
    Reads a JSON file and returns the parsed JSON object.

    Args:
        path (str): Path to the JSON file.

    Returns:
        json: Parsed JSON object.
    """
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json_file(json_object: json, path: str):
    """
    Writes a JSON object to a file in JSON format.

    Args:
        json_object (json): JSON object to be written to the file.
        path (str): Path to the output JSON file.
    """
    create_parent_directory_if_not_exist(path)
    with open(path, "w", encoding="utf-8") as file:
        return json.dump(json_object, file)


def read_pickle_file(path: str) -> json:
    """
    Reads a pickled object from a file and returns it.

    Args:
        path (str): Path to the pickled file.

    Returns:
        json: Pickled object.
    """
    with open(path, "rb") as file:
        return pickle.load(file)


def write_pickle_file(json_object: json, path: str):
    """
    Writes a Python object to a file in pickled format.

    Args:
        json_object (json): Python object to be pickled and written to the file.
        path (str): Path to the output pickled file.
    """
    create_parent_directory_if_not_exist(path)
    with open(path, "wb") as file:
        return pickle.dump(json_object, file)


def create_parent_directory_if_not_exist(path: str) -> str:
    """
    Creates the parent directory for a given file path if it does not exist.

    Args:
        path (str): Path to the file.

    Returns:
        str: The input path.
    """
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    return path


def create_directory_if_not_exists(path: str):
    """
    Creates a directory if it does not exist.

    Args:
        path (str): Path to the directory.

    Returns:
        str: The input path.
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def delete_files_in_directory(directory: str):
    """
    Deletes all files in a directory.

    Args:
        directory (str): Path to the directory.
    """
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                LOG.info(f"Deleted file: {file_path}")


def delete_subdirectories_in_directory(directory: str):
    """
    Deletes all subdirectories in a directory.

    Args:
        directory (str): Path to the directory.
    """
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if not os.path.isfile(file_path):
                shutil.rmtree(file_path)
                LOG.info(f"Deleted directory: {file_path}")


def delete_file(file: str):
    """
    Deletes a file.

    Args:
        file (str): Path to the file.
    """
    if os.path.isfile(file):
        os.remove(file)
        LOG.info(f"Deleted file: {file}")
