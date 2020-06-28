from abc import ABCMeta, abstractmethod, ABC
import control_panel
import game_board
import random
import numpy as np
import copy


class Agent(metaclass=ABCMeta):
    def __init__(self, agent_name, is_lunch_control_panel):
        self.__belong_game_board = None
        self.__is_lunch_control_panel = is_lunch_control_panel
        self.__agent_number = 0
        if is_lunch_control_panel:
            self.__control_panel = control_panel.ControlPanel(agent_name)
            self.__control_panel.start()
            while not self.__control_panel.is_ready:
                pass

    @property
    def belong_game_board(self):
        if self.__belong_game_board is None:
            raise Exception("Must init Agent belong GameBoard")
        return self.__belong_game_board

    @belong_game_board.setter
    def belong_game_board(self, value):
        if not isinstance(value, game_board.GameBoard):
            raise Exception("Must set GameBoard Class")
        self.__belong_game_board = value

    @abstractmethod
    def receive_update_signal(self):
        pass

    @abstractmethod
    def receive_game_end_signal(self):
        pass

    # board Read Only
    @abstractmethod
    def next_step(self):
        pass

    @property
    def agent_number(self):
        return self.__agent_number

    @agent_number.setter
    def agent_number(self, value):
        self.__agent_number = value

    @property
    def is_lunch_control_panel(self):
        return self.__is_lunch_control_panel

    @property
    def control_panel(self):
        return self.__control_panel

    @property
    def is_ready(self):
        if self.__is_lunch_control_panel:
            return self.__control_panel.is_ready
        return True

    @property
    def is_running(self):
        if self.__is_lunch_control_panel:
            return self.__control_panel.is_running
        return True


class HumanAgent(Agent):
    def __init__(self, agent_name):
        super().__init__(agent_name, True)

    def receive_update_signal(self):
        self.control_panel.update_board(self.belong_game_board.reversi_board)

    def receive_game_end_signal(self):
        pass

    def next_step(self):
        return self.control_panel.wait_choice_cell(self.belong_game_board.get_selectable_cells(self.agent_number))


class RandomAgent(Agent, ABC):
    def __init__(self):
        super().__init__("random", False)

    def receive_update_signal(self):
        pass

    def receive_game_end_signal(self):
        pass

    def next_step(self):
        selectable = self.belong_game_board.get_selectable_cells(self.agent_number)
        index = random.randint(0, len(selectable) - 1)
        return selectable[index]


# Learning the board
class GABoardAgent(Agent, ABC):
    def __init__(self):
        super().__init__("learning", False)
        self.__evaluation_board = np.zeros(8 * 8)

    def set_random_evaluation_board(self):
        for index in range(0, 8 * 8):
            self.__evaluation_board[index] = random.randint(-15, 15)

    def cross_over_one_point(self, another_parent):
        if not isinstance(another_parent, GABoardAgent):
            raise Exception("this method same class as the argument")
        divide_index = random.randint(0, 8 * 8 - 1)
        start_this = random.randint(0, 1)
        ret = GABoardAgent()
        for index in range(0, 8 * 8):
            check = start_this
            if index >= divide_index:
                check = check ^ 1
            if check == 0:
                ret.__evaluation_board[index] = self.__evaluation_board[index]
            else:
                ret.__evaluation_board[index] = another_parent.__evaluation_board[index]
        return ret

    def cross_over_uniform(self, another_parent):
        if not isinstance(another_parent, GABoardAgent):
            raise Exception("this method same class as the argument")
        ret = GABoardAgent()
        for index in range(0, 8 * 8):
            select_parent = random.randint(0, 1)
            if select_parent == 0:
                ret.__evaluation_board[index] = self.__evaluation_board[index]
            else:
                ret.__evaluation_board[index] = another_parent.__evaluation_board[index]
        return ret

    def normal_mutation(self):
        ret = GABoardAgent()
        ret.__evaluation_board = copy.deepcopy(self.__evaluation_board)

        def update(index):
            nonlocal ret
            before_value = abs(self.__evaluation_board[index])
            ret.__evaluation_board[index] = random.randint(-before_value - 5, before_value + 5)

        update(random.randint(0, 8 * 4 - 1))
        update(random.randint(8 * 4, 8 * 8 - 1))
        return ret

    def plus_mutation(self):
        ret = GABoardAgent()
        ret.__evaluation_board = copy.deepcopy(self.__evaluation_board)
        for index in range(0, 8 * 8):
            is_plus = random.randint(0, 1)
            if is_plus == 1:
                ret.__evaluation_board[index] += random.randint(0, 25)
        return ret

    def receive_update_signal(self):
        pass

    def receive_game_end_signal(self):
        pass

    def __get_evaluation_value(self, vertical_index, horizontal_index):
        return self.__evaluation_board[8 * vertical_index + horizontal_index]

    def next_step(self):
        selectable_cells = self.belong_game_board.get_selectable_cells(self.agent_number)
        ret = selectable_cells[0]
        now_evaluation_value = self.__get_evaluation_value(ret[0], ret[1])
        for explore in selectable_cells:
            if now_evaluation_value < self.__get_evaluation_value(explore[0], explore[1]):
                ret = explore
                now_evaluation_value = self.__get_evaluation_value(explore[0], explore[1])
        return ret
