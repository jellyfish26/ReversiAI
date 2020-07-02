import game_board
import agent
import random
import tqdm
import numpy as np
import concurrent.futures


class GALearning:
    def __init__(self, evolve_times):
        self.__NUMBER_INDIVIDUALS = 20  # more than 10
        self.__NUMBER_BATTLES = 40
        self.__EVOLVE_TIMES = evolve_times
        self.__now_generation = []
        self.__progress_bar = None
        self.__data_generation_average = []
        for number in range(0, self.__NUMBER_INDIVIDUALS):
            self.__now_generation.append([agent.GABoardAgent(), 0])
            self.__now_generation[number][0].set_random_evaluation_board()

    # calc expectation value
    def __battle_random_agent(self):
        executor = concurrent.futures.ProcessPoolExecutor()
        for index in range(0, self.__NUMBER_INDIVIDUALS):
            waiting_queue = []
            for times in range(0, self.__NUMBER_BATTLES):
                first = self.__now_generation[index][0].copy()
                second = agent.RandomAgent()
                game = game_board.GameBoard(first, second)
                waiting_queue.append(executor.submit(game.game_start))
            for end_task in concurrent.futures.as_completed(waiting_queue):
                self.__progress_bar.update(1)
                if end_task.result() == -1:
                    self.__now_generation[index][1] += 2
                elif end_task.result() == 2:
                    self.__now_generation[index][1] += 1
        executor.shutdown()

    def __generation_sort(self):
        self.__now_generation.sort(key=lambda x: x[1], reverse=True)

    # before exec generation_sort method
    def __update_generation(self):
        ret = [[self.__now_generation[0][0], 0], [self.__now_generation[1][0], 0]]
        for times in range(2, self.__NUMBER_INDIVIDUALS):
            select_elite = self.__now_generation[random.randint(0, 1)][0]
            select_another = self.__now_generation[random.randint(2, self.__NUMBER_INDIVIDUALS - 1)][0]
            probability = random.randint(0, 99)
            if probability < 40:
                ret.append([select_elite.cross_over_one_point(select_another), 0])
            elif probability < 80:
                ret.append([select_elite.cross_over_uniform(select_another), 0])
            elif probability < 90:
                ret.append([select_elite.normal_mutation(), 0])
            elif probability < 95:
                ret.append([select_elite.plus_mutation(1, 25), 0])
            else:
                ret.append([select_elite.plus_mutation(-15, -1), 0])
        self.__now_generation = ret

    def __calc_generation_average(self):
        ret = 0.0
        for now in self.__now_generation:
            ret += now[1]
        return ret / self.__NUMBER_INDIVIDUALS

    def save_data_generation_average(self, file_path):
        np.save(file_path, np.array(self.__data_generation_average))

    def start(self, file_path, save_interval):
        self.__progress_bar = tqdm.tqdm(total=self.__NUMBER_BATTLES * self.__NUMBER_INDIVIDUALS * self.__EVOLVE_TIMES)
        self.__progress_bar.set_description('learning ' + str(self.__EVOLVE_TIMES) + ' generations...')
        for times in range(1, self.__EVOLVE_TIMES + 1):
            if times != 1:
                self.__update_generation()
            self.__battle_random_agent()
            self.__generation_sort()
            self.__data_generation_average.append(self.__calc_generation_average())
            if times % save_interval == 0:
                self.__now_generation[0][0].save_evaluation_board(file_path + str(times))
        self.__progress_bar.close()


