import game_board
import agent
import tqdm
import concurrent.futures


def battle_start(times, first_agent, second_agent):
    progress_bar = tqdm.tqdm(total=times)
    executor = concurrent.futures.ProcessPoolExecutor()
    waiting_queue = []
    count = [0, 0, 0]
    for index in range(0, times):
        first_copy = first_agent.copy()
        second_copy = second_agent.copy()
        game = game_board.GameBoard(first_copy, second_copy)
        waiting_queue.append(executor.submit(game.game_start))
    for end_game in concurrent.futures.as_completed(waiting_queue):
        game_result = end_game.result() + 1
        if game_result == 3:
            game_result = 1
        count[game_result] += 1
        progress_bar.update(1)
    progress_bar.close()
    print("Number of trials %d" % times)
    print("win(%s): %d, win(%s): %d, draw: %d" % (
        first_agent.agent_name, count[0], second_agent.agent_name, count[2], count[1]))


if __name__ == '__main__':
    trials = int(input())
    one_agent = agent.QLeaningAgent(False)
    one_agent.load_weight_vector("../data/Q-self-1/Q-2000.npy")
    two_agent = agent.QLeaningAgent(False)
    two_agent.load_weight_vector("../data/Q-self-1/Q-200-rev.npy")
    battle_start(trials, one_agent, two_agent)
