from abc import ABCMeta, abstractmethod


class Agent(metaclass=ABCMeta):
    def __init__(self, game_board):
        self.__belong_game_board = game_board
        self.__agent_number = 0

    @property
    def belong_game_board(self):
        return self.__belong_game_board

    @abstractmethod
    def accept_update(self):
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


class HumanAgent(Agent):
    def __init__(self, game_board):
        super().__init__(game_board)

    def accept_update(self):
        pass

    def next_step(self):
        pass
