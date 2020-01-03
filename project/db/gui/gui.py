from flask import request
from . import app
from yoozen_db.yc_database import YcDataBase

yc_db = YcDataBase()


@app.route('/config/check', methods=['POST'])
def check_gui_config():
    data = request.get_json()
    yc_db.gui_config_check(data)


@app.route('/config/modify', methods=['POST'])
def modify_config():
    data = request.get_json()
    yc_db.gui_config_modify(data)


@app.route('/user/login', methods=['POST'])
def operator_login():
    data = request.get_json()
    yc_db.user_login_operator(data)
