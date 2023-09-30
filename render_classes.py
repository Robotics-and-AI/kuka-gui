import customtkinter

from ctkinter_elements import CTkBoxList, CTkMessageDisplay, CTkFloatSpinbox, CTkOkCancel
from robotic_system import RoboticSystem

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

SMALL_HALF_Y_PAD = (5, 0)
SMALL_Y_PAD = 5
MEDIUM_HALF_Y_PAD = (10, 0)
MEDIUM_Y_PAD = 10
BIG_HALF_Y_PAD = (20, 0)
BIG_Y_PAD = 20

SMALL_HALF_X_PAD = (10, 0)
SMALL_X_PAD = (10, 10)
MEDIUM_HALF_X_PAD = (20, 0)
MEDIUM_X_PAD = (20, 20)
BIG_HALF_X_PAD = (30, 0)
BIG_X_PAD = (30, 30)

ORANGE_COLORS = '#DB8B1A'
RED_COLORS = ('#dc3545', '#a82835')
BLUE_COLORS = ('#3B8ED0', '#1F6AA5')
GREEN_COLORS = '#198754'

BLUE_HOVER = ('#36719F', '#144870')
ORANGE_HOVER = "#b87818"
RED_HOVER = "#85202A"


# Class inherited from CTkBoxList to communicate with program_data class
class CTkProgramBoxList(CTkBoxList):
    def __init__(self, master, robotic_system: RoboticSystem, **kwargs):
        super().__init__(master, **kwargs)
        self.robotic_system = robotic_system

    def delete_element(self, index: int) -> None:
        """
        Delete element by index.

        :param index: Index of element to delete
        """
        try:
            self.robotic_system.delete_task_from_program(index)
        except ValueError:
            raise
        super().delete_element(index)

    def _up_event(self, index: int) -> None:
        """
        Swap element with given index with the previous element.

        :param index: index of element
        """
        if index > 0:
            try:
                self.robotic_system.swap_tasks_in_program(index, index - 1)
            except ValueError:
                raise
            super()._up_event(index)

    def _down_event(self, index: int) -> None:
        """
        Swap element with given index with the next element.

        :param index: index of element
        """
        if index < len(self.elements) - 1:
            try:
                self.robotic_system.swap_tasks_in_program(index, index + 1)
            except ValueError:
                raise
            super()._down_event(index)


# Element manage the robot connection
class CTkRobotConnector(customtkinter.CTkFrame):
    def __init__(self, master, robotic_system: RoboticSystem, message_display: CTkMessageDisplay):
        super().__init__(master)
        # configure grid layout
        self.grid_columnconfigure((0, 3), weight=1)

        self.message_display = message_display
        self.robotic_system = robotic_system

        # entry to input robot's ip and respective label
        self.ip_entry_label = customtkinter.CTkLabel(self, text="Robot's ip:")
        self.ip_entry_label.grid(row=0, column=1, padx=SMALL_HALF_X_PAD, pady=SMALL_Y_PAD)
        self.ip_entry = customtkinter.CTkEntry(self, width=140)
        self.ip_entry.insert(0, "172.31.1.147")
        self.ip_entry.grid(row=0, column=2, padx=SMALL_X_PAD, pady=SMALL_Y_PAD, sticky="nsew")

        # button to connect to robot and lamp to inform if robot is connected
        self.connect = customtkinter.CTkButton(self, text="Connect", width=140, height=28, command=self._connect_event)
        self.connect.grid(row=1, column=2, padx=SMALL_X_PAD, pady=SMALL_Y_PAD, sticky="nsew")
        self.connect_lamp = customtkinter.CTkLabel(self, text="", width=26, height=26, corner_radius=13,
                                                   fg_color="transparent")
        self.connect_lamp.grid(row=1, column=1, padx=SMALL_X_PAD, pady=SMALL_Y_PAD)

    def _connect_event(self) -> None:
        """
        Attempt to connect with the robot, if successful lamp turns on.
        If robot already connected it disconnects.
        """
        if self.robotic_system.is_robot_connected():
            self.robotic_system.stop_robot_connection()
            self.connect.configure(text="Connect")
            self.connect_lamp.configure(fg_color="transparent")
        else:
            try:
                ip = self.robotic_system.start_robot_connection(self.ip_entry.get())
            except ValueError as e:
                self.message_display.display_message(e)
                return
            except OSError as e:
                self.message_display.display_message(e)
                return

            self.ip_entry.delete(0, customtkinter.END)
            self.ip_entry.insert(0, ip)
            self.connect.configure(text="Disconnect")
            self.connect_lamp.configure(fg_color=GREEN_COLORS)


# Sidebar element
class CTkSidebar(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # App name
        self.logo_label = customtkinter.CTkLabel(self, text="Kuka iiwa GUI",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))

        # configure grid layout
        self.grid_rowconfigure(1, weight=1)
        self.logo_label.grid(row=0, column=0, padx=MEDIUM_X_PAD, pady=(20, 10))

        # option menu to select appearance mode and respective label
        self.appearance_mode_label = customtkinter.CTkLabel(self, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=2, column=0, padx=MEDIUM_X_PAD, pady=(10, 0))
        self.appearance_mode_option_menu = customtkinter.CTkOptionMenu(self,
                                                                       values=["Light", "Dark", "System"],
                                                                       command=self._change_appearance_mode_event)
        self.appearance_mode_option_menu.grid(row=3, column=0, padx=MEDIUM_X_PAD, pady=(10, 10))

        # option menu to change scaling and respective label
        self.scaling_label = customtkinter.CTkLabel(self, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=4, column=0, padx=MEDIUM_X_PAD, pady=(10, 0))
        self.scaling_option_menu = customtkinter.CTkOptionMenu(self,
                                                               values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self._change_scaling_event)
        self.scaling_option_menu.grid(row=5, column=0, padx=MEDIUM_X_PAD, pady=(10, 20))

        # set default values
        self.appearance_mode_option_menu.set("System")
        self.scaling_option_menu.set("100%")

    def _change_scaling_event(self, new_scaling: str) -> None:
        """
        Change scaling of the app.

        :param new_scaling: new scaling value
        """
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def _change_appearance_mode_event(self, new_appearance_mode: str) -> None:
        """
        Change appearance mode between Light, Dark and System.

        :param new_appearance_mode: appearance mode to display
        """
        customtkinter.set_appearance_mode(new_appearance_mode)


