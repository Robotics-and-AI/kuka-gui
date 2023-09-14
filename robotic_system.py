import re
import time

from program_data import ProgramData
from ctkinter_elements import CTkOkCancel
from robot_communication import RobotCommunication
from task_data import TaskData


class RoboticSystem:
    def __init__(self, robot: RobotCommunication, task_data: TaskData, program_data: ProgramData):
        self._robot = robot
        self._task_data = task_data
        self._program_data = program_data

    def _validate_str(self, name: str) -> str:
        """Validate name input. Extra spaces are trimmed and final format is: Aaa aaa aaa"""
        name = re.sub(r'[^\w_. -]', '', name)
        name = name.replace("_", " ").strip()
        if name:
            name = " ".join(name.split()).lower()
            name = name[0].upper() + name[1:]
            return name
        return ""

    def _encode_str(self, input_str: str) -> str:
        """Encodes name for file storage and "database" management. It follows the format: aaa_aaa_aaa"""
        return input_str.lower().strip().replace(" ", "_")

    def _decode_str(self, input_str: str) -> str:
        """Decode name to display"""
        return input_str[0].upper() + input_str[1:].replace("_", " ")

    def _decode_str_list(self, encoded_str_list):
        """Function to decode entire list"""
        decoded_str_list = []
        for encoded_str in encoded_str_list:
            decoded_str_list.append(self._decode_str(encoded_str))
        return decoded_str_list

    def add_task(self, task_name: str) -> str:
        """Add new task to the "database". Returns validated name. Raises error if not successful"""
        task_name = self._validate_str(task_name)
        if task_name == "":
            raise ValueError(f"Name {task_name} is not valid! Make sure it has characters that are not space and "
                             f"underscore")

        encoded_name = self._encode_str(task_name)
        try:
            self._task_data.add_task(encoded_name)
        except ValueError:
            raise
        return task_name

    def load_task(self, task_name: str) -> str:
        """load a preexisting task to the "database". Raises error if not successful"""
        task_name = self._validate_str(task_name)
        encoded_name = self._encode_str(task_name)
        try:
            self._task_data.load_task(encoded_name)
        except ValueError:
            raise
        except FileNotFoundError:
            raise
        return task_name

    """Deletes task from the "database" if exists. If requested if a file exists it is also deleted
       Raises error if not successful"""

    def delete_task(self, task_name: str, delete_file: bool):
        encoded_name = self._encode_str(task_name)
        try:
            self._task_data.delete_task(encoded_name, delete_file)
        except ValueError:
            raise

    def save_task(self, task_name: str):
        """Saves task from the "database" to the corresponding file. Raises error if not successful"""
        encoded_name = self._encode_str(task_name)
        try:
            self._task_data.save_task(encoded_name)
        except ValueError:
            raise

    def get_task_info(self, task_name: str) -> dict:
        """Returns info of the requested task. Raises error if not successful"""
        encoded_name = self._encode_str(task_name)
        try:
            task = self._task_data.get_task_info(encoded_name)
            task["positions"] = self._decode_str_list(task["positions"])
            return task
        except ValueError:
            raise

    def get_tasks(self) -> list:
        """Returns list of tasks"""
        return self._decode_str_list(self._task_data.get_tasks())

    def add_operation(self, task_name: str) -> dict:
        """Add new operation to the requested task. Raises error if not successful"""
        encoded_name = self._encode_str(task_name)
        try:
            return self._task_data.add_operation(encoded_name)
        except ValueError:
            raise

    def update_operation(self, task_name: str, index: int, operation_type: str, position: str = "",
                         wait_input: bool = False, delay: float = 1, linear_velocity: float = 5) -> dict:
        """Update operation values. Raises error if not successful"""
        encoded_name = self._encode_str(task_name)
        encoded_position = self._encode_str(position)
        try:
            return self._task_data.update_operation(encoded_name, index, operation_type, encoded_position, wait_input,
                                                    delay, linear_velocity)
        except ValueError:
            raise

    def delete_operation(self, task_name: str, index: int):
        """Delete operation from task. Raises error if not successful"""
        encoded_name = self._encode_str(task_name)
        try:
            self._task_data.delete_operation(encoded_name, index)
        except ValueError:
            raise

    def add_position(self, task_name: str, position_name: str, cartesian, joints) -> str:
        """Associate a new position to the task. Raises error if not successful. Raises error if not successful"""
        encoded_task_name = self._encode_str(task_name)
        position_name = self._validate_str(position_name)
        encoded_position_name = self._encode_str(position_name)
        if encoded_position_name == "":
            raise ValueError(f"Name {position_name} is not valid! Make sure it has characters that are not space "
                             f"and underscore")
        try:
            self._task_data.add_position(encoded_task_name, encoded_position_name, cartesian, joints)
        except ValueError:
            raise
        return position_name

    def update_position(self, task_name: str, position_name: str, cartesian: list, joints: list):
        """Update position values. Raises error if not successful"""
        encoded_task_name = self._encode_str(task_name)
        encoded_position_name = self._encode_str(position_name)
        try:
            self._task_data.update_position(encoded_task_name, encoded_position_name, cartesian, joints)
        except ValueError:
            raise

    def delete_position(self, task_name: str, position_name: str):
        """Delete position from task. Raises error if not successful"""
        encoded_task_name = self._encode_str(task_name)
        encoded_position_name = self._encode_str(position_name)
        try:
            self._task_data.delete_position(encoded_task_name, encoded_position_name)
        except ValueError:
            raise

    def get_position_names(self, task_name: str) -> list:
        """Get names of all positions from task. Raises error if not successful"""
        encoded_task = self._encode_str(task_name)
        try:
            return self._decode_str_list(self._task_data.get_position_names(encoded_task))
        except ValueError:
            raise

    def get_operation(self, task_name: str, operation_index: int) -> dict:
        """Get position by index of operation and task name. Raises error if not successful"""
        encoded_task = self._encode_str(task_name)
        try:
            return self._task_data.get_operation(encoded_task, operation_index)
        except ValueError:
            raise

    def get_position(self, task_name: str, position_name: str) -> dict:
        """Get position by position name and task name. Raises error if not successful"""
        encoded_task = self._encode_str(task_name)
        encoded_position = self._encode_str(position_name)
        try:
            return self._task_data.get_position(encoded_task, encoded_position)
        except ValueError:
            raise

    def start_robot_connection(self, ip: str) -> str:
        """Attempts connection to the robot. Raises error if unsuccessful"""
        try:
            return self._robot.start_connection(ip)
        except OSError:
            raise
        except ValueError:
            raise

    def stop_robot_connection(self):
        """Stops connection with the robot"""
        self._robot.stop_connection()

    def is_robot_connected(self) -> bool:
        """Checks if robot is currently connected"""
        return self._robot.is_connected()

    def get_robot_position(self) -> tuple:
        """Gets robot's current position"""
        try:
            position = self._robot.get_position()
        except OSError:
            raise
        except ValueError:
            raise

        return position

    def run_program(self):
        tasks = self._program_data.get_tasks()
        for task in tasks:
            if self._get_task_state_from_input(task) == 2:
                raise RuntimeError(f"Task {task} doesn't exist")
        for task in tasks:
            try:
                if not self.run_task(task):
                    return
            except ValueError:
                raise
            except OSError:
                raise

    def run_task(self, task_name: str) -> bool:
        ready_to_continue = True
        try:
            task = self._task_data.get_task_info(task_name)
        except ValueError:
            self._task_data.load_task(task_name)
            task = self._task_data.get_task_info(task_name)

        for operation in task["operations"]:
            if operation["type"] == "move line":
                try:
                    position = self.get_position(task_name, operation["position"])
                    print(position)
                    self.move_robot_line(position["cartesian"], [operation["linear_velocity"]])
                except ValueError:
                    raise
                except OSError:
                    raise
            elif operation["type"] == "hand-guide":
                try:
                    self.hand_guide()
                except OSError:
                    raise
            elif operation["type"] == "open":
                try:
                    self.open_gripper()
                except OSError:
                    raise
            elif operation["type"] == "close":
                try:
                    self.close_gripper()
                except OSError:
                    raise

            time.sleep(operation["delay"])

            if operation["wait"]:
                ready = CTkOkCancel("Continue task", "Ready to continue?", "Continue", "Stop").get_input()
                if not ready:
                    ready_to_continue = False
                    return ready_to_continue
        return True

    def is_task_up_to_date(self, task_name: str) -> bool:
        """Check if task is up to date. Raise error if unsuccessful on getting response"""
        encoded_task = self._encode_str(task_name)
        try:
            return self._task_data.is_task_up_to_date(encoded_task)
        except ValueError:
            raise

    def exists_task_file(self, task_name: str) -> tuple:
        """Check if a task file already exists with the given name"""
        return self._task_data.file_manager.file_exists(self._encode_str(task_name))

    def exists_program_file(self, program_name: str) -> bool:
        """Check if a program file already exists with the given name"""
        return self._program_data.file_manager.file_exists(self._encode_str(program_name))

    def add_program(self, program_name: str) -> str:
        """Start new program. Raises error if unsuccessful"""
        program_name = self._validate_str(program_name)
        if program_name == "":
            raise ValueError(f"Name {program_name} is not valid! Make sure it has characters that are not space and "
                             f"underscore")
        encoded_program = self._encode_str(program_name)
        try:
            self._program_data.add_program(encoded_program)
        except ValueError:
            raise
        return program_name

    def load_program(self, program_name: str) -> str:
        """Load program from file. Raises error if unsuccessful"""
        program_name = self._validate_str(program_name)
        encoded_program = self._encode_str(program_name)
        try:
            self._program_data.load_program(encoded_program)
        except ValueError:
            raise
        except FileNotFoundError:
            raise
        return program_name

    def close_program(self):
        """Close program."""
        try:
            self._program_data.close_program()
        except ValueError:
            raise

    def get_tasks_and_states_from_program(self) -> tuple[list[str], list[int]]:
        """Get tasks from program. Returns list of task names, list of 0, 1 and 2 representing:
                                                           0 -> task found and up to date
                                                           1 -> task found but changes not saved
                                                           2 -> task not found
        """
        tasks = self._program_data.get_tasks()
        status = []
        for task in tasks:
            state = self._get_task_state_from_input(task)
            status.append(state)
        return self._decode_str_list(tasks), status

    def _get_task_state_from_input(self, encoded_task_name: str) -> int:
        """Get task name and state: 0 -> exists and saved
                                    1 -> exists and not up to date
                                    2 -> doesn't exist"""
        if self._task_data.task_exists(encoded_task_name):
            state = 0 if self.is_task_up_to_date(encoded_task_name) else 1
        else:
            state = 0 if self.exists_task_file(encoded_task_name) else 2
        return state

    def is_program_open(self) -> bool:
        """Check if a program is open"""
        return self._program_data.is_open()

    def add_task_to_program(self, task_name: str) -> tuple[str, int]:
        """Add a task to the open program"""
        task_name = self._validate_str(task_name)
        if task_name == "":
            raise ValueError(f"Name {task_name} is not valid! Make sure it has characters that are not space and "
                             f"underscore")

        encoded_name = self._encode_str(task_name)
        try:
            self._program_data.add_task(encoded_name)
        except ValueError:
            raise

        return task_name, self._get_task_state_from_input(encoded_name)

    def save_program(self):
        """Save program to file"""
        try:
            self._program_data.save_program()
        except ValueError:
            raise

    def swap_tasks_in_program(self, index_1: int, index_2: int):
        """Swap order of tasks in program"""
        try:
            self._program_data.swap_tasks(index_1, index_2)
        except ValueError:
            raise

    def delete_task_from_program(self, index: int):
        """Delete task in program by index"""
        try:
            self._program_data.delete_task(index)
        except ValueError:
            raise

    def is_program_up_to_date(self):
        """Returns weather program file is up to date"""
        try:
            return self._program_data.is_up_to_date()
        except ValueError:
            raise

    def is_up_to_date(self) -> bool:
        """Check if any task or program isn't saved"""
        if self.is_program_open():
            if not self.is_program_up_to_date():
                return False

        for task in self.get_tasks():
            if not self.is_task_up_to_date(task):
                return False

        return True

    def move_robot(self, position: list, velocity: list):
        try:
            self._robot.move_robot(position, velocity)
        except ValueError:
            raise
        except OSError:
            raise

    def move_robot_line(self, position: list, velocity: list):
        try:
            self._robot.move_robot_line(position, velocity)
        except ValueError:
            raise
        except OSError:
            raise

    def open_gripper(self):
        try:
            self._robot.open_gripper()
        except OSError:
            raise

    def close_gripper(self):
        try:
            self._robot.close_gripper()
        except OSError:
            raise

    def hand_guide(self, weight_of_tool, centre_of_mass):
        try:
            self._robot.hand_guide(weight_of_tool, centre_of_mass)
        except OSError:
            raise
        except ValueError:
            raise




