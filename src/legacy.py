import agent
import copy
import game_board
import numpy as np
import random


class NeuralNetworkGALeaningAgent(agent.Agent):
    def __init__(self):
        super().__init__("LegacyNNGA", False)
        self.__now_vector = np.zeros(64)
        self.__input_weight = np.random.rand(64, 100)
        self.__middle_one_weight = np.random.rand(100, 50)
        self.__middle_two_weight = np.random.rand(50, 20)
        self.__output_weight = np.random.rand(20, 1)

    # under about Neural Network
    @staticmethod
    def sigmoid(x):
        return (np.tanh(x / 2) + 1) / 2

    # forward propagation
    def forward(self):
        # input layer
        now_layer = copy.deepcopy(self.__now_vector)
        # first middle layer
        now_layer = np.dot(now_layer, self.__input_weight)
        now_layer = self.sigmoid(now_layer)
        # second middle layer
        now_layer = np.dot(now_layer, self.__middle_one_weight)
        now_layer = self.sigmoid(now_layer)
        # third middle layer
        now_layer = np.dot(now_layer, self.__middle_two_weight)
        now_layer = self.sigmoid(now_layer)
        # output layer
        now_layer = np.dot(now_layer, self.__output_weight)
        return now_layer[0]

    # end Neural Network

    @staticmethod
    def __generate_vector_from_custom_board(agent_number, custom_reversi_board):
        vector = custom_reversi_board.reshape(64)
        # my_stones = game_board.GameBoard.count_stones_custom_board(agent_number, custom_reversi_board)
        # enemy_stones = game_board.GameBoard.count_stones_custom_board(agent_number * -1, custom_reversi_board)
        # add_vector = np.array([my_stones - enemy_stones, 64 - my_stones - enemy_stones])
        if agent_number == 1:
            vector *= -1
        # return np.concatenate([vector, add_vector])
        return vector

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
        return [self.__input_weight, self.__middle_one_weight, self.__middle_two_weight, self.__output_weight]

    def cross_over_one_point(self, add_agent):
        ret = NeuralNetworkGALeaningAgent()
        if not isinstance(add_agent, NeuralNetworkGALeaningAgent):
            raise Exception("this method same class as the argument")

        def array_bound(index, first_array, second_array):
            if random.randint(0, 1) == 0:
                return np.concatenate([first_array[:index], second_array[index:]])
            else:
                return np.concatenate([second_array[:index], first_array[index:]])

        ret_weight = []
        for my_weight, add_weight in zip(self.__get_all_weight_array(), add_agent.__get_all_weight_array()):
            shape_info = my_weight.shape
            first_weight = my_weight.reshape(shape_info[0] * shape_info[1])
            second_weight = my_weight.reshape(shape_info[0] * shape_info[1])
            new_weight = array_bound(random.randint(0, shape_info[0] * shape_info[1] - 1), first_weight, second_weight)
            ret_weight.append(new_weight.reshape(shape_info))
        ret.__input_weight = ret_weight[0]
        ret.__middle_one_weight = ret_weight[1]
        ret.__middle_two_weight = ret_weight[2]
        ret.__output_weight = ret_weight[3]
        return ret

    def normal_mutation(self):
        ret = self.copy()

        def mutation(array_weight):
            now_weight = copy.deepcopy(array_weight)
            shape_info = now_weight.shape
            now_weight = now_weight.reshape(shape_info[0] * shape_info[1])
            for i in range(0, 3):
                now_weight[random.randint(0, shape_info[0] * shape_info[1] - 1)] = random.random()
            now_weight = now_weight.reshape(shape_info)
            for first_index, inner_array in enumerate(now_weight):
                for second_index, value in enumerate(inner_array):
                    array_weight[first_index][second_index] = value
        mutation(ret.__input_weight)
        mutation(ret.__middle_one_weight)
        mutation(ret.__middle_two_weight)
        mutation(ret.__output_weight)
        return ret

    def save_weight_vector(self, file_path):
        np.save(file_path, np.array(self.__get_all_weight_array()))

    def load_weight_vector(self, file_path):
        weight_vector = np.load(file_path, allow_pickle=True)
        self.__input_weight = weight_vector[0]
        self.__middle_one_weight = weight_vector[1]
        self.__middle_two_weight = weight_vector[2]
        self.__output_weight = weight_vector[3]