# Element to command robot movements (cartesian movements, open/close gripper)
class CTkMoveRobot(customtkinter.CTkFrame):
    def __init__(self, master, robotic_system: RoboticSystem, message_display: CTkMessageDisplay):
        super().__init__(master)

        self.robotic_system = robotic_system
        self.message_display = message_display

        # configure grid layout
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.grid_columnconfigure((0, 2, 4), weight=1)

        # frame to encapsulate upper buttons
        self.top_frame = customtkinter.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, columnspan=5, padx=SMALL_X_PAD, pady=MEDIUM_HALF_Y_PAD, sticky="nsew")
        self.top_frame.grid_rowconfigure((0, 1), weight=1)
        self.top_frame.grid_columnconfigure((0, 1), weight=1)

        # button to open gripper
        self.open_gripper = customtkinter.CTkButton(self.top_frame, width=120, height=20, text="Open",
                                                    command=self._open_gripper_event)
        self.open_gripper.grid(row=1, column=0, padx=SMALL_X_PAD, pady=MEDIUM_Y_PAD, sticky="nsew")

        # button to close gripper
        self.close_gripper = customtkinter.CTkButton(self.top_frame, width=120, height=20, text="Close",
                                                     command=self._close_gripper_event)
        self.close_gripper.grid(row=1, column=1, padx=SMALL_X_PAD, pady=MEDIUM_Y_PAD, sticky="nsew")

        # button to start hand-guide
        self.hand_guide = customtkinter.CTkButton(self.top_frame, width=120, height=20, text="Hand-guide",
                                                  command=self._hand_guide_event)
        self.hand_guide.grid(row=0, column=1, padx=SMALL_X_PAD, pady=MEDIUM_HALF_Y_PAD, sticky="nsew")

        # option menu to select tool for the hand-guide mode
        self.robot_tool = customtkinter.CTkOptionMenu(self.top_frame, width=120, height=20,
                                                      values=self.robotic_system.get_tool_names(),
                                                      fg_color=("#979da2", "#4a4a4a"),
                                                      button_color=("#60676c", "#666666"),
                                                      button_hover_color=("#60676c", "#666666"),
                                                      dynamic_resizing=False)
        self.robot_tool.set(self.robotic_system.get_tool_names()[0])
        self.robot_tool.grid(row=0, column=0, padx=SMALL_X_PAD, pady=MEDIUM_HALF_Y_PAD, sticky="ew")

        # buttons to move in the X, Y and Z axis
        self.move_buttons = {}
        for i, letter in enumerate(["X", "Y", "Z"]):
            self.move_buttons[f"{letter}+"] = customtkinter.CTkButton(self, width=120, height=20, text=f"{letter}+",
                                                                      font=customtkinter.CTkFont(size=17),
                                                                      command=lambda axis=i:
                                                                      self._move_robot(axis, True))
            self.move_buttons[f"{letter}+"].grid(row=i + 1, column=1, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_HALF_Y_PAD,
                                                 sticky="nsew")
            self.move_buttons[f"{letter}-"] = customtkinter.CTkButton(self, width=120, height=20, text=f"{letter}-",
                                                                      font=customtkinter.CTkFont(size=17),
                                                                      command=lambda axis=i:
                                                                      self._move_robot(axis, False))
            self.move_buttons[f"{letter}-"].grid(row=i + 1, column=3, padx=MEDIUM_X_PAD, pady=MEDIUM_HALF_Y_PAD,
                                                 sticky="nsew")

        # entry to define the amount the robot moves in [mm] and respective label
        self.amount_label = customtkinter.CTkLabel(self, text="Amount [mm]:")
        self.amount_label.grid(row=4, column=1, padx=SMALL_HALF_X_PAD, pady=SMALL_HALF_Y_PAD)
        self.amount = CTkFloatSpinbox(self, width=120, max_value=200.0, min_value=1.0, step_size=10)
        self.amount.set(10.0)
        self.amount.grid(row=5, column=1, padx=SMALL_X_PAD, pady=SMALL_Y_PAD)
        self.amount.configure(fg_color=('gray86', 'gray17'))

        # entry to define the speed the robot moves at in [mm/s] and respective label
        self.velocity_label = customtkinter.CTkLabel(self, text="Velocity [mm/s]:")
        self.velocity_label.grid(row=4, column=3, padx=SMALL_HALF_X_PAD, pady=SMALL_HALF_Y_PAD)
        self.velocity = CTkFloatSpinbox(self, width=120, max_value=100.0, min_value=1.0, step_size=10)
        self.velocity.set(10.0)
        self.velocity.grid(row=5, column=3, padx=SMALL_X_PAD, pady=SMALL_Y_PAD)
        self.velocity.configure(fg_color=('gray86', 'gray17'))

    def _move_robot(self, axis: int, positive_direction: bool) -> None:
        """
        Move robot in the specified axis and orientation.

        :param axis: axis of movement (0 for X, 1 for Y and 2 for Z)
        :param positive_direction: bool indicating whether to move in the positive direction
        """

        # check if robot is connected
        if not self.robotic_system.is_robot_connected():
            self.message_display.display_message("Robot communication has not been established")
            return

        # create vector with amount to move relative to EEF in the specified actions and the correct orientation
        position = [0.0, 0.0, 0.0]
        position[axis] = self.amount.get() if positive_direction else -self.amount.get()
        velocity = self.velocity.get()

        # send command to move robot
        try:
            self.robotic_system.move_robot(position, velocity)
        except OSError as e:
            self.message_display.display_message(e)

    def _open_gripper_event(self) -> None:
        """
        Open gripper.
        """

        # check if robot is connected
        if not self.robotic_system.is_robot_connected():
            self.message_display.display_message("Robot communication has not been established")
            return

        # send command to open gripper
        try:
            self.robotic_system.open_gripper()
        except OSError as e:
            self.message_display.display_message(e)

    def _close_gripper_event(self) -> None:
        """
        Close gripper.
        """
        # check if robot is connected
        if not self.robotic_system.is_robot_connected():
            self.message_display.display_message("Robot communication has not been established")
            return

        # send command to close gripper
        try:
            self.robotic_system.close_gripper()
        except OSError as e:
            self.message_display.display_message(e)

    def _hand_guide_event(self) -> None:
        """
        Enter hand-guiding mode with the selected tool.
        """

        # check if robot is connected
        if not self.robotic_system.is_robot_connected():
            self.message_display.display_message("Robot communication has not been established")
            return

        # Fetch weight of tool and centre of mass of the selected tool
        try:
            tool = self.robotic_system.get_tool_info(self.robot_tool.get())
        except ValueError as e:
            self.message_display.display_message(e)
            return

        # send command to start hand-guiding mode with the specified tool data
        try:
            self.robotic_system.hand_guide(tool["weight_of_tool"], tool["centre_of_mass"])
        except OSError as e:
            self.message_display.display_message(e)
        except ValueError as e:
            self.message_display.display_message(e)


