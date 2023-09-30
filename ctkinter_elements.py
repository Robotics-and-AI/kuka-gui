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

        # label to display messages
        self.message_label = customtkinter.CTkLabel(self, text="", anchor="w")
        self.message_label.grid(row=0, column=0, padx=MEDIUM_HALF_X_PAD, pady=MEDIUM_Y_PAD, sticky="w")

        # button to clear displayed message
        self.clear_button = customtkinter.CTkButton(self, width=28, height=28, text="X",
                                                    command=self._clear_message)
        self.clear_button.grid(row=0, column=1, padx=SMALL_X_PAD, pady=SMALL_Y_PAD, sticky="e")

        # grid layout configure
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _clear_message(self) -> None:
        """
        Clear currently displayed message.
        """

        self.message_label.configure(text="")

    def display_message(self, text) -> None:
        """
        Display given message.

        :param text: message to display
        """

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
    def insert_element(self, element: customtkinter.CTkFrame) -> None:
        """
        Add new element in the box list.

        :param element: element to add
        """

        # append new element, generate buttons to manage it and render it
        self.elements.append(element)
        self._generate_buttons()
        self._render_element(len(self.elements) - 1)

    def _up_event(self, index: int) -> None:
        """
        Swap element with the previous element.

        :param index: index of the element
        """

        if index > 0:
            temp = self.elements[index]
            self.elements[index] = self.elements[index - 1]
            self.elements[index - 1] = temp

            self._render_element(index)
            self._render_element(index - 1)

    def _down_event(self, index: int) -> None:
        """
        Swap element with the next element.

        :param index: index of the element
        """
        if index < len(self.elements) - 1:
            temp = self.elements[index]
            self.elements[index] = self.elements[index + 1]
            self.elements[index + 1] = temp

            self._render_element(index)
            self._render_element(index + 1)

    def delete_element(self, index: int) -> None:
        """
        Delete element with a given index.

        :param index: index of the element to delete
        """

        # destroy buttons of the last element
        self._destroy_buttons()

        # delete element at specified index
        self.elements[index].destroy()
        self.elements.pop(index)

        # re-render elements after the destroyed element
        for shift, element in enumerate(self.elements[index:]):
            self._render_element(index + shift)

    def reset(self) -> None:
        """
        Reset box list. Removes rendered elements and respective buttons.
        """

        # delete all elements
        while self.elements:
            element = self.elements.pop()
            element.destroy()

        # delete all management buttons
        while self.buttons:
            up, down, delete = self.buttons.pop()
            up.destroy()
            down.destroy()
            delete.destroy()

    def update_elements(self, elements: list) -> None:
        """
        Update elements from list of elements.

        :param elements: list of elements to be rendered
        """

        # delete previously rendered elements
        while self.elements:
            element = self.elements.pop()
            element.destroy()

        # render new elements
        for element in elements:
            self.elements.append(element)
            self._render_element(-1)

        # render or destroy management buttons to match number of elements
        while len(self.buttons) != len(self.elements):
            if len(self.buttons) > len(self.elements):
                self._destroy_buttons()
            else:
                self._generate_buttons()

    def _render_element(self, index: int) -> None:
        """
        Render element at given index.

        :param index: index of element to render
        """

        if index == -1:
            index = len(self.elements) - 1
        self.elements[index].grid(row=index, column=0, padx=SMALL_HALF_X_PAD, pady=SMALL_Y_PAD, sticky="nsew")

    def _generate_buttons(self) -> None:
        """
        Generate buttons to manage elements.
        """

        # button to swap element with the previous
        up_button = customtkinter.CTkButton(self, width=28, height=28, text=u"\u2191",
                                            command=lambda ind=len(self.buttons): self._up_event(ind))
        up_button.grid(row=len(self.buttons), column=1, padx=SMALL_HALF_X_PAD, pady=SMALL_Y_PAD)

        # button to swap element with the next
        down_button = customtkinter.CTkButton(self, width=28, height=28, text=u"\u2193",
                                              command=lambda ind=len(self.buttons): self._down_event(ind))
        down_button.grid(row=len(self.buttons), column=2, padx=SMALL_HALF_X_PAD, pady=SMALL_Y_PAD)

        # button to delete element
        delete_button = customtkinter.CTkButton(self, width=28, height=28, text="X", fg_color=RED_COLORS,
                                                hover_color=RED_HOVER,
                                                command=lambda ind=len(self.buttons): self.delete_element(ind))
        delete_button.grid(row=len(self.buttons), column=3, padx=SMALL_X_PAD, pady=SMALL_Y_PAD)
        self.buttons.append((up_button, down_button, delete_button))

    def _destroy_buttons(self) -> None:
        """
        Destroy buttons corresponding to the last index.
        """

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

        self._user_input = None
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

    def _create_widgets(self) -> None:
        """
        Generate widgets for user interaction.
        """

        # configure grid layout
        self.grid_columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)

        # label to display message to the user
        self._label = customtkinter.CTkLabel(master=self,
                                             width=300,
                                             wraplength=300,
                                             fg_color="transparent",
                                             text=self.text)
        self._label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        # button with the first option (accepts or confirms)
        self._ok_button = customtkinter.CTkButton(master=self,
                                                  width=100,
                                                  border_width=0,
                                                  text=self.first_button,
                                                  command=self._ok_event)
        self._ok_button.grid(row=2, column=0, columnspan=1, padx=(20, 10), pady=(0, 20), sticky="ew")

        # button with the second option (cancels or declines)
        self._cancel_button = customtkinter.CTkButton(master=self,
                                                      width=100,
                                                      border_width=0,
                                                      text=self.second_button,
                                                      command=self._cancel_event)
        self._cancel_button.grid(row=2, column=1, columnspan=1, padx=(10, 20), pady=(0, 20), sticky="ew")

    def _ok_event(self) -> None:
        """
        User accepts event.
        """
        self._user_input = True
        self.grab_release()
        self.destroy()

    def _on_closing(self) -> None:
        """
        Window closing event.
        """
        self.grab_release()
        self.destroy()

    def _cancel_event(self) -> None:
        """
        User declines event.
        """
        self._user_input = False
        self.grab_release()
        self.destroy()

    def get_input(self) -> bool:
        """
        Wait for user input.
        """
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

        # configure grid layout
        self.grid_columnconfigure((0, 2), weight=0)  # buttons don't expand
        self.grid_columnconfigure(1, weight=1)  # entry expands

        # button to subtract from entry
        self.subtract_button = customtkinter.CTkButton(self, text="-", width=height - 6, height=height - 6,
                                                       command=self._subtract_button_callback)
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        # entry to display current value
        self.entry = customtkinter.CTkEntry(self, width=width - (2 * height), height=height - 6, border_width=0)
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")
        self.entry.bind("<Return>", lambda e: self._validate_entry())

        # button to add to entry
        self.add_button = customtkinter.CTkButton(self, text="+", width=height - 6, height=height - 6,
                                                  command=self._add_button_callback)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)

        self.entry.insert(0, "0.0")

    def _add_button_callback(self) -> None:
        """
        Add step size to current value.
        """
        try:
            value = float(self.entry.get()) + self.step_size
            self.set(value)
        except ValueError:
            return

    def _subtract_button_callback(self) -> None:
        """
        Remove step size from current value.
        """
        try:
            value = float(self.entry.get()) - self.step_size
            self.set(value)
        except ValueError:
            return

    def get(self) -> float:
        """
        Get current value

        :return: current value
        """
        try:
            return float(self.entry.get())
        except ValueError:
            return self.min_value

    def set(self, value: float) -> None:
        """
        Update value.

        :param value: value to be updated to
        """

        # force value to be between the min value and max value
        value = max(self.min_value, value)
        value = min(value, self.max_value)

        # update value
        self.entry.delete(0, "end")
        self.entry.insert(0, f"{float(value):.1f}")
        if self.command:
            self.command()

    def _validate_entry(self) -> None:
        """
        Validate if entry is a valid positive number.
        """

        value = self.entry.get()
        if value.isnumeric():
            self.set(float(value))
