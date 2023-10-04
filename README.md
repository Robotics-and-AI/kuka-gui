# Kuka iiwa GUI

## Install
### Kuka Sunrise Server
The gui requires the usage of the [Kuka Sunrise Server](https://github.com/Modi1987/KST-Kuka-Sunrise-Toolbox/tree/master/KUKA_Sunrise_server_source_code) to control and connect with the Kuka iiwa robot.
Make sure you follow the instructions and install the correct flange version.

### iiwaPy3
The interface connects with the robot through the [iiwaPy3 library](https://github.com/Modi1987/iiwaPy3), which is already integrated in the code.

### Code
To get a fully operational interface follow the following steps:
1. Download the source code.
2. Install [anaconda](https://www.anaconda.com/).
3. Open anaconda navigator:
   - Select environments.
   - Press import button.
   - Import from local drive the file kuka-gui-env.yml.
   <img src="/images/anaconda_navigator.png" width="800" alt="Anaconda Navigator"/>

4. Open anaconda prompt.
5. Go to the project folder:
```cd "path/to/folder"```

7. Run gui.py in anaconda prompt:
```python gui.py```

### Robot tools
To be able to properly use the hand-guiding mode, the tools attached to the robot should be added in the **tools.json** file before starting the app.

Tools must have information regarding their weight [N] and centre of mass [mm] like the following examples:
```
{
  "Schunk gripper": {
    "weight_of_tool": 17.89,
    "centre_of_mass": [0, 0, 105]
  },
  "OnRobot screw": {
    "weight_of_tool": 28.06,
    "centre_of_mass": [0, 3.5, 60.6]
  }
}
```

The first tool in the list will be used in the app as the default tool.

## Interface
The designed interface allows a quick and less demanding programming interaction with Kuka iiwa robots.

The interface is subdivided into 8 sections (A - H) as can be observed in the following image:

<img src="/images/light_interface_sections.png" width="1000" alt="Light mode sections"/>

### A: Interface settings

The sidebar allows some setting changes for the appearance mode (light mode or dark mode) and scaling.
<p float="left">
  <img src="/images/light_interface.png" width="400" alt="Light mode"/>
  <img src="/images/dark_interface.png" width="400" alt="Dark mode"/> 
</p>

### B: Robot connection

To connect the robot with the interface:
1. Enter the robot's ip.
2. Start MatlabToolboxServer on the robot side.
3. Press the connect button.

### C: Move robot

For any robotic movement please connect to the robot first.

#### Hand-guide 
Enter precise hand-guiding mode, allowing a precise movement in any axis and rotation in respect to the robot's EEF.

#### Open/Close
Activate pins to open and close gripper. Tested on a SCHUNK Co-act EGP-C 64 gripper. If using a different gripper verify if the required pins are the same, if not make the necessary adjustments.

#### Axis movement
Move the robot in the positive (+) or negative (-) selected axis direction. The distance and speed of the movement can be specified in the entries below.

### D: Managing tasks

In this section tasks can be created, loaded, saved and deleted. 

A task contains multiple operations, i.e. (line movements, open gripper, close gripper and hand-guide) and robot positions.

If the task is up to date it will have a green outline, otherwise it will have an orange outline, remembering the user to save the task.

### E: Managing task operations

In this section, task operations can be added, saved and deleted.
If the save button is orange the operation has changes which weren't saved.

#### There are 4 types of operations:
| Operation  | Description                                    |
| ---------- | ---------------------------------------------- |
| Move Line  | Move robot to the specified position in a line |
| Open       | Open the gripper                               |
| Close      | Close the gripper                              |
| Hand-guide | Enter hand-guiding mode                        |

#### For each operation there are some additional settings which can be changed:
| Setting         | Description                                                                 | Valid for      |
| --------------- | --------------------------------------------------------------------------- | -------------- |
| Wait for input  | Whether the user must provide an input to continue the task                 | All operations |
| Delay           | Amount of time in seconds to wait before executing the next operation       | All operations |
| Position        | Position to move to when executing the move line operation                  | Move line      |
| Linear velocity | Velocity at which the robot moves when executing the move line operation    | Move line      |
| Tool            | Tool currently attached in the gripper                                      | Hand-guide     |

### F: Managing robot positions

In this section, robot positions can be added, updated and saved to the associated task.

Additionally, if a position is selected, the user may ask the robot to move to the selected position through the **go to** button.

### G: Managing programs

In this section, programs can be created to design a sequence of tasks.

Next to each task, the task's state is colour coded in green, orange or red. If the task is green, it exists and is up to date. If the task is orange, it exists but some changes have not been saved (when running such a task, the changes will be used). If the task is red, it does not exist and the program will not run.

### H: Error message display

In this section, error messages are displayed to relay important information to the user.