# Task management interface to create, load, save and delete tasks
class CTkTaskManager(customtkinter.CTkFrame):
    def __init__(self, master, robotic_system: RoboticSystem, message_display: CTkMessageDisplay):
        super().__init__(master)

        self.robotic_system = robotic_system
        self.message_display = message_display

        # configure grid layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # task related information and elements
        self.tasks_labels = {}
        self.task_state = {}
        self.task_frame = {}

        # button to create a new task
        self.create_task = customtkinter.CTkButton(self, width=80, height=40, text="New task",
                                                   command=self._new_task_event)
        self.create_task.grid(row=0, column=0, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD)

        # button to load a saved task
        self.load_task = customtkinter.CTkButton(self, width=80, height=40, text="Load task",
                                                 command=self._load_task_event)
        self.load_task.grid(row=0, column=1, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD)

        # button to save a task to its corresponding file
        self.save_task = customtkinter.CTkButton(self, width=80, height=40, text="Save task",
                                                 command=self._save_task_event)
        self.save_task.grid(row=0, column=2, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD)

        # button to delete a task, the file can also be deleted
        self.delete_task = customtkinter.CTkButton(self, width=80, height=40, text="Delete task",
                                                   command=self._delete_task_event)
        self.delete_task.grid(row=0, column=3, padx=MEDIUM_X_PAD, pady=MEDIUM_Y_PAD)

        # element to display tasks
        self.task_tabview = customtkinter.CTkTabview(self)
        self.task_tabview.configure(fg_color=("gray76", "gray23"), command=self.render)
        self.task_tabview.grid(row=1, column=0, columnspan=4, padx=MEDIUM_X_PAD, pady=MEDIUM_Y_PAD, sticky="nsew")

    def _new_task_event(self) -> None:
        """
        Create a new task.
        """

        # ask user a name for the task
        dialog = customtkinter.CTkInputDialog(text="Type in a name:", title="New task")
        task_name = dialog.get_input()

        # check if user canceled operation
        if task_name is not None:
            # check if a task with this name exists in a saved file. If it exists ask if file should be overridden
            if self.robotic_system.exists_task_file(task_name):
                ok_cancel = CTkOkCancel(text="A file with this name already exists. \n"
                                             "Do you wish to override it?",
                                        title="Override previous file", first_button="Yes", second_button="Cancel")

                # if user does not want to override file, cancel creation of task
                if not ok_cancel.get_input():
                    return

            # create new task
            try:
                task_name = self.robotic_system.add_task(task_name)
            except ValueError as e:
                self.message_display.display_message(e)
                return
            except FileNotFoundError as e:
                self.message_display.display_message(e)
                return

            # render new empty task
            self._render_task(task_name)

    def _load_task_event(self) -> None:
        """
        Load task from previously created file.
        """

        # ask name of the task to be loaded
        dialog = customtkinter.CTkInputDialog(text="Type task name:", title="Load task")
        task_name = dialog.get_input()
        if task_name is not None:
            # load requested task
            try:
                task_name = self.robotic_system.load_task(task_name)
            except ValueError as e:
                self.message_display.display_message(e)
                return
            except FileNotFoundError as e:
                self.message_display.display_message(e)
                return

            # render task and fetch data
            self._render_task(task_name)
            self._update_task_info(task_name)

    def _render_task(self, task_name: str) -> None:
        """
        Render task with given name.

        :param task_name: name of the task to render
        """
        try:
            # add tab for the task and configure grid layout
            self.task_tabview.add(task_name)
            self.task_tabview.tab(task_name).grid_columnconfigure(0, weight=1)
            self.task_tabview.tab(task_name).grid_rowconfigure((0, 3), weight=1)

            # create the task's frame
            self.task_frame[task_name] = customtkinter.CTkFrame(self.task_tabview.tab(task_name), border_width=2,
                                                                height=200, width=200,
                                                                border_color=ORANGE_COLORS,
                                                                fg_color="transparent")
            self.task_frame[task_name].grid(row=2, column=0, padx=MEDIUM_X_PAD, pady=MEDIUM_Y_PAD)

            # crete the task's state
            self.task_state[task_name] = customtkinter.CTkLabel(self.task_tabview.tab(task_name),
                                                                text="Save task to confirm changes")
            self.task_state[task_name].grid(row=1, column=0, padx=MEDIUM_X_PAD, pady=MEDIUM_HALF_Y_PAD)

            # configure grid layout of task_frame
            self.task_frame[task_name].grid_columnconfigure((0, 2, 4), weight=1)
            self.task_frame[task_name].grid_rowconfigure((0, 3), weight=1)

            # labels to display number of operations in the task
            operations_label = customtkinter.CTkLabel(self.task_frame[task_name], text="# of operations:",
                                                      font=customtkinter.CTkFont(size=13))
            operations_label.grid(row=1, column=1, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_HALF_Y_PAD)
            operations_value = customtkinter.CTkLabel(self.task_frame[task_name], text="0",
                                                      font=customtkinter.CTkFont(size=13))
            operations_value.grid(row=2, column=1, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD)

            # labels to display number of robot positions in the task
            positions_label = customtkinter.CTkLabel(self.task_frame[task_name], text="# of points:",
                                                     font=customtkinter.CTkFont(size=13))
            positions_label.grid(row=1, column=3, padx=MEDIUM_X_PAD, pady=MEDIUM_HALF_Y_PAD)
            positions_value = customtkinter.CTkLabel(self.task_frame[task_name], text="0",
                                                     font=customtkinter.CTkFont(size=13))
            positions_value.grid(row=2, column=3, padx=MEDIUM_X_PAD, pady=MEDIUM_Y_PAD)

            # save labels
            self.tasks_labels[task_name] = {
                "operations": operations_value,
                "positions": positions_value
            }

        except ValueError:
            self.message_display.display_message(f"There already exists a task {task_name}")

    def _save_task_event(self) -> None:
        """
        Save task to its corresponding file.
        """

        if self.task_tabview.get() != "":
            task_name = self.task_tabview.get()
            try:
                # save task
                self.robotic_system.save_task(task_name)
            except ValueError as e:
                self.message_display.display_message(e)

            # update status of the task
            self._update_task_status(task_name)

    def _delete_task_event(self) -> None:
        """
        Delete task and optionally delete corresponding file.
        """
        if self.task_tabview.get() != "":
            task_name = self.task_tabview.get()
            # confirm task deletion
            ok_cancel = CTkOkCancel(text="Do you want to delete the task?", title="Delete task", first_button="Yes")
            if ok_cancel.get_input():
                # ask if file should also be deleted
                ok_no = CTkOkCancel(text="Delete the file, if it exists?", title="Delete file",
                                    first_button="Yes", second_button="No")
                try:
                    # delete task (and file if requested)
                    self.robotic_system.delete_task(task_name, ok_no.get_input())
                except ValueError as e:
                    self.message_display.display_message(e)
                    return

                # delete the task's tab
                self.task_tabview.delete(task_name)

    def _update_task_info(self, task_name: str) -> None:
        """
        Update the task's displayed information.

        :param task_name: name of the task to update
        """

        try:
            # fetch task data
            retrieved_data = self.robotic_system.get_task_info(task_name)
            # update task status
            self._update_task_status(task_name)
        except ValueError as e:
            self.message_display.display_message(e)
            return

        # update displayed information
        if retrieved_data:
            self.tasks_labels[task_name]["operations"].configure(text=str(len(retrieved_data["operations"])))
            self.tasks_labels[task_name]["positions"].configure(text=str(len(retrieved_data["positions"])))

    def _update_tasks_event(self) -> None:
        """
        Update for all tasks the information displayed.
        """

        for task in self.tasks_labels:
            self._update_task_info(task)

    def _update_task_status(self, task_name: str) -> None:
        """
        Update the status of the task with the given name.

        :param task_name: name of the task
        """

        # check if task is up to date
        try:
            status = self.robotic_system.is_task_up_to_date(task_name)
        except ValueError as e:
            self.message_display.display_message(e)
            return

        # display the task status information
        if status:
            self.task_frame[task_name].configure(border_color=GREEN_COLORS)
            self.task_state[task_name].configure(text="Task up to date")
        else:
            self.task_frame[task_name].configure(border_color=ORANGE_COLORS)
            self.task_state[task_name].configure(text="Save task to confirm changes")

    def render(self) -> None:
        """
        Basic task rendering. Checks if all tasks have been rendered and updates currently selected task.
        """
        # for each task in the "database" check if it has a tab, if not render it
        for task in self.robotic_system.get_tasks():
            try:
                self.task_tabview.tab(task)
            except ValueError:
                self._render_task(task)

        # update the task info of the currently selected task
        if self.task_tabview.get() != "":
            self._update_task_info(self.task_tabview.get())


