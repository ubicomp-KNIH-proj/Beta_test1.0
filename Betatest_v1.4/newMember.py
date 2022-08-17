from pymongo import MongoClient
import csv

client = MongoClient('localhost', 27017)
db = client['survey']
members = db["members"]

while True:
    memb = []
    f = open('members.csv', 'r')
    reader = csv.reader(f)

    for line in reader:
        memb.append(line[0])

    f.close()
    sid = members.find()

    for doc in sid:
        f = open('members.csv', 'a+')

        if doc["id"] not in memb:
            print("Welcome " + doc["id"])
            f.write(doc["id"] + '\n')
            f.close()
            break

    


