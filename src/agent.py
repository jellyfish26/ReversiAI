from abc import ABCMeta, abstractmethod, ABC
import control_panel
import game_board
import random
import numpy as np
import copy
import math
import tensorflow as tf
import tensorflow.keras.layers as krs_layer
import tensorflow.keras.models as krs_models
import tensorflow.keras.optimizers as krs_optimizers
import tensorflow.keras.utils as krs_utils
import tensorflow.keras.losses as krs_losses
from collections import deque



class Agent(metaclass=ABCMeta):
    def __init__(self, agent_name, is_lunch_control_panel):
        self.__belong_game_board = None
        self.__agent_name = agent_name
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
        self.control_panel.update_game_status(self.belong_game_board.check_game_end(), self.agent_number)
        self.control_panel.update_game_stone(
            self.belong_game_board.count_stones(self.agent_number),
            self.belong_game_board.count_stones(self.agent_number * -1)
        )

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
        self.__ALPHA = 0.025
        self.__GAMMA = 0.9
        self.__TEMPERATURE = 0.08
        self.__is_learning = is_learning
        self.__now_time = 1
        # plus one is endgame flag (value)
        self.__now_feature_vector = np.zeros(8 * 8 * 3 + 1)
        self.__weight_vector = np.full(8 * 8 * 3 + 1, 0.05)

    @staticmethod
    def __calc_index_from_board_index(agent_number, vertical_index, horizontal_index):
        return int((agent_number + 1) * 64 + vertical_index * 8 + horizontal_index)

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

    @staticmethod
    def __convert_board_to_feature_vector(board):
        ret = np.zeros(8 * 8 * 3 + 1)
        for vertical_index in range(0, 8):
            for horizontal_index in range(0, 8):
                ret[
                    QLeaningAgent.__calc_index_from_board_index(
                        board[vertical_index][horizontal_index],
                        vertical_index,
                        horizontal_index
                    )
                ] = 1
        return ret

    @staticmethod
    def __calc_custom_q_value(gravity_vector, feature_vector):
        ret = 0
        for gravity, feature in zip(gravity_vector, feature_vector):
            ret += feature * gravity
        return ret

    def __calc_custom_q_value_not_change(self, agent_number, action, weight_vector, feature_vector):
        reversi_board = self.__convert_feature_vector_to_board(feature_vector)
        game_board.GameBoard.put_stone_custom_board(action[0], action[1], agent_number, reversi_board)
        ret = self.__calc_custom_q_value(
            weight_vector,
            self.__convert_board_to_feature_vector(reversi_board)
        )
        return ret

    def __calc_game_end_q_value_not_change(self, weight_vector, feature_vector):
        feature_vector[8 * 8 * 3] = 1
        ret = self.__calc_custom_q_value(weight_vector, feature_vector)
        feature_vector[8 * 8 * 3] = 0
        return ret

    # action require tuple
    def __calc_action_q_value(self, action):
        return self.__calc_custom_q_value_not_change(self.agent_number, action, self.__weight_vector,
                                                     self.__now_feature_vector)

    def calc_now_q_value(self):
        return self.__calc_custom_q_value(self.__weight_vector, self.__now_feature_vector)

    # after exec next step (exec in receive?*_signal)
    def __update_gravity_vector(self, reward, is_game_end):
        max_value = 0
        enemy_selectable = self.belong_game_board.get_selectable_cells(self.agent_number * -1)
        next_feature_vector = copy.deepcopy(self.__now_feature_vector)
        reversi_board = copy.deepcopy(self.belong_game_board.reversi_board)

        def update_max_value(agent_number, action):
            nonlocal max_value, reversi_board
            my_change_cells = game_board.GameBoard.put_stone_custom_board(
                action[0],
                action[1],
                self.agent_number,
                reversi_board
            )
            max_value = max(
                max_value,
                self.__calc_custom_q_value_not_change(
                    agent_number,
                    action,
                    self.__weight_vector,
                    self.__convert_board_to_feature_vector(reversi_board)
                )
            )
            reversi_board[my_change_cells[0][0]][my_change_cells[0][1]] = 0
            for my_cell in my_change_cells[1:]:
                reversi_board[my_cell[0]][my_cell[1]] *= -1

        if is_game_end:
            max_value = max(
                max_value,
                self.__calc_game_end_q_value_not_change(
                    self.__weight_vector,
                    next_feature_vector
                )
            )
        else:
            for enemy in enemy_selectable:
                change_cells = game_board.GameBoard.put_stone_custom_board(
                    enemy[0],
                    enemy[1],
                    self.agent_number * -1,
                    reversi_board
                )
                next_my_selectable = game_board.GameBoard.get_selectable_cells_custom_board(
                    self.agent_number,
                    reversi_board
                )
                for my in next_my_selectable:
                    update_max_value(self.agent_number, my)
                reversi_board[change_cells[0][0]][change_cells[0][1]] = 0
                for enemy_cell in change_cells[1:]:
                    reversi_board[enemy_cell[0]][enemy_cell[1]] *= -1
            if len(enemy_selectable) == 0:
                next_my_selectable = game_board.GameBoard.get_selectable_cells_custom_board(
                    self.agent_number,
                    reversi_board
                )
                for my in next_my_selectable:
                    update_max_value(self.agent_number, my)
        now_value = self.calc_now_q_value()

        def calc(inner_index):
            nonlocal max_value, now_value, reward
            inner_value = (reward + self.__GAMMA * max_value - now_value)
            inner_value *= self.__now_feature_vector[inner_index]
            return self.__weight_vector[inner_index] + self.__ALPHA * inner_value

        np.set_printoptions(suppress=True)
        next_weight_vector = np.zeros(8 * 8 * 3 + 1)

        for index in range(0, 8 * 8 * 3 + 1):
            next_weight_vector[index] = calc(index)
        self.__weight_vector = next_weight_vector

    def __get_boltzmann_select(self):
        selectable_cells = self.belong_game_board.get_selectable_cells(self.agent_number)
        base_value = 0
        max_q_value = -1000000
        for cell in selectable_cells:
            max_q_value = max(max_q_value, self.__calc_action_q_value(cell) / self.__TEMPERATURE)
        for cell in selectable_cells:
            base_value += math.exp(self.__calc_action_q_value(cell) / self.__TEMPERATURE - max_q_value)
        sum_value = 0
        probability = []
        for cell in selectable_cells:
            sum_value += (math.exp(self.__calc_action_q_value(cell) / self.__TEMPERATURE - max_q_value)) / base_value
            probability.append(sum_value)
        probability[-1] = 1
        select_value = random.random()
        for index, value in enumerate(probability):
            if probability[index] < select_value:
                return selectable_cells[index]
        return selectable_cells[-1]

    def __get_best_move(self):
        selectable_cells = self.belong_game_board.get_selectable_cells(self.agent_number)
        ret = selectable_cells[0]
        max_value = -100
        for cell in selectable_cells:
            now_value = self.__calc_action_q_value(cell)
            if max_value < now_value:
                ret = cell
                max_value = now_value
        return ret

    def time_increment(self):
        self.__now_time += 1

    def receive_update_signal(self):
        if not self.__is_learning:
            return
        if self.belong_game_board.turn_agent_number == 0:
            self.__now_feature_vector = self.__convert_board_to_feature_vector(self.belong_game_board.reversi_board)
            return
        if self.agent_number != self.belong_game_board.turn_agent_number:
            return
        self.__now_feature_vector = self.__convert_board_to_feature_vector(self.belong_game_board.reversi_board)
        self.__update_gravity_vector(0, False)

    # -1, 0, 1
    def receive_game_end_signal(self):
        if not self.__is_learning:
            return
        self.__now_feature_vector[8 * 8 * 3] = 1
        result = self.belong_game_board.check_game_end()
        if result == 2:
            result = 0
        # thinking
        result *= self.agent_number
        result *= 100
        self.__update_gravity_vector(result, True)

    def next_step(self):
        if self.__is_learning:
            self.__now_feature_vector = self.__convert_board_to_feature_vector(self.belong_game_board.reversi_board)
            return self.__get_boltzmann_select()
        else:
            self.__now_feature_vector = self.__convert_board_to_feature_vector(self.belong_game_board.reversi_board)
            return self.__get_best_move()

    def save_weight_vector(self, file_path):
        np.save(file_path, self.__weight_vector)

    def load_weight_vector(self, file_path):
        self.__weight_vector = np.load(file_path)


