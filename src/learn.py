import game_board
import agent
import random


class GALearn:
    def __init__(self, evolve_times):
        self.__NUMBER_INDIVIDUALS = 20  # more than 10
        self.__EVOLVE_TIMES = evolve_times
        self.__now_generation = []
        for number in range(0, self.__NUMBER_INDIVIDUALS):
            self.__now_generation.append([agent.GABoardAgent(), 0])
            self.__now_generation[number][0].set_random_evaluation_board()

    # calc expectation value
    def __battle_random_agent(self):
        for index in range(0, self.__NUMBER_INDIVIDUALS):
            print(index)
            for times in range(0, 100):
                temp = agent.RandomAgent()
                game = game_board.GameBoard(self.__now_generation[index][0], temp)
                game.game_start()
                if game.check_game_end() == -1:
                    self.__now_generation[index][1] += 1

    def __generation_sort(self):
        self.__now_generation.sort(key=lambda x: x[1], reverse=True)

    def __update_generation(self):
        self.__battle_random_agent()
        self.__generation_sort()
        ret = [[self.__now_generation[0], 0], [self.__now_generation[1], 0]]
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
            else:
                ret.append([select_elite.plus_mutation(), 0])

    def start(self):
        for times in range(0, self.__EVOLVE_TIMES):
            self.__update_generation()
            print(times + 1, self.__now_generation[0][1], sep=' ')
