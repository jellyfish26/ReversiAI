import game_board
import tqdm
import concurrent.futures


def output_match_result(times, count, first_agent, second_agent):
    print("Number of trials %d" % times)
    print("win(%s): %d, win(%s): %d, draw: %d" % (
        first_agent.agent_name, count[0], second_agent.agent_name, count[2], count[1]))


def battle_start_parallelization(times, first_agent, second_agent):
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
        game_result = end_game.result()[0] + 1
        if game_result == 3:
            game_result = 1
        count[game_result] += 1
        progress_bar.update(1)
    progress_bar.close()
    output_match_result(times, count, first_agent, second_agent)


def battle_start(times, first_agent, second_agent):
    progress_bar = tqdm.tqdm(total=times)
    count = [0, 0, 0]
    for index in range(0, times):
        game = game_board.GameBoard(first_agent, second_agent)
        game_result = game.game_start()[0] + 1
        if game_result == 3:
            game_result = 1
        count[game_result] += 1
        progress_bar.update(1)
    progress_bar.close()
    output_match_result(times, count, first_agent, second_agent)
