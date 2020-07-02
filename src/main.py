import learn
import agent

if __name__ == '__main__':
    now = learn.NNGALearning(10000)
    now.start("../data/NNGA-2/NNGA-", 200)
    now.save_data_generation_average("../data/NNGA-2/NNGA-data-")