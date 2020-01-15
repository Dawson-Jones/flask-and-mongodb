from pymongo import MongoClient
from ..config import PYMONGO_DATABASE_URL

client = MongoClient(PYMONGO_DATABASE_URL, serverSelectionTimeoutMS=5)
db = client['tttt']

user_collection = db['user']
user_log_collection = db['user_log']
permission_collection = db['permission']
el_config_collection = db['el_config']
el_string_collection = db['el_string']
gui_setting_collection = db['gui_setting']
panel_collection = db['panel']
test_collection = db['test']


test_collection.insert()
