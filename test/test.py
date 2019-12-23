from pymongo import MongoClient

# MongoDB的客户端
client = MongoClient("localhost", 27011)
# MongoDB database
db = client['jdq_db']
# collection 相当于 table
collection = db['jdq_tb']

# res = collection.find()
# print(res[0])

name = ['chen', 'zy', 'gg', 'hb', 'ql', 'xy', 'dq']

dd = [{'name': i} for i in name]

res = collection.insert_many(dd)
print(res.inserted_ids)
