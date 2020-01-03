from flask import jsonify, Response
from project.db.panel import api


# from yoozen_db.yc_database import YcDataBase

# yc_db = YcDataBase()


@api.route('/jj')
def jj():
    return Response('1', content_type='application/json')


@api.route('/<re(r".*"):name>')
def html(name):
    return 'hello, {}'.format(name), 200, {'Content-Type': 'application/json'}


@api.route('/barcode/find/<int:barcode>')
def barcode_find(barcode):
    result = panel_collection.find_one({"barcode": barcode}, {"_id": 0})
    return jsonify(result)


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
