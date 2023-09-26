import schema

from file_manager import FileManager

from schema import Schema, Use, And, Or


class TaskData:
    """Class that implements data management related to tasks"""
    def __init__(self, path):
        self.task_saved = {}
        self.tasks = {}
        self.file_manager = FileManager(path)

    def _validate_task(self, task):
        """Fully validate task loaded"""
        task_schema = Schema(
            {
                "operations": Use(list),
                "positions": Use(dict)
            }
        )

        operation_schema = Schema(
            {
                "type": And(Use(str), lambda t: t in ["move line", "open", "close", "hand-guide"]),
                "position": Use(str),
                "wait": Use(bool),
                "delay": And(Or(Use(int), Use(float)), lambda d: d >= 0),
                "linear_velocity": And(Or(Use(int), Use(float)), lambda d: d >= 0),
                "tool": Use(str)
            }
        )

        position_schema = Schema(
            {
                "joints": And(Use(list), lambda j: len(j) == 7),
                "cartesian": And(Use(list), lambda c: len(c) == 6)
            }
        )

        try:
            task = task_schema.validate(task)
        except schema.SchemaError:
            raise ValueError("Task file doesn't have the required structure")

        for operation in task["operations"]:
            try:
                operation_schema.validate(operation)
            except schema.SchemaError:
                raise ValueError("Operation improperly defined")

        for position in task["positions"]:
            try:
                position_schema.validate(task["positions"][position])
            except schema.SchemaError as e:
                raise ValueError("Position improperly defined")

            for element in task["positions"][position]["joints"]:
                if not isinstance(element, int) and not isinstance(element, float):
                    raise ValueError("Joints improperly defined")

            for element in task["positions"][position]["cartesian"]:
                if not isinstance(element, int) and not isinstance(element, float):
                    raise ValueError("Cartesian coordinates improperly defined")

        for operation in task["operations"]:
            if operation["type"] == "move line":
                if operation["position"] not in task["positions"].keys():
                    raise ValueError("Position referenced doesn't exist")

    def add_task(self, encoded_name: str):
        """Add new task to the "database". Returns validated name. Raises error if not successful"""
        if encoded_name in self.tasks:
            raise ValueError(f"There already exists a task {encoded_name}")

        self.tasks[encoded_name] = {
            "operations": [],
            "positions": {}
        }

        self.task_saved[encoded_name] = False

    def load_task(self, encoded_name: str):
        """load a preexisting task to the "database". Raises error if not successful"""

        if encoded_name not in self.tasks:
            if self.file_manager.file_exists(encoded_name):
                task = self.file_manager.load_file(encoded_name)
                try:
                    self._validate_task(task)
                except ValueError:
                    raise

                self.tasks[encoded_name] = task
            else:
                raise FileNotFoundError(f"There is no file {encoded_name}.json")
        else:
            raise ValueError(f"A task {encoded_name} already exists")

        self.task_saved[encoded_name] = True

    """Deletes task from the "database" if exists. If requested if a file exists it is also deleted
       Raises error if not successful"""
    def delete_task(self, encoded_name: str, delete_file: bool):
        if encoded_name in self.tasks:
            self.tasks.pop(encoded_name)
            if delete_file:
                self.file_manager.delete_file(encoded_name)
        else:
            raise ValueError(f"There is no task {encoded_name}")

    def save_task(self, encoded_name: str):
        """Saves task from the "database" to the corresponding file. Raises error if not successful"""
        if encoded_name in self.tasks:
            self.file_manager.save_file(encoded_name, self.tasks[encoded_name])
        else:
            raise ValueError(f"There is no task {encoded_name}")

        self.task_saved[encoded_name] = True

    def get_task_info(self, encoded_name: str) -> dict:
        """Returns info of the requested task. Raises error if not successful"""
        if encoded_name in self.tasks:
            operations = []
            for i in range(len(self.tasks[encoded_name]["operations"])):
                operations.append(self.get_operation(encoded_name, i))

            return {
                "operations": operations,
                "positions": self.get_position_names(encoded_name)
            }
        raise ValueError(f"There is no task {encoded_name}")

    def get_tasks(self) -> list:
        """Returns list of tasks"""
        return list(self.tasks.keys())

    def add_operation(self, encoded_name: str) -> dict:
        """Add new operation to the requested task. Raises error if not successful"""
        if encoded_name in self.tasks:
            self.tasks[encoded_name]["operations"].append({
                "type": "open",
                "position": "",
                "delay": 0,
                "wait": False,
                "linear_velocity": 5,
                "tool": ""
            })
        else:
            raise ValueError(f"There is no task {encoded_name}")

        self.task_saved[encoded_name] = False
        return self.get_operation(encoded_name, -1)

    def update_operation(self, encoded_name: str, index: int, operation_type: str, position: str = "",
                         wait_input: bool = False, delay: float = 1, linear_velocity: float = 5,
                         tool: str = "") -> dict:
        """Update operation values. Raises error if not successful"""
        if encoded_name in self.tasks and index < len(self.tasks[encoded_name]["operations"]):
            self.tasks[encoded_name]["operations"][index] = {
                "type": operation_type,
                "position": position,
                "wait": wait_input,
                "delay": delay,
                "linear_velocity": linear_velocity,
                "tool": tool
            }
        elif encoded_name in self.tasks:
            raise ValueError(f"Operation with index {index} does not exist in task {encoded_name}")
        else:
            raise ValueError(f"There is no task {encoded_name}")

        self.task_saved[encoded_name] = False
        return self.get_operation(encoded_name, index)

    def delete_operation(self, encoded_name: str, index: int):
        """Delete operation from task. Raises error if not successful"""
        if encoded_name in self.tasks and len(self.tasks[encoded_name]["operations"]) > index:
            self.tasks[encoded_name]["operations"].pop(index)
        elif encoded_name in self.tasks:
            raise ValueError(f"Operation with index {index} does not exist in task {encoded_name}")
        else:
            raise ValueError(f"There is no task {encoded_name}")

        self.task_saved[encoded_name] = False

    def add_position(self, encoded_task_name: str, encoded_position_name: str, cartesian, joints):
        """Associate a new position to the task. Raises error if not successful. Raises error if not successful"""
        if encoded_task_name in self.tasks:
            self.tasks[encoded_task_name]["positions"][encoded_position_name] = {
                "cartesian": cartesian,
                "joints": joints
            }
        else:
            raise ValueError(f"There is no task {encoded_task_name}")

        self.task_saved[encoded_task_name] = False

    def update_position(self, encoded_task_name: str, encoded_position_name: str, cartesian: list, joints: list):
        """Update position values. Raises error if not successful"""
        if encoded_task_name in self.tasks and encoded_position_name in self.tasks[encoded_task_name]["positions"]:
            self.tasks[encoded_task_name]["positions"][encoded_position_name] = {
                "cartesian": cartesian,
                "joints": joints
            }
        elif encoded_task_name in self.tasks:
            raise ValueError(f"There is no position {encoded_position_name} in task {encoded_task_name}")
        else:
            raise ValueError(f"There is no task {encoded_task_name}")

        self.task_saved[encoded_task_name] = False

    def delete_position(self, encoded_task_name: str, encoded_position_name: str):
        """Delete position from task. Raises error if not successful"""
        if encoded_task_name in self.tasks and encoded_position_name in self.tasks[encoded_task_name]["positions"]:
            task = self.get_task_info(encoded_task_name)
            for operation in task["operations"]:
                if operation["position"] == encoded_position_name:
                    raise ValueError(f"Position {encoded_position_name} is being used in one operation")
            self.tasks[encoded_task_name]["positions"].pop(encoded_position_name)
        elif encoded_task_name in self.tasks:
            raise ValueError(f"There is no position {encoded_position_name} in task {encoded_task_name}")
        else:
            raise ValueError(f"There is no task {encoded_task_name}")

        self.task_saved[encoded_task_name] = False

    def get_position_names(self, encoded_task: str) -> list:
        """Get names of all positions from task. Raises error if not successful"""
        if encoded_task in self.tasks:
            return list(self.tasks[encoded_task]["positions"].keys())
        else:
            raise ValueError(f"There is no task {encoded_task}")

    def get_operation(self, encoded_task: str, operation_index: int) -> dict:
        """Get position by index of operation and task name. Raises error if not successful"""
        if encoded_task in self.tasks and operation_index < len(self.tasks[encoded_task]["operations"]):
            operation = self.tasks[encoded_task]["operations"][operation_index]
            return {
                "type": operation["type"],
                "position": operation["position"],
                "wait": operation["wait"],
                "delay": operation["delay"],
                "linear_velocity": operation["linear_velocity"],
                "tool": operation["tool"]
            }
        if encoded_task in self.tasks:
            raise ValueError(f"Operation with index {operation_index} does not exist in task {encoded_task}")
        else:
            raise ValueError(f"There is no task {encoded_task}")

    def get_position(self, encoded_task: str, encoded_position: str) -> dict:
        """Get position by position name and task name. Raises error if not successful"""
        if encoded_task in self.tasks and encoded_position in self.tasks[encoded_task]["positions"]:
            return self.tasks[encoded_task]["positions"][encoded_position].copy()
        elif encoded_task in self.tasks:
            raise ValueError(f"Position {encoded_position} does not exist in task {encoded_task}")
        raise ValueError(f"There is no task {encoded_task}")

    def is_task_up_to_date(self, encoded_task: str):
        """Is task up to date"""
        if encoded_task in self.tasks and encoded_task in self.task_saved:
            return self.task_saved[encoded_task]
        elif encoded_task in self.tasks:
            raise ValueError(f"Information about the status of task {encoded_task} does not exist")
        else:
            raise ValueError(f"There is no task {encoded_task}")

    def task_exists(self, encoded_task: str) -> bool:
        """Return if task exists"""
        return encoded_task in self.tasks
