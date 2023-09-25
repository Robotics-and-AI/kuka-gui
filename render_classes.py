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

    def delete_element(self, index):
        try:
            self.robotic_system.delete_task_from_program(index)
        except ValueError:
            raise
        super().delete_element(index)

    def _up_event(self, index):
        if index > 0:
            try:
                self.robotic_system.swap_tasks_in_program(index, index - 1)
            except ValueError:
                raise
            super()._up_event(index)

    def _down_event(self, index):
        if index < len(self.elements) - 1:
            try:
                self.robotic_system.swap_tasks_in_program(index, index + 1)
            except ValueError:
                raise
            super()._down_event(index)


# Robot connection
class CTkRobotConnector(customtkinter.CTkFrame):
    def __init__(self, master, robotic_system: RoboticSystem, message_display: CTkMessageDisplay):
        super().__init__(master)
        self.grid_columnconfigure((0, 3), weight=1)
        self.message_display = message_display
        self.robotic_system = robotic_system
        self.ip_entry_label = customtkinter.CTkLabel(self, text="Robot's ip:")
        self.ip_entry_label.grid(row=0, column=1, padx=SMALL_HALF_X_PAD, pady=SMALL_Y_PAD)
        self.ip_entry = customtkinter.CTkEntry(self, width=140)
        self.ip_entry.insert(0, "172.31.1.147")
        self.ip_entry.grid(row=0, column=2, padx=SMALL_X_PAD, pady=SMALL_Y_PAD, sticky="nsew")
        self.connect = customtkinter.CTkButton(self, text="Connect", width=140, height=28, command=self._connect_event)
        self.connect.grid(row=1, column=2, padx=SMALL_X_PAD, pady=SMALL_Y_PAD, sticky="nsew")
        self.connect_lamp = customtkinter.CTkLabel(self, text="", width=26, height=26, corner_radius=13,
                                                   fg_color="transparent")
        self.connect_lamp.grid(row=1, column=1, padx=SMALL_X_PAD, pady=SMALL_Y_PAD)

    def _connect_event(self):
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


# Sidebar
class CTkSidebar(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # create sidebar frame with widgets
        self.logo_label = customtkinter.CTkLabel(self, text="Kuka iiwa GUI",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
        self.grid_rowconfigure(1, weight=1)
        self.logo_label.grid(row=0, column=0, padx=MEDIUM_X_PAD, pady=(20, 10))

        self.appearance_mode_label = customtkinter.CTkLabel(self, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=2, column=0, padx=MEDIUM_X_PAD, pady=(10, 0))
        self.appearance_mode_option_menu = customtkinter.CTkOptionMenu(self,
                                                                       values=["Light", "Dark", "System"],
                                                                       command=self._change_appearance_mode_event)
        self.appearance_mode_option_menu.grid(row=3, column=0, padx=MEDIUM_X_PAD, pady=(10, 10))

        self.scaling_label = customtkinter.CTkLabel(self, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=4, column=0, padx=MEDIUM_X_PAD, pady=(10, 0))
        self.scaling_option_menu = customtkinter.CTkOptionMenu(self,
                                                               values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self._change_scaling_event)
        self.scaling_option_menu.grid(row=5, column=0, padx=MEDIUM_X_PAD, pady=(10, 20))

        # set default values
        self.appearance_mode_option_menu.set("System")
        self.scaling_option_menu.set("100%")

    def _change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def _change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)


# Interface to command robot movements (cartesian movements, open/close gripper, move home)
class CTkMoveRobot(customtkinter.CTkFrame):
    def __init__(self, master, robotic_system: RoboticSystem, message_display: CTkMessageDisplay):
        super().__init__(master)

        self.robotic_system = robotic_system
        self.message_display = message_display

        self.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.grid_columnconfigure((0, 2, 4), weight=1)

        self.top_frame = customtkinter.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, columnspan=5, padx=SMALL_X_PAD, pady=MEDIUM_HALF_Y_PAD, sticky="nsew")
        self.top_frame.grid_rowconfigure((0, 1), weight=1)
        self.top_frame.grid_columnconfigure((0, 1), weight=1)

        self.open_gripper = customtkinter.CTkButton(self.top_frame, width=120, height=20, text="Open",
                                                    command=self._open_gripper_event)
        self.open_gripper.grid(row=1, column=0, padx=SMALL_X_PAD, pady=MEDIUM_Y_PAD, sticky="nsew")

        self.close_gripper = customtkinter.CTkButton(self.top_frame, width=120, height=20, text="Close",
                                                     command=self._close_gripper_event)
        self.close_gripper.grid(row=1, column=1, padx=SMALL_X_PAD, pady=MEDIUM_Y_PAD, sticky="nsew")

        self.hand_guide = customtkinter.CTkButton(self.top_frame, width=120, height=20, text="Hand-guide",
                                                  command=self._hand_guide_event)
        self.hand_guide.grid(row=0, column=1, padx=SMALL_X_PAD, pady=MEDIUM_HALF_Y_PAD, sticky="nsew")

        self.robot_tool = customtkinter.CTkOptionMenu(self.top_frame, width=120, height=20,
                                                      values=self.robotic_system.get_tool_names(),
                                                      fg_color=("#979da2", "#4a4a4a"),
                                                      button_color=("#60676c", "#666666"),
                                                      button_hover_color=("#60676c", "#666666"),
                                                      dynamic_resizing=False)
        self.robot_tool.set(self.robotic_system.get_tool_names()[0])
        self.robot_tool.grid(row=0, column=0, padx=SMALL_X_PAD, pady=MEDIUM_HALF_Y_PAD, sticky="ew")

        self.move_buttons = {}
        for i, letter in enumerate(["X", "Y", "Z"]):
            self.move_buttons[f"{letter}+"] = customtkinter.CTkButton(self, width=120, height=20, text=f"{letter}+",
                                                                      font=customtkinter.CTkFont(size=17),
                                                                      command=lambda axis=i:
                                                                      self._move_robot(axis, True))
            self.move_buttons[f"{letter}+"].grid(row=i+1, column=1, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_HALF_Y_PAD,
                                                 sticky="nsew")
            self.move_buttons[f"{letter}-"] = customtkinter.CTkButton(self, width=120, height=20, text=f"{letter}-",
                                                                      font=customtkinter.CTkFont(size=17),
                                                                      command=lambda axis=i:
                                                                      self._move_robot(axis, False))
            self.move_buttons[f"{letter}-"].grid(row=i+1, column=3, padx=MEDIUM_X_PAD, pady=MEDIUM_HALF_Y_PAD,
                                                 sticky="nsew")
        self.amount_label = customtkinter.CTkLabel(self, text="Amount [mm]:")
        self.amount_label.grid(row=4, column=1, padx=SMALL_HALF_X_PAD, pady=SMALL_HALF_Y_PAD)
        self.amount = CTkFloatSpinbox(self, width=120, max_value=200.0, min_value=1.0, step_size=2)
        self.amount.set(5)
        self.amount.grid(row=5, column=1, padx=SMALL_X_PAD, pady=SMALL_Y_PAD)
        self.amount.configure(fg_color=('gray86', 'gray17'))
        self.velocity_label = customtkinter.CTkLabel(self, text="Velocity [mm/s]:")
        self.velocity_label.grid(row=4, column=3, padx=SMALL_HALF_X_PAD, pady=SMALL_HALF_Y_PAD)
        self.velocity = CTkFloatSpinbox(self, width=120, max_value=100.0, min_value=1.0, step_size=2)
        self.velocity.set(5.0)
        self.velocity.grid(row=5, column=3, padx=SMALL_X_PAD, pady=SMALL_Y_PAD)
        self.velocity.configure(fg_color=('gray86', 'gray17'))

    def _move_robot(self, direction: int, positive: bool):
        if not self.robotic_system.is_robot_connected():
            self.message_display.display_message("Robot communication has not been established")
            return

        position = [0.0, 0.0, 0.0]
        position[direction] = self.amount.get() if positive else -self.amount.get()
        velocity = self.velocity.get()

        try:
            self.robotic_system.move_robot(position, [velocity])
        except OSError as e:
            self.message_display.display_message(e)

    def _open_gripper_event(self):
        if self.robotic_system.is_robot_connected():
            try:
                self.robotic_system.open_gripper()
            except OSError as e:
                self.message_display.display_message(e)
        else:
            self.message_display.display_message("Robot communication has not been established")

    def _close_gripper_event(self):
        if self.robotic_system.is_robot_connected():
            try:
                self.robotic_system.close_gripper()
            except OSError as e:
                self.message_display.display_message(e)

            self.message_display.display_message("Robot communication has not been established")

    def _hand_guide_event(self):
        """Weight of tool in Newtons and centre of mass in mm"""
        try:
            tool = self.robotic_system.get_tool_info(self.robot_tool.get())
        except ValueError as e:
            self.message_display.display_message(e)
            return

        print(tool)
        if self.robotic_system.is_robot_connected():
            try:
                self.robotic_system.hand_guide(tool["weight_of_tool"], tool["centre_of_mass"])
            except OSError as e:
                self.message_display.display_message(e)
            except ValueError as e:
                self.message_display.display_message(e)
        else:
            self.message_display.display_message("Robot communication has not been established")


