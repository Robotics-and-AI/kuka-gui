import json
import time
import iiwaPy3.python_client.iiwaPy3


class RobotCommunication:
    def __init__(self, tool_file: str):
        self.connection = None
        self.tools = {}
        try:
            self.import_tools(tool_file)
        except OSError:
            raise
        except ValueError:
            raise

    def import_tools(self, tool_file):
        try:
            with open(tool_file) as file:
                self.tools = json.load(file)
        except OSError:
            self.tools = {
                "none": {
                    "weight_of_tool": 0.0,
                    "centre_of_mass": [0, 0, 0]
                }
            }
            return

        for tool in self.tools:
            if "weight_of_tool" not in self.tools[tool]:
                raise ValueError(f"There is no weight_of_tool in tool {tool}")
            try:
                float(self.tools[tool]["weight_of_tool"])
            except TypeError:
                raise TypeError(f"Weight of tool for tool {tool} must be numeric")
            if self.tools[tool]["weight_of_tool"] < 0:
                raise ValueError(f"Weight of tool for tool {tool} must be positive")
            if "centre_of_mass" not in self.tools[tool]:
                raise ValueError(f"There is no centre_of_mass in tool {tool}")
            if not isinstance(self.tools[tool]["centre_of_mass"], list) or len(self.tools[tool]["centre_of_mass"]) != 3:
                raise ValueError(f"Centre of mass for tool {tool} must be a size 3 vector [x, y, z]")
            try:
                for num in self.tools[tool]["centre_of_mass"]:
                    float(num)
            except TypeError:
                raise TypeError(f"Centre of mass values for tool {tool} must be numeric")

    def start_connection(self, ip: str) -> str:
        try:
            ip = self._validate_ip(ip)
        except ValueError:
            raise

        try:
            self.connection = iiwaPy3.python_client.iiwaPy3.iiwaPy3(ip)

            # Check if connection is up
            self.connection.getJointsPos()
        except OSError:
            self.connection = None
            raise OSError("Connection failed")

        return ip

    def stop_connection(self):
        """Function to close communication with Kuka robot"""
        try:
            self.connection.close()
        except OSError as e:
            raise OSError(e)
        finally:
            self.connection = None

    def send_command(self, command):
        pass

    def is_connected(self) -> bool:
        return self.connection is not None

    def get_position(self) -> tuple:
        if self.is_connected():
            cartesian = self.connection.getEEFPos()
            joints = self.connection.getJointsPos()
        else:
            raise OSError("There is no connection")

        return cartesian, joints

    def _validate_ip(self, ip: str) -> str:
        ip = ip.split(".")
        if len(ip) != 4:
            raise ValueError("Ip must have 4 integer numbers separated by dots")

        for i in range(4):
            ip[i] = ip[i].strip()
            try:
                value = int(ip[i])
            except ValueError:
                raise ValueError("Make sure all 4 elements of the ip address are integers")
            if value < 0 or value > 255:
                raise ValueError("Ip values must be in the range [0, 255]")
        return ".".join(ip)

    def move_robot(self, position: list, velocity: list):
        if len(position) != 3:
            raise ValueError("Position must be a vector with size 3 [X, Y, Z]")

        if len(velocity) != 1:
            raise ValueError("Velocity must be a vector with size 1")

        if velocity[0] < 0.1:
            raise ValueError("Velocity must be at least 0.1")

        if self.is_connected():
            self.connection.movePTPLineEefRelBase(position, velocity)

    def move_robot_line(self, position: list, velocity: list):
        if len(position) != 6:
            raise ValueError("Position must be a vector with size 6 [X, Y, Z, A, B, C]")

        if len(velocity) != 1:
            raise ValueError("Velocity must be a vector with size 1")

        if velocity[0] < 0.1:
            raise ValueError("Velocity must be at least 0.1")

        if self.is_connected():
            self.connection.movePTPLineEEF(position, velocity)

    def hand_guide(self, weight_of_tool, centre_of_mass):
        if weight_of_tool < 0:
            raise ValueError("Weight of tool must be positive and in Newtons")
        if len(centre_of_mass) != 3:
            raise ValueError("Centre of mass must be a vector with size 3 [x, y, z] in mm")
        if centre_of_mass[2] < 0:
            raise ValueError("Coordinate z of centre of mass must be positive")

        try:
            self.connection.preciseHandGuiding(weight_tool=weight_of_tool, centre_mass=centre_of_mass)
        except OSError:
            raise

    def open_gripper(self):
        self.connection.setPin1Off()
        time.sleep(0.1)
        self.connection.setPin11On()
        time.sleep(0.5)

    def close_gripper(self):
        self.connection.setPin11Off()
        time.sleep(0.1)
        self.connection.setPin1On()
        time.sleep(0.5)

    def get_tool_names(self) -> list:
        return list(self.tools.keys())

    def get_tool_info(self, tool: str) -> dict:
        if tool in self.tools:
            return self.tools[tool]
        raise ValueError(f"There is no tool {tool}")
