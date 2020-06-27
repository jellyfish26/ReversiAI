import tkinter as tk


class ControlPanel(tk.Tk):
    def __init__(self, agent_name):
        super().__init__()
        self.__agent_name = agent_name
        self.title(agent_name)
        self.geometry("{}x{}+{}+{}".format(850, 650, 450, 150))
        self.resizable(width=0, height=0)
        self.__reversi_board = None
        self.__save_tags = {}

    @staticmethod
    def __pressed_button(event):
        print(event)

    # tag: vertical * 10 + horizontal
    def __generate_board(self):
        self.__reversi_canvas = tk.Canvas(self, bg="forest green", width=650, height=650)
        self.__reversi_canvas.place(x=0, y=0)
        for vertical_index, vertical_coordinate in enumerate(range(25, 625, 75)):
            for horizontal_index, horizontal_coordinate in enumerate(range(25, 625, 75)):
                rectangle_position = vertical_coordinate, horizontal_coordinate, \
                                     vertical_coordinate + 75, horizontal_coordinate + 75
                rectangle_tag = "cell" + str(vertical_index) + str(horizontal_index)
                self.__reversi_canvas.create_rectangle(*rectangle_position, fill="forest green", tags=rectangle_tag)
                self.__reversi_canvas.tag_bind(rectangle_tag, "<ButtonPress-1>", self.__pressed_button)

    def run(self):
        self.__generate_board()
        self.mainloop()