# Interface to add, edit and delete operations
class CTkOperationManager(customtkinter.CTkFrame):
    def __init__(self, master, robotic_system: RoboticSystem, message_display: CTkMessageDisplay):
        super().__init__(master)

        self.robotic_system = robotic_system
        self.message_display = message_display

        # configure grid layout
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure((0, 1), weight=1)

        # option menu to select a task and respective label
        self.selected_task_label = customtkinter.CTkLabel(self, text="Task")
        self.selected_task_label.grid(row=0, column=0, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_HALF_Y_PAD)
        self.selected_task = customtkinter.CTkOptionMenu(self, width=120, height=28, values=[""],
                                                         command=self._render_task)
        self.selected_task.grid(row=1, column=0, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD)

        # option menu to select an operation and the respective label
        self.operations_label = customtkinter.CTkLabel(self, text="Operation")
        self.operations_label.grid(row=0, column=1, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_HALF_Y_PAD)
        self.selected_operation = customtkinter.CTkOptionMenu(self, width=120, height=28, values=[""],
                                                              command=self._render_operation)
        self.selected_operation.grid(row=1, column=1, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD)

        # frame to encapsulate the operation management
        self.operation_frame = customtkinter.CTkFrame(self)
        self.operation_frame.grid(row=2, column=0, columnspan=2, padx=MEDIUM_X_PAD, pady=MEDIUM_Y_PAD, sticky="nsew")

        # configure grid layout of operation_frame
        self.operation_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.operation_frame.grid_rowconfigure((0, 2, 5, 8), weight=1)
        self.operation_frame.configure(fg_color=("gray76", "gray23"))

        # button to create a new operation in the selected task
        self.new_operation = customtkinter.CTkButton(self.operation_frame, width=120, height=28, text="New operation",
                                                     command=self._new_operation_event)
        self.new_operation.grid(row=1, column=0, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD)

        # button to save the changes to the operation (doesn't update the task's file)
        self.save_operation = customtkinter.CTkButton(self.operation_frame, width=120, height=28, text="Save changes",
                                                      command=self._save_operation)
        self.save_operation.grid(row=1, column=1, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD)

        # button to delete the selected operation
        self.delete_operation = customtkinter.CTkButton(self.operation_frame, width=120, height=28,
                                                        text="Delete operation", command=self._delete_operation)
        self.delete_operation.grid(row=1, column=2, padx=MEDIUM_X_PAD, pady=MEDIUM_Y_PAD)

        # option menu to select the type of operation and respective label
        self.operation_type_label = customtkinter.CTkLabel(self.operation_frame, text="Type")
        self.operation_type_label.grid(row=3, column=0, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD)
        self.operation_type = customtkinter.CTkOptionMenu(self.operation_frame, width=120, height=28,
                                                          values=["move line", "open", "close", "hand-guide"],
                                                          command=lambda o: self._operation_change_event())
        self.operation_type.grid(row=4, column=0, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_HALF_Y_PAD)

        # option menu to select the tool attached to the robot (valid for hand-guide operations) and respective label
        self.robot_tool_label = customtkinter.CTkLabel(self.operation_frame, text="Tool")
        self.robot_tool_label.grid(row=6, column=0, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_HALF_Y_PAD)
        self.robot_tool = customtkinter.CTkOptionMenu(self.operation_frame, width=120, height=20,
                                                      values=self.robotic_system.get_tool_names(),
                                                      fg_color=("#979da2", "#4a4a4a"),
                                                      button_color=("#60676c", "#666666"),
                                                      button_hover_color=("#60676c", "#666666"),
                                                      dynamic_resizing=False,
                                                      command=lambda t: self._operation_change_event())
        self.robot_tool.set(self.robotic_system.get_tool_names()[0])
        self.robot_tool.grid(row=7, column=0, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD)

        # entry to select the amount of time the robot should wait before continuing to the next operation
        # and respective label
        self.delay_label = customtkinter.CTkLabel(self.operation_frame, text="Delay")
        self.delay_label.grid(row=6, column=1, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_HALF_Y_PAD)
        self.delay = CTkFloatSpinbox(self.operation_frame, width=100, height=20, max_value=30.0, step_size=1.0,
                                     min_value=1.0, command=self._requires_save)
        self.delay.configure(fg_color=("gray76", "gray23"))
        self.delay.grid(row=7, column=1, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD)

        # check box to define if robot should wait for an user input before proceeding to next operation
        # and respective label
        self.wait_label = customtkinter.CTkLabel(self.operation_frame, text="Wait for input")
        self.wait_label.grid(row=3, column=1, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_HALF_Y_PAD)
        self.wait = customtkinter.CTkCheckBox(self.operation_frame, width=1, height=28, text="",
                                              command=self._requires_save)
        self.wait.grid(row=4, column=1, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_HALF_Y_PAD)

        # option menu to select the robot position to move to (valid for move line operations) and respective label
        self.position_label = customtkinter.CTkLabel(self.operation_frame, text="Position")
        self.position_label.grid(row=3, column=2, padx=MEDIUM_X_PAD, pady=MEDIUM_HALF_Y_PAD)
        self.position = customtkinter.CTkOptionMenu(self.operation_frame, width=120, height=28,
                                                    command=lambda p: self._operation_change_event())
        self.position.grid(row=4, column=2, padx=MEDIUM_X_PAD, pady=MEDIUM_HALF_Y_PAD)

        # linear velocity in [mm/s] the robot should move at (valid for move line operations) and respective label
        self.linear_velocity_label = customtkinter.CTkLabel(self.operation_frame, text="Linear velocity")
        self.linear_velocity_label.grid(row=6, column=2, padx=MEDIUM_X_PAD, pady=MEDIUM_HALF_Y_PAD)
        self.linear_velocity = CTkFloatSpinbox(self.operation_frame, width=100, height=20, max_value=250.0,
                                               min_value=1.0, step_size=10, command=self._requires_save)
        self.linear_velocity.set(10.0)
        self.linear_velocity.configure(fg_color=("gray76", "gray23"))
        self.linear_velocity.grid(row=7, column=2, padx=MEDIUM_X_PAD, pady=MEDIUM_Y_PAD)

        # render the operation management elements
        self.render()

        # update button states
        self._button_state(new_operation=True, save_operation=False, delete_operation=False, operation_type=False,
                           position=False, wait_input=False, delay=False, linear_velocity=False, tool=False)

    def _requires_save(self) -> None:
        """
        Check if operation has been changed and requires being saved.
        """

        # exit if task can not be saved
        if self.save_operation.cget("state") == "disabled":
            self.save_operation.configure(fg_color=BLUE_COLORS, hover_color=BLUE_HOVER)
            return

        # exit if no task is selected
        if self.selected_task.get() == "" or self.selected_task.get() is None:
            self.save_operation.configure(fg_color=BLUE_COLORS, hover_color=BLUE_HOVER)
            return

        # exit if no operation is selected
        if self.selected_operation.get() == "" or self.selected_operation.get() is None:
            self.save_operation.configure(fg_color=BLUE_COLORS, hover_color=BLUE_HOVER)
            return

        # fetch current operation
        operation = self.robotic_system.get_operation(self.selected_task.get(),
                                                      int(self.selected_operation.get().split(": ")[0]))

        # check if there is any difference
        requires_save = False
        if operation["type"] != self.operation_type.get():
            requires_save = True
        if operation["position"] != self.position.get():
            requires_save = True
        if operation["wait"] != self.wait.get():
            requires_save = True
        if operation["delay"] != self.delay.get():
            requires_save = True
        if operation["linear_velocity"] != self.linear_velocity.get():
            requires_save = True
        if operation["tool"] != self.robot_tool.get():
            requires_save = True

        # display if operation requires being saved
        if requires_save:
            self.save_operation.configure(fg_color=ORANGE_COLORS, hover_color=ORANGE_HOVER)
        else:
            self.save_operation.configure(fg_color=BLUE_COLORS, hover_color=BLUE_HOVER)

    def render(self) -> None:
        """
        Basic rendering of elements to manage operations.
        """

        # update existing tasks and deselect the current task
        tasks_name_list = self.robotic_system.get_tasks()
        self.selected_task.configure(values=tasks_name_list)
        self.selected_task.set("")

        # remove operations from option menu
        self.selected_operation.configure(values=[])
        self.selected_operation.set("")

        # remove positions from option menu
        self.position.configure(values=[])
        self.position.set("")

        # deselect operation type
        self.operation_type.set("")

        # calculate state and save button rendering
        self._calculate_state()
        self._requires_save()

    def _render_task(self, task_name: str) -> None:
        """
        Render selected task.
        :param task_name: name of the task
        """

        # fetch task info
        task_dict = self.robotic_system.get_task_info(task_name)

        # add positions to option menu
        self.position.configure(values=task_dict["positions"])
        self.position.set("")

        # add operations to option menu
        operations = task_dict["operations"]
        for i in range(len(operations)):
            operations[i] = self._operation_to_str(i, operations[i])

        self.selected_operation.configure(values=operations)
        self.selected_operation.set("")

        # calculate state and render save button state
        self._calculate_state()
        self._requires_save()

    def _button_state(self, new_operation: bool, save_operation: bool, delete_operation: bool, operation_type: bool,
                      position: bool, wait_input: bool, delay: bool, linear_velocity: bool, tool: bool) -> None:
        """
        Set button and labels states.

        :param new_operation: is new operation action allowed
        :param save_operation: is save operation action allowed
        :param delete_operation: is delete operation action allowed
        :param operation_type: is operation type required to save
        :param position: is position required
        :param wait_input: is wait for input required
        :param delay: is delay required
        :param linear_velocity: is linear velocity required
        :param tool: is tool required
        """

        # disable or enable buttons to create, save and delete operations
        self.new_operation.configure(state="normal" if new_operation else "disabled")
        self.save_operation.configure(state="normal" if save_operation else "disabled")
        self.delete_operation.configure(state="normal" if delete_operation else "disabled")

        # label rendering for operation properties
        self.operation_type_label.configure(text_color=['gray10', '#DCE4EE'] if operation_type else ["#888888",
                                                                                                     "#777777"])
        self.position_label.configure(text_color=['gray10', '#DCE4EE'] if position else ["#888888", "#777777"])
        self.wait_label.configure(text_color=['gray10', '#DCE4EE'] if wait_input else ["#888888", "#777777"])

        self.delay_label.configure(text_color=['gray10', '#DCE4EE'] if delay else ["#888888", "#777777"])
        self.linear_velocity_label.configure(text_color=['gray10', '#DCE4EE'] if linear_velocity else ["#888888",
                                                                                                       "#777777"])
        self.robot_tool_label.configure(text_color=['gray10', '#DCE4EE'] if tool else ["#888888", "#777777"])

    def _operation_to_str(self, i: int, operation: dict) -> str:
        """
        Encode operation into a string description.

        :param i: operation index
        :param operation: operation to encode
        :return: operation's string encoding
        """

        if operation["type"] == "move line":
            suffix = f"move to {operation['position']}"
        elif operation["type"] == "hand-guide":
            suffix = f"hand-guide with {operation['tool']}"
        else:
            suffix = operation["type"]

        return f"{i}: {suffix}"

    def _calculate_state(self) -> None:
        """
        Calculate button states.
        """

        # if no task is selected everything is disabled
        if self.selected_task.get() == "":
            self._button_state(new_operation=False, save_operation=False, delete_operation=False, operation_type=False,
                               position=False, wait_input=False, delay=False, linear_velocity=False, tool=False)

        # if no operation is selected only allow to create new operations
        elif self.selected_operation.get() == "":
            self._button_state(new_operation=True, save_operation=False, delete_operation=False, operation_type=False,
                               position=False, wait_input=False, delay=False, linear_velocity=False, tool=False)
        else:
            # identify relevant properties of the operation given the operation type
            operation_type = self.operation_type.get()
            if operation_type == "open" or operation_type == "close":
                self._button_state(new_operation=True, save_operation=True, delete_operation=True,
                                   operation_type=True, position=False, wait_input=True, delay=True,
                                   linear_velocity=False, tool=False)
            elif operation_type == "hand-guide":
                save = False if self.robot_tool.get() == "" or self.robot_tool.get() is None else True
                self._button_state(new_operation=True, save_operation=save, delete_operation=True,
                                   operation_type=True, position=False, wait_input=True, delay=True,
                                   linear_velocity=False, tool=True)
            elif operation_type == "move line":
                save = False if self.position.get() == "" or self.position.get() is None else True
                self._button_state(new_operation=True, save_operation=save, delete_operation=True,
                                   operation_type=True, position=True, wait_input=True, delay=True,
                                   linear_velocity=True, tool=False)

    def _new_operation_event(self) -> None:
        """
        Create a operation in the selected task.
        """

        # add new operation to the task
        self.robotic_system.add_operation(self.selected_task.get())
        operations = self.selected_operation.cget("values")

        # calculate index of new operation
        if operations:
            new_index = int(operations[-1].split(": ")[0]) + 1
        else:
            new_index = 0

        # add placeholder for the new operation
        placeholder = f"{new_index}: Placeholder"
        self.selected_operation.set(placeholder)

        # render new operation
        self._render_operation(placeholder)

    def _render_operation(self, operation_str: str) -> None:
        """
        Render operation with the given name.

        :param operation_str: name of the operation
        """

        # fetch operation by index
        operation_index = int(operation_str.split(": ")[0])
        operation = self.robotic_system.get_operation(self.selected_task.get(), operation_index)

        # update operation encoding
        operations_list = self.selected_operation.cget("values")
        operation_str = self._operation_to_str(operation_index, operation)
        if operation_index == len(operations_list):
            operations_list.append(operation_str)
        else:
            operations_list[operation_index] = operation_str

        self.selected_operation.configure(values=operations_list)
        self.selected_operation.set(operation_str)

        # update displayed information relative to position
        self.operation_type.set(operation["type"])
        if "position" in operation:
            self.position.set(operation["position"])
        else:
            positions = self.position.cget("values")
            if positions:
                self.position.set(positions[0])
            else:
                self.position.set("")

        # update displayed information relative to wait for input
        if "wait" in operation:
            if operation["wait"]:
                self.wait.select()
            else:
                self.wait.deselect()
        else:
            self.wait.deselect()

        # update displayed information relative to tool selected
        if "tool" in operation:
            self.robot_tool.set(operation["tool"])

        # update displayed information relative to delay
        self.delay.set(operation["delay"] if "delay" in operation else 0)

        # update displayed information relative to linear velocity
        self.linear_velocity.set(operation["linear_velocity"] if "linear_velocity" in operation else 5)

        # calculate state and render save button state
        self._calculate_state()
        self._requires_save()

    def _save_operation(self) -> None:
        """
        Save operation properties in the task.
        """

        # fetch some operation propertied and index
        operation_index = self.selected_operation.get().split(": ")[0]
        operation_type = self.operation_type.get()
        cur_delay = self.delay.get()
        cur_lin_vel = self.linear_velocity.get()

        # update operation if type is open or close -> required info: type, wait for input, delay
        if operation_type == "open" or operation_type == "close":
            try:
                if cur_delay is not None:
                    self.robotic_system.update_operation(self.selected_task.get(), index=int(operation_index),
                                                         operation_type=operation_type,
                                                         wait_input=bool(self.wait.get()),
                                                         delay=cur_delay)
            except ValueError as e:
                self.message_display.display_message(e)

        # update operation if type is hand-guide -> required info: type, wait for input, delay, tool
        elif operation_type == "hand-guide":
            try:
                if cur_delay is not None:
                    self.robotic_system.update_operation(self.selected_task.get(), index=int(operation_index),
                                                         operation_type=operation_type,
                                                         wait_input=bool(self.wait.get()),
                                                         delay=cur_delay, tool=self.robot_tool.get())

            except ValueError as e:
                self.message_display.display_message(e)

        # update operation if type is move line -> required info: type, position, wait for input, delay, linear velocity
        elif operation_type == "move line":
            try:
                if cur_delay is not None and cur_lin_vel is not None:
                    self.robotic_system.update_operation(self.selected_task.get(), index=int(operation_index),
                                                         position=self.position.get(), operation_type=operation_type,
                                                         wait_input=bool(self.wait.get()), delay=cur_delay,
                                                         linear_velocity=cur_lin_vel)
            except ValueError as e:
                self.message_display.display_message(e)

        # re-render operation and update save button state
        self._render_operation(self.selected_operation.get())
        self.save_operation.configure(fg_color=BLUE_COLORS, hover_color=BLUE_HOVER)

    def _operation_change_event(self) -> None:
        """
        Reflect changes to the operation.
        """

        # calculate state and render save button state
        self._calculate_state()
        self._requires_save()

    def _delete_operation(self) -> None:
        """
        Delete selected operation from task.
        """

        # fetch operation index
        operation_str = self.selected_operation.get()
        if operation_str == "":
            return
        operation_index = int(operation_str.split(": ")[0])

        # delete operation from task
        try:
            self.robotic_system.delete_operation(self.selected_task.get(), operation_index)
            self._render_task(self.selected_task.get())
        except ValueError as e:
            self.message_display.display_message(e)


