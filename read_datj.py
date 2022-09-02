#read json or datj file

import json

f = open("C:/CPI/cad/AOITestBoard_new.datj")

data = json.load(f)

for i in data["device"]:
    print(i['id'])
# print(data["device"][0])