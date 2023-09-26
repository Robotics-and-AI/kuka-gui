from typing import Union
import os
import json


class FileManager:
    def __init__(self, path: str):
        self.path = path

    def file_exists(self, file_name: str):
        return os.path.exists(f"{self.path}\\{file_name}.json")

    def save_file(self, file_name: str, file_data: Union[list, dict]):
        with open(f"{self.path}\\{file_name}.json", "w+") as file:
            json.dump(file_data, file, indent=2, sort_keys=True)

    def load_file(self, file_name: str) -> Union[list, dict]:
        if self.file_exists(file_name):
            with open(f"{self.path}\\{file_name}.json") as file:
                return json.load(file)
        else:
            raise FileNotFoundError(f"There is no file {file_name}.json")

    def delete_file(self, file_name: str):
        if self.file_exists(file_name):
            os.remove(f"{self.path}\\{file_name}.json")
