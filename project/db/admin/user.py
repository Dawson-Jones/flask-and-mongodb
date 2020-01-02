from flask import request
from . import app
from yoozen_db.yc_database import YcDataBase

yc_db = YcDataBase()


@app.route('/user/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    return yc_db.user_login_admin(data)


@app.route('/user/add', methods=['POST'])
def add_user():
    data = request.get_json()
    return yc_db.user_add(data)


@app.route('/user/delete', methods=['POST'])
def delete_user():
    data = request.get_json()
    return yc_db.user_delete(data)


@app.route('/user/modify', methods=['POST'])
def modify_user():
    data = request.get_json()
    return yc_db.user_modify(data)


@app.route('/user/display', methods=['GET'])
def user_display():
    return yc_db.user_display


@app.route('/permission/modify', methods=['POST'])
def modify_permission():
    data = request.get_json()
    return yc_db.permission_modify(data)
