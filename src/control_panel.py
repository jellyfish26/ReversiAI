import tkinter as tk
import threading
import copy


class ControlPanel(threading.Thread):
    def __init__(self, agent_name):
        threading.Thread.__init__(self)
        self.__root_tk = None
        self.__agent_name = agent_name
        self.__reversi_board = None
        self.__tag_to_position = {}
        self.__is_ready = False
        self.__is_running = False
        self.__is_waiting_for_select = False
        self.__selectable_cells = []  # search tags
        self.__before_select_cell = ()

    # tag: "cell" + vertical index + horizontal index, string join
    @staticmethod
    def __index_to_tag(vertical_index, horizontal_index):
        return "cell" + str(vertical_index) + str(horizontal_index)

    def __pressed_button(self, event):
        if not self.__is_waiting_for_select:
            return
        horizontal_index = int((event.x - 25) / 75)
        vertical_index = int((event.y - 25) / 75)
        print(vertical_index, horizontal_index)
        self.__before_select_cell = (vertical_index, horizontal_index)
        if self.__index_to_tag(vertical_index, horizontal_index) in self.__selectable_cells:
            self.__is_waiting_for_select = False

    def __generate_board(self):
        self.__reversi_canvas = tk.Canvas(self.__root_tk, bg="forest green", width=650, height=650)
        self.__reversi_canvas.place(x=0, y=0)
        for vertical_index, vertical_coordinate in enumerate(range(25, 625, 75)):
            for horizontal_index, horizontal_coordinate in enumerate(range(25, 625, 75)):
                rectangle_position = [horizontal_coordinate, vertical_coordinate,
                                      horizontal_coordinate + 75, vertical_coordinate + 75]
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

    def __put_stone(self, vertical_index, horizontal_index, agent_number):
        if agent_number == 0:
            return
        stone_color = "black" if agent_number == 1 else "white"
        position_tag = ControlPanel.__index_to_tag(vertical_index, horizontal_index)
        oval_position = copy.deepcopy(self.__tag_to_position[position_tag])
        oval_position[0] += 5
        oval_position[1] += 5
        oval_position[2] -= 5
        oval_position[3] -= 5
        self.__reversi_canvas.create_oval(*oval_position, fill=stone_color, tags="stone_" + position_tag)

    def update_board(self, reversi_board):
        for vertical_index, vertical_array in enumerate(reversi_board):
            for horizontal_index, cell_state in enumerate(vertical_array):
                self.__put_stone(vertical_index, horizontal_index, cell_state)

    def __update_cell(self, cell_tag, is_selectable):
        self.__reversi_canvas.itemconfig(cell_tag, fill="lime green" if is_selectable else "forest green")

    # selectable_cells = [tuple]
    def wait_choice_cell(self, selectable_cells):
        self.__selectable_cells = []
        for now in selectable_cells:
            cell_tag = self.__index_to_tag(now[0], now[1])
            self.__selectable_cells.append(cell_tag)
            self.__update_cell(cell_tag, True)
        self.__is_waiting_for_select = True
        while self.__is_waiting_for_select:
            pass
        for now in selectable_cells:
            self.__update_cell(self.__index_to_tag(now[0], now[1]), False)
        return self.__before_select_cell

    @property
    def is_ready(self):
        return self.__is_ready

    @property
    def is_running(self):
        return self.__is_running
