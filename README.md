# Kuka iiwa GUI

## Install
### Kuka Sunrise Server
The gui requires the usage of the [Kuka Sunrise Server](https://github.com/Modi1987/KST-Kuka-Sunrise-Toolbox/tree/master/KUKA_Sunrise_server_source_code) to control and connect with the Kuka iiwa robot.
Make sure you follow the instructions and install the correct server version.

### iiwaPy3
The interface connects with the robot through the [iiwaPy3 library](https://github.com/Modi1987/iiwaPy3), which is already integrated in the code.

### Code
To get a fully operational interface follow the following steps:
1. Install [anaconda](https://www.anaconda.com/).
2. Create a new python environment through anaconda prompt:

   ```conda env create -f environment.yml```
4. Install visual studio code
5. Download project and open it in Visual Studio Code
6. Add anaconda env as the interpreter
7. Run gui.py

## Interface

The designed interface allows a quick a less demanding programming interaction with Kuka iiwa robots.

### A: Interface settings

The sidebar allows some setting changes for the appearance mode (light mode or dark mode) and for the scaling.
<p float="left">
  <img src="/images/Interface.png" width="100" alt="Light mode"/>
  <img src="/images/Dark_Interface.png" width="100" alt="Dark mode"/> 
</p>

### B: Robot connection

To connect the robot with the interface:
1. Enter the robot's ip in the entry
2. Start MatlabToolboxServer on the robot side
3. Press the connect button

### C: Move robot

For any robotic movement please connect the robot first.

**Hand-guide**
: by pressing the hand-guide button the robot enters in precise hand-guiding mode, which allows a precise movement in any axis and rotation in respect with the robot's EEF.

**Open/Close**: by pressing the Open or Close buttons the robot activates the pins to open and close the Schunk gripper. If using a different gripper verify if the pins required are the same, if not make the necessary adjustments in the code.

**Move positive / Move negative**: by pressing the button X+ or X- the robot moves in the positive and negative world X axis directions respectively. The buttons work similarly for the Y and Z axis. The amount and speed of the movement can be specified in the entries below.

### D: Managing tasks

In this section tasks can be created, loaded, saved and deleted. 

A task contains multiple operations, i.e. (line movements, open gripper, close gripper and hand-guide) and robot positions.

If the task is up to date it will have a green outline, otherwise it will have an orange outline, remembering the user to save the task.

### E: Managing task operations

In this section, operations can be added to tasks.
If the save button is orange the operation has had some changes which weren't saved.

There are 4 types of operations:
- **Move line**: Moves the robot to the specified position in a line
- **Open**: Opens the gripper
- **Close**: Closes the gripper
- **Hand-guide**: Enters hand-guiding mode

For each operation there are some additional settings which can be changed:
- **Wait for input**: whether the user must provide an input to continue the task (valid for all operations)
- **Delay**: amount of time in seconds to wait before executing the next operation (valid for all operations)
- **Position**: position to move to when executing a move line operation (only valid for move line)
- **Linear velocity**: velocity at which the robot should move when executing the move line operation (only valid for move line)

### F: Managing robot positions

### G: Managing programs