# is_ReLU is True Relu, False is sigmoid
class NeuralNetworkGALeaningAgent(Agent):
    def __init__(self, is_ReLU):
        super().__init__("NNGA", False)
        self.__is_ReLU = is_ReLU
        self.__now_vector = np.zeros(8)
        self.__input_weight = 20 * np.random.rand(8, 15) - 10
        self.__output_weight = 20 * np.random.rand(15, 1) - 10
        if not is_ReLU:
            self.__input_weight = 2 * np.random.rand(8, 15) - 1
            self.__output_weight = 2 * np.random.rand(15, 1) - 1

    # under about Neural Network
    @staticmethod
    def sigmoid(x):
        return 1.0 / (1.0 + np.exp(-x))

    @staticmethod
    def ReLU(x):
        return np.maximum(0, x)

    # forward propagation
    def forward(self):
        # input layer
        now_layer = copy.deepcopy(self.__now_vector)
        # first middle layer
        now_layer = np.dot(now_layer, self.__input_weight)
        if self.__is_ReLU:
            now_layer = self.ReLU(now_layer)
        else:
            now_layer = self.sigmoid(now_layer)
        # output layer
        now_layer = np.dot(now_layer, self.__output_weight)
        return now_layer[0]

    # end Neural Network

    @staticmethod
    def __generate_vector_from_custom_board(agent_number, custom_reversi_board):
        ret = np.zeros(8)
        my_count = 0
        enemy_count = 0

        def specific_count_stone(vertical_array, horizontal_array):
            nonlocal my_count, enemy_count
            my_count = 0
            enemy_count = 0
            for vertical_index in vertical_array:
                for horizontal_index in horizontal_array:
                    if custom_reversi_board[vertical_index][horizontal_index] == agent_number:
                        my_count += 1
                    elif custom_reversi_board[vertical_index][horizontal_index] == agent_number * -1:
                        enemy_count += 1

        specific_count_stone([0, 7], [0, 7])
        ret[0] = my_count
        ret[1] = enemy_count
        ret[2] = game_board.GameBoard.count_stones_custom_board(agent_number, custom_reversi_board)
        ret[3] = game_board.GameBoard.count_stones_custom_board(agent_number * -1, custom_reversi_board)
        specific_count_stone([3, 4], [3, 4])
        ret[4] = my_count - enemy_count
        specific_count_stone([2, 3, 4, 5], [2, 3, 4, 5])
        ret[5] = my_count - enemy_count
        ret[6] = len(game_board.GameBoard.get_selectable_cells_custom_board(agent_number * -1, custom_reversi_board))
        specific_count_stone([1, 6], [1, 6])
        ret[7] = my_count - enemy_count
        return ret

    def __update_vector(self):
        self.__now_vector = self.__generate_vector_from_custom_board(
            self.agent_number,
            self.belong_game_board.reversi_board
        )

    def receive_update_signal(self):
        self.__update_vector()

    def receive_game_end_signal(self):
        pass

    def next_step(self):
        selectable_cells = self.belong_game_board.get_selectable_cells(self.agent_number)
        ret = 0
        max_value = -10000
        reversi_board = copy.deepcopy(self.belong_game_board.reversi_board)
        for index, cell in enumerate(selectable_cells):
            change_cells = game_board.GameBoard.put_stone_custom_board(
                cell[0],
                cell[1],
                self.agent_number,
                reversi_board
            )
            self.__now_vector = self.__generate_vector_from_custom_board(
                self.agent_number,
                reversi_board
            )
            calc_value = self.forward()
            if max_value < calc_value:
                ret = index
                max_value = calc_value
            reversi_board[change_cells[0][0], change_cells[0][1]] = 0
            for change_cell in change_cells[1:]:
                reversi_board[change_cell[0]][change_cell[1]] = self.agent_number * -1
        return selectable_cells[ret]

    def __get_all_weight_array(self):
        return [self.__input_weight, self.__output_weight]

    def cross_over_one_point(self, add_agent):
        ret = NeuralNetworkGALeaningAgent(self.__is_ReLU)
        if not isinstance(add_agent, NeuralNetworkGALeaningAgent):
            raise Exception("this method same class as the argument")

        def array_concatenate(index, first_array, second_array):
            if random.randint(0, 1) == 0:
                return np.concatenate([first_array[:index], second_array[index:]])
            else:
                return np.concatenate([second_array[:index], first_array[index:]])

        ret_weight = []
        for my_weight, add_weight in zip(self.__get_all_weight_array(), add_agent.__get_all_weight_array()):
            shape_info = my_weight.shape
            first_weight = my_weight.reshape(shape_info[0] * shape_info[1])
            second_weight = add_weight.reshape(shape_info[0] * shape_info[1])
            new_weight = array_concatenate(
                random.randint(0, shape_info[0] * shape_info[1] - 1),
                first_weight,
                second_weight
            )
            ret_weight.append(new_weight.reshape(shape_info))
        ret.__input_weight = ret_weight[0]
        ret.__output_weight = ret_weight[1]
        return ret

    def normal_mutation(self):
        ret = self.copy()

        def mutation(array_weight):
            now_weight = copy.deepcopy(array_weight)
            shape_info = now_weight.shape
            now_weight = now_weight.reshape(shape_info[0] * shape_info[1])
            for i in range(0, 2):
                if self.__is_ReLU:
                    now_weight[random.randint(0, shape_info[0] * shape_info[1] - 1)] = 20 * random.random() - 10
                else:
                    now_weight[random.randint(0, shape_info[0] * shape_info[1] - 1)] = 2 * random.random() - 1

            now_weight = now_weight.reshape(shape_info)
            for first_index, inner_array in enumerate(now_weight):
                for second_index, value in enumerate(inner_array):
                    array_weight[first_index][second_index] = value

        mutation(ret.__input_weight)
        mutation(ret.__output_weight)
        return ret

    def save_weight_vector(self, file_path):
        np.save(file_path, np.array(self.__get_all_weight_array()))

    def load_weight_vector(self, file_path):
        weight_vector = np.load(file_path, allow_pickle=True)
        self.__input_weight = weight_vector[0]
        self.__output_weight = weight_vector[1]


