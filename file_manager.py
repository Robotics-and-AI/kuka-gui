from typing import Union
import os
import json


# class for file management
class FileManager:
    def __init__(self, path: str):
        # directory where files are saved
        self.path = path

    def file_exists(self, file_name: str) -> bool:
        """
        Check if file exists.

        :param file_name: file name
        :return: True if file exists, False otherwise
        """
        return os.path.exists(os.path.join(self.path, f"{file_name}.json"))

    def save_file(self, file_name: str, file_data: Union[list, dict]) -> None:
        """
        Save given data to the specified file.

        :param file_name: file to save to
        :param file_data: data to save
        :return:
        """
        with open(os.path.join(self.path, f"{file_name}.json"), "w+") as file:
            json.dump(file_data, file, indent=2, sort_keys=True)

    def load_file(self, file_name: str) -> Union[list, dict]:
        """
        Load file.

        :param file_name: name of the file to load from
        :return: data read on the specified file
        """
        if self.file_exists(file_name):
            with open(os.path.join(self.path, f"{file_name}.json")) as file:
                return json.load(file)
        else:
            raise FileNotFoundError(f"There is no file {file_name}.json")

    def delete_file(self, file_name: str) -> None:
        """
        Delete file with given name.

        :param file_name: name of file to be deleted
        """
        if self.file_exists(file_name):
            os.remove(os.path.join(self.path, f"{file_name}.json"))
