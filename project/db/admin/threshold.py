from . import app
from flask import request
from yoozen_db.yc_database import YcDataBase

yc_db = YcDataBase()


@app.route('/thresholds/modify', methods=['POST'])
def modify_thresholds():
    data = request.get_json()
    return yc_db.el_panel_thresholds_modify(data)
