import wx
from datetime import datetime
import pyperclip
import pickle
import os

class TodoList(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, title="To-Do List", size=(500, 500))

        self.task_file = "tasks.pkl"  # File to store tasks
        self.load_tasks()  # Load tasks from file

        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour('#f0f5f9')

        font = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        self.task_label = wx.StaticText(self.panel, label="Task:")
        self.task_label.SetFont(font)
        self.task_input = wx.TextCtrl(self.panel)

        self.priority_label = wx.StaticText(self.panel, label="Priority:")
        self.priority_label.SetFont(font)
        self.priority_input = wx.Choice(self.panel, choices=["Low", "Medium", "High"])

        self.date_label = wx.StaticText(self.panel, label="Due Date (YYYY-MM-DD):")
        self.date_label.SetFont(font)
        self.date_input = wx.TextCtrl(self.panel)
        self.today_button = self.create_styled_button("Today's Date", "#007BFF")
        self.today_button.Bind(wx.EVT_BUTTON, self.set_today)

        self.add_button = self.create_styled_button("Add Task", "#28a745")
        self.add_button.Bind(wx.EVT_BUTTON, self.add_task)

        self.update_button = self.create_styled_button("Update Task", "#ffc107")
        self.update_button.Bind(wx.EVT_BUTTON, self.update_task)

        self.copy_button = self.create_styled_button("Copy Tasks", "#17a2b8")
        self.copy_button.Bind(wx.EVT_BUTTON, self.copy_tasks)

        self.task_list = wx.ListCtrl(self.panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.task_list.InsertColumn(0, 'Task', width=200)
        self.task_list.InsertColumn(1, 'Priority', width=100)
        self.task_list.InsertColumn(2, 'Due Date', width=150)
        self.task_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_task_selected)

        self.delete_button = self.create_styled_button("Delete Task", "#dc3545")
        self.delete_button.Bind(wx.EVT_BUTTON, self.delete_task)

        self.done_button = self.create_styled_button("Mark as Done", "#6c757d")
        self.done_button.Bind(wx.EVT_BUTTON, self.mark_done)

        self.layout()
        self.populate_task_list()

    def create_styled_button(self, label, color):
        """Creates a styled button with a custom color."""
        btn = wx.Button(self.panel, label=label)
        btn.SetBackgroundColour(color)
        btn.SetForegroundColour('#FFFFFF')  
        btn.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        return btn

    def layout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        input_sizer = wx.FlexGridSizer(3, 3, 5, 5)
        input_sizer.AddMany([
            (self.task_label), (self.task_input, 1, wx.EXPAND), (wx.StaticText(self.panel)),
            (self.priority_label), (self.priority_input), (wx.StaticText(self.panel)),
            (self.date_label), (self.date_input, 1, wx.EXPAND), (self.today_button)
        ])
        input_sizer.AddGrowableCol(1, 1)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.add_button, 0, wx.ALL, 5)
        button_sizer.Add(self.update_button, 0, wx.ALL, 5)
        button_sizer.Add(self.copy_button, 0, wx.ALL, 5)

        list_sizer = wx.BoxSizer(wx.VERTICAL)
        list_sizer.Add(self.task_list, 1, wx.EXPAND | wx.ALL, 5)

        button_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer2.Add(self.delete_button, 0, wx.ALL, 5)
        button_sizer2.Add(self.done_button, 0, wx.ALL, 5)

        sizer.Add(input_sizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT)
        sizer.Add(list_sizer, 1, wx.EXPAND)
        sizer.Add(button_sizer2, 0, wx.ALIGN_RIGHT)

        self.panel.SetSizer(sizer)

    def set_today(self, event):
        """Sets today's date in the date input."""
        self.date_input.SetValue(datetime.now().strftime('%Y-%m-%d'))

    def add_task(self, event):
        """Adds a new task and saves immediately."""
        task = self.task_input.GetValue()
        priority = self.priority_input.GetStringSelection()
        date = self.date_input.GetValue()
        if task and priority and date:
            self.tasks.append({'task': task, 'priority': priority, 'date': date, 'done': False})
            self.sort_tasks()
            self.save_tasks()
            self.populate_task_list()
            self.task_input.SetValue("")

    def update_task(self, event):
        """Updates a task and saves immediately."""
        selection = self.task_list.GetFirstSelected()
        if selection != -1:
            task = self.task_input.GetValue()
            priority = self.priority_input.GetStringSelection()
            date = self.date_input.GetValue()
            if task and priority and date:
                self.tasks[selection] = {'task': task, 'priority': priority, 'date': date, 'done': False}
                self.sort_tasks()
                self.save_tasks()
                self.populate_task_list()

    def on_task_selected(self, event):
        """Populates input fields with selected task."""
        index = event.GetIndex()
        task = self.tasks[index]
        self.task_input.SetValue(task['task'])
        self.priority_input.SetStringSelection(task['priority'])
        self.date_input.SetValue(task['date'])

    def mark_done(self, event):
        """Marks a task as completed and moves it to the bottom."""
        selection = self.task_list.GetFirstSelected()
        if selection != -1:
            self.tasks[selection]['done'] = True
            self.sort_tasks()
            self.save_tasks()
            self.populate_task_list()

    def delete_task(self, event):
        """Deletes a task and saves immediately."""
        selection = self.task_list.GetFirstSelected()
        if selection != -1:
            del self.tasks[selection]
            self.save_tasks()
            self.populate_task_list()

    def copy_tasks(self, event):
        """Copies pending tasks to clipboard."""
        tasks_str = '\n'.join([f'Task: {task["task"]}, Priority: {task["priority"]}' for task in self.tasks if not task['done']])
        pyperclip.copy(tasks_str)

    def sort_tasks(self):
        """Sorts tasks by priority (High > Medium > Low) with completed tasks at the bottom."""
        self.tasks.sort(key=lambda x: (x['done'], ["High", "Medium", "Low"].index(x['priority'])))

    def populate_task_list(self):
        """Refreshes the task list display."""
        self.task_list.DeleteAllItems()
        for index, task in enumerate(self.tasks):
            self.task_list.Append((task['task'], task['priority'], task['date']))
            if task['done']:
                self.task_list.SetItemTextColour(index, wx.Colour(128, 128, 128))

    def save_tasks(self):
        """Saves tasks to a file."""
        with open(self.task_file, 'wb') as f:
            pickle.dump(self.tasks, f)

    def load_tasks(self):
        """Loads tasks from a file."""
        if os.path.exists(self.task_file):
            with open(self.task_file, 'rb') as f:
                self.tasks = pickle.load(f)
        else:
            self.tasks = []

class MyApp(wx.App):
    def OnInit(self):
        self.frame = TodoList(None)
        self.frame.Show()
        return True

if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
