import game_board
import agent

if __name__ == '__main__':
    first_agent = agent.HumanAgent("First")
    second_agent = agent.GABoardAgent()
    second_agent.set_random_evaluation_board()
    game = game_board.GameBoard(first_agent, second_agent)
    game.game_start()
