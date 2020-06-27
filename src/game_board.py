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
        self.__VERTICAL_SIZE = 8
        self.__HORIZONTAL_SIZE = 8
        self.__reversi_board = np.zeros(self.__VERTICAL_SIZE * self.__HORIZONTAL_SIZE, dtype=np.int)\
            .reshape(self.__VERTICAL_SIZE, self.__HORIZONTAL_SIZE)
        self.__is_game_over = 0
        self.__turn_agent_number = 0

    def __init_board(self):
        self.__turn_agent_number = -1 if random.randint(0, 2) == 0 else 1
        self.__reversi_board[3][3] = 1
        self.__reversi_board[3][4] = -1
        self.__reversi_board[4][3] = -1
        self.__reversi_board[4][4] = 1

    def __get_reverse_cells(self, vertical_index, horizontal_index, agent_number):
        if (vertical_index < 0 or vertical_index >= self.__VERTICAL_SIZE) and (
                horizontal_index < 0 or vertical_index >= self.__HORIZONTAL_SIZE):
            raise IndexError("Reference outside of the board.")
        if abs(agent_number) != 1:
            raise Exception("Select 1 or -1 for Agent Number.(-1: white, 1: black)")

        ret = []
        save = []
        if self.__reversi_board[vertical_index][horizontal_index] != 0:
            return ret

        def check(inner_vertical_index, inner_horizontal_index):
            nonlocal agent_number, ret, save
            temp = self.__reversi_board[inner_vertical_index][inner_horizontal_index]
            if temp == agent_number * -1:
                save.append((inner_vertical_index, inner_horizontal_index))
                return False
            elif temp == agent_number:
                ret.extend(save)
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

        move_straight(True)  # move vertical
        move_straight(False)  # move horizontal
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
        return np.array(ret)

    def get_selectable_cells(self, agent_number):
        if abs(agent_number) != 1:
            raise Exception("Select 1 or -1 for Agent Number.(-1: white, 1: black)")
        ret = []
        for vertical_index in range(0, self.__VERTICAL_SIZE):
            for horizontal_index in range(0, self.__HORIZONTAL_SIZE):
                if len(self.__get_reverse_cells(vertical_index, horizontal_index, agent_number)) != 0:
                    ret.append((vertical_index, horizontal_index))
        return np.array(ret)

    def count_stones(self, agent_number):
        if abs(agent_number) != 1:
            raise Exception("Select 1 or -1 for Agent Number.(-1: white, 1: black)")
        ret = 0
        for vertical_index in range(0, self.__VERTICAL_SIZE):
            for horizontal_index in range(0, self.__HORIZONTAL_SIZE):
                if self.__reversi_board[vertical_index][horizontal_index] == agent_number:
                    ret += 1
        return ret

    # white win = -1, black win = 1, draw = 2, nothing = 0
    def check_game_over(self):
        if self.__is_game_over != 0:
            return self.__is_game_over
        if len(self.get_selectable_cells(1)) != 0 or len(self.get_selectable_cells(-1)) != 0:
            return 0
        white_stones = self.count_stones(-1)
        black_stones = self.count_stones(1)
        if white_stones == black_stones:
            self.__is_game_over = 2
        elif white_stones < black_stones:
            self.__is_game_over = -1
        else:
            self.__is_game_over = 1
        return self.__is_game_over

    def put_stone(self, vertical_index, horizontal_index, agent_number):
        replace_cells = self.__get_reverse_cells(vertical_index, horizontal_index, agent_number)
        self.__reversi_board[vertical_index][horizontal_index] = agent_number
        for temp in replace_cells:
            self.__reversi_board[temp[0]][temp[1]] = agent_number

    def game_start(self):
        self.__init_board()
        self.__first_agent.accept_update()
        self.__second_agent.accept_update()
        while self.check_game_over() == 0:
            if (not self.__first_agent.is_running) or (not self.__second_agent.is_running):
                break
            select_cell = []
            if self.__turn_agent_number == -1:
                select_cell = self.__first_agent.next_step()
            else:
                select_cell = self.__second_agent.next_step()
            self.put_stone(select_cell[0], select_cell[1], self.__turn_agent_number)
            print(self.reversi_board)
            self.__first_agent.accept_update()
            self.__second_agent.accept_update()
            self.__turn_agent_number *= -1

    @property
    def reversi_board(self):
        return self.__reversi_board

    @property
    def vertical_size(self):
        return self.__VERTICAL_SIZE

    @property
    def horizontal_size(self):
        return self.__HORIZONTAL_SIZE
