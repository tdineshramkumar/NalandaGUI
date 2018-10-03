from tkinter import *
import os   # to check if file exists
from PIL import ImageTk, Image  # to view captcha
from view.basicapplicationgui import BasicApplicationGUI


class AuthenticationWindow(BasicApplicationGUI):
    """
        Extends BasicApplicationGUI to provide Login functionality.
        Optional View of Captcha ( To Display When Required )
    """
    def __initialize_variables__(self):
        self.username_variable = StringVar()
        self.password_variable = StringVar()
        self.captcha_variable = StringVar()
        self.captcha_enabled = False

    def __initialize_gui__(self):
        Label(self.window, text='Username:').grid(row=0, sticky='W')
        Label(self.window, text='Password:').grid(row=1, sticky='W')
        Entry(self.window, textvariable=self.username_variable, bd=5, relief=SUNKEN, width=30)\
            .grid(row=0, columnspan=3, column=1)
        Entry(self.window, textvariable=self.password_variable, show='*', bd=5, relief=SUNKEN, width=30)\
            .grid(row=1, columnspan=3, column=1)
        self.submit_button = Button(self.window, text='Submit', bd=5, relief=RAISED, width=10)
        self.submit_button.grid(row=10, sticky=E, columnspan=4)

        self.captcha_image = Label(self.window, bd=5, relief=RAISED)
        self.captcha_entry = Entry(self.window, textvariable=self.captcha_variable,  bd=5, relief=SUNKEN)
        self.captcha_button = Button(self.window, text='[R]', bd=2, relief=RAISED)

        # Attach the status bar
        self.busy_status.grid(row=15, column=3, sticky=EW)
        self.status_bar.grid(row=15, column=0, columnspan=3, sticky=EW)
        self.update_status('Enter Nalanda Login Details.')
        self.window.title('Authentication Window')

    def view_captcha(self, captcha_file_name):

        assert isinstance(captcha_file_name, str)   # check if string
        assert os.path.exists(captcha_file_name)    # check if file exists
        self.captcha_enabled = True
        captcha = ImageTk.PhotoImage(Image.open(captcha_file_name))     # Read the captcha image
        self.captcha_image.configure(image=captcha)     # Update the image
        self.captcha_image.photo = captcha              # Update the image ?
        self.captcha_image.grid(row=2, column=1, columnspan=2, rowspan=5)
        self.captcha_entry.grid(row=7, columnspan=1, column=1)
        self.captcha_button.grid(row=7, column=2)

    def remove_captcha(self):
        self.captcha_enabled = False
        self.captcha_image.grid_forget()
        self.captcha_button.grid_forget()
        self.captcha_entry.grid_forget()


    def is_captcha_enabled(self):
        return self.captcha_enabled

    def set_submit_button_command(self, action):
        assert callable(action)
        self.submit_button.configure(command=action)

    def set_captcha_button_command(self, action):
        assert callable(action)
        self.captcha_button.configure(command=action)

    def get_username(self):
        return self.username_variable.get()

    def get_password(self):
        return self.password_variable.get()

    def get_captcha(self):
        return self.captcha_variable.get()
