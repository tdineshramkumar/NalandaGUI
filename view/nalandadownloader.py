from tkinter import *
from view.scrollablelistbox import ScrollableListBox
from view.basicapplicationgui import BasicApplicationGUI


class NalandaDownloader(BasicApplicationGUI):
    """
        Extends the BasicApplicationGUI and provides the Main Application GUI or interface to download content
        from nalanda.
    """
    def __initialize_variables__(self):
        self.search_variable = StringVar()  #
        self.attachments_variable = BooleanVar()

    def __initialize_gui__(self):
        # Course Input Frame
        Label(self.window, text='Course').grid(row=0, sticky='W')
        Entry(self.window, textvariable=self.search_variable, bd=5, relief=SUNKEN, width=30)\
            .grid(row=0, column=1, columnspan=2)    # Entry for Search String
        self.search_button = Button(self.window, text=' Submit ', bd=4, relief=RAISED)
        self.search_button.grid(row=0, column=3, columnspan=2, sticky=E)

        # Scrollable List Box for containing list of courses
        self.courses = ScrollableListBox(self.window, bd=2, relief=SUNKEN, selectmode=EXTENDED)
        self.courses.grid(row=1, columnspan=5, rowspan=5, sticky=NSEW)   # Place it in grid
        self.courses.title('New Courses')       # Update the title
        self.courses_listbox = self.courses.listbox_widget
        self.courses.enable_select_options()     # Enable Select Options
        self.courses.enable_check_button('Announcements')
        self.courses.enable_action_button('Submit')    # Define and Enable Action Button

        # Scrollable List Box for containing Downloadable files
        self.downloads = ScrollableListBox(self.window,  bd=2, relief=SUNKEN)
        self.downloads.grid(row=6, columnspan=5, rowspan=5, sticky=NSEW)
        self.downloads.title('Files To Download')
        self.downloads_listbox = self.downloads.listbox_widget
        self.downloads.enable_select_options()
        self.downloads.enable_action_button('Download')

        # Attach the status bar
        self.busy_status.grid(row=15, column=4, rowspan=2, sticky=EW)
        self.status_bar.grid(row=15, column=0, columnspan=4, rowspan=2, sticky=EW)
        self.window.title('Nalanda Attachment Downloader')
        self.update_status('Enter course to search.')

    def set_search_button_command(self, command):
        assert callable(command)
        self.search_button.configure(command=command)

    def set_courses_button_command(self, command):
        assert callable(command)
        self.courses.set_action(command)

    def set_downloads_button_command(self, command):
        assert callable(command)
        self.downloads.set_action(command)

    def get_search_string(self):
        return self.search_variable.get()

    @staticmethod
    def __update_listbox(list_box, contents):
        assert isinstance(contents, list)
        assert isinstance(list_box, Listbox)
        if contents:
            list_box.delete(0, END)     # Remove Existing Entries
            for content in contents:
                list_box.insert(END, content)

    def update_courses(self, courses):
        self.__update_listbox(list_box=self.courses_listbox, contents=courses)

    def update_downloads(self, downloads):
        self.__update_listbox(list_box=self.downloads_listbox, contents=downloads)

    def courses_selected(self):
        return self.courses_listbox.curselection()

    def downloads_selected(self):
        return self.downloads_listbox.curselection()

    def is_announcements_selected(self):
        return self.courses.get_check_button_state()

