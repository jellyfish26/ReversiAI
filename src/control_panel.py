import tkinter as tk
import threading


class ControlPanel(threading.Thread):
    def __init__(self, agent_name):
        threading.Thread.__init__(self)
        self.__root_tk = None
        self.__agent_name = agent_name
        self.__reversi_board = None
        self.__tag_to_position = {}
        self.__is_ready = False
        self.__is_running = False

    def __pressed_button(self, event):
        print(event)

    # tag: "cell" + vertical index + horizontal index, string join
    @staticmethod
    def __index_to_tag(vertical_index, horizontal_index):
        return "cell" + str(vertical_index) + str(horizontal_index)

    def __generate_board(self):
        self.__reversi_canvas = tk.Canvas(self.__root_tk, bg="forest green", width=650, height=650)
        self.__reversi_canvas.place(x=0, y=0)
        for vertical_index, vertical_coordinate in enumerate(range(25, 625, 75)):
            for horizontal_index, horizontal_coordinate in enumerate(range(25, 625, 75)):
                rectangle_position = vertical_coordinate, horizontal_coordinate, \
                                     vertical_coordinate + 75, horizontal_coordinate + 75
                position_tag = ControlPanel.__index_to_tag(vertical_index, horizontal_index)
                self.__tag_to_position[position_tag] = rectangle_position
                self.__reversi_canvas.create_rectangle(*rectangle_position, fill="forest green", tags=position_tag)
                self.__reversi_canvas.tag_bind(position_tag, "<ButtonPress-1>", self.__pressed_button)

    def __callback(self):
        self.__root_tk.destroy()
        self.__root_tk.quit()
        self.__is_running = False

    def run(self):
        self.__is_running = True
        self.__root_tk = tk.Tk()
        self.__root_tk.protocol("WM_DELETE_WINDOW", self.__callback)
        self.__root_tk.title(self.__agent_name)
        self.__root_tk.geometry("{}x{}+{}+{}".format(850, 650, 450, 150))
        self.__root_tk.resizable(width=0, height=0)
        self.__generate_board()
        self.__is_ready = True
        self.__root_tk.mainloop()

    def __update_cell(self, vertical_index, horizontal_index, agent_number):
        if agent_number == 0:
            return
        stone_color = "black" if agent_number == 1 else "white"
        position_tag = ControlPanel.__index_to_tag(vertical_index, horizontal_index)
        self.__reversi_canvas.create_oval(*self.__tag_to_position[position_tag], fill=stone_color)

    def update_board(self, reversi_board):
        for vertical_index, vertical_array in enumerate(reversi_board):
            for horizontal_index, cell_state in enumerate(vertical_array):
                self.__update_cell(vertical_index, horizontal_index, cell_state)

    @property
    def is_ready(self):
        return self.__is_ready

    @property
    def is_running(self):
        return self.__is_running
