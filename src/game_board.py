import numpy as np
import random
import agent


# white = -1, nothing = 0. black = 1
class GameBoard(object):
    def __init__(self, first_agent, second_agent):
        if (not isinstance(first_agent, agent.Agent)) or (not isinstance(second_agent, agent.Agent)):
            raise Exception("Inherit the Agent class.")
        self.__first_agent = first_agent
        self.__first_agent.belong_game_board = self
        self.__first_agent.agent_number = -1
        self.__second_agent = second_agent
        self.__second_agent.belong_game_board = self
        self.__second_agent.agent_number = 1
        self.__reversi_board = np.zeros(8 * 8).reshape(8, 8)
        self.__is_game_end = 0
        self.__turn_agent_number = 0

    def __init_board(self):
        self.__reversi_board[3][3] = 1
        self.__reversi_board[3][4] = -1
        self.__reversi_board[4][3] = -1
        self.__reversi_board[4][4] = 1

    @staticmethod
    def get_reverse_cells_custom_board(vertical_index, horizontal_index, agent_number, custom_reversi_board):
        if (vertical_index < 0 or vertical_index >= 8) or (
                horizontal_index < 0 or horizontal_index >= 8):
            raise IndexError("Reference outside of the board.")
        if abs(agent_number) != 1:
            raise Exception("Select 1 or -1 for Agent Number.(-1: white, 1: black)")

        ret = []
        save = []
        if custom_reversi_board[vertical_index][horizontal_index] != 0:
            return np.array(ret)

        def check(inner_vertical_index, inner_horizontal_index):
            nonlocal agent_number, ret, save, custom_reversi_board
            temp = custom_reversi_board[inner_vertical_index][inner_horizontal_index]
            if temp == agent_number * -1:
                save.append((inner_vertical_index, inner_horizontal_index))
                return False
            elif temp == agent_number:
                ret.extend(save)
            return True

        def move_diagonally(move_vertical_value, move_horizontal_value):
            nonlocal vertical_index, horizontal_index, save
            save = []
            move_vertical_index = vertical_index + move_vertical_value
            move_horizontal_index = horizontal_index + move_horizontal_value
            while 0 <= move_vertical_index < 8 and 0 <= move_horizontal_index < 8:
                if check(move_vertical_index, move_horizontal_index):
                    break
                move_vertical_index += move_vertical_value
                move_horizontal_index += move_horizontal_value

        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if i == 0 and j == 0:
                    continue
                move_diagonally(i, j)

        return np.array(ret)

    def get_reverse_cells(self, vertical_index, horizontal_index, agent_number):
        return self.get_reverse_cells_custom_board(vertical_index, horizontal_index, agent_number, self.__reversi_board)

    @staticmethod
    def get_selectable_cells_custom_board(agent_number, custom_reversi_board):
        if abs(agent_number) != 1:
            raise Exception("Select 1 or -1 for Agent Number.(-1: white, 1: black)")
        ret = []
        for vertical_index in range(0, 8):
            for horizontal_index in range(0, 8):
                if len(GameBoard.get_reverse_cells_custom_board(vertical_index, horizontal_index,
                                                                agent_number, custom_reversi_board)) != 0:
                    ret.append((vertical_index, horizontal_index))
        return np.array(ret)

    def get_selectable_cells(self, agent_number):
        return self.get_selectable_cells_custom_board(agent_number, self.__reversi_board)

    @staticmethod
    def count_stones_custom_board(agent_number, custom_reversi_board):
        if abs(agent_number) != 1:
            raise Exception("Select 1 or -1 for Agent Number.(-1: white, 1: black)")
        ret = 0
        for vertical_index in range(0, 8):
            for horizontal_index in range(0, 8):
                if custom_reversi_board[vertical_index][horizontal_index] == agent_number:
                    ret += 1
        return ret

    def count_stones(self, agent_number):
        return self.count_stones_custom_board(agent_number, self.__reversi_board)

    # white win = -1, black win = 1, draw = 2, nothing = 0
    def check_game_end(self):
        if self.__is_game_end != 0:
            return self.__is_game_end
        if len(self.get_selectable_cells(1)) != 0 or len(self.get_selectable_cells(-1)) != 0:
            return 0
        white_stones = self.count_stones(-1)
        black_stones = self.count_stones(1)
        if white_stones == black_stones:
            self.__is_game_end = 2
        elif white_stones > black_stones:
            self.__is_game_end = -1
        else:
            self.__is_game_end = 1
        return self.__is_game_end

    # warning, this method is rewrite reversi board (argument). return is change index
    @staticmethod
    def put_stone_custom_board(vertical_index, horizontal_index, agent_number, custom_reversi_board):
        ret = [(vertical_index, horizontal_index)]
        replace_cells = GameBoard.get_reverse_cells_custom_board(
            vertical_index,
            horizontal_index,
            agent_number,
            custom_reversi_board
        )
        custom_reversi_board[vertical_index][horizontal_index] = agent_number
        for cell in replace_cells:
            custom_reversi_board[cell[0]][cell[1]] = agent_number
            ret.append((cell[0], cell[1]))
        return np.array(ret)

    def put_stone(self, vertical_index, horizontal_index, agent_number):
        self.put_stone_custom_board(
            vertical_index,
            horizontal_index,
            agent_number,
            self.__reversi_board
        )

    def game_start(self, save_data=None):
        self.__init_board()
        self.__first_agent.receive_update_signal()
        self.__second_agent.receive_update_signal()
        self.__turn_agent_number = -1 if random.randint(0, 2) == 0 else 1
        while self.check_game_end() == 0:
            if (not self.__first_agent.is_running) or (not self.__second_agent.is_running):
                break
            if len(self.get_selectable_cells(self.__turn_agent_number)) == 0:
                self.__turn_agent_number *= -1
                continue
            if self.__turn_agent_number == -1:
                select_cell = self.__first_agent.next_step()
            else:
                select_cell = self.__second_agent.next_step()
            self.put_stone(select_cell[0], select_cell[1], self.__turn_agent_number)
            self.__first_agent.receive_update_signal()
            self.__second_agent.receive_update_signal()
            self.__turn_agent_number *= -1
        self.__first_agent.receive_game_end_signal()
        self.__second_agent.receive_game_end_signal()
        return self.check_game_end(), save_data

    @property
    def reversi_board(self):
        return self.__reversi_board

    @property
    def turn_agent_number(self):
        return self.__turn_agent_number
