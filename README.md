# Kuka iiwa GUI

## Install
### Kuka Sunrise Server
The gui requires the usage of the [Kuka Sunrise Server](https://github.com/Modi1987/KST-Kuka-Sunrise-Toolbox/tree/master/KUKA_Sunrise_server_source_code) to control and connect with the Kuka iiwa robot.
Make sure you follow the instructions and install the correct flange version.

### iiwaPy3
The interface connects with the robot through the [iiwaPy3 library](https://github.com/Modi1987/iiwaPy3), which is already integrated in the code.

### Code
To get a fully operational interface follow the following steps:
1. Install [anaconda](https://www.anaconda.com/)
2. Create a new python environment through the anaconda prompt:
   ```conda env create -f environment.yml```
   
4. Install visual studio code
5. Download the source code of this project and open it in Visual Studio Code
6. Add anaconda env as the interpreter
<img src="/images/interpreter_tutorial.png" width="100" alt="Visual Studio Code interpreter"/>
8. Run gui.py

## Interface
The designed interface allows a quick and less demanding programming interaction with Kuka iiwa robots.

The interface is subdivided into 8 sections (A - H) as can be observed in the following image:

<img src="/images/light_interface_sections.png" width="100" alt="Light mode sections"/>

### A: Interface settings

The sidebar allows some setting changes for the appearance mode (light mode or dark mode) and for the scaling.
<p float="left">
  <img src="/images/light_interface.png" width="100" alt="Light mode"/>
  <img src="/images/dark_interface.png" width="100" alt="Dark mode"/> 
</p>

### B: Robot connection

To connect the robot with the interface:
1. Enter the robot's ip
2. Start MatlabToolboxServer on the robot side
3. Press the connect button

### C: Move robot

For any robotic movement please connect to the robot first.

**Hand-guide**: by pressing the hand-guide button the robot enters in precise hand-guiding mode, which allows a precise movement in any axis and rotation in respect with the robot's EEF.

**Open/Close**: by pressing the Open or Close buttons the robot activates the pins to open and close a SCHUNK Co-act EGP-C 64 gripper. If using a different gripper verify if the pins required are the same, if not make the necessary adjustments in the code.

**Move positive / Move negative**: by pressing the button X+ or X- the robot moves in the positive and negative world X axis directions respectively. The buttons work similarly for the Y and Z axis. The amount and speed of the movement can be specified in the entries below.

### D: Managing tasks

In this section tasks can be created, loaded, saved and deleted. 

A task contains multiple operations, i.e. (line movements, open gripper, close gripper and hand-guide) and robot positions.

If the task is up to date it will have a green outline, otherwise it will have an orange outline, remembering the user to save the task.

### E: Managing task operations

In this section, task operations can be added, saved and deleted.
If the save button is orange the operation has had some changes which weren't saved.

There are 4 types of operations:
- **Move line**: Moves the robot to the specified position in a line.
- **Open**: Opens the gripper.
- **Close**: Closes the gripper.
- **Hand-guide**: Enters hand-guiding mode.

For each operation there are some additional settings which can be changed:
- **Wait for input**: whether the user must provide an input to continue the task (valid for all operations).
- **Delay**: amount of time in seconds to wait before executing the next operation (valid for all operations).
- **Position**: position to move to when executing a move line operation (only valid for move line).
- **Linear velocity**: velocity at which the robot should move when executing the move line operation (only valid for move line).
- **Attatched tool**: tool currently attatched in the gripper (only valid for the hand-guide mode).

### F: Managing robot positions

In this section, task's robot positions can be added, updated and saved.

Additionally, if a position is open, the user may ask the robot to move to the selected position trough the **go to** button.

### G: Managing programs

In this section, programs can be created to design a sequence of tasks.

Next to each task, the task's state is colour coded in green, orange and red. If the task is green it exists and is up to date. If the task is orange it exists but some changes have not been saved (when running such a task, the changes will be used). If the task is red it does not exist and the program will not run.

### H: Error message display

In this section error messages are displayed to the user to inform any important information.
