from pymongo import MongoClient
import pymongo
import csv

client = MongoClient('localhost', 27017)
db = client['survey']
collection = db.members

sid = ["S119", "S501"]

f = open("members.csv", "w")
s = collection.estimated_document_count()


for i in sid:
    docs = collection.find({})

    for doc in docs:
        f.write(doc["id"] + '\n')

print(s)  
