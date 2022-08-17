from pymongo import MongoClient
import pymongo

client = MongoClient('localhost', 27017)
db = client['survey']
members = db["members"]

docs = members.find()

for i in docs:
    print(i["id"])

