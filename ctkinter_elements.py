import customtkinter

SMALL_Y_PAD = 5
SMALL_HALF_Y_PAD = (5, 0)
MEDIUM_Y_PAD = 10
MEDIUM_HALF_Y_PAD = (10, 0)
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


# Class to display error messages with a button to clear
class CTkMessageDisplay(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.message_label = customtkinter.CTkLabel(self, text="", anchor="w")
        self.message_label.grid(row=0, column=0, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD, sticky="w")
        self.clear_button = customtkinter.CTkButton(self, width=28, height=28, text="X",
                                                    command=self._clear_message)
        self.clear_button.grid(row=0, column=1, padx=SMALL_X_PAD, pady=SMALL_Y_PAD, sticky="e")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _clear_message(self):
        self.message_label.configure(text="")

    def display_message(self, text):
        self.message_label.configure(text=text)


# Standard Box List with add, delete and swap options. Receives elements of type CTkFrame
class CTkBoxList(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.elements = []
        self.buttons = []
        self.selected_element = None
        self.grid_columnconfigure(0, weight=1)

    # Insert frame element
    def insert_element(self, element: customtkinter.CTkFrame):
        self.elements.append(element)
        self._generate_buttons()
        self._render_element(len(self.elements) - 1)

    def _up_event(self, index):
        if index > 0:
            temp = self.elements[index]
            self.elements[index] = self.elements[index - 1]
            self.elements[index - 1] = temp

            self._render_element(index)
            self._render_element(index - 1)

    def _down_event(self, index):
        if index < len(self.elements) - 1:
            temp = self.elements[index]
            self.elements[index] = self.elements[index + 1]
            self.elements[index + 1] = temp

            self._render_element(index)
            self._render_element(index + 1)

    def delete_element(self, index):
        self._destroy_buttons()
        self.elements[index].destroy()
        self.elements.pop(index)
        for shift, element in enumerate(self.elements[index:]):
            self._render_element(index + shift)

    def reset(self):
        while self.elements:
            element = self.elements.pop()
            element.destroy()

        while self.buttons:
            up, down, delete = self.buttons.pop()
            up.destroy()
            down.destroy()
            delete.destroy()

    def update_elements(self, elements):
        while self.elements:
            element = self.elements.pop()
            element.destroy()

        for element in elements:
            self.elements.append(element)
            self._render_element(-1)

        while len(self.buttons) != len(self.elements):
            if len(self.buttons) > len(self.elements):
                self._destroy_buttons()
            else:
                self._generate_buttons()

    def _render_element(self, index: int):
        if index == -1:
            index = len(self.elements) - 1
        self.elements[index].grid(row=index, column=0, padx=SMALL_HALF_X_PAD, pady=SMALL_Y_PAD, sticky="nsew")

    def _generate_buttons(self):
        up_button = customtkinter.CTkButton(self, width=28, height=28, text=u"\u2191",
                                            command=lambda ind=len(self.buttons): self._up_event(ind))
        up_button.grid(row=len(self.buttons), column=1, padx=SMALL_HALF_X_PAD, pady=SMALL_Y_PAD)
        down_button = customtkinter.CTkButton(self, width=28, height=28, text=u"\u2193",
                                              command=lambda ind=len(self.buttons): self._down_event(ind))
        down_button.grid(row=len(self.buttons), column=2, padx=SMALL_HALF_X_PAD, pady=SMALL_Y_PAD)
        delete_button = customtkinter.CTkButton(self, width=28, height=28, text="X", fg_color=RED_COLORS,
                                                hover_color=RED_HOVER,
                                                command=lambda ind=len(self.buttons): self.delete_element(ind))
        delete_button.grid(row=len(self.buttons), column=3, padx=SMALL_X_PAD, pady=SMALL_Y_PAD)
        self.buttons.append((up_button, down_button, delete_button))

    def _destroy_buttons(self):
        up, down, delete = self.buttons.pop()
        up.destroy()
        down.destroy()
        delete.destroy()


# 2 button input window
class CTkOkCancel(customtkinter.CTkToplevel):

    def __init__(self,
                 title: str = "CTkDialog",
                 text: str = "CTkDialog",
                 first_button: str = "Ok",
                 second_button: str = "Cancel"):
        super().__init__()

        self.user_input = None
        self.running: bool = False
        self.title = title
        self.text = text
        self.first_button = first_button
        self.second_button = second_button

        self.lift()  # lift window on top
        self.attributes("-topmost", True)  # stay on top
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.after(10,
                   self._create_widgets)  # create widgets with slight delay, to avoid white flickering of background
        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable

    def _create_widgets(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)

        self._label = customtkinter.CTkLabel(master=self,
                                             width=300,
                                             wraplength=300,
                                             fg_color="transparent",
                                             text=self.text)
        self._label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self._ok_button = customtkinter.CTkButton(master=self,
                                                  width=100,
                                                  border_width=0,
                                                  text=self.first_button,
                                                  command=self._ok_event)
        self._ok_button.grid(row=2, column=0, columnspan=1, padx=(20, 10), pady=(0, 20), sticky="ew")

        self._cancel_button = customtkinter.CTkButton(master=self,
                                                      width=100,
                                                      border_width=0,
                                                      text=self.second_button,
                                                      command=self._cancel_event)
        self._cancel_button.grid(row=2, column=1, columnspan=1, padx=(10, 20), pady=(0, 20), sticky="ew")

    def _ok_event(self):
        self._user_input = True
        self.grab_release()
        self.destroy()

    def _on_closing(self):
        self.grab_release()
        self.destroy()

    def _cancel_event(self):
        self._user_input = False
        self.grab_release()
        self.destroy()

    def get_input(self):
        self.master.wait_window(self)
        return self._user_input


# Spinbox to select float values
class CTkFloatSpinbox(customtkinter.CTkFrame):
    def __init__(self, *args,
                 width: int = 100,
                 height: int = 32,
                 step_size: float = 5,
                 min_value: float = 0,
                 max_value: float = 100,
                 command: callable = None,
                 **kwargs):

        super().__init__(*args, width=width, height=height, **kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.step_size = step_size
        self.command = command

        self.grid_columnconfigure((0, 2), weight=0)  # buttons don't expand
        self.grid_columnconfigure(1, weight=1)  # entry expands

        self.subtract_button = customtkinter.CTkButton(self, text="-", width=height - 6, height=height - 6,
                                                       command=self._subtract_button_callback)
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        self.entry = customtkinter.CTkEntry(self, width=width - (2 * height), height=height - 6, border_width=0)
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")

        self.add_button = customtkinter.CTkButton(self, text="+", width=height - 6, height=height - 6,
                                                  command=self._add_button_callback)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)

        self.entry.insert(0, "0.0")

    def _add_button_callback(self):
        try:
            value = float(self.entry.get()) + self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, f"{min(value, self.max_value):.1f}")
            if self.command:
                self.command()
        except ValueError:
            return

    def _subtract_button_callback(self):
        try:
            value = float(self.entry.get()) - self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, f"{max(self.min_value, value):.1f}")
            if self.command:
                self.command()
        except ValueError:
            return

    def get(self):
        try:
            return float(self.entry.get())
        except ValueError:
            return None

    def set(self, value: float):
        self.entry.delete(0, "end")
        self.entry.insert(0, f"{float(value):.1f}")
