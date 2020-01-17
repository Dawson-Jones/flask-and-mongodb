from flask import request
from . import api
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



