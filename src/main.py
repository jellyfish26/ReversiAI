import learn
import agent

if __name__ == '__main__':
    now = learn.QLearning(2000)
    first = agent.QLeaningAgent(True)
    second = agent.QLeaningAgent(True)
    now.start("../data/Q-self-1/Q-", 200, first, second)