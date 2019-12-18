import json
from flask import jsonify
from project.panel import api
from yoozen_db.yc_database import YcDataBase

yc_db = YcDataBase()


@api.route('/')
def index():
    return 'hello, world'


@api.route('/<re(r".*"):name>')
def html(name):
    return 'hello, {}'.format(name)


@api.route('/test')
def test():
    return yc_db.user_display()

# @api.route('/agg')
# def agg():
#     el_config_collection = db['el_config']
#     limit = list(el_config_collection.aggregate([
#         {'$match': {'gui_no': 'op0'}},
#         {'$group': {
#             '_id': '$gui_no',
#             'limit': {'$sum': 1}
#         }}
#     ]))
#     print(limit)
#     return 'yes'
