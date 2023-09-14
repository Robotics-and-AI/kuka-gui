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
    def __init__(self):
        super().__init__()

        self.robot = RobotCommunication()
        self.task_data = TaskData("task_data")
        self.program_data = ProgramData("program_data")
        self.robotic_system = RoboticSystem(self.robot, self.task_data, self.program_data)
        self.message_display = CTkMessageDisplay(self)

        # configure window
        self.title("Kuka iiwa GUI")
        self.geometry(f"{1150}x{600}")

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

        if self.robot.is_connected():
            self.robot.stop_connection()
        super().destroy()

        """
        vcmd = (self.register(self.validate_float),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.title('Control iiwa remotely from external PC')
        self.minsize(width=1000, height=350)  # TODO - check real values
        self.maxsize(width=1500, height=700)  # TODO - check real values

        # Make the interface
        self.IP_of_robot = tk.StringVar()
        self.stateMessage = tk.StringVar()
        self.connection_state = False
        self.weight_of_tool = 17.89
        self.centre_of_mass = [0, 0, 105]
        self.jText = [tk.StringVar() for x in range(7)]
        self.dText = [tk.StringVar() for x in range(6)]
        self.commandsList = []
        self.commandsAngleList = []
        self.iiwa = None
        self.positions = None
        self.position_names = None
        self.shuffle_amount = tk.StringVar()
        self.shuffle_velocity = tk.StringVar()
        self.movement_type = [
            ("Line", 0),
            ("Hand guide", 1),
            ("Wait", 2),
            ("Open gripper", 3),
            ("Close gripper", 4)
        ]
        self.movement_type_selected = tk.IntVar()
        self.movement_type_selected.set(self.movement_type[0][1])
        self.resume = True

        button_height = 2
        button_width = 15

        # Add the STATE MESSAGE textbox
        tk.Label(self, text="Msg: ").grid(row=8, column=0, sticky=tk.W)
        self.msgTxt = tk.Label(self, textvariable=self.stateMessage, width="40", anchor="w")
        self.msgTxt.grid(row=8, column=1, columnspan=4, rowspan=1, sticky=tk.W)
        self.stateMessage.set("Not connected")

        "row 0"
        tk.Label(self, text="Joint").grid(row=0)
        tk.Label(self, text="Angle (Degree)").grid(row=0, column=1)
        tk.Label(self, text="Cartesian coordinates").grid(row=0, column=2, columnspan=2)

        "column 0 and 1"
        for i in range(7):
            label_name = "J" + str(i)
            tk.Label(self, text=label_name).grid(row=i + 1, column=0)
            tk.Label(self, justify='center', textvariable=self.jText[i], width=13).grid(row=i + 1, column=1)
            self.jText[i].set("0.0")

        "column 2 and 3"
        cartesian = ["X", "Y", "Z", "A", "B", "C"]
        for i in range(len(cartesian)):
            label_name = cartesian[i]
            tk.Label(self, text=label_name).grid(row=i + 1, column=2)
            tk.Label(self, justify='center', textvariable=self.dText[i], width=13).grid(row=i + 1, column=3)
            self.dText[i].set("0.0")

        "column 4 and 5"
        tk.Button(self, text="X+", command=lambda: self.shuffle_cartesian(0, True), height=button_height,
                  width=5).grid(
            row=1, column=4)
        tk.Button(self, text="X-", command=lambda: self.shuffle_cartesian(0, False), height=button_height,
                  width=5).grid(
            row=1, column=5)
        tk.Button(self, text="Y+", command=lambda: self.shuffle_cartesian(1, True), height=button_height,
                  width=5).grid(
            row=2, column=4)
        tk.Button(self, text="Y-", command=lambda: self.shuffle_cartesian(1, False), height=button_height,
                  width=5).grid(
            row=2, column=5)
        tk.Button(self, text="Z+", command=lambda: self.shuffle_cartesian(2, True), height=button_height,
                  width=5).grid(
            row=3, column=4)
        tk.Button(self, text="Z-", command=lambda: self.shuffle_cartesian(2, False), height=button_height,
                  width=5).grid(
            row=3, column=5)

        tk.Label(self, text="Amount [mm]:").grid(row=4, column=4)
        tk.Entry(self, textvariable=self.shuffle_amount, width=7, validate="key", validatecommand=vcmd,
                 justify="center").grid(row=4, column=5)
        self.shuffle_amount.set("0.0")

        tk.Label(self, text="Velocity [mm/s]:").grid(row=5, column=4)
        tk.Entry(self, textvariable=self.shuffle_velocity, width=7, validate="key", validatecommand=vcmd,
                 justify="center").grid(row=5, column=5)
        self.shuffle_velocity.set("0.0")

        self.connect_button = tk.Button(self, text="Connect", command=self.connect_disconnect, height=button_height,
                                        width=button_width)
        self.connect_button.grid(row=6, column=4, columnspan=2)
        tk.Label(self, text="IP:").grid(row=7, column=4)
        tk.Entry(self, textvariable=self.IP_of_robot, width=button_width, justify="center").grid(row=7, column=5)
        self.IP_of_robot.set("172.31.1.147")

        # column 6
        row_num = 1
        tk.Button(self, text="Add point", command=self.add_point, height=button_height,
                  width=button_width).grid(row=row_num, column=6)
        row_num = row_num + 1
        tk.Button(self, text="Delete point", command=self.remove_point, height=button_height,
                  width=button_width).grid(row=row_num, column=6)
        row_num = row_num + 1
        tk.Button(self, text="Add movement", command=self.add_movement, height=button_height,
                  width=button_width).grid(row=row_num, column=6)
        row_num = row_num + 1
        tk.Button(self, text="Delete movement", command=self.remove_movement, height=button_height,
                  width=button_width).grid(row=row_num, column=6)
        row_num = row_num + 1
        tk.Button(self, text="Run program", command=self.run_program, height=button_height,
                  width=button_width).grid(row=row_num, column=6)
        row_num = row_num + 1
        tk.Button(self, text="Home", command=self.move_home, height=button_height,
                  width=button_width).grid(
            row=row_num, column=6)

        # column 7
        row = 1
        for txt, val in self.movement_type:
            tk.Radiobutton(self, text=txt, variable=self.movement_type_selected, value=val) \
                .grid(row=row, column=7, sticky="w")
            row += 1

        # column 8 through 11
        tk.Label(self, text="Points").grid(row=1, column=8)
        self.position_names = tk.Listbox(self, height=button_height * 8)
        self.position_names.grid(row=2, column=8, rowspan=5)
        scroll_position = tk.Scrollbar(self)
        scroll_position.grid(row=2, column=9, rowspan=5, sticky='NS')
        self.position_names.config(yscrollcommand = scroll_position.set)
        scroll_position.config(command = self.position_names.yview)
        tk.Label(self, text="Actions").grid(row=1, column=10)
        self.movement_commands = tk.Listbox(self, height=button_height * 8)
        self.movement_commands.grid(row=2, column=10, rowspan=5)
        scroll_movement = tk.Scrollbar(self)
        scroll_movement.grid(row=2, column=11, rowspan=5, sticky='NS')
        self.movement_commands.config(yscrollcommand=scroll_movement.set)
        scroll_movement.config(command=self.movement_commands.yview)

        # column 12
        self.connect_lidar_button = tk.Button(self, text="Connect lidar", command=self.connect_disconnect_lidar,
                                              height=button_height, width=button_width)
        self.connect_lidar_button.grid(row=1, column=12)
        tk.Button(self, text="Connect lidar", command=self.start_stop_measuring,
                  height=button_height, width=button_width).grid(row=2, column=12)

        self.protocol("WM_DELETE_WINDOW", self.close_program)
        try:
            self.mainloop()
        except:
            print('An error happened')
            print('Closing connection if opened')
            if self.connection_state:
                self.connect_disconnect()
    """

    """
    def close_program(self):
        if not self.connection_state:
            self.destroy()
        else:
            self.connect_disconnect()
            self.destroy()

    def connect_disconnect(self):
        # Check if already connected to the robot
        if self.connection_state:
            # If made it to here, then there is an active connection
            message = "Disconnecting from robot"
            self.print_message(message)
            # Try to disconnect
            try:
                self.iiwa.close()
                self.connection_state = False
                message = "Disconnected successfully"
                self.print_message(message)
                self.connect_button.config(text="Connect")
            except:
                message = "Error could not disconnect"
                self.print_message(message)
                return
        else:
            # If the program made it to here, then there is no connection yet
            message = "Connecting to robot at ip: " + self.IP_of_robot.get()
            self.print_message(message, '#00ff00')
            sleep(0.1)
            try:
                self.iiwa = iiwaPy3.iiwaPy3(self.IP_of_robot.get())
                self.update_position()
                self.connection_state = True
                message = "Connection established successfully"
                self.print_message(message, '#0000ff')
                self.connect_button.config(text="Disconnect")
            except:
                message = "Error, could not connect at the specified IP"
                self.print_message(message, '#ff0000')
                return

    def connect_disconnect_lidar(self):
        # Check if already connected to the lidar
        if self.lidar.is_connected:
            # If made it to here, then there is an active connection
            message = "Disconnecting from lidar"
            self.print_message(message)
            self.lidar.disconnect()
            message = "Disconnected from lidar"
            self.print_message(message)
            self.connect_lidar_button.config(text="Connect")
        else:
            # If the program made it to here, then there is no connection yet
            message = "Connecting to lidar at ip: " + self.lidar.ip
            self.print_message(message, '#00ff00')
            sleep(0.1)
            self.lidar.connect()
            if self.lidar.is_connected:
                self.connect_lidar_button.config(text="Disconnect")

    def start_stop_measuring(self):
        # Check if already connected to the lidar
        if self.lidar.is_connected:
            if self.lidar.measure:
                # If made it to here, then there is an active connection
                message = "Stopping measurements"
                self.print_message(message)
                self.lidar.stop_measurements()
                sleep(0.2)
                if not self.lidar.measuring:
                    message = "Measurements stopped"
                    self.print_message(message)
                    self.connect_lidar_button.config(text="Start measurements")
            else:
                # If the program made it to here, then there is no connection yet
                message = "Starting measurements"
                self.print_message(message)
                sleep(0.2)
                if self.lidar.measuring:
                    message = "Measurements started"
                    self.print_message(message)
                    self.connect_lidar_button.config(text="Stop measurements")

    def move_home(self):
        # Check if there is an active connection
        if self.check_connection():
            rel_vel = [0.1]
            self.iiwa.movePTPHomeJointSpace(rel_vel)
            self.update_position()

    def shuffle_cartesian(self, axis, positive):
        # Check if there is an active connection
        if self.check_connection():
            velocity = [float(self.shuffle_velocity.get())]
            pos = [0.0, 0.0, 0.0]
            if positive:
                pos[axis] += float(self.shuffle_amount.get())
            else:
                pos[axis] -= float(self.shuffle_amount.get())

            if velocity[0] < 0.1 or float(self.shuffle_amount.get()) < 0.1:
                self.print_message("Velocity and shuffle amount must be greater than zero")
            else:
                print(f"Shuffle command {pos} with velocity {velocity}")
                self.iiwa.movePTPLineEefRelBase(pos, velocity)
                self.update_position()

    def run_program(self):
        # Check if there is an active connection
        if self.check_connection():
            for movement in self.movement_commands.get(0, "end"):
                sleep(0.1)
                if movement.startswith("line"):
                    movement = movement.split("_")
                    index = self.position_names.get(0, "end").index(movement[1])
                    self.iiwa.movePTPLineEEF(self.positions[index].tolist(), [float(movement[2])])
                elif movement.startswith("handguide"):
                    self.iiwa.preciseHandGuiding(weight_tool=self.weight_of_tool, centre_mass=self.centre_of_mass)
                elif movement.startswith("open"):
                    self.iiwa.setPin1Off()
                    sleep(0.1)
                    self.iiwa.setPin11On()
                elif movement.startswith("close"):
                    self.iiwa.setPin11Off()
                    sleep(0.1)
                    self.iiwa.setPin1On()
                    sleep(0.3)
                elif movement.startswith("wait"):
                    ans = messagebox.showinfo("Waiting for human", "Press OK when ready to continue program!")
            self.print_message("")
            self.update_position()

    def add_point(self):
        # Check if there is an active connection
        if self.check_connection():
            try:
                cpos = self.iiwa.getEEFPos()

                answer = simpledialog.askstring("Add point", "Point name?",
                                                parent=self)
                if answer is None or answer.strip() == "":
                    self.print_message("Input a non empty string")
                else:
                    self.position_names.insert("end", answer.strip())
                    if self.positions is None:
                        self.positions = np.array([cpos])
                    else:
                        self.positions = np.append(self.positions, [cpos], axis=0)
                    self.print_message("")
            except:
                self.print_message("Could not obtain current position")

    def remove_point(self):
        # Check if there is an active connection
        if self.check_connection():
            if len(self.position_names.curselection()) == 1:
                index = self.position_names.curselection()[0]
                position = self.position_names.get(index)
                if not self.check_point_in_program(position):
                    self.position_names.delete(index)
                    self.positions = np.delete(self.positions, index, 0)
                    self.print_message("")
                else:
                    self.print_message("Position in program! Delete related movements first")
            else:
                self.print_message("No point selected")

    def add_movement(self):
        # Check if there is an active connection
        if self.check_connection():
            if self.movement_type_selected.get() == 0:
                if len(self.position_names.curselection()) == 1:
                    answer = simpledialog.askfloat("Add movement", "Robot velocity?", parent=self)
                    if answer > 0.1:
                        if len(self.position_names.curselection()) != 0:
                            self.movement_commands.\
                                insert("end", f"line_{self.position_names.get(self.position_names.curselection()[0])}_"
                                              f"{answer}")
                            self.print_message("")
                    else:
                        self.print_message("Add a positive velocity")
                else:
                    self.print_message("Select one target position")
            elif self.movement_type_selected.get() == 1:
                self.movement_commands.insert("end", "handguide")
                self.print_message("")
            elif self.movement_type_selected.get() == 2:
                self.movement_commands.insert("end", "wait")
                self.print_message("")
            elif self.movement_type_selected.get() == 3:
                self.movement_commands.insert("end", "open")
                self.print_message("")
            elif self.movement_type_selected.get() == 4:
                self.movement_commands.insert("end", "close")
                self.print_message("")
            else:
                self.print_message("Such command has not been implemented!")

    def remove_movement(self):
        # Check if there is an active connection
        if self.check_connection():
            if len(self.movement_commands.curselection()) == 1:
                index = self.movement_commands.curselection()[0]
                self.movement_commands.delete(index)
                self.print_message("")
            else:
                self.print_message("Select movement to delete")

    def print_message(self, message, color='#000000'):
        # print message
        self.stateMessage.set(message)
        self.msgTxt.config(fg=color)

    def update_position(self):
        joint_pos = self.iiwa.getJointsPos()
        for i in range(7):
            temp = joint_pos[i] * 180 / math.pi
            self.jText[i].set("{:.2f}".format(temp) + " º")
        cart_pos = self.iiwa.getEEFPos()
        for i in range(6):
            if i < 3:
                self.dText[i].set("{:.2f}".format(cart_pos[i]) + " mm")
            else:
                self.dText[i].set("{:.2f}".format(cart_pos[i] * 180 / math.pi) + " º")

    def validate_float(self, d, i, P, s, S, v, V, W):
        if P == "":
            return True
        else:
            try:
                float(P)
                return True
            except:
                return False

    def check_connection(self):
        if not self.connection_state:
            message = "Error, connect first"
            self.print_message(message)
            return False
        else:
            return True

    def check_point_in_program(self, position):
        for movement in self.movement_commands.get(0, "end"):
            if movement.startswith("line"):
                if movement.split("_")[1] == position:
                    return True
        return False
    """


if __name__ == '__main__':
    app = App()
    app.mainloop()
