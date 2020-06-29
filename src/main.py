import learn

if __name__ == '__main__':
    now = learn.GALearn(10)
    now.start("../data/2020-06-29-GA-2/GA-", 1)
    now.save_data_generation_average("../data/2020-06-29-GA-2/GA-data")