# Interface to add, edit and delete positions
class CTkPositionManager(customtkinter.CTkFrame):
    def __init__(self, master, robotic_system: RoboticSystem, message_display: CTkMessageDisplay):
        super().__init__(master)

        self.robotic_system = robotic_system
        self.message_display = message_display

        # configure grid layout
        self.grid_rowconfigure((2, 5, 7, 9), weight=1)
        self.grid_columnconfigure(1, weight=1)

        # option menu to select task and respective label
        self.selected_task_label = customtkinter.CTkLabel(self, text="Task")
        self.selected_task_label.grid(row=0, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_HALF_Y_PAD)
        self.selected_task = customtkinter.CTkOptionMenu(self, width=120, height=28, values=[""],
                                                         command=self._render_task)
        self.selected_task.grid(row=1, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_Y_PAD)

        # option menu to select position from task and respective label
        self.selected_position_label = customtkinter.CTkLabel(self, text="Position")
        self.selected_position_label.grid(row=3, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_HALF_Y_PAD)
        self.selected_position = customtkinter.CTkOptionMenu(self, width=120, height=28, values=[""],
                                                             command=self._render_position)
        self.selected_position.grid(row=4, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_Y_PAD)

        # button to add new robotic position
        self.new_position = customtkinter.CTkButton(self, width=120, height=28, text="New position",
                                                    command=self._new_position_event)
        self.new_position.grid(row=6, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_Y_PAD)

        # button to update selected position
        self.update_position = customtkinter.CTkButton(self, width=120, height=28, text="Update position",
                                                       command=self._update_position_event)
        self.update_position.grid(row=8, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_Y_PAD)

        # button to delete selected position from task
        self.delete_position = customtkinter.CTkButton(self, width=120, height=28,
                                                       text="Delete position", command=self._delete_position_event)
        self.delete_position.grid(row=10, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_Y_PAD)

        # frame to display position cartesian coordinates and joint positions
        self.labels_frame = customtkinter.CTkFrame(self)
        self.labels_frame.grid(row=0, rowspan=11, column=1, padx=MEDIUM_X_PAD, pady=SMALL_Y_PAD, sticky="nsew")

        # configure grid layout of labels_frame
        self.labels_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        self.labels_frame.grid_columnconfigure((0, 3, 6), weight=1)

        # labels to display joint positions
        self.joint_labels = []
        self.joints = []
        for i in range(7):
            self.joint_labels.append(customtkinter.CTkLabel(self.labels_frame, text=f"Joint {i}: "))
            self.joint_labels[i].grid(row=i, column=1, padx=SMALL_HALF_X_PAD, pady=SMALL_Y_PAD)
            self.joints.append(customtkinter.CTkLabel(self.labels_frame, width=50, height=30, text="0.0",
                                                      fg_color=("#ebebeb", "#3d3d3d"), corner_radius=5))
            self.joints[i].grid(row=i, column=2, padx=SMALL_HALF_X_PAD, pady=SMALL_Y_PAD)

        # labels to display cartesian coordinates
        self.coord_labels = []
        self.coords = []
        for i, letter in enumerate(["X", "Y", "Z", "A", "B", "C"]):
            self.coord_labels.append(customtkinter.CTkLabel(self.labels_frame, text=f"{letter}: "))
            self.coord_labels[i].grid(row=i, column=4, padx=SMALL_HALF_X_PAD, pady=SMALL_Y_PAD)
            self.coords.append(customtkinter.CTkLabel(self.labels_frame, width=50, height=35, text="0.0",
                                                      fg_color=("#ebebeb", "#3d3d3d"), corner_radius=5))
            self.coords[i].grid(row=i, column=5, padx=SMALL_X_PAD, pady=SMALL_Y_PAD)

        # button to send robot to the selected position
        self.go_to = customtkinter.CTkButton(self.labels_frame, width=80, height=28,
                                             text="Go to", command=self._go_to_point)
        self.go_to.grid(row=6, column=4, columnspan=2, padx=SMALL_X_PAD, pady=SMALL_Y_PAD)

    def render(self) -> None:
        """
        Basic rendering of position elements.
        """

        # update tasks
        tasks_name_list = self.robotic_system.get_tasks()
        self.selected_task.configure(values=tasks_name_list)
        self.selected_task.set("")

        # update position
        self.selected_position.configure(values=[])
        self.selected_position.set("")

        # reset cartesian coordinates and joint position labels
        for joint in self.joints:
            joint.configure(text="0.0")
        for coord in self.coords:
            coord.configure(text="0.0")

        # calculate current state
        self._calculate_state()

    def _render_task(self, task_name: str) -> None:
        """
        Render task.

        :param task_name: name of the task
        """

        # fetch positions from task and update option menu
        positions = self.robotic_system.get_position_names(task_name)
        self.selected_position.configure(values=positions)

        # calculate new state
        self._calculate_state()

    def _render_position(self, position_name: str) -> None:
        """
        Render position.

        :param position_name: name of the position
        :return:
        """

        # fetch position
        try:
            position = self.robotic_system.get_position(self.selected_task.get(), position_name)
        except ValueError as e:
            self.message_display.display_message(e)
            return

        # update cartesian coordinate and joint position labels
        self._update_labels(position["joints"], position["cartesian"])

        # calculate new state
        self._calculate_state()

    def _delete_position_event(self) -> None:
        """
        Delete selected position from task.
        """

        # delete selected position
        try:
            self.robotic_system.delete_position(self.selected_task.get(), self.selected_position.get())
        except ValueError as e:
            self.message_display.display_message(e)
            return
        self.selected_position.set("")

        # re-render task
        self._render_task(self.selected_task.get())

    def _update_position_event(self) -> None:
        """
        Update position in the task.
        """

        # check robot connection
        if not self.robotic_system.is_robot_connected():
            self.message_display.display_message("Robot communication has not been established")
            return

        # update position
        try:
            cartesian, joints = self.robotic_system.get_robot_position()
            self.robotic_system.update_position(self.selected_task.get(), self.selected_position.get(), cartesian,
                                                joints)
        except OSError as e:
            self.message_display.display_message(e)
            return
        except ValueError as e:
            self.message_display.display_message(e)
            return

        # re-render position
        self._render_position(self.selected_position.get())

    def _new_position_event(self) -> None:
        """
        Create new position in the selected task.
        """

        # check robot connection
        if not self.robotic_system.is_robot_connected():
            self.message_display.display_message("Robot communication has not been established")
            return

        # request name for the new position
        dialog = customtkinter.CTkInputDialog(text="Type in a name:", title="New position")
        position_name = dialog.get_input()

        # create position
        try:
            cartesian, joints = self.robotic_system.get_robot_position()
            position_name = self.robotic_system.add_position(self.selected_task.get(), position_name, cartesian, joints)
        except OSError as e:
            self.message_display.display_message(e)
            return
        except ValueError as e:
            self.message_display.display_message(e)
            return

        # re-render task and position
        self.selected_position.set(position_name)
        self._render_task(self.selected_task.get())
        self._render_position(self.selected_position.get())

    def _calculate_state(self) -> None:
        """
        Calculate button states.
        """

        # if no task is selected all buttons are disabled
        if self.selected_task.get() == "":
            self._set_button_state(new_position=False, update_delete_position=False)

        # if no position is selected only allow to create positions
        elif self.selected_position.get() == "":
            self._set_button_state(new_position=True, update_delete_position=False)

        # allow all actions
        else:
            self._set_button_state(new_position=True, update_delete_position=True)

    def _set_button_state(self, new_position: bool, update_delete_position: bool) -> None:
        """
        Set states for position management buttons.

        :param new_position: is the creation of new positions allowed
        :param update_delete_position: is the update and deletion of positions allowed
        """

        # set button states
        self.new_position.configure(state="normal" if new_position else "disabled")
        self.update_position.configure(state="normal" if update_delete_position else "disabled")
        self.delete_position.configure(state="normal" if update_delete_position else "disabled")
        self.go_to.configure(state="normal" if update_delete_position else "disabled")

    def _update_labels(self, joints: list, coordinates: list) -> None:
        """
        Update cartesian coordinate and joint position labels.

        :param joints: joint positions
        :param coordinates: cartesian coordinates
        """

        for i, joint in enumerate(joints):
            self.joints[i].configure(text=f"{joint:.1f}")
        for i, coord in enumerate(coordinates):
            self.coords[i].configure(text=f"{coord:.1f}")

    def _go_to_point(self) -> None:
        """
        Move robot to the selected position.
        """

        # check robot connection
        if not self.robotic_system.is_robot_connected():
            self.message_display.display_message("Robot communication has not been established")
            return

        # send command to move to the selected position
        if self.selected_task.get() != "" and self.selected_position.get() != "":
            try:
                position = self.robotic_system.get_position(self.selected_task.get(), self.selected_position.get())
                self.robotic_system.move_robot_line(position["cartesian"], 20)

            except OSError as e:
                self.message_display.display_message(e)
                return
            except ValueError as e:
                self.message_display.display_message(e)
                return


