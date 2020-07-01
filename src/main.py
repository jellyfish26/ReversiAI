import learn
import agent

if __name__ == '__main__':
    now = learn.QLearning(3000)
    first = agent.QLeaningAgent(True)
    second = agent.QLeaningAgent(True)
    now.start("../data/Q-self-2/Q-", 200, first, second)
    now.save_data_trajectory("../data/Q-self-2/Q-data")