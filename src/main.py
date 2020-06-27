import game_board
import agent

if __name__ == '__main__':
    first_agent = agent.HumanAgent("First")
    second_agent = agent.HumanAgent("Second")
    game = game_board.GameBoard(first_agent, second_agent)
    game.game_start()