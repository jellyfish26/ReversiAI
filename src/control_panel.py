import tkinter as tk


class ControlPanel(tk.Tk):
    def __init__(self, agent_name):
        super().__init__()
        self.__agent_name = agent_name
        self.title(agent_name)
        self.geometry("{}x{}+{}+{}".format(800, 800, 600, 200))
        self.resizable(width=0, height=0)

    def run(self):
        self.mainloop()