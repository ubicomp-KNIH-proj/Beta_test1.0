from pymongo import MongoClient
import gridfs
import pymongo

client = MongoClient('localhost', 27017)
db = client['survey']

print(db.list_collection_names())
coll = 'S999'
fs = gridfs.GridFS(db, collection=coll)

# file = "data.csv"

# with open(file, 'rb') as f:
#     contents = f.read()

for grid_out in fs.find({"filename": "data.csv"}):
    data = grid_out.read().decode()

    print(data)

