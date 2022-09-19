import pickle
import os

data = os.listdir("/home/data/xx")
data_list = []
for l in data:
    data_list.append(l)
with open("data_list_name.pkl","wb") as f:
    pickle.dump(data_list,f)