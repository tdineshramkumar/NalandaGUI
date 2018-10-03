from tkinter import *


class ScrollableListBox(Frame):
    """
        Scrollable List Box: A Compound Widget with a Scrollable Listbox (Both X and Y) with Optionally Title (Label)
        selection options for selecting items of listbox (select all and select none), a check box and a Action Button
        To enable or make visible check box, title or action button call appropriate methods.
        Also Add functionality to the action button.
    """
    def __init__(self, master=None, selectmode=EXTENDED, cnf={}, **kw):
        Frame.__init__(self, master, cnf, **kw)

        self.listbox_widget = Listbox(self, selectmode=selectmode, **kw)    # Create List Box
        self.horizontal_scroll = Scrollbar(self, orient=HORIZONTAL)         # Create Scrollbars
        self.vertical_scroll = Scrollbar(self, orient=VERTICAL)
        self.action_frame = Frame(self)             # Create Frame to contain the Buttons and CheckBox
        self.title_widget = Label(self, anchor=W)   # Label to contain the title

        self.action_frame.pack(fill=X, side=BOTTOM)  # Pack the frame at the botton
        self.horizontal_scroll.pack(side=BOTTOM, fill=X)    # Place Scrollbars
        self.vertical_scroll.pack(side=RIGHT, fill=Y)
        self.listbox_widget.pack(expand=True, fill=BOTH, side=BOTTOM)   # Place the listbox

        self.horizontal_scroll.configure(command=self.listbox_widget.xview)     # Configure the scrollbar and listbox
        self.vertical_scroll.configure(command=self.listbox_widget.yview)
        self.listbox_widget.configure(yscrollcommand=self.vertical_scroll.set, xscrollcommand=self.horizontal_scroll.set)

        self.select_all = Button(self.action_frame, text='Select All ')     # define the buttons and checkboxes
        self.select_none = Button(self.action_frame, text='Select None')
        self.action_button = Button(self.action_frame, bd=5, relief=RAISED)
        self.check_button_variable = BooleanVar()
        self.check_button = Checkbutton(self.action_frame, variable=self.check_button_variable)

    def title(self, title):     # pack the title to display
        assert isinstance(title, str)
        self.title_widget.configure(text=title)
        self.title_widget.pack(side=TOP, fill=X)

    def enable_check_button(self, text):    # pack check button to display
        assert isinstance(text, str)
        self.check_button.configure(text=text, offvalue=False, onvalue=True)
        self.check_button.pack(side=LEFT, expand=True)

    def enable_select_options(self):    # pack the select buttons
        self.select_all.configure(command=lambda: self.listbox_widget.selection_set(0, END))
        self.select_none.configure(command=lambda: self.listbox_widget.select_clear(0, END))
        self.select_all.pack(side=LEFT)
        self.select_none.pack(side=LEFT)

    def get_check_button_state(self):      # get the state of check button
        return self.check_button_variable.get()

    def enable_action_button(self, text):   # pack the action button
        assert isinstance(text, str)
        self.action_button.configure(text=text)
        self.action_button.pack(side=RIGHT)

    def set_action(self, command):  # define the functionality of action button
        assert command is None or callable(command)
        self.action_button.configure(command=command)
