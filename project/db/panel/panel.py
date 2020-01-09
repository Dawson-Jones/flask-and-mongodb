import time
from flask import request, jsonify
from . import api
from log_manager import logger
from yoozen_db.basic.db import *
from project.utils.response_code import RET
from yoozen_db.yc_database import YcDataBase

yc_db = YcDataBase()


@api.route('/send_db', methods=['POST'])
def add_panel():
    data = request.get_json()
    return yc_db.panel_add(data)


@api.route('/mes_defects/update', methods=['POST'])
def mes_defects_update():
    data = request.get_json()
    return yc_db.mes_defects_update(data)


@api.route('/config/check', methods=['POST'])
def check_panel_config():
    data = request.get_json()
    return yc_db.el_panel_config_check(data)


@api.route('/config/modify', methods=['POST'])
def modify_panel_config():
    data = request.get_json()
    return yc_db.el_panel_config_modify(data)


@api.route('/thresholds/modify', methods=['POST'])
def modify_thresholds():
    data = request.get_json()
    return yc_db.el_panel_thresholds_modify(data)


@api.route('/find')
def panel_check():
    hours = request.args.get('hours', '4')
    try:
        hours = int(hours)
    except Exception as e:
        logger.error(e)
        return jsonify(resno=RET.PARAMERR, msg='param must be a integer')
    res = panel_collection.find({"create_time": {"$gt": time.time() - hours * 3600}}, {'_id': 0})
    res.sort('create_time', -1)
    res = list(res)
    if not res:
        return jsonify(resno=RET.NODATA, msg='there is no matching data')
    for i in res:
        num = panel_collection.count_documents({'barcode': i['barcode'], "create_time": {
            '$lte': i['create_time']
        }})
        # print(f'{i["barcode"]}: {num}')
        i['times_of_storage'] = num
    return jsonify(resno=RET.OK, msg=res)
