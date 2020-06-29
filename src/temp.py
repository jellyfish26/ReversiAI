import numpy as np
import game_board
import agent

if __name__ == '__main__':
    first = agent.HumanAgent("first")
    second = agent.GABoardAgent()
    second.load_evaluation_board("../data/GA-200.npy")
    game = game_board.GameBoard(first, second)
    game.game_start()