import os
import shutil
import fileinput
import re
import yaml
from typing import List, Dict, Any, Optional

class CommandManager:
    """
    Provides utility methods for managing files and directories, including creation, deletion, copying, and content modification.
    """
    @staticmethod
    def delete_folder(name: str) -> None:
        """
        Deletes all files and directories within a given directory.
        
        :param name: Path of the directory to delete.
        """
        for root, dirs, files in os.walk(name, topdown=False):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

    @staticmethod
    def create_folder(name: str) -> None:
        """
        Creates a new directory if it does not exist.

        :param name: Path of the new directory.
        """
        if not os.path.exists(name):
            os.makedirs(name)

    @staticmethod
    def create_folder_recursive(name: str) -> None:
        """
        Creates a directory and all necessary parent directories.

        :param name: Path of the directory, possibly including multiple levels.
        """
        os.makedirs(name, exist_ok=True)

    @staticmethod
    def recursive_copy(src: str, dest: str) -> None:
        """
        Recursively copies content from the source to the destination directory.

        :param src: Source directory path.
        :param dest: Destination directory path.
        """
        shutil.copytree(src, dest, dirs_exist_ok=True)

    @staticmethod
    def file_copy(src: str, dest: str) -> None:
        """
        Copies a file from source to destination.

        :param src: Source file path.
        :param dest: Destination file path.
        """
        shutil.copy(src, dest)

    @staticmethod
    def replacement(file: str, previousw: str, nextw: str) -> None:
        """
        Replaces a specified word in a file with a new word.

        :param file: Path to the file for replacement.
        :param previousw: Word to be replaced.
        :param nextw: New word to replace with.
        """
        with fileinput.FileInput(file, inplace=True) as f:
            for line in f:
                print(line.replace(previousw, nextw), end='')

    @staticmethod
    def convert_string_to_list(string: Optional[str]) -> List[str]:
        """
        Converts a space-separated string into a list of words.

        :param string: The string to convert; can be None.
        :return: List of words, or an empty list if the string is None.
        """
        if string is None:
            return []
        return string.split()

    @staticmethod
    def convert_list_to_string(values: List[str]) -> str:
        """
        Converts a list of words into a single string with spaces.

        :param values: List of words.
        :return: Single string.
        """
        return ' '.join(values)

    @staticmethod
    def _is_directory_empty(path: str) -> bool:
        """
        Checks if a directory is empty.

        :param path: Directory path.
        :return: True if empty, False otherwise.
        """
        return not os.listdir(path)

    @staticmethod
    def _clear_directory(path: str) -> None:
        """
        Clears all content in a directory.

        :param path: Directory path.
        """
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)

    @staticmethod
    def check_and_clear_directory(path: str) -> None:
        """
        Checks if a directory is not empty and clears it.

        :param path: Directory path.
        """
        if not CommandManager._is_directory_empty(path):
            CommandManager._clear_directory(path)

    @staticmethod
    def create_directory(path: str) -> None:
        """
        Creates a directory if it doesn't exist and clears it if it does.

        :param path: Directory path.
        """
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def convert_key_format(key: str) -> str:
        """
        Converts a key format by replacing all hyphens with underscores.

        :param key: The key to convert.
        :return: The converted key.
        """
        # Replace all hyphens with underscores
        return re.sub(r'-', '_', key)

    @staticmethod
    def determine_domain_name(cluster_type: str, domain_type: str) -> str:
        """
        Determines the domain name based on the cluster type and specified domain type.

        :param cluster_type: The type of the cluster (e.g., 'dev', 'prod').
        :param domain_type: The type of the domain to determine (e.g., 'dev', 'prod').
        :return: The determined domain type.
        """
        split_types = [t.strip() for t in cluster_type.split('|')]
        for type in split_types:
            if type == domain_type:
                return type
        return domain_type  # Default return if not found in split_types

    @staticmethod
    def save_dict_as_yaml(dictionary: Dict[str, Any], file_path: str) -> None:
        """
        Saves a dictionary as a YAML file.

        :param dictionary: The dictionary to be saved.
        :param file_path: The file path where the YAML file will be saved.
        """
        # Convert the dictionary to a YAML-formatted string
        yaml_string = yaml.dump(dictionary, default_flow_style=False)

        # Write the YAML string to the specified file
        with open(file_path, 'w') as file:
            file.write(yaml_string)