# Interface to create programs, edit them and run.
class CTkProgramManager(customtkinter.CTkFrame):
    def __init__(self, master, robotic_system: RoboticSystem, message_display: CTkMessageDisplay):
        super().__init__(master)

        self.robotic_system = robotic_system
        self.message_display = message_display

        # frames to display task info
        self.task_frames = []

        # configure grid layout
        self.grid_rowconfigure((0, 2, 4, 6, 8, 10, 12), weight=1)
        self.grid_columnconfigure(1, weight=1)

        # frame to display the program
        self.program_frame = customtkinter.CTkFrame(self)
        self.program_frame.grid(row=1, rowspan=11, column=1, padx=MEDIUM_X_PAD, pady=SMALL_Y_PAD, sticky="nsew")

        # configure grid layout of program_frame
        self.program_frame.grid_columnconfigure((0, 1), weight=1)
        self.program_frame.grid_rowconfigure(3, weight=1)
        self.program_frame.configure(fg_color=("gray76", "gray23"))

        # button to add new program
        self.new_program = customtkinter.CTkButton(self, width=120, height=28, text="New program",
                                                   command=self._new_program_event)
        self.new_program.grid(row=1, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_Y_PAD)

        # button to load program
        self.load_program = customtkinter.CTkButton(self, width=120, height=28, text="Load program",
                                                    command=self._load_program_event)
        self.load_program.grid(row=3, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_Y_PAD)

        # button to save program
        self.save_program = customtkinter.CTkButton(self, width=120, height=28, text="Save program",
                                                    command=self._save_program_event)
        self.save_program.grid(row=5, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_Y_PAD)
        self.save_program.configure(state="disabled")

        # button to close program
        self.close_program = customtkinter.CTkButton(self, width=120, height=28, text="Close program",
                                                     command=self._close_program_event)
        self.close_program.grid(row=7, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_Y_PAD)
        self.close_program.configure(state="disabled")

        # button to run program
        self.run_program = customtkinter.CTkButton(self, width=120, height=28, text="Run program",
                                                   command=self._run_program_event)
        self.run_program.grid(row=9, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_Y_PAD)
        self.run_program.configure(state="disabled")

        # program display and program name label
        self.program_display = CTkProgramBoxList(self.program_frame, self.robotic_system)
        self.program_display.grid(row=3, column=0, columnspan=2, padx=MEDIUM_X_PAD, pady=BIG_Y_PAD, sticky="nsew")
        self.program_name_label = customtkinter.CTkLabel(self.program_frame, text="")
        self.program_name_label.grid(row=0, column=0, columnspan=2, padx=MEDIUM_X_PAD, pady=MEDIUM_HALF_Y_PAD)

        # option menu of loaded tasks
        self.available_tasks = customtkinter.CTkOptionMenu(self.program_frame, width=120, height=28, values=[""],
                                                           command=lambda t: self._selected_task_event())
        self.available_tasks.grid(row=1, column=1, padx=MEDIUM_X_PAD, pady=MEDIUM_HALF_Y_PAD)

        # button to add a new task manually
        self.add_task_manually = customtkinter.CTkButton(self.program_frame, width=120, height=60,
                                                         text="Add task manually",
                                                         command=self._add_task_manually_event)
        self.add_task_manually.grid(row=1, rowspan=2, column=0, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_HALF_Y_PAD)
        self.add_task_manually.configure(state="disabled")

        # button to add a task from currently loaded tasks
        self.add_task = customtkinter.CTkButton(self.program_frame, width=120, height=28, text="Add selected task",
                                                command=self._add_task_event)
        self.add_task.grid(row=2, column=1, padx=MEDIUM_X_PAD, pady=MEDIUM_HALF_Y_PAD)
        self.add_task.configure(state="disabled")

        # legend frame and labels to explain task states
        self.legend_frame = customtkinter.CTkFrame(self)
        self.legend_frame.grid(row=11, column=0, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD, sticky="nsew")
        self.legend_frame.grid_columnconfigure(0, weight=1)
        self.legend_frame.grid_rowconfigure((0, 2, 4, 6), weight=1)
        self.green_legend = self._create_frame_task_state(self.legend_frame, "Ready", 0)
        self.green_legend.configure(fg_color="transparent")
        self.green_legend.grid(row=1, column=0, padx=SMALL_X_PAD, pady=SMALL_HALF_Y_PAD, sticky="nsew")
        self.orange_legend = self._create_frame_task_state(self.legend_frame, "Not saved", 1)
        self.orange_legend.grid(row=3, column=0, padx=SMALL_X_PAD, pady=SMALL_HALF_Y_PAD, sticky="nsew")
        self.orange_legend.configure(fg_color="transparent")
        self.red_legend = self._create_frame_task_state(self.legend_frame, "Non existent", 2)
        self.red_legend.grid(row=5, column=0, padx=SMALL_X_PAD, pady=SMALL_Y_PAD, sticky="nsew")
        self.red_legend.configure(fg_color="transparent")

    def _load_program_event(self) -> None:
        """
        Load a program from a previously created file.
        """

        # request name of the program to be loaded
        dialog = customtkinter.CTkInputDialog(text="Type program name:", title="Load program")
        program_name = dialog.get_input()

        # load program from file
        if program_name is not None:
            try:
                program_name = self.robotic_system.load_program(program_name)
            except ValueError as e:
                self.message_display.display_message(e)
                return
            except FileNotFoundError as e:
                self.message_display.display_message(e)
                return

            # render loaded program
            self._render_program(program_name)
            self._update_info()

    def _new_program_event(self) -> None:
        """
        Create a new program.
        """

        # request name for the new program
        dialog = customtkinter.CTkInputDialog(text="Type in a name:", title="New program")
        program_name = dialog.get_input()

        # create program
        if program_name is not None:
            if self.robotic_system.exists_program_file(program_name):
                # if program already exists ask whether to override previous file
                ok_cancel = CTkOkCancel(text="A file with this name already exists. \n"
                                             "Do you wish to override it?",
                                        title="Override previous file", first_button="Yes", second_button="Cancel")
                if not ok_cancel.get_input():
                    return

            # create new program
            try:
                program_name = self.robotic_system.add_program(program_name)
            except ValueError as e:
                self.message_display.display_message(e)
                return
            except FileNotFoundError as e:
                self.message_display.display_message(e)
                return

            # render program
            self._render_program(program_name)

    def _close_program_event(self) -> None:
        """
        Close currently open program.
        """

        # ask to confirm program closure
        ok_cancel = CTkOkCancel(text="Do you want to close the program?", title="Close program", first_button="Yes")
        if ok_cancel.get_input():
            try:
                self.robotic_system.close_program()
            except ValueError as e:
                self.message_display.display_message(e)
                return

            # reset elements and calculate button states
            self.program_name_label.configure(text="")
            self.program_display.reset()
            self.program_frame.configure(border_color=('gray81', 'gray20'))
            self._calculate_state()

    def _run_program_event(self) -> None:
        """
        Run currently open program
        """

        # check if robot is connected
        if not self.robotic_system.is_robot_connected():
            self.message_display.display_message("There is no open connection")
            return

        # run program
        try:
            self.robotic_system.run_program()
        except ValueError as e:
            self.message_display.display_message(e)
            return
        except RuntimeError as e:
            self.message_display.display_message(e)
            return
        except OSError as e:
            self.message_display.display_message(e)
            return

        # update task info
        self._update_info()

    def _render_program(self, program_name: str) -> None:
        """
        Render program.

        :param program_name: name of the program
        """

        # render program name and calculate button states
        self.program_name_label.configure(text=program_name)
        self._calculate_state()

    def _calculate_state(self) -> None:
        """
        Calculate state of buttons.
        """

        # if a program is open activate buttons to add tasks, to save program and to run
        # if no task is selected in available tasks, disable state for button to add tak
        if self.robotic_system.is_program_open():
            self.new_program.configure(state="disabled")
            self.load_program.configure(state="disabled")
            self.close_program.configure(state="normal")
            self.run_program.configure(state="normal")
            self.add_task_manually.configure(state="normal")
            self.available_tasks.configure(state="normal")
            self.save_program.configure(state="normal")
            if self.available_tasks.get() != "" and self.available_tasks.get():
                self.add_task.configure(state="normal")
            else:
                self.add_task.configure(state="disabled")

        # if no program is open activate buttons to create or load a program
        else:
            self.new_program.configure(state="normal")
            self.load_program.configure(state="normal")
            self.close_program.configure(state="disabled")
            self.run_program.configure(state="disabled")
            self.add_task.configure(state="disabled")
            self.add_task_manually.configure(state="disabled")
            self.available_tasks.set("")
            self.available_tasks.configure(state="disabled")
            self.save_program.configure(state="disabled")

    def render(self):
        """
        Basic render of program management elements.
        """

        # get loaded tasks to update option menu
        tasks = self.robotic_system.get_tasks()
        self.available_tasks.configure(values=tasks)
        self.available_tasks.set("")

        # calculate button states
        self._calculate_state()

        # if program is open update displayed program task related info
        if self.robotic_system.is_program_open():
            self._update_info()

    def _update_info(self) -> None:
        """
        Update program task related information.
        """

        # remove previously rendered tasks
        while self.task_frames:
            task_frame = self.task_frames.pop()
            task_frame.destroy()

        # get tasks from program and render
        tasks, states = self.robotic_system.get_tasks_and_states_from_program()
        for task, state in zip(tasks, states):
            self.task_frames.append(self._create_frame_task_state(self.program_display, task, state))
        self.program_display.update_elements(self.task_frames)

    def _add_task_manually_event(self) -> None:
        """
        Add task to program from name.
        """

        # request name of the task to add
        dialog = customtkinter.CTkInputDialog(text="Type in the task name:", title="Add task")
        task_name = dialog.get_input()

        # add task
        if task_name:
            self._add_task_to_program(task_name)

    def _add_task_event(self) -> None:
        """
        Add task to program from loaded tasks.
        """

        self._add_task_to_program(self.available_tasks.get())

    def _add_task_to_program(self, task_name: str) -> None:
        """
        Add task to program.

        :param task_name: name of the task
        """

        # add task to program
        try:
            task_name, state = self.robotic_system.add_task_to_program(task_name)
        except ValueError as e:
            self.message_display.display_message(e)
            return

        # create task representation and add to display
        frame = self._create_frame_task_state(self.program_display, task_name, state)
        self.program_display.insert_element(frame)

    def _save_program_event(self) -> None:
        """
        Save program to file.
        """

        # save program
        try:
            self.robotic_system.save_program()
        except ValueError as e:
            self.message_display.display_message(e)
            return

    def _create_frame_task_state(self, frame_parent, task: str, state: int) -> \
            customtkinter.CTkFrame:
        """
        Create frame in the passed in parent frame containing the given task and state.

        :param frame_parent: element where the new frame should be rendered
        :param task: name of the task
        :param state: state of the task (0 if exists, 1 if exists and not up to date, 2 if does not exist)
        """

        # create new frame
        new_frame = customtkinter.CTkFrame(frame_parent, height=28, width=200)

        # configure grid layout of new_frame
        new_frame.grid_columnconfigure(1, weight=1)
        new_frame.grid_rowconfigure(0, weight=1)

        # label to indicate state
        state_label = customtkinter.CTkLabel(new_frame, text="", width=20, height=20, corner_radius=10)
        if state == 0:
            state_label.configure(fg_color=GREEN_COLORS)
        elif state == 1:
            state_label.configure(fg_color=ORANGE_COLORS)
        elif state == 2:
            state_label.configure(fg_color=RED_COLORS)

        # label to display the task name
        task_name_label = customtkinter.CTkLabel(new_frame, text=task, anchor="w")
        state_label.grid(row=0, column=0, padx=SMALL_HALF_X_PAD, pady=SMALL_Y_PAD)
        task_name_label.grid(row=0, column=1, padx=SMALL_X_PAD, pady=SMALL_Y_PAD, sticky="nsew")

        return new_frame

    def _selected_task_event(self) -> None:
        """
        Calculate state when a new task is selected.
        """
        self._calculate_state()


