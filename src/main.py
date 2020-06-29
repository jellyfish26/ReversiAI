import learn

if __name__ == '__main__':
    now = learn.GALearn(200)
    now.start("../data/2020-06-29-GA-3/GA-", 50)
    now.save_data_generation_average("../data/2020-06-29-GA-3/GA-data")