# Task management interface to create, load, save and delete tasks
class CTkTaskManager(customtkinter.CTkFrame):
    def __init__(self, master, robotic_system: RoboticSystem, message_display: CTkMessageDisplay):
        super().__init__(master)
        self.robotic_system = robotic_system
        self.message_display = message_display

        self.tasks_labels = {}
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.task_state = {}
        self.task_frame = {}

        self.create_task = customtkinter.CTkButton(self, width=80, height=40, text="New task",
                                                   command=self._new_task_event)
        self.create_task.grid(row=0, column=0, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD)
        self.load_task = customtkinter.CTkButton(self, width=80, height=40, text="Load task",
                                                 command=self._load_task_event)
        self.load_task.grid(row=0, column=1, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD)
        self.save_task = customtkinter.CTkButton(self, width=80, height=40, text="Save task",
                                                 command=self._save_task_event)
        self.save_task.grid(row=0, column=2, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD)
        self.delete_task = customtkinter.CTkButton(self, width=80, height=40, text="Delete task",
                                                   command=self._delete_task_event)
        self.delete_task.grid(row=0, column=3, padx=MEDIUM_X_PAD, pady=MEDIUM_Y_PAD)

        self.task_tabview = customtkinter.CTkTabview(self)
        self.task_tabview.configure(fg_color=("gray76", "gray23"), command=self.render)
        self.task_tabview.grid(row=1, column=0, columnspan=4, padx=MEDIUM_X_PAD, pady=MEDIUM_Y_PAD, sticky="nsew")

    def _new_task_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a name:", title="New task")
        task_name = dialog.get_input()
        if task_name is not None:
            if self.robotic_system.exists_task_file(task_name):
                ok_cancel = CTkOkCancel(text="A file with this name already exists. \n"
                                             "Do you wish to override it?",
                                        title="Override previous file", first_button="Yes", second_button="Cancel")
                if not ok_cancel.get_input():
                    return
            try:
                task_name = self.robotic_system.add_task(task_name)
            except ValueError as e:
                self.message_display.display_message(e)
                return
            except FileNotFoundError as e:
                self.message_display.display_message(e)
                return
            self._render_task(task_name)

    def _load_task_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type task name:", title="Load task")
        task_name = dialog.get_input()
        if task_name is not None:
            try:
                task_name = self.robotic_system.load_task(task_name)
            except ValueError as e:
                self.message_display.display_message(e)
                return
            except FileNotFoundError as e:
                self.message_display.display_message(e)
                return

            self._render_task(task_name)
            self._update_task_info(task_name)

    def _render_task(self, task_name: str):
        try:
            self.task_tabview.add(task_name)
            self.task_tabview.tab(task_name).grid_columnconfigure(0, weight=1)
            self.task_tabview.tab(task_name).grid_rowconfigure((0, 3), weight=1)

            self.task_frame[task_name] = customtkinter.CTkFrame(self.task_tabview.tab(task_name), border_width=2,
                                                                height=200, width=200,
                                                                border_color=ORANGE_COLORS,
                                                                fg_color="transparent")
            self.task_frame[task_name].grid(row=2, column=0, padx=MEDIUM_X_PAD, pady=MEDIUM_Y_PAD)

            self.task_state[task_name] = customtkinter.CTkLabel(self.task_tabview.tab(task_name),
                                                                text="Save task to confirm changes")
            self.task_state[task_name].grid(row=1, column=0, padx=MEDIUM_X_PAD, pady=MEDIUM_HALF_Y_PAD)

            self.task_frame[task_name].grid_columnconfigure((0, 2, 4), weight=1)
            self.task_frame[task_name].grid_rowconfigure((0, 3), weight=1)

            operations_label = customtkinter.CTkLabel(self.task_frame[task_name], text="# of operations:",
                                                      font=customtkinter.CTkFont(size=13))
            operations_label.grid(row=1, column=1, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_HALF_Y_PAD)
            operations_value = customtkinter.CTkLabel(self.task_frame[task_name], text="0",
                                                      font=customtkinter.CTkFont(size=13))
            operations_value.grid(row=2, column=1, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD)
            positions_label = customtkinter.CTkLabel(self.task_frame[task_name], text="# of points:",
                                                     font=customtkinter.CTkFont(size=13))
            positions_label.grid(row=1, column=3, padx=MEDIUM_X_PAD, pady=MEDIUM_HALF_Y_PAD)
            positions_value = customtkinter.CTkLabel(self.task_frame[task_name], text="0",
                                                     font=customtkinter.CTkFont(size=13))
            positions_value.grid(row=2, column=3, padx=MEDIUM_X_PAD, pady=MEDIUM_Y_PAD)

            self.tasks_labels[task_name] = {
                "operations": operations_value,
                "positions": positions_value
            }

        except ValueError:  # THERE ALREADY EXISTS A TASK WITH THIS NAME
            self.message_display.display_message(f"There already exists a task {task_name}")

    def _save_task_event(self):
        if self.task_tabview.get() != "":
            task_name = self.task_tabview.get()
            try:
                self.robotic_system.save_task(task_name)
            except ValueError as e:
                self.message_display.display_message(e)

            self._update_task_status(task_name)

    def _delete_task_event(self):
        if self.task_tabview.get() != "":
            task_name = self.task_tabview.get()
            ok_cancel = CTkOkCancel(text="Do you want to delete the task?", title="Delete task", first_button="Yes")
            if ok_cancel.get_input():
                ok_no = CTkOkCancel(text="Delete the file, if it exists?", title="Delete file",
                                    first_button="Yes", second_button="No")
                try:
                    self.robotic_system.delete_task(task_name, ok_no.get_input())
                except ValueError as e:
                    self.message_display.display_message(e)
                    return

                self.task_tabview.delete(task_name)

    def _update_task_info(self, task_name: str):
        try:
            retrieved_data = self.robotic_system.get_task_info(task_name)
            self._update_task_status(task_name)
        except ValueError as e:
            self.message_display.display_message(e)
            return

        if retrieved_data:
            self.tasks_labels[task_name]["operations"].configure(text=str(len(retrieved_data["operations"])))
            self.tasks_labels[task_name]["positions"].configure(text=str(len(retrieved_data["positions"])))

    def _update_tasks_event(self):
        for task in self.tasks_labels:
            self._update_task_info(task)

    def _update_task_status(self, task_name):
        try:
            status = self.robotic_system.is_task_up_to_date(task_name)
        except ValueError as e:
            self.message_display.display_message(e)
            return

        if status:
            self.task_frame[task_name].configure(border_color=GREEN_COLORS)
            self.task_state[task_name].configure(text="Task up to date")
        else:
            self.task_frame[task_name].configure(border_color=ORANGE_COLORS)
            self.task_state[task_name].configure(text="Save task to confirm changes")

    def render(self):
        for task in self.robotic_system.get_tasks():
            try:
                self.task_tabview.tab(task)
            except ValueError:
                self._render_task(task)
        if self.task_tabview.get() != "":
            self._update_task_info(self.task_tabview.get())


