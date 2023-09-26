# -*- coding: utf-8 -*-
import customtkinter

from program_data import ProgramData
from render_classes import CTkSidebar, CTkTabViewer, CTkRobotConnector, CTkMessageDisplay, CTkOkCancel, \
    CTkMoveRobot
from robot_communication import RobotCommunication
from robotic_system import RoboticSystem
from task_data import TaskData

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

BIG_Y_PAD = 20
BIG_HALF_Y_PAD = (20, 0)

BIG_HALF_X_PAD = (30, 0)
BIG_X_PAD = (30, 30)


class App(customtkinter.CTk):
    def __init__(self, robotic_system: RoboticSystem):
        super().__init__()

        self.robotic_system = robotic_system
        self.message_display = CTkMessageDisplay(self)

        # configure window
        self.title("Kuka iiwa GUI")
        self.geometry(f"{1300}x{600}")

        # configure grid layout (?x?)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.sidebar = CTkSidebar(self)
        self.sidebar.grid(row=0, rowspan=3, column=0, sticky="nswe")

        self.robot_connector = CTkRobotConnector(self, self.robotic_system, self.message_display)
        self.robot_connector.grid(row=0, column=1, padx=BIG_HALF_X_PAD, pady=BIG_HALF_Y_PAD, sticky="nswe")

        self.move_robot = CTkMoveRobot(self, self.robotic_system, self.message_display)
        self.move_robot.grid(row=1, column=1, padx=BIG_HALF_X_PAD, pady=BIG_HALF_Y_PAD, sticky="nsew")

        self.tab_viewer = CTkTabViewer(self, self.robotic_system, self.message_display)
        self.tab_viewer.grid(row=0, rowspan=2, column=2, padx=BIG_X_PAD, pady=BIG_HALF_Y_PAD, sticky="nsew")

        self.message_display.grid(row=2, column=1, columnspan=2, padx=BIG_X_PAD, pady=BIG_Y_PAD, sticky="nsew")

    def destroy(self):
        if not self.robotic_system.is_up_to_date():
            exit_dialog = CTkOkCancel(title="Exit", text="There are unsaved elements. Exit anyway?",
                                      first_button="Yes", second_button="Cancel")
            if not exit_dialog.get_input():
                return

        if self.robotic_system.is_robot_connected():
            self.robotic_system.stop_robot_connection()
        super().destroy()


if __name__ == '__main__':
    robot = RobotCommunication("tools.json")
    task_data = TaskData("task_data")
    program_data = ProgramData("program_data")
    robotic_system = RoboticSystem(robot, task_data, program_data)
    app = App(robotic_system)
    app.mainloop()