class DQNAgent(Agent):
    @staticmethod
    def __generate_model():
        now_state_input = krs_layer.Input(shape=(8, 8, 1))
        action_state_input = krs_layer.Input(shape=(8, 8, 1))
        now_state_conv = krs_layer.Conv2D(32, (5, 5), strides=(2, 2), activation="relu", padding="same")(now_state_input)
        action_state_conv = krs_layer.Conv2D(32, (5, 5), strides=(2, 2), activation="relu", padding="same")(action_state_input)
        combined_layer = krs_layer.concatenate([now_state_conv, action_state_conv])
        combined_layer = krs_layer.Conv2D(64, (3, 3), strides=(3, 3), activation="relu", padding="same")(combined_layer)
        combined_layer = krs_layer.Conv2D(64, (3, 3), strides=(3, 3), activation="relu", padding="same")(combined_layer)
        combined_layer = krs_layer.Flatten()(combined_layer)
        last_layer = krs_layer.Dense(1, activation="relu")(combined_layer)
        rms_prop = krs_optimizers.RMSprop(lr=0.001, rho=0.9, epsilon=0.01, decay=0.0)
        model = krs_models.Model(inputs=[now_state_input, action_state_input], outputs=last_layer)
        model.compile(rms_prop, loss=krs_losses.Huber())
        return model

    @staticmethod
    def get_model_picture(file_path):
        krs_utils.plot_model(DQNAgent.__generate_model(), file_path, show_shapes=True)

    @staticmethod
    def setting_gpu():
        physical_devices = tf.config.experimental.list_physical_devices('GPU')
        if len(physical_devices) > 0:
            for k in range(len(physical_devices)):
                tf.config.experimental.set_memory_growth(physical_devices[k], True)

    def __init__(self, is_learning, batch_size=None, epsilon=None, gamma=None):
        self.setting_gpu()
        super().__init__("DQN", False)
        self.__q_network = self.__generate_model()  # q_network
        self.__t_network = self.__generate_model()  # target_network
        self.__is_learning = is_learning
        self.__EPSILON = epsilon
        self.__GAMMA = gamma
        self.__BATCH_SIZE = batch_size
        self.__before_reversi_board = None
        self.__replay_data = deque()

    def __get_q_value(self, now_state_input, action_state_input):
        first = np.array(now_state_input)
        first = first.reshape((1, 8, 8))
        second = np.array(action_state_input)
        second = second.reshape((1, 8, 8))
        return self.__t_network.predict_on_batch([first, second])[0]

    def __train_model(self, state_batch, calc_batch):
        self.__q_network.train_on_batch(state_batch, calc_batch)

    # From the state this agent was in.
    def __get_next_state_max_q_value(self, now_game_board):
        enemy_selectable_cells = game_board.GameBoard.get_selectable_cells_custom_board(
            self.agent_number * -1,
            now_game_board
        )
        accumulation_q_value = []

        def my_selectable_calc(enemy_game_board):
            nonlocal accumulation_q_value
            my_selectable_cells = game_board.GameBoard.get_selectable_cells_custom_board(
                self.agent_number,
                enemy_game_board
            )
            if len(my_selectable_cells) == 0:
                accumulation_q_value.append(self.__get_q_value(enemy_game_board, enemy_game_board))
            else:
                next_game_board = copy.deepcopy(now_game_board)
                for my_select_cell in my_selectable_cells:
                    my_change_cells = game_board.GameBoard.put_stone_custom_board(
                        my_select_cell[0],
                        my_select_cell[1],
                        self.agent_number,
                        next_game_board
                    )
                    accumulation_q_value.append(self.__get_q_value(enemy_game_board, next_game_board))
                    game_board.GameBoard.undo_put_stone_custom_board(my_change_cells, next_game_board)

        if len(enemy_selectable_cells) == 0:
            my_selectable_calc(now_game_board)
        else:
            for enemy_select_cell in enemy_selectable_cells:
                change_cells = game_board.GameBoard.put_stone_custom_board(
                    enemy_select_cell[0],
                    enemy_select_cell[1],
                    self.agent_number,
                    now_game_board
                )
                my_selectable_calc(now_game_board)
                game_board.GameBoard.undo_put_stone_custom_board(change_cells, now_game_board)
        return max(accumulation_q_value)

    def __get_action(self, epsilon):
        my_selectable_cells = self.belong_game_board.get_selectable_cells(self.agent_number)
        if random.random() < epsilon:
            return my_selectable_cells[random.randint(0, len(my_selectable_cells) - 1)]
        next_game_board = copy.deepcopy(self.belong_game_board.reversi_board)
        ret = 0
        max_value = -1000
        for index, select_cell in enumerate(my_selectable_cells):
            change_cells = game_board.GameBoard.put_stone_custom_board(
                select_cell[0],
                select_cell[1],
                self.agent_number,
                next_game_board
            )
            now_value = self.__get_q_value(
                self.belong_game_board.reversi_board,
                next_game_board
            )[0]
            if max_value < now_value:
                ret = index
                max_value = now_value
            game_board.GameBoard.undo_put_stone_custom_board(change_cells, next_game_board)
        return my_selectable_cells[ret]

    def __save_action(self, reward):
        if len(self.__replay_data) == self.__BATCH_SIZE * 2:
            self.__replay_data.popleft()
        max_value = self.__get_next_state_max_q_value(copy.deepcopy(self.belong_game_board.reversi_board))
        update_value = reward + self.__GAMMA * max_value
        self.__replay_data.append(
            [
                np.array(self.__before_reversi_board),
                np.array(self.belong_game_board.reversi_board),
                update_value
            ]
        )

    def __generate_batch(self):
        batch_data = random.sample(self.__replay_data, self.__BATCH_SIZE)
        first_batch, second_batch, update_value = map(np.array, zip(*batch_data))
        state_batch = [first_batch, second_batch]
        return state_batch, update_value

    def receive_update_signal(self):
        if not self.__is_learning:
            return
        if self.belong_game_board.turn_agent_number == self.agent_number:
            self.__save_action(0)
            if len(self.__replay_data) < self.__BATCH_SIZE:
                return
            state_batch, update_value = self.__generate_batch()
            self.__train_model(state_batch, update_value)

    def receive_game_end_signal(self):
        if not self.__is_learning:
            return 
        self.__before_reversi_board = copy.deepcopy(self.belong_game_board.reversi_board)
        if self.belong_game_board.check_game_end() == self.agent_number:
            self.__save_action(1)
        elif self.belong_game_board.check_game_end() == 2:
            self.__save_action(0)
        else:
            self.__save_action(-1)
        state_batch, update_value = self.__generate_batch()
        self.__train_model(state_batch, update_value)

    def next_step(self):
        self.__before_reversi_board = copy.deepcopy(self.belong_game_board.reversi_board)
        return self.__get_action(self.__EPSILON if self.__is_learning else 0)

    def weight_copy(self):
        self.__q_network.save_weights("temp.hdf5")
        self.__t_network.load_weights("temp.hdf5")

    def save_weight(self, file_path):
        self.__t_network.save_weights(file_path + ".h5")

    def save(self, file_path):
        self.__t_network.save(file_path + ".h5")

    def load_weight(self, file_path):
        self.__t_network.load_weights(file_path + ".h5")

    def load(self, file_path):
        self.__t_network = krs_models.load_model(file_path + ".h5")

    def copy(self):
        ret = DQNAgent(self.__is_learning, self.__BATCH_SIZE, self.__EPSILON, self.__GAMMA)
        ret.__t_network.set_weights(self.__t_network.get_weights())
        return ret