# Tab with the multiple interfaces to control the robot and edit tasks, operations and positions
class CTkTabViewer(customtkinter.CTkFrame):
    def __init__(self, master, robotic_system: RoboticSystem, message_display: CTkMessageDisplay):
        super().__init__(master)

        self.robotic_system = robotic_system
        self.message_display = message_display

        # configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # create tabview with tabs for the multiple sections
        self.tabview = customtkinter.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=MEDIUM_X_PAD, pady=BIG_Y_PAD, sticky="nsew")
        self.tabview.add("Manage tasks")
        self.tabview.add("Manage operations")
        self.tabview.add("Manage positions")
        self.tabview.add("Program")

        # configure grid layout for each tab
        self.tabview.tab("Manage tasks").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Manage tasks").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Manage operations").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Manage operations").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Manage positions").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Manage positions").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Program").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Program").grid_columnconfigure(0, weight=1)

        # render elements for task management
        self.task_manager = CTkTaskManager(self.tabview.tab("Manage tasks"), self.robotic_system, self.message_display)
        self.task_manager.configure(fg_color="transparent")
        self.task_manager.grid(row=0, column=0, padx=MEDIUM_X_PAD, pady=MEDIUM_Y_PAD, sticky="nsew")

        # render elements for operation management
        self.operation_manager = CTkOperationManager(self.tabview.tab("Manage operations"), self.robotic_system,
                                                     self.message_display)
        self.operation_manager.configure(fg_color="transparent")
        self.operation_manager.grid(row=0, column=0, padx=MEDIUM_X_PAD, pady=MEDIUM_Y_PAD, sticky="nsew")

        # render elements for position management
        self.position_manager = CTkPositionManager(self.tabview.tab("Manage positions"), self.robotic_system,
                                                   self.message_display)
        self.position_manager.configure(fg_color="transparent")
        self.position_manager.grid(row=0, column=0, padx=MEDIUM_X_PAD, pady=MEDIUM_Y_PAD, sticky="nsew")

        # render elements for program management
        self.program_manager = CTkProgramManager(self.tabview.tab("Program"), self.robotic_system, self.message_display)
        self.program_manager.configure(fg_color="transparent")
        self.program_manager.grid(row=0, column=0, padx=MEDIUM_X_PAD, pady=MEDIUM_Y_PAD, sticky="nsew")

        self.tabview.configure(command=self.render)

    def render(self) -> None:
        """
        Update rendering of elements when changing tabs.
        """

        if self.tabview.get() == "Manage tasks":
            self.task_manager.render()
        elif self.tabview.get() == "Manage operations":
            self.operation_manager.render()
        elif self.tabview.get() == "Manage positions":
            self.position_manager.render()
        elif self.tabview.get() == "Program":
            self.program_manager.render()
