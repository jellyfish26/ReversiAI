import learn
import agent

if __name__ == '__main__':
    now = learn.QLearning(2000)
    partner = agent.RandomAgent()
    now.start("../data/2020-06-30-Q-4/Q-", 200, True, partner)
    now.save_data_trajectory("../data/2020-06-30-Q-4/Q-data")