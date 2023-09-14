import functools

from file_manager import FileManager


def check_open_program(func):
    @functools.wraps(func)
    def wrapper(self, *arg, **kw):
        if not self.is_open():
            raise ValueError("There is no open program")
        return func(self, *arg, **kw)
    return wrapper


class ProgramData:
    """Class that implements data management related to programs"""
    def __init__(self, path: str):
        self.file_manager = FileManager(path)
        self.program = None
        self.program_name = None
        self.program_saved = None

    def _validate_program(self, program):
        if isinstance(program, list):
            for element in program:
                if not isinstance(element, str):
                    raise ValueError("Task must be a string")
        else:
            raise ValueError("Program must be a list")

    def is_open(self) -> bool:
        """Return if a program is currently open"""
        return self.program is not None and self.program_name is not None and self.program_saved is not None

    def add_program(self, encoded_program: str):
        """Creates new program"""
        self.program_name = encoded_program
        self.program = []
        self.program_saved = False

    def load_program(self, encoded_program: str):
        """Loads program from file. Raises error if unsuccessful"""
        if self.file_manager.file_exists(encoded_program):
            program = self.file_manager.load_file(encoded_program)
            try:
                self._validate_program(program)
            except ValueError:
                raise
            self.program = self.file_manager.load_file(encoded_program)
            self.program_name = encoded_program
            self.program_saved = True
        else:
            raise FileNotFoundError(f"There is no file {encoded_program}.json")

    @check_open_program
    def close_program(self):
        """Closes currently open program"""
        self.program = None
        self.program_name = None
        self.program_saved = None

    @check_open_program
    def get_tasks(self) -> list:
        """Get tasks from program"""
        return self.program

    @check_open_program
    def add_task(self, encoded_task_name: str):
        """Add task to program"""
        self.program.append(encoded_task_name)
        self.program_saved = False

    @check_open_program
    def delete_task(self, index: int):
        """Delete task from program"""
        if 0 <= index < len(self.program):
            self.program.pop(index)
            self.program_saved = False
        else:
            raise ValueError(f"There is no task with index {index} in program {self.program_name}")

    @check_open_program
    def swap_tasks(self, index_1: int, index_2: int):
        """Swap order of 2 tasks in program"""
        if 0 <= index_1 < len(self.program) and 0 <= index_2 < len(self.program):
            temp = self.program[index_1]
            self.program[index_1] = self.program[index_2]
            self.program[index_2] = temp
            self.program_saved = False
        elif index_1 < 0 or index_1 >= len(self.program):
            raise ValueError(f"There is no task with index {index_1} in program {self.program_name}")
        else:
            raise ValueError(f"There is no task with index {index_2} in program {self.program_name}")

    @check_open_program
    def save_program(self):
        """Save program to file"""
        self.file_manager.save_file(self.program_name, self.program)
        self.program_saved = True

    @check_open_program
    def is_up_to_date(self):
        """Returns weather program is up to date"""
        return self.program_saved
