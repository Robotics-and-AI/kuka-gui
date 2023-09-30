import json
import time

import iiwaPy3.python_client.iiwaPy3


class RobotCommunication:
    """
    Class to manage communication with a Kuka iiwa robot.
    """

    def __init__(self, tool_file: str):
        self.connection = None
        self.tools = {}
        try:
            self.import_tools(tool_file)
        except OSError:
            raise
        except ValueError:
            raise

    def import_tools(self, tool_file: str) -> None:
        """
        Import tool data from file.

        :param tool_file: file to load data from
        """
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

        # check for each tool
        for tool in self.tools:

            # check if tool has weight of tool information
            if "weight_of_tool" not in self.tools[tool]:
                raise ValueError(f"There is no weight_of_tool in tool {tool}")
            try:
                # check if weight of tool is a numeric value
                float(self.tools[tool]["weight_of_tool"])
            except TypeError:
                raise TypeError(f"Weight of tool for tool {tool} must be numeric")

            # check if weight of tool is non negative
            if self.tools[tool]["weight_of_tool"] < 0:
                raise ValueError(f"Weight of tool for tool {tool} must be positive")

            # check if tool as centre of mass information
            if "centre_of_mass" not in self.tools[tool]:
                raise ValueError(f"There is no centre_of_mass in tool {tool}")

            # check if centre of mass is a size 3 vector
            if not isinstance(self.tools[tool]["centre_of_mass"], list) or len(self.tools[tool]["centre_of_mass"]) != 3:
                raise ValueError(f"Centre of mass for tool {tool} must be a size 3 vector [x, y, z]")

            # check if values of centre of mass are numeric
            try:
                for num in self.tools[tool]["centre_of_mass"]:
                    float(num)
            except TypeError:
                raise TypeError(f"Centre of mass values for tool {tool} must be numeric")

    def start_connection(self, ip: str) -> str:
        """
        Initiate connection with kuka robot.

        :param ip: ip of robot to connect to
        :return: return validated ip
        """
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

    def stop_connection(self) -> None:
        """
        Stop communication to Kuka robot.
        """
        try:
            self.connection.close()
        except OSError as e:
            raise OSError(e)
        finally:
            self.connection = None

    def is_connected(self) -> bool:
        """
        Check if a communication is open.

        :return: True if there is an open communication with a Kuka robot
        """
        return self.connection is not None

    def get_position(self) -> tuple:
        """
        Get current robot position.

        :return: cartesian coordinates and joint positions
        """
        if self.is_connected():
            cartesian = self.connection.getEEFPos()
            joints = self.connection.getJointsPos()
        else:
            raise OSError("There is no connection")

        return cartesian, joints

    def _validate_ip(self, ip: str) -> str:
        """
        Validate given ip.

        :param ip: ip to validate
        :return: validated ip
        """

        # check if ip has 4 numeric sections separated by dots
        ip = ip.split(".")
        if len(ip) != 4:
            raise ValueError("Ip must have 4 integer numbers separated by dots")

        # check if numeric sections are integers
        for i in range(4):
            ip[i] = ip[i].strip()
            try:
                value = int(ip[i])
            except ValueError:
                raise ValueError("Make sure all 4 elements of the ip address are integers")
            if value < 0 or value > 255:
                raise ValueError("Ip values must be in the range [0, 255]")
        return ".".join(ip)

    def move_robot(self, position: list, velocity: float) -> None:
        """
        Move robot's EEF the given amount relative to the base at the given speed.

        :param position: EEF position shift relative to base [x, y, z]
        :param velocity: velocity in [mm/s]
        """

        # check position is a size 3 vector
        if len(position) != 3:
            raise ValueError("Position must be a vector with size 3 [X, Y, Z]")

        # check if position contains only numeric values
        for element in position:
            if not isinstance(element, float) and not isinstance(element, int):
                raise ValueError("Position must be a vector of numeric values")

        # check positive velocity
        if velocity < 0.1:
            raise ValueError("Velocity must be at least 0.1")

        # send move command
        if self.is_connected():
            self.connection.movePTPLineEefRelBase(position, [velocity])

    def move_robot_line(self, position: list, velocity: float) -> None:
        """
        Move robot to the given position at the gicen speed.

        :param position: final position of the robot [x, y, z, a, b, c]
        :param velocity: velocity in [mm/s]
        """

        # check position is a size 6 vector
        if len(position) != 6:
            raise ValueError("Position must be a vector with size 6 [X, Y, Z, A, B, C]")

        # check if position contains only numeric values
        for element in position:
            if not isinstance(element, float) and not isinstance(element, int):
                raise ValueError("Position must be a vector of numeric values")

        # check if velocity is positive
        if velocity < 0.1:
            raise ValueError("Velocity must be at least 0.1")

        # send command to move robot
        if self.is_connected():
            self.connection.movePTPLineEEF(position, velocity)

    def hand_guide(self, weight_of_tool: float, centre_of_mass: list) -> None:
        """
        Start hand-guiding mode.

        :param weight_of_tool: weight of the tool in Newtons
        :param centre_of_mass: centre of mass of the tool [x, y, z] in [mm]
        """

        # check non negative weight of tool
        if weight_of_tool < 0:
            raise ValueError("Weight of tool must be positive and in Newtons")

        # check centre of mass is size 3
        if len(centre_of_mass) != 3:
            raise ValueError("Centre of mass must be a vector with size 3 [x, y, z] in mm")

        # check centre of mass comprised of only numeric elements
        for element in centre_of_mass:
            if not isinstance(element, float) and not isinstance(element, int):
                raise ValueError("Centre of mass must be a vector of numeric elements")

        # check if z coordinate of centre of mass is non negative
        if centre_of_mass[2] < 0:
            raise ValueError("Coordinate z of centre of mass must be positive")

        # send command to start hand-guiding
        try:
            self.connection.preciseHandGuiding(weight_tool=weight_of_tool, centre_mass=centre_of_mass)
        except OSError:
            raise

    def open_gripper(self) -> None:
        """
        Open gripper (Pin 11).
        """
        self.connection.setPin1Off()
        time.sleep(0.1)
        self.connection.setPin11On()
        time.sleep(0.5)

    def close_gripper(self) -> None:
        """
        Close gripper (Pin1).
        """
        self.connection.setPin11Off()
        time.sleep(0.1)
        self.connection.setPin1On()
        time.sleep(0.5)

    def get_tool_names(self) -> list:
        """
        Get names of existing tools.

        :return: names of tools
        """
        return list(self.tools.keys())

    def get_tool_info(self, tool: str) -> dict:
        """
        Get weight and centre of mass of given tool.

        :param tool: name of the tool
        :return: weight and centre of mass
        """
        if tool in self.tools:
            return self.tools[tool]
        raise ValueError(f"There is no tool {tool}")
