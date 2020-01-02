from flask import request
from . import app
from yoozen_db.yc_database import YcDataBase

yc_db = YcDataBase()


@app.route('/config/check', methods=['POST'])
def check_gui_config():
    data = request.get_json()
    yc_db.gui_config_check(data)
