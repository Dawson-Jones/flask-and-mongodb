import time
from yoozen_db.basic.db import *


def agg():
    limit = list(el_config_collection.aggregate([
        {'$match': {'cell_type': 'mono'}},
        {'$group': {
            '_id': '$display_mode',
            'limit': {'$sum': 1}
        }}
    ]))
    print(limit)
    return 'yes'

inserted_id
def query():
    res = panel_collection.find({}).sort('create_time', -1)
    print(len(list(res)))


if __name__ == '__main__':
    query()

