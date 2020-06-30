import learn

if __name__ == '__main__':
    now = learn.QLearning(10000)
    now.start("../data/2020-06-30-Q-1/Q-", 1000)
    now.save_data_trajectory("../data/2020-06-30-Q-1/Q-data")