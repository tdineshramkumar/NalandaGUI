from tkinter import messagebox
from tkinter import *

__AUTHOR__ = 'attachmentdownloadernalanda@gmail.com'
ABOUT_STRING = 'Downloads Attachments from Nalanda BITS Pilani. ' \
                   'Contact "{}" for Bug Reports or Suggestions.'.format(__AUTHOR__)
HELP_STRING = 'Enable Less Secure Apps in G-Mail to use this Application.'


class BasicApplicationGUI:
    """
        Creates a Base GUI for other Compound Widgets.
        Creates a menu bar with submenu and a status bar (not packed)
        It provides facility to update the status bar
        extend __initialize_variables__, __initialize_gui__ to add GUI functionality
    """
    def __init__(self):
        """
            Calls various initializing methods.
            Note: you need to manually start the mainloop after setting up the controller and model
        """
        self.window = Tk()      # The main window
        self.__initialize_variables__()     # Initialize the variables
        self.__initialize_menu__()      # Initialize the Menu
        self.__initialize_status_bar__()
        self.__initialize_gui__()   # Initialize the GUI widgets

    def __initialize_variables__(self):
        pass

    def __initialize_menu__(self):
        # Define Main Menu
        self.main_menu = Menu(self.window)
        self.window.config(menu=self.main_menu)

        # Define Sub-menu(s)
        file_submenu = Menu(self.main_menu)
        file_submenu.add_command(label='Quit', command=self.__close__)

        help_submenu = Menu(self.main_menu)
        help_submenu.add_command(label='About', command=self.showinfo('About', ABOUT_STRING))
        help_submenu.add_command(label='Help', command=self.showinfo('Help', HELP_STRING))
        # Attach the submenus to main menu
        self.main_menu.add_cascade(label='File', menu=file_submenu)
        self.main_menu.add_cascade(label='Help', menu=help_submenu)

    def __initialize_gui__(self):
        pass

    def __initialize_status_bar__(self):
        # Defining Status Bar for containing Any Notifications
        # NOTE: To Use it You Must Pack it to your layout
        self.status_variable = StringVar()
        self.busy_status_variable = StringVar()
        self.status_bar = Label(self.window, textvariable=self.status_variable, bd=5, relief=SUNKEN, anchor=W)
        self.busy_status = Label(self.window, textvariable=self.busy_status_variable, bd=5, relief=SUNKEN, anchor=E)

    def update_status(self, status):    # Update the status bar
        assert isinstance(status, str)
        self.status_variable.set(status)

    def update_busy_status(self, status):
        self.busy_status_variable.set(value=status)

    def start_mainloop(self):
        self.window.mainloop()

    def __close__(self):
        self.window.quit()

    def __destroy__(self):
        self.window.destroy()

    @staticmethod
    def showinfo(title, message):  # Show info using Message Box
        return lambda: messagebox.showinfo(title, message)
