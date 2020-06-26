from abc import ABCMeta, abstractmethod


class Agent(metaclass=ABCMeta):
    def __init__(self):
        self.__agent_number = None

    @abstractmethod
    def next_step(self, board):
        pass

    @property
    def agent_number(self):
        return self.__agent_number

    @agent_number.setter
    def agent_number(self, value):
        self.__agent_number = value
