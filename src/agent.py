from abc import ABCMeta, abstractmethod, ABC
from control_panel import ControlPanel
from game_board import GameBoard
import random
import numpy as np
import copy
import math


class Agent(metaclass=ABCMeta):
    def __init__(self, agent_name, is_lunch_control_panel):
        self.__belong_game_board = None
        self.__agent_name = agent_name
        self.__is_lunch_control_panel = is_lunch_control_panel
        self.__agent_number = 0
        if is_lunch_control_panel:
            self.__control_panel = ControlPanel(agent_name)
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
        if not isinstance(value, GameBoard):
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

    @property
    def agent_name(self):
        return self.__agent_name

    def copy(self):
        return copy.deepcopy(self)


class HumanAgent(Agent):
    def __init__(self, agent_name):
        super().__init__(agent_name, True)

    def receive_update_signal(self):
        self.control_panel.update_board(self.belong_game_board.reversi_board)

    def receive_game_end_signal(self):
        pass

    def next_step(self):
        return self.control_panel.wait_choice_cell(self.belong_game_board.get_selectable_cells(self.agent_number))


class RandomAgent(Agent):
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
class GABoardAgent(Agent):
    def __init__(self):
        super().__init__("GALearning", False)
        self.__evaluation_board = np.zeros(8 * 8)

    def receive_game_end_signal(self):
        pass

    def receive_update_signal(self):
        pass

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

    def plus_mutation(self, lower, upper):
        ret = GABoardAgent()
        ret.__evaluation_board = copy.deepcopy(self.__evaluation_board)
        for index in range(0, 8 * 8):
            is_plus = random.randint(0, 1)
            if is_plus == 1:
                ret.__evaluation_board[index] += random.randint(lower, upper)
        return ret

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

    def save_evaluation_board(self, file_path):
        np.save(file_path, self.__evaluation_board)

    def load_evaluation_board(self, file_path):
        self.__evaluation_board = np.load(file_path)


class QLeaningAgent(Agent):
    def __init__(self, is_learning):
        super().__init__("QLearning", False)
        self.__ALPHA = 0.1
        self.__GAMMA = 0.9
        self.__is_learning = is_learning
        # plus one is endgame flag (value)
        self.__before_feature_vector = np.zeros(8 * 8 * 3 + 1)
        self.__now_feature_vector = np.zeros(8 * 8 * 3 + 1)
        self.__weight_vector = np.zeros(8 * 8 * 3 + 1)

    @staticmethod
    def __calc_index_from_board_index(agent_number, vertical_index, horizontal_index):
        return (agent_number + 1) * 64 + vertical_index * 8 + horizontal_index

    @staticmethod
    def __temperature_function(times):
        return 1 / math.log(times + 1, 3)

    @staticmethod
    def __calc_custom_q_value(gravity_vector, feature_vector):
        ret = 0
        for gravity, feature in zip(gravity_vector, feature_vector):
            ret += feature * gravity
        return ret

    @staticmethod
    def __convert_feature_vector_to_board(feature_vector):
        ret = np.zeros(8 * 8).reshape(8, 8)
        for agent_number in [-1, 1]:
            for vertical_index in range(0, 8):
                for horizontal_index in range(0, 8):
                    if feature_vector[
                        QLeaningAgent.__calc_index_from_board_index(
                            agent_number,
                            vertical_index,
                            horizontal_index
                        )
                    ] == 1:
                        ret[vertical_index][horizontal_index] = agent_number
        return ret

    # action require tuple
    def __calc_action_q_value(self, action):
        action_feature_vector = copy.deepcopy(self.__now_feature_vector)
        action_feature_vector[self.__calc_index_from_board_index(self.agent_number, action[0], action[1])] = 1
        return self.__calc_custom_q_value(self.__weight_vector, action_feature_vector)

    def calc_now_q_value(self):
        return self.__calc_custom_q_value(self.__weight_vector, self.__now_feature_vector)

    def __calc_custom_q_value_not_change(self, index, weight_vector, feature_vector):
        feature_vector[index] = 1
        ret = self.__calc_custom_q_value(weight_vector, feature_vector)
        feature_vector[index] = 0
        return ret

    # after exec next step (exec in receive?*_signal)
    def __update_gravity_vector(self, reward):
        max_value = -100
        enemy_selectable = self.belong_game_board.get_selectable_cells(self.agent_number * -1)
        next_feature_vector = copy.deepcopy(self.__weight_vector)

        def update_max_value(inner_index):
            nonlocal max_value, next_feature_vector
            max_value = max(
                max_value,
                self.__calc_custom_q_value_not_change(
                    inner_index,
                    self.__weight_vector,
                    next_feature_vector
                )
            )

        if len(enemy_selectable) == 0:
            update_max_value(8 * 8 * 3)
        else:
            for enemy in enemy_selectable:
                change_cell_enemy_index = self.__calc_index_from_board_index(self.agent_number * -1, enemy[0], enemy[1])
                next_feature_vector[change_cell_enemy_index] = 1
                next_my_selectable = GameBoard.get_selectable_cells_custom_board(
                    self.agent_number,
                    self.__convert_feature_vector_to_board(next_feature_vector)
                )
                if len(next_my_selectable) == 0:
                    update_max_value(8 * 8 * 3)
                else:
                    for my in next_my_selectable:
                        update_max_value(self.__calc_index_from_board_index(self.agent_number, my[0], my[1]))
                next_feature_vector[change_cell_enemy_index] = 0
        now_value = self.calc_now_q_value()

        def calc(inner_index):
            nonlocal max_value, now_value, reward
            inner_value = (reward + self.__GAMMA * max_value - now_value)
            inner_value *= (self.__weight_vector[inner_index] * self.__weight_vector[inner_index])
            return self.__weight_vector[inner_index] + self.__ALPHA * inner_value

        for index in range(0, 8 * 8 * 3 + 1):
            self.__weight_vector[index] = calc(index)

    def __get_best_move(self):
        selectable_cells = self.belong_game_board.get_selectable_cells(self.agent_number)
        ret = selectable_cells[0]
        max_value = -100
        for cell in selectable_cells:
            now_value = self.__calc_custom_q_value_not_change(
                self.__calc_index_from_board_index(self.agent_number, cell[0], cell[1]),
                self.__weight_vector,
                self.__now_feature_vector
            )
            if max_value < now_value:
                ret = cell
                max_value = now_value
        return ret

    def receive_update_signal(self):
        pass

    def receive_game_end_signal(self):
        pass

    def next_step(self):
        pass
