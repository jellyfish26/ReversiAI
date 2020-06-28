from abc import ABCMeta, abstractmethod, ABC
import control_panel
import game_board
import random


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
    def __init__(self, agent_name):
        super().__init__(agent_name, False)

    def receive_update_signal(self):
        pass

    def receive_game_end_signal(self):
        pass

    def next_step(self):
        selectable = self.belong_game_board.get_selectable_cells(self.agent_number)
        index = random.randint(0, len(selectable) - 1)
        return selectable[index]


# Learning the board
class GALearningBoardAgent(Agent, ABC):
    def __init__(self, agent_name):
        super().__init__(agent_name, False)

    def receive_update_signal(self):
        pass

    def receive_game_end_signal(self):
        pass

    def next_step(self):
        pass
