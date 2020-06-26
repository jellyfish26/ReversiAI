import numpy as np
from . import Agent


# white = -1, nothing = 0. black = 1
class GameBoard(object):
    def __init__(self, first_agent, second_agent):
        if (not isinstance(first_agent, Agent.Agent)) or (not isinstance(second_agent, Agent.Agent)):
            raise Exception("AgentClassError, Inherit the Agent class.")
        self.__first_agent = first_agent
        self.__first_agent.agent_number = -1
        self.__second_agent = second_agent
        self.__second_agent.agent_number = 1
        self.__VERTICAL_SIZE = 8
        self.__HORIZONTAL_SIZE = 8
        self.__reversi_board = np.arange(self.__VERTICAL_SIZE * self.__HORIZONTAL_SIZE).reshape(self.__VERTICAL_SIZE,
                                                                                                self.__HORIZONTAL_SIZE)
        self.__is_game_over = 0

    def __init_board(self):
        self.__reversi_board[3][3] = 1
        self.__reversi_board[3][4] = -1
        self.__reversi_board[4][3] = -1
        self.__reversi_board[4][4] = 1

    def __get_reverse_cells(self, vertical_index, horizontal_index, agent_number):
        ret = np.empty(0)
        save = []

        def check(inner_vertical_index, inner_horizontal_index):
            nonlocal agent_number, ret, save
            temp = self.__reversi_board[inner_vertical_index][inner_horizontal_index]
            if temp == agent_number * -1:
                save.append((inner_vertical_index, inner_horizontal_index))
                return False
            elif temp == agent_number:
                ret = np.concatenate([ret, np.array(save)])
            return True

        def move_straight(is_move_vertical):
            nonlocal vertical_index, horizontal_index, save
            save = []
            move_index = vertical_index - 1 if is_move_vertical else horizontal_index - 1
            while move_index >= 0:
                if check(move_index, horizontal_index) if is_move_vertical else check(vertical_index, move_index):
                    break
                move_index -= 1
            save = []
            move_index = vertical_index + 1 if is_move_vertical else horizontal_index + 1
            while move_index < 8:
                if check(move_index, horizontal_index) if is_move_vertical else check(vertical_index, move_index):
                    break
                move_index += 1

        move_straight(True)  # vertical
        move_straight(False)  # horizontal
        # Upper Left
        save = []
        move_vertical = vertical_index - 1
        move_horizontal = horizontal_index - 1
        while move_vertical >= 0 and move_horizontal >= 0:
            if check(move_vertical, move_horizontal):
                break
            move_vertical -= 1
            move_horizontal -= 1
        # Lower Right
        save = []
        move_vertical = vertical_index + 1
        move_horizontal = horizontal_index + 1
        while move_vertical < 8 and move_horizontal < 8:
            if check(move_vertical, move_horizontal):
                break
            move_vertical += 1
            move_horizontal += 1
        return ret

    def get_selectable_cells(self, agent_number):
        ret = []
        for vertical_index in range(0, 8):
            for horizontal_index in range(0, 8):
                if len(self.__get_reverse_cells(vertical_index, horizontal_index, agent_number)) != 0:
                    ret.append((vertical_index, horizontal_index))
        return np.array(ret)

    def check_game_over(self):
        if self.__is_game_over != 0:
            return self.__is_game_over

    def game_start(self):
        self.__init_board()
        pass

    @property
    def vertical_size(self):
        return self.__VERTICAL_SIZE

    @property
    def horizontal_size(self):
        return self.__HORIZONTAL_SIZE