# Interface to add, edit and delete operations
# TODO: Add gripper mass and COM. Loaded from file?
# TODO: LOAD TOOL INFO
# TODO: SAVE TOOL NAME IN OPERATION
class CTkOperationManager(customtkinter.CTkFrame):
    def __init__(self, master, robotic_system: RoboticSystem, message_display: CTkMessageDisplay):
        super().__init__(master)
        self.robotic_system = robotic_system
        self.message_display = message_display

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure((0, 1), weight=1)

        self.selected_task_label = customtkinter.CTkLabel(self, text="Task")
        self.selected_task_label.grid(row=0, column=0, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_HALF_Y_PAD)
        self.selected_task = customtkinter.CTkOptionMenu(self, width=120, height=28, values=[""],
                                                         command=self._render_task)
        self.selected_task.grid(row=1, column=0, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD)

        self.operations_label = customtkinter.CTkLabel(self, text="Operation")
        self.operations_label.grid(row=0, column=1, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_HALF_Y_PAD)
        self.selected_operation = customtkinter.CTkOptionMenu(self, width=120, height=28, values=[""],
                                                              command=self._render_operation)
        self.selected_operation.grid(row=1, column=1, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD)

        # Frame with buttons to edit operation properties
        self.operation_frame = customtkinter.CTkFrame(self)
        self.operation_frame.grid(row=2, column=0, columnspan=2, padx=MEDIUM_X_PAD, pady=MEDIUM_Y_PAD, sticky="nsew")

        self.operation_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.operation_frame.grid_rowconfigure((0, 2, 5, 8), weight=1)
        self.operation_frame.configure(fg_color=("gray76", "gray23"))

        self.new_operation = customtkinter.CTkButton(self.operation_frame, width=120, height=28, text="New operation",
                                                     command=self._new_operation_event)
        self.new_operation.grid(row=1, column=0, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD)
        self.save_operation = customtkinter.CTkButton(self.operation_frame, width=120, height=28, text="Save changes",
                                                      command=self._save_operation)
        self.save_operation.grid(row=1, column=1, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD)
        self.delete_operation = customtkinter.CTkButton(self.operation_frame, width=120, height=28,
                                                        text="Delete operation", command=self._delete_operation)
        self.delete_operation.grid(row=1, column=2, padx=MEDIUM_X_PAD, pady=MEDIUM_Y_PAD)

        self.operation_type_label = customtkinter.CTkLabel(self.operation_frame, text="Type")
        self.operation_type_label.grid(row=3, column=0, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD)
        self.operation_type = customtkinter.CTkOptionMenu(self.operation_frame, width=120, height=28,
                                                          values=["move line", "open", "close", "hand-guide"],
                                                          command=self._operation_change_event)
        self.operation_type.grid(row=4, column=0, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_HALF_Y_PAD)

        self.robot_tool_label = customtkinter.CTkLabel(self.operation_frame, text="Tool")
        self.robot_tool_label.grid(row=6, column=0, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_HALF_Y_PAD)
        self.robot_tool = customtkinter.CTkOptionMenu(self.operation_frame, width=120, height=20,
                                                      values=self.robotic_system.get_tool_names(),
                                                      fg_color=("#979da2", "#4a4a4a"),
                                                      button_color=("#60676c", "#666666"),
                                                      button_hover_color=("#60676c", "#666666"),
                                                      dynamic_resizing=False)
        self.robot_tool.set(self.robotic_system.get_tool_names()[0])
        self.robot_tool.grid(row=7, column=0, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD)

        self.delay_label = customtkinter.CTkLabel(self.operation_frame, text="Delay")
        self.delay_label.grid(row=6, column=1, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_HALF_Y_PAD)
        self.delay = CTkFloatSpinbox(self.operation_frame, width=100, height=20, max_value=30.0, step_size=1.0,
                                     min_value=0.0, command=self._requires_save)
        self.delay.configure(fg_color=("gray76", "gray23"))
        self.delay.grid(row=7, column=1, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD)

        self.wait_label = customtkinter.CTkLabel(self.operation_frame, text="Wait for input")
        self.wait_label.grid(row=3, column=1, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_HALF_Y_PAD)
        self.wait = customtkinter.CTkCheckBox(self.operation_frame, width=1, height=28, text="",
                                              command=self._requires_save)
        self.wait.grid(row=4, column=1, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_HALF_Y_PAD)

        self.position_label = customtkinter.CTkLabel(self.operation_frame, text="Position")
        self.position_label.grid(row=3, column=2, padx=MEDIUM_X_PAD, pady=MEDIUM_HALF_Y_PAD)
        self.position = customtkinter.CTkOptionMenu(self.operation_frame, width=120, height=28,
                                                    command=self._operation_change_event)
        self.position.grid(row=4, column=2, padx=MEDIUM_X_PAD, pady=MEDIUM_HALF_Y_PAD)

        self.linear_velocity_label = customtkinter.CTkLabel(self.operation_frame, text="Linear velocity")
        self.linear_velocity_label.grid(row=6, column=2, padx=MEDIUM_X_PAD, pady=MEDIUM_HALF_Y_PAD)
        self.linear_velocity = CTkFloatSpinbox(self.operation_frame, width=100, height=20, max_value=250.0,
                                               min_value=1.0, step_size=2, command=self._requires_save)
        self.linear_velocity.set(5)
        self.linear_velocity.configure(fg_color=("gray76", "gray23"))
        self.linear_velocity.grid(row=7, column=2, padx=MEDIUM_X_PAD, pady=MEDIUM_Y_PAD)

        self.render()
        self._button_state(new_operation=False, save_operation=False, delete_operation=False, operation_type=False,
                           position=False, wait_input=False, delay=False, linear_velocity=False)
        self.new_operation.configure(state="normal")

    def _requires_save(self):
        if self.save_operation.cget("state") == "disabled":
            self.save_operation.configure(fg_color=BLUE_COLORS, hover_color=BLUE_HOVER)
            return

        if self.selected_task.get() == "" or self.selected_task.get() is None:
            self.save_operation.configure(fg_color=BLUE_COLORS, hover_color=BLUE_HOVER)
            return

        if self.selected_operation.get() == "" or self.selected_operation.get() is None:
            self.save_operation.configure(fg_color=BLUE_COLORS, hover_color=BLUE_HOVER)
            return

        operation = self.robotic_system.get_operation(self.selected_task.get(),
                                                      int(self.selected_operation.get().split(": ")[0]))

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

        if requires_save:
            self.save_operation.configure(fg_color=ORANGE_COLORS, hover_color=ORANGE_HOVER)
        else:
            self.save_operation.configure(fg_color=BLUE_COLORS, hover_color=BLUE_HOVER)

    def render(self):
        # update tasks
        tasks_name_list = self.robotic_system.get_tasks()
        self.selected_task.configure(values=tasks_name_list)
        self.selected_task.set("")

        # update operations
        self.selected_operation.configure(values=[])
        self.selected_operation.set("")
        self.position.configure(values=[])
        self.position.set("")
        self.operation_type.set("")
        self._calculate_state()
        self._requires_save()

    def _render_task(self, task_name: str):
        task_dict = self.robotic_system.get_task_info(task_name)
        self.position.configure(values=task_dict["positions"])
        self.position.set("")

        operations = task_dict["operations"]
        for i in range(len(operations)):
            operations[i] = self._operation_to_str(i, operations[i])

        self.selected_operation.configure(values=operations)
        self.selected_operation.set("")
        self._calculate_state()
        self._requires_save()

    def _button_state(self, new_operation, save_operation, delete_operation, operation_type, position, wait_input,
                      delay, linear_velocity):

        self.new_operation.configure(state="normal" if new_operation else "disabled")
        self.save_operation.configure(state="normal" if save_operation else "disabled")
        self.delete_operation.configure(state="normal" if delete_operation else "disabled")

        self.operation_type_label.configure(text_color=['gray10', '#DCE4EE'] if operation_type else ["#888888",
                                                                                                     "#777777"])
        self.position_label.configure(text_color=['gray10', '#DCE4EE'] if position else ["#888888", "#777777"])
        self.wait_label.configure(text_color=['gray10', '#DCE4EE'] if wait_input else ["#888888", "#777777"])

        self.delay_label.configure(text_color=['gray10', '#DCE4EE'] if delay else ["#888888", "#777777"])
        self.linear_velocity_label.configure(text_color=['gray10', '#DCE4EE'] if linear_velocity else ["#888888",
                                                                                                       "#777777"])

    def _operation_to_str(self, i, operation):
        if operation["type"] == "move line":
            suffix = f"move to {operation['position']}"
        else:
            suffix = operation["type"]

        return f"{i}: {suffix}"

    def _calculate_state(self):
        if self.selected_task.get() == "":
            self._button_state(new_operation=False, save_operation=False, delete_operation=False, operation_type=False,
                               position=False, wait_input=False, delay=False, linear_velocity=False)
        elif self.selected_operation.get() == "":
            self._button_state(new_operation=True, save_operation=False, delete_operation=False, operation_type=False,
                               position=False, wait_input=False, delay=False, linear_velocity=False)
        else:
            operation_type = self.operation_type.get()
            if operation_type == "open" or operation_type == "close" or operation_type == "hand-guide":
                self._button_state(new_operation=True, save_operation=True, delete_operation=True,
                                   operation_type=True, position=False, wait_input=True, delay=True,
                                   linear_velocity=False)
            elif operation_type == "move line":
                save = False if self.position.get() == "" or self.position.get() is None else True

                self._button_state(new_operation=True, save_operation=save, delete_operation=True,
                                   operation_type=True, position=True, wait_input=True, delay=True,
                                   linear_velocity=True)

    def _new_operation_event(self):
        self.robotic_system.add_operation(self.selected_task.get())
        operations = self.selected_operation.cget("values")
        if operations:
            new_index = int(operations[-1].split(": ")[0]) + 1
        else:
            new_index = 0
        placeholder = f"{new_index}: Placeholder"
        self.selected_operation.set(placeholder)
        self._render_operation(placeholder)

    def _render_operation(self, operation_str):
        operation_index = int(operation_str.split(": ")[0])
        operation = self.robotic_system.get_operation(self.selected_task.get(), operation_index)
        operations_list = self.selected_operation.cget("values")
        operation_str = self._operation_to_str(operation_index, operation)
        if operation_index == len(operations_list):
            operations_list.append(operation_str)
        else:
            operations_list[operation_index] = operation_str
        self.selected_operation.configure(values=operations_list)
        self.selected_operation.set(operation_str)

        self.operation_type.set(operation["type"])
        if "position" in operation:
            self.position.set(operation["position"])
        else:
            positions = self.position.cget("values")
            if positions:
                self.position.set(positions[0])
            else:
                self.position.set("")

        if "wait" in operation:
            if operation["wait"]:
                self.wait.select()
            else:
                self.wait.deselect()
        else:
            self.wait.deselect()

        self.delay.set(operation["delay"] if "delay" in operation else 0)
        self.linear_velocity.set(operation["linear_velocity"] if "linear_velocity" in operation else 5)
        self._calculate_state()
        self._requires_save()

    def _save_operation(self):
        operation_index = self.selected_operation.get().split(": ")[0]
        operation_type = self.operation_type.get()
        cur_delay = self.delay.get()
        cur_lin_vel = self.linear_velocity.get()
        if operation_type == "open" or operation_type == "close":
            try:
                if cur_delay is not None:
                    self.robotic_system.update_operation(self.selected_task.get(), index=int(operation_index),
                                                         operation_type=operation_type,
                                                         wait_input=bool(self.wait.get()),
                                                         delay=cur_delay)
            except ValueError as e:
                self.message_display.display_message(e)

        elif operation_type == "hand-guide":
            print(self.robot_tool.get())
            try:
                if cur_delay is not None:
                    self.robotic_system.update_operation(self.selected_task.get(), index=int(operation_index),
                                                         operation_type=operation_type,
                                                         wait_input=bool(self.wait.get()),
                                                         delay=cur_delay, tool=self.robot_tool.get())

            except ValueError as e:
                self.message_display.display_message(e)
        elif operation_type == "move line":
            try:
                if cur_delay is not None and cur_lin_vel is not None:
                    self.robotic_system.update_operation(self.selected_task.get(), index=int(operation_index),
                                                         position=self.position.get(), operation_type=operation_type,
                                                         wait_input=bool(self.wait.get()), delay=cur_delay,
                                                         linear_velocity=cur_lin_vel)
            except ValueError as e:
                self.message_display.display_message(e)

        self._render_operation(self.selected_operation.get())
        self.save_operation.configure(fg_color=BLUE_COLORS, hover_color=BLUE_HOVER)

    def _operation_change_event(self, operation_type: str):
        self._calculate_state()
        self._requires_save()

    def _delete_operation(self):
        operation_str = self.selected_operation.get()
        if operation_str == "":
            return

        operation_index = int(operation_str.split(": ")[0])
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
        self.grid_rowconfigure((2, 5, 7, 9), weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.selected_task_label = customtkinter.CTkLabel(self, text="Task")
        self.selected_task_label.grid(row=0, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_HALF_Y_PAD)
        self.selected_task = customtkinter.CTkOptionMenu(self, width=120, height=28, values=[""],
                                                         command=self._render_task)
        self.selected_task.grid(row=1, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_Y_PAD)

        self.selected_position_label = customtkinter.CTkLabel(self, text="Position")
        self.selected_position_label.grid(row=3, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_HALF_Y_PAD)
        self.selected_position = customtkinter.CTkOptionMenu(self, width=120, height=28, values=[""],
                                                             command=self._render_position)
        self.selected_position.grid(row=4, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_Y_PAD)

        self.new_position = customtkinter.CTkButton(self, width=120, height=28, text="New position",
                                                    command=self._new_position_event)
        self.new_position.grid(row=6, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_Y_PAD)

        self.update_position = customtkinter.CTkButton(self, width=120, height=28, text="Update position",
                                                       command=self._update_position_event)
        self.update_position.grid(row=8, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_Y_PAD)

        self.delete_position = customtkinter.CTkButton(self, width=120, height=28,
                                                       text="Delete position", command=self._delete_position_event)
        self.delete_position.grid(row=10, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_Y_PAD)

        self.labels_frame = customtkinter.CTkFrame(self)
        self.labels_frame.grid(row=0, rowspan=11, column=1, padx=MEDIUM_X_PAD, pady=SMALL_Y_PAD, sticky="nsew")
        self.labels_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        self.labels_frame.grid_columnconfigure((0, 3, 6), weight=1)

        self.joint_labels = []
        self.joints = []
        for i in range(7):
            self.joint_labels.append(customtkinter.CTkLabel(self.labels_frame, text=f"Joint {i}: "))
            self.joint_labels[i].grid(row=i, column=1, padx=SMALL_HALF_X_PAD, pady=SMALL_Y_PAD)
            self.joints.append(customtkinter.CTkLabel(self.labels_frame, width=50, height=30, text="0.0",
                                                      fg_color=("#ebebeb", "#3d3d3d"), corner_radius=5))
            self.joints[i].grid(row=i, column=2, padx=SMALL_HALF_X_PAD, pady=SMALL_Y_PAD)

        self.coord_labels = []
        self.coords = []
        for i, letter in enumerate(["X", "Y", "Z", "A", "B", "C"]):
            self.coord_labels.append(customtkinter.CTkLabel(self.labels_frame, text=f"{letter}: "))
            self.coord_labels[i].grid(row=i, column=4, padx=SMALL_HALF_X_PAD, pady=SMALL_Y_PAD)
            self.coords.append(customtkinter.CTkLabel(self.labels_frame, width=50, height=35, text="0.0",
                                                      fg_color=("#ebebeb", "#3d3d3d"), corner_radius=5))
            self.coords[i].grid(row=i, column=5, padx=SMALL_X_PAD, pady=SMALL_Y_PAD)

        self.go_to = customtkinter.CTkButton(self.labels_frame, width=80, height=28,
                                                       text="Go to", command=self._go_to_point)
        self.go_to.grid(row=6, column=4, columnspan=2, padx=SMALL_X_PAD, pady=SMALL_Y_PAD)

    def render(self):
        # update tasks
        tasks_name_list = self.robotic_system.get_tasks()
        self.selected_task.configure(values=tasks_name_list)
        self.selected_task.set("")

        # update position
        self.selected_position.configure(values=[])
        self.selected_position.set("")

        for joint in self.joints:
            joint.configure(text="0.0")
        for coord in self.coords:
            coord.configure(text="0.0")

        self._calculate_state()

    def _render_task(self, task_name):
        positions = self.robotic_system.get_position_names(task_name)
        self.selected_position.configure(values=positions)
        self._calculate_state()

    def _render_position(self, position_name):
        try:
            position = self.robotic_system.get_position(self.selected_task.get(), position_name)
        except ValueError as e:
            self.message_display.display_message(e)
            return
        self._update_labels(position["joints"], position["cartesian"])
        self._calculate_state()

    def _delete_position_event(self):
        try:
            self.robotic_system.delete_position(self.selected_task.get(), self.selected_position.get())
        except ValueError as e:
            self.message_display.display_message(e)
            return
        self.selected_position.set("")
        self._render_task(self.selected_task.get())

    def _update_position_event(self):
        if not self.robotic_system.is_robot_connected():
            self.message_display.display_message("Robot communication has not been established")
            return
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
        self._render_position(self.selected_position.get())

    def _new_position_event(self):
        if not self.robotic_system.is_robot_connected():
            self.message_display.display_message("Robot communication has not been established")
            return
        dialog = customtkinter.CTkInputDialog(text="Type in a name:", title="New position")
        position_name = dialog.get_input()
        try:
            cartesian, joints = self.robotic_system.get_robot_position()
            position_name = self.robotic_system.add_position(self.selected_task.get(), position_name, cartesian, joints)
        except OSError as e:
            self.message_display.display_message(e)
            return
        except ValueError as e:
            self.message_display.display_message(e)
            return
        self.selected_position.set(position_name)
        self._render_task(self.selected_task.get())
        self._render_position(self.selected_position.get())

    def _calculate_state(self):
        if self.selected_task.get() == "":
            self._set_button_state(new_position=False, update_delete_position=False)
        elif self.selected_position.get() == "":
            self._set_button_state(new_position=True, update_delete_position=False)
        else:
            self._set_button_state(new_position=True, update_delete_position=True)

    def _set_button_state(self, new_position: bool, update_delete_position: bool):
        self.new_position.configure(state="normal" if new_position else "disabled")
        self.update_position.configure(state="normal" if update_delete_position else "disabled")
        self.delete_position.configure(state="normal" if update_delete_position else "disabled")
        self.go_to.configure(state="normal" if update_delete_position else "disabled")

    def _update_labels(self, joints: list, coordinates: list):
        for i, joint in enumerate(joints):
            self.joints[i].configure(text=f"{joint:.1f}")
        for i, coord in enumerate(coordinates):
            self.coords[i].configure(text=f"{coord:.1f}")

    def _go_to_point(self):
        if not self.robotic_system.is_robot_connected():
            self.message_display.display_message("Robot communication has not been established")
            return

        if self.selected_task.get() != "" and self.selected_position.get() != "":
            try:
                position = self.robotic_system.get_position(self.selected_task.get(), self.selected_position.get())
                self.robotic_system.move_robot_line(position["cartesian"], [20])

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
        self.task_frames = []
        self.grid_rowconfigure((0, 2, 4, 6, 8, 10, 12), weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.program_frame = customtkinter.CTkFrame(self)
        self.program_frame.grid(row=1, rowspan=11, column=1, padx=MEDIUM_X_PAD, pady=SMALL_Y_PAD, sticky="nsew")

        self.program_frame.grid_columnconfigure((0, 1), weight=1)
        self.program_frame.grid_rowconfigure(3, weight=1)
        self.program_frame.configure(fg_color=("gray76", "gray23"))

        self.new_program = customtkinter.CTkButton(self, width=120, height=28, text="New program",
                                                   command=self._new_program_event)
        self.new_program.grid(row=1, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_Y_PAD)

        self.load_program = customtkinter.CTkButton(self, width=120, height=28, text="Load program",
                                                    command=self._load_program_event)
        self.load_program.grid(row=3, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_Y_PAD)

        self.save_program = customtkinter.CTkButton(self, width=120, height=28, text="Save program",
                                                    command=self._save_program_event)
        self.save_program.grid(row=5, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_Y_PAD)
        self.save_program.configure(state="disabled")

        self.close_program = customtkinter.CTkButton(self, width=120, height=28, text="Close program",
                                                     command=self._close_program_event)
        self.close_program.grid(row=7, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_Y_PAD)
        self.close_program.configure(state="disabled")

        self.run_program = customtkinter.CTkButton(self, width=120, height=28, text="Run program",
                                                   command=self._run_program_event)
        self.run_program.grid(row=9, column=0, padx=MEDIUM_HALF_X_PAD, pady=SMALL_Y_PAD)
        self.run_program.configure(state="disabled")

        self.program_display = CTkProgramBoxList(self.program_frame, self.robotic_system)
        self.program_display.grid(row=3, column=0, columnspan=2, padx=MEDIUM_X_PAD, pady=BIG_Y_PAD, sticky="nsew")
        self.program_name_label = customtkinter.CTkLabel(self.program_frame, text="")
        self.program_name_label.grid(row=0, column=0, columnspan=2, padx=MEDIUM_X_PAD, pady=MEDIUM_HALF_Y_PAD)

        self.available_tasks = customtkinter.CTkOptionMenu(self.program_frame, width=120, height=28, values=[""],
                                                           command=self._selected_task_event)
        self.available_tasks.grid(row=1, column=1, padx=MEDIUM_X_PAD, pady=MEDIUM_HALF_Y_PAD)

        self.add_task_manually = customtkinter.CTkButton(self.program_frame, width=120, height=60,
                                                         text="Add task manually",
                                                         command=self._add_task_manually_event)
        self.add_task_manually.grid(row=1, rowspan=2, column=0, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_HALF_Y_PAD)
        self.add_task_manually.configure(state="disabled")

        self.add_task = customtkinter.CTkButton(self.program_frame, width=120, height=28, text="Add selected task",
                                                command=self._add_task_event)
        self.add_task.grid(row=2, column=1, padx=MEDIUM_X_PAD, pady=MEDIUM_HALF_Y_PAD)
        self.add_task.configure(state="disabled")

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

    def _load_program_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type program name:", title="Load program")
        program_name = dialog.get_input()
        if program_name is not None:
            try:
                program_name = self.robotic_system.load_program(program_name)
            except ValueError as e:
                self.message_display.display_message(e)
                return
            except FileNotFoundError as e:
                self.message_display.display_message(e)
                return

            self._render_program(program_name)
            self._update_info()

    def _new_program_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a name:", title="New program")
        program_name = dialog.get_input()
        if program_name is not None:
            if self.robotic_system.exists_program_file(program_name):
                ok_cancel = CTkOkCancel(text="A file with this name already exists. \n"
                                             "Do you wish to override it?",
                                        title="Override previous file", first_button="Yes", second_button="Cancel")
                if not ok_cancel.get_input():
                    return
            try:
                program_name = self.robotic_system.add_program(program_name)
            except ValueError as e:
                self.message_display.display_message(e)
                return
            except FileNotFoundError as e:
                self.message_display.display_message(e)
                return

            self._render_program(program_name)

    def _close_program_event(self):
        ok_cancel = CTkOkCancel(text="Do you want to close the program?", title="Close program", first_button="Yes")
        if ok_cancel.get_input():
            try:
                self.robotic_system.close_program()
            except ValueError as e:
                self.message_display.display_message(e)
                return

            self.program_name_label.configure(text="")
            self.program_display.reset()
            self.program_frame.configure(border_color=('gray81', 'gray20'))
            self._calculate_state()

    def _run_program_event(self):
        if self.robotic_system.is_robot_connected():
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
            self._update_info()
        else:
            self.message_display.display_message("There is no open connection")

    def _render_program(self, program_name: str):
        self.program_name_label.configure(text=program_name)
        self._calculate_state()

    def _calculate_state(self):
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
        tasks = self.robotic_system.get_tasks()
        self.available_tasks.configure(values=tasks)
        self.available_tasks.set("")
        self._calculate_state()
        if self.robotic_system.is_program_open():
            self._update_info()

    def _update_info(self):
        while self.task_frames:
            task_frame = self.task_frames.pop()
            task_frame.destroy()

        tasks, states = self.robotic_system.get_tasks_and_states_from_program()
        for task, state in zip(tasks, states):
            self.task_frames.append(self._create_frame_task_state(self.program_display, task, state))

        self.program_display.update_elements(self.task_frames)

    def _add_task_manually_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in the task name:", title="Add task")
        task_name = dialog.get_input()
        if task_name:
            self._add_task_to_program(task_name)

    def _add_task_event(self):
        self._add_task_to_program(self.available_tasks.get())

    def _add_task_to_program(self, task_name: str):
        try:
            task_name, state = self.robotic_system.add_task_to_program(task_name)
        except ValueError as e:
            self.message_display.display_message(e)
            return

        frame = self._create_frame_task_state(self.program_display, task_name, state)
        self.program_display.insert_element(frame)

    def _save_program_event(self):
        try:
            self.robotic_system.save_program()
        except ValueError as e:
            self.message_display.display_message(e)
            return

    def _create_frame_task_state(self, frame_parent, task: str, state: int) -> \
            customtkinter.CTkFrame:
        new_frame = customtkinter.CTkFrame(frame_parent, height=28, width=200)
        new_frame.grid_columnconfigure(1, weight=1)
        new_frame.grid_rowconfigure(0, weight=1)
        state_label = customtkinter.CTkLabel(new_frame, text="", width=20, height=20, corner_radius=10)
        if state == 0:
            state_label.configure(fg_color=GREEN_COLORS)
        elif state == 1:
            state_label.configure(fg_color=ORANGE_COLORS)
        elif state == 2:
            state_label.configure(fg_color=RED_COLORS)

        task_name_label = customtkinter.CTkLabel(new_frame, text=task, anchor="w")
        state_label.grid(row=0, column=0, padx=SMALL_HALF_X_PAD, pady=SMALL_Y_PAD)
        task_name_label.grid(row=0, column=1, padx=SMALL_X_PAD, pady=SMALL_Y_PAD, sticky="nsew")

        return new_frame

    def _selected_task_event(self, task_name):
        self._calculate_state()


# Tab with the multiple interfaces to control the robot and edit tasks, operations and positions
class CTkTabViewer(customtkinter.CTkFrame):
    def __init__(self, master, robotic_system: RoboticSystem, message_display: CTkMessageDisplay):
        super().__init__(master)

        self.robotic_system = robotic_system
        self.message_display = message_display

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.tabview = customtkinter.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=MEDIUM_X_PAD, pady=BIG_Y_PAD, sticky="nsew")
        self.tabview.add("Manage tasks")
        self.tabview.add("Manage operations")
        self.tabview.add("Manage positions")
        self.tabview.add("Program")

        self.tabview.tab("Manage tasks").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Manage tasks").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Manage operations").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Manage operations").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Manage positions").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Manage positions").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Program").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Program").grid_columnconfigure(0, weight=1)

        self.task_manager = CTkTaskManager(self.tabview.tab("Manage tasks"), self.robotic_system, self.message_display)
        self.task_manager.configure(fg_color="transparent")
        self.task_manager.grid(row=0, column=0, padx=MEDIUM_X_PAD, pady=MEDIUM_Y_PAD, sticky="nsew")

        self.operation_manager = CTkOperationManager(self.tabview.tab("Manage operations"), self.robotic_system,
                                                     self.message_display)
        self.operation_manager.configure(fg_color="transparent")
        self.operation_manager.grid(row=0, column=0, padx=MEDIUM_X_PAD, pady=MEDIUM_Y_PAD, sticky="nsew")

        self.position_manager = CTkPositionManager(self.tabview.tab("Manage positions"), self.robotic_system,
                                                   self.message_display)
        self.position_manager.configure(fg_color="transparent")
        self.position_manager.grid(row=0, column=0, padx=MEDIUM_X_PAD, pady=MEDIUM_Y_PAD, sticky="nsew")

        self.program_manager = CTkProgramManager(self.tabview.tab("Program"), self.robotic_system, self.message_display)
        self.program_manager.configure(fg_color="transparent")
        self.program_manager.grid(row=0, column=0, padx=MEDIUM_X_PAD, pady=MEDIUM_Y_PAD, sticky="nsew")

        self.tabview.configure(command=self.render)

    def render(self):
        if self.tabview.get() == "Manage tasks":
            self.task_manager.render()
        elif self.tabview.get() == "Manage operations":
            self.operation_manager.render()
        elif self.tabview.get() == "Manage positions":
            self.position_manager.render()
        elif self.tabview.get() == "Program":
            self.program_manager.render()
