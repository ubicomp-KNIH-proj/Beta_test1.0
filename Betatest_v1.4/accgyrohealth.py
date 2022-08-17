from pymongo import MongoClient
import pymongo

# S119, S501 빅데이터공학과 2명 각속도, 가속도 개수

client = MongoClient('localhost', 27017)
db = client['survey']

sid = ["S119", "S501"]
s = []

counted = [0, 0, 0]
counting = [0, 0, 0]
other_file = []
other_file2 = []


for i in sid:
    collection = db[i]
    collection_mood = db[i].files

    docs = collection.files.find({})
    docs_mood = collection.find({})

    s.append(collection.estimated_document_count())
    s.append(collection_mood.estimated_document_count())

    for doc in docs:
        file_name = str(doc["filename"])
        attached_date = str(doc["uploadDate"])

        file_type = file_name.split('_')[1]

        if i == sid[0]:
            if file_type == "accelerometer" or file_type == "acceleration":
                counted[0] = counted[0] + 1
            elif file_type == "acceleration1" or file_type == "acceleration2":
                counted[0] = counted[0] + 1  
            elif file_type == "gyroscope" or file_type == "gyroscope1" or file_type == "gyroscope2":
                counted[1] = counted[1] + 1  
            else:
                counted[2] = counted[2] + 1
                other_file.append(file_type)

        if i == sid[1]:
            if file_type == "accelerometer" or file_type == "acceleration":
                counting[0] = counting[0] + 1  
            elif file_type == "acceleration1" or file_type == "acceleration2":
                counting[0] = counting[0] + 1 
            elif file_type == "gyroscope" or file_type == "gyroscope1" or file_type == "gyroscope2":
                counting[1] = counting[1] + 1  
            else:
                counting[2] = counting[2] + 1
                other_file2.append(file_type)
        
        

print(sid[0] + ":  " + str(counted))
print(sid[1] + ":  " + str(counting))  
print(other_file)
print(other_file2)

