from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['survey']
members = db["members"]

while True:
    sid = 'S' + str(input("Enter SID (Only number) : "))

    members.delete_one({ "id": sid })

    collection = db[sid]

    collection.drop() # Sxxx
    collection.files.drop() # Sxxx.files
    collection.chunks.drop() # Sxxx.chunks
