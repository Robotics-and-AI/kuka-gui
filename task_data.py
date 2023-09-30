import schema

from file_manager import FileManager

from schema import Schema, Use, And, Or


class TaskData:
    """Class that implements data management related to tasks"""
    def __init__(self, path):
        self.task_saved = {}
        self.tasks = {}
        self.file_manager = FileManager(path)

    def _validate_task(self, task: dict) -> None:
        """
        Fully validate task loaded.

        :param task: task to validate
        """

        # task's schema
        task_schema = Schema(
            {
                "operations": Use(list),
                "positions": Use(dict)
            }
        )

        # operation's schema
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

        # position's schema
        position_schema = Schema(
            {
                "joints": And(Use(list), lambda j: len(j) == 7),
                "cartesian": And(Use(list), lambda c: len(c) == 6)
            }
        )

        # validate task
        try:
            task = task_schema.validate(task)
        except schema.SchemaError:
            raise ValueError("Task file doesn't have the required structure")

        # validate each operation
        for operation in task["operations"]:
            try:
                operation_schema.validate(operation)
            except schema.SchemaError:
                raise ValueError("Operation improperly defined")

        # validate each position
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

        # validate if positions in operations exist
        for operation in task["operations"]:
            if operation["type"] == "move line":
                if operation["position"] not in task["positions"].keys():
                    raise ValueError("Position referenced doesn't exist")

    def add_task(self, encoded_name: str) -> None:
        """
        Add new task to the "database".

        :param encoded_name: name of the task to add
        """

        # check if task already exists
        if encoded_name in self.tasks:
            raise ValueError(f"There already exists a task {encoded_name}")

        # add task
        self.tasks[encoded_name] = {
            "operations": [],
            "positions": {}
        }

        self.task_saved[encoded_name] = False

    def load_task(self, encoded_name: str) -> None:
        """
        load a preexisting task to the "database".

        :param encoded_name: name of task to load
        """

        # check if file exists and load task
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

    def delete_task(self, encoded_name: str, delete_file: bool) -> None:
        """
        Deletes task from the "database" if exists. Delete file if requested.

        :param encoded_name: name of task to delete
        :param delete_file: if True delete file
        """

        # delete task and file if requested
        if encoded_name in self.tasks:
            self.tasks.pop(encoded_name)
            if delete_file:
                self.file_manager.delete_file(encoded_name)
        else:
            raise ValueError(f"There is no task {encoded_name}")

    def save_task(self, encoded_name: str) -> None:
        """
        Saves task to a file.

        :param encoded_name: name of task to save
        """

        # save task
        if encoded_name in self.tasks:
            self.file_manager.save_file(encoded_name, self.tasks[encoded_name])
        else:
            raise ValueError(f"There is no task {encoded_name}")

        self.task_saved[encoded_name] = True

    def get_task_info(self, encoded_name: str) -> dict:
        """
        Get information related to the given task.

        :param encoded_name: name of task to fetch
        """

        # fetch operations
        if encoded_name in self.tasks:
            operations = []
            for i in range(len(self.tasks[encoded_name]["operations"])):
                operations.append(self.get_operation(encoded_name, i))

            # create dict with operations and name of positions
            return {
                "operations": operations,
                "positions": self.get_position_names(encoded_name)
            }
        raise ValueError(f"There is no task {encoded_name}")

    def get_tasks(self) -> list:
        """
        Get names of existing tasks.

        :return: list of task names
        """
        return list(self.tasks.keys())

    def add_operation(self, encoded_name: str) -> dict:
        """
        Add a new operation to the given task

        :param encoded_name: name of task
        :return: created operation
        """

        # create new operation
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
        """
        Update operation in the given task.

        :param encoded_name: name of the task
        :param index: index of the operation to update
        :param operation_type: type of operation
        :param position: position to move to (valid for "move line" tasks)
        :param wait_input: if True task only completed when user gives input
        :param delay: time to wait before continuing to the next task
        :param linear_velocity: velocity to move at in [mm/s] (valid for "move line" tasks)
        :param tool: tool attached to robot (valid for hand-guide tasks)
        :return: updated operation
        """

        # update operation
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

    def delete_operation(self, encoded_name: str, index: int) -> None:
        """
        Delete operation from task.

        :param encoded_name: task to delete operation from
        :param index: index of operation to be deleted
        """
        if encoded_name in self.tasks and len(self.tasks[encoded_name]["operations"]) > index:
            self.tasks[encoded_name]["operations"].pop(index)
        elif encoded_name in self.tasks:
            raise ValueError(f"Operation with index {index} does not exist in task {encoded_name}")
        else:
            raise ValueError(f"There is no task {encoded_name}")

        self.task_saved[encoded_name] = False

    def add_position(self, encoded_task_name: str, encoded_position_name: str, cartesian, joints) -> None:
        """
        Add position to task.

        :param encoded_task_name: task name where position will be added
        :param encoded_position_name: position name
        :param cartesian: cartesian coordinates
        :param joints: joint positions
        """
        if encoded_task_name in self.tasks:
            self.tasks[encoded_task_name]["positions"][encoded_position_name] = {
                "cartesian": cartesian,
                "joints": joints
            }
        else:
            raise ValueError(f"There is no task {encoded_task_name}")

        self.task_saved[encoded_task_name] = False

    def update_position(self, encoded_task_name: str, encoded_position_name: str, cartesian: list, joints: list) \
            -> None:
        """
        Update position values.

        :param encoded_task_name: task name where position is stored
        :param encoded_position_name: position name to update
        :param cartesian: new cartesian coordinates
        :param joints: joint positions
        """

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

    def delete_position(self, encoded_task_name: str, encoded_position_name: str) -> None:
        """
        Delete position from task.

        :param encoded_task_name: task name where position will be deleted from
        :param encoded_position_name: name of position to delete
        """
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
        """
        Get names of all positions in given task.

        :param encoded_task: name of task
        :return: list of position names
        """
        if encoded_task in self.tasks:
            return list(self.tasks[encoded_task]["positions"].keys())
        else:
            raise ValueError(f"There is no task {encoded_task}")

    def get_operation(self, encoded_task: str, operation_index: int) -> dict:
        """
        Get operation by index of operation and task name.

        :param encoded_task: name of task
        :param operation_index: index of operation
        :return: operation
        """
        if encoded_task in self.tasks and operation_index < len(self.tasks[encoded_task]["operations"]):
            operation = self.tasks[encoded_task]["operations"][operation_index]
            # create operation copy
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
        """
        Get position by position name and task name.

        :param encoded_task: task name
        :param encoded_position: position name
        :return: position's cartesian coordinates and joint positions
        """
        if encoded_task in self.tasks and encoded_position in self.tasks[encoded_task]["positions"]:
            return self.tasks[encoded_task]["positions"][encoded_position].copy()
        elif encoded_task in self.tasks:
            raise ValueError(f"Position {encoded_position} does not exist in task {encoded_task}")
        raise ValueError(f"There is no task {encoded_task}")

    def is_task_up_to_date(self, encoded_task: str):
        """
        Get state of task.

        :param encoded_task: task name
        :return: True if task is up to date, False otherwise
        """
        if encoded_task in self.tasks and encoded_task in self.task_saved:
            return self.task_saved[encoded_task]
        elif encoded_task in self.tasks:
            raise ValueError(f"Information about the status of task {encoded_task} does not exist")
        else:
            raise ValueError(f"There is no task {encoded_task}")

    def task_exists(self, encoded_task: str) -> bool:
        """
        Check if task exists.

        :param encoded_task: task name
        :return: True if task exists, False otherwise
        """
        return encoded_task in self.tasks
