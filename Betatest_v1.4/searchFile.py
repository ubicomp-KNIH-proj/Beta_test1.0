from pymongo import MongoClient
import pymongo
import csv

client = MongoClient('localhost', 27017)
db = client['survey']

sid = ["S119", "S501"]
s = []
f = open("bigdata_KNIH.csv", "w")

for i in sid:
    collection = db[i]
    collection_mood = db[i].files

    docs = collection.files.find({})
    docs_mood = collection.find({})

    s.append(collection.estimated_document_count())
    s.append(collection_mood.estimated_document_count())

    f.write(i + '\n')
    for doc in docs:
        f.write(doc["filename"] + ',' + str(doc["uploadDate"]) + '\n')

print(s)  