class QLearning:
    def __init__(self, evolve_times):
        self.__EVOLVE_TIMES = evolve_times
        self.__progress_bar = None
        self.__learning_data = []

    def save_data_trajectory(self, file_path):
        np.save(file_path, np.array(self.__learning_data))

    def start(self, file_path, save_interval, first_agent, second_agent):
        if (not isinstance(first_agent, agent.Agent)) or (not isinstance(second_agent, agent.Agent)):
            raise Exception("The object of learning must be an Agent Class.")
        self.__progress_bar = tqdm.tqdm(total=self.__EVOLVE_TIMES)
        self.__progress_bar.set_description('learning ' + str(self.__EVOLVE_TIMES) + ' times...')
        for times in range(1, self.__EVOLVE_TIMES + 1):
            if isinstance(first_agent, agent.QLeaningAgent):
                first = first_agent
            else:
                first = first_agent.copy()
            if isinstance(second_agent, agent.QLeaningAgent):
                second = second_agent
            else:
                second = second_agent.copy()
            game = game_board.GameBoard(first, second)
            game.game_start()
            self.__learning_data.append([game.count_stones(-1), game.count_stones(1)])
            if times % save_interval == 0:
                if isinstance(first_agent, agent.QLeaningAgent):
                    first_agent.save_weight_vector(file_path + str(times))
                if isinstance(second_agent, agent.QLeaningAgent):
                    second_agent.save_weight_vector(file_path + str(times) + "-rev")
            self.__progress_bar.update(1)
        self.__progress_bar.close()


class NNGALearning:
    def __init__(self, evolve_times):
        self.__NUMBER_INDIVIDUALS = 20  # more than 10
        self.__NUMBER_MUTATION = 4
        self.__EVOLVE_TIMES = evolve_times
        self.__now_generation = []
        self.__data_generation_average = []
        self.__progress_bar = None
        for number in range(0, self.__NUMBER_INDIVIDUALS):
            self.__now_generation.append([agent.NeuralNetworkGALeaningAgent(), 0])

    def __battle_all_agent(self):
        executor = concurrent.futures.ProcessPoolExecutor()
        waiting_queue = []
        for index in range(0, self.__NUMBER_INDIVIDUALS):
            for times in range(0, self.__NUMBER_INDIVIDUALS):
                if times == index:
                    continue
                first = self.__now_generation[index][0].copy()
                second = self.__now_generation[times][0].copy()
                game = game_board.GameBoard(first, second)
                waiting_queue.append(executor.submit(game.game_start, (index, times)))
        for end_task in concurrent.futures.as_completed(waiting_queue):
            self.__progress_bar.update(1)
            if end_task.result()[0] == -1:
                self.__now_generation[end_task.result()[1][0]][1] += 1
            elif end_task.result()[0] == 1:
                self.__now_generation[end_task.result()[1][1]][1] += 1
        executor.shutdown()

    def __generation_sort(self):
        self.__now_generation.sort(key=lambda x: x[1], reverse=True)

    def __update_generation(self):
        ret = [[self.__now_generation[0][0], 0], [self.__now_generation[1][0], 0]]
        for times in range(2, self.__NUMBER_INDIVIDUALS - self.__NUMBER_MUTATION):
            select_elite = self.__now_generation[random.randint(0, 1)][0]
            select_another = self.__now_generation[random.randint(2, self.__NUMBER_INDIVIDUALS - 1)][0]
            ret.append([select_elite.cross_over_one_point(select_another), 0])
        for times in range(0, self.__NUMBER_MUTATION):
            select_agent = self.__now_generation[random.randint(0, self.__NUMBER_INDIVIDUALS -1)][0]
            ret.append([select_agent.normal_mutation(), 0])
        self.__now_generation = ret

    def __calc_generation_average(self):
        ret = 0.0
        for now in self.__now_generation:
            ret += now[1]
        return ret / self.__NUMBER_INDIVIDUALS

    def save_data_generation_average(self, file_path):
        np.save(file_path, np.array(self.__data_generation_average))

    def start(self, file_path, save_interval):
        self.__progress_bar = tqdm.tqdm(total=self.__NUMBER_INDIVIDUALS * self.__NUMBER_INDIVIDUALS * self.__EVOLVE_TIMES)
        self.__progress_bar.set_description('learning ' + str(self.__EVOLVE_TIMES) + ' generations...')
        for times in range(1, self.__EVOLVE_TIMES + 1):
            if times != 1:
                self.__update_generation()
            self.__battle_all_agent()
            self.__generation_sort()
            self.__data_generation_average.append(self.__calc_generation_average())
            if times % save_interval == 0:
                self.__now_generation[0][0].save_weight_vector(file_path + str(times))
        self.__progress_bar.close()
