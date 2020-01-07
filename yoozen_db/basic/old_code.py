import time
import csv
import json

from log_manager import logger
from .db import (
    user_collection, user_log_collection, permission_collection, panel_collection,
    el_string_collection, gui_setting_collection, el_config_collection
)
from ..utils.const_def import (
    CELL_AMOUNT_COLLECTION, CELL_SHAPE_COLLECTION, CELL_TYPE_COLLECTION, AI_RESULT,
    DEFECT_TYPE_COLLECTION, GUI_RESULT, PANEL_LIMIT
)

with open('./SETUP/url.csv', 'r', newline='') as f:
    reader = csv.DictReader(f)
    for csv_url in reader:
        url = csv_url


def user_display():
    res = dict()
    res['user'] = list(
        user_collection.find({'type': {'$ne': 'yc_admin'}, 'activate': 1}, {'_id': 0, "user_pw": 0, "activate": 0}))
    return json.dumps(res), 200


def user_login_operator(info: dict):
    user_name = info.get('user_name')
    user_pw = info.get('user_pw')
    time = info.get('time')
    if not all([user_name, user_pw, time]):
        logger.error('incomplete params')
        return 'incomplete params', 421

    user_check = user_collection.find_one(
        {"user_name": user_name, "user_pw": user_pw, "activate": 1})
    if user_check:
        user_log_collection.insert_one({'user_id': user_check['_id'], 'user_name': user_name,
                                        'time': time, 'action': 'login_%s' % user_name})
        logger.info("login_%s" % user_name)
        return user_check['type'], 200
    else:
        logger.error("user:%s didn't exist" % user_name)
        return 'login failed', 421


def user_login_admin(info: dict):
    res = dict()
    user_name = info.get('user_name')
    user_pw = info.get('user_pw')
    time = info.get('time')
    admin_url = info.get('admin_url')
    if not all([user_name, user_pw, time, admin_url]):
        logger.error('incomplete params')
        return 'incomplete params', 421

    user_check = user_collection.find_one(
        {"user_name": user_name, "user_pw": user_pw, "activate": 1})
    if not user_check:
        logger.error("user:%s didn't exist" % user_name)
        return "user didn't exist", 421
    if user_check['type'] == 'operator':
        return "not admin", 421
    user_log_collection.insert_one({'user_id': user_check['_id'], 'user_name': user_name, 'time': time,
                                    'action': "login_%s" % user_name})

    res['type'] = user_check['type']
    # TODO: don't understand
    pre_url = url.get(admin_url)
    res['previous_url'] = user_check.get("previous_url") if user_check.get('previous_url') != pre_url else ''

    user_check['previous_url'] = pre_url
    user_collection.replace_one({'user_name': user_name, 'activate': 1}, user_check)
    res['permission_mng'] = list(permission_collection.find({}, {'_id': 0}))
    res['line_setting'] = list(el_config_collection.find({}, {'_id': 0}))
    res['string_setting'] = list(el_string_collection.find({}, {'_id': 0}))
    res['gui_setting'] = list(gui_setting_collection.find({}, {'_id': 0}))
    logger.info("admin_login_%s" % user_name)
    return json.dumps(res), 200


def user_logout(info: dict):
    user_name = info.get('user_name')
    info_time = info.get('time')
    if not all([user_name, info_time]):
        logger.error('incomplete params')
        return 'incomplete params', 421

    user_check = user_collection.find_one({'user_name': user_name, 'activate': 1})
    if user_check:
        context = {
            'user_id': user_check['_id'],
            'user_name': user_name,
            'time': info_time,
            'action': "logout_%s" % user_name
        }
        user_log_collection.insert_one(context)
        logger.info("logout_%s" % user_name)
        return '1', 200
    else:
        logger.error("user:%s didn't exist" % user_name)
        return "user didn't exist", 400


def el_config_display():
    el_config = list(el_config_collection.find({}, {"_id": 0}))
    logger.info('el_config_display')
    return json.dumps(el_config)


def el_panel_config_check(info: dict):
    el_no = info.get('el_no')
    if not el_no:
        logger.error('incomplete params')
        return 'incomplete params', 421

    el_check = el_config_collection.find_one({'el_no': el_no}, {'_id': 0})
    if not el_check:
        return 'null', 400
    logger.info('el_panel_config_check')
    return json.dumps(el_check), 200


def el_string_config_check(info: dict):
    string_line = info.get('string_line')
    if not string_line:
        logger.error('incomplete params')
        return 'incomplete params', 421
    el_check = el_string_collection.find_one({'string_line': string_line}, {'_id': 0})
    if not el_check:
        return 'null', 400
    logger.info('el_string_config_check')
    return json.dumps(el_check), 200


def gui_config_check(info: dict):
    gui_no = info.get('gui_no')
    if not gui_no:
        logger.error('incomplete params')
        return 'incomplete params', 421
    gui_setting_check = gui_setting_collection.find_one({'gui_no': gui_no}, {'_id': 0})
    if not gui_setting_check:
        return 'null', 400
    logger.info('gui_config_check')
    return json.dumps(gui_setting_check), 200


def barcode_find(info: dict):
    barcode = info.get('barcode')
    print(barcode)
    if not barcode:
        logger.error('incomplete params')
        return 'incomplete params', 421
    res = panel_collection.find_one({'barcode': barcode}, {'_id': 0, 'thresholds': 0})
    # res = \
    # list(panel_collection.aggregate([{'$match': {'barcode': barcode}}, {'$project': {'_id': 0, 'thresholds': 0}}]))[0]
    return res, 200


def panel_check_last(info: dict):
    barcode = info.get('barcode')
    create_time = info.get('create_time')
    if not all([barcode, create_time]):
        logger.error('incomplete params')
        return 'incomplete params', 421
    res = panel_collection.find_one({'barcode': barcode, 'create_time': create_time})
    return '1' if res else '0'


def repair(info: dict):
    barcode = info.get('barcode')
    if not barcode:
        logger.error('incomplete params')
        return 'incomplete params', 421
    res = list(panel_collection.aggregate([
        {'$match': {"barcode": barcode}},
        {'$sort': {'create_time': -1}},
        {'$project': {'_id': 0, 'defects': '$mes_defects'}},
        {'$limit': 1}]))[0]
    return json.dumps(res), 200 if res else '0', 400


def update():
    result = dict()
    result['users'] = list(user_collection.find({'type': {'$ne': 'yc_admin'}, 'activate': 1},
                                                {'_id': 0, 'user_pw': 0, 'activate': 0}))
    result['permission_mng'] = list(permission_collection.find({}, {'_id': 0}))
    result['line_setting'] = list(el_config_collection.find({}, {'_id': 0}))
    result['string_setting'] = list(el_string_collection.find({}, {'_id': 0}))
    result['gui_setting'] = list(gui_setting_collection.find({}, {'_id': 0}))

    return json.dumps(result)


def set_set(cell_amount):
    try:
        cell_amount = int(cell_amount)
    except:
        cell_amount = 144

    init_config = {
        "cr": {
            "cell_set": [
                {"name": "0", "l_cr": [], "v_cr": [], "x_cr": []},
                {"name": "1", "l_cr": [], "v_cr": [], "x_cr": []},
                {"name": "2", "l_cr": [], "v_cr": [], "x_cr": []},
                {"name": "3", "l_cr": [], "v_cr": [], "x_cr": []},
                {"name": "4", "l_cr": [], "v_cr": [], "x_cr": []},
                {"name": "5", "l_cr": [], "v_cr": [], "x_cr": []}
            ],
            "cc": []
        },
        "cs": {
            "cell_set": [
                {"name": "0", "cs_rules": []},
                {"name": "1", "cs_rules": []},
                {"name": "2", "cs_rules": []},
                {"name": "3", "cs_rules": []},
                {"name": "4", "cs_rules": []},
                {"name": "5", "cs_rules": []}
            ],
            "cc": []
        },
        "mr": {
            "dark": [],
            "bright": []
        },
        "update_time": 0
    }
    list_set = []
    cell = cell_amount / 6
    for x in range(6):
        for y in range(int(cell)):
            list_set.append([x, y])
    for z in range(1, 6):
        init_config['cr']['cell_set'][z]['set'] = []
        init_config['cs']['cell_set'][z]['set'] = []
    init_config['cr']['cell_set'][0]['set'] = list_set
    init_config['cs']['cell_set'][0]['set'] = list_set
    return init_config


def el_panel_config_modify(info: dict):  # TODO: unclear about data structure sent by front-end
    change_list = list()
    t = time.time()
    el_no = info.get('el_no')
    admin_name = info.get('admin_name')
    changed_items: dict = info.get('changed_items')

    if not all([el_no, admin_name, changed_items]):
        logger.error('incomplete params')
        return update(), 400

    el_check = el_config_collection.find_one({"el_no": el_no})
    el_check2 = el_config_collection.find_one({"el_no": el_no})
    admin_check = user_collection.find_one({"user_name": admin_name, "activate": 1})

    if el_check and el_check.get("update_time") == changed_items.get("update_time"):
        limit = list(el_config_collection.aggregate([{'$match': {'gui_no': changed_items.get("gui_no")}},
                                                     {"$group": {
                                                         '_id': {'_id': '$gui_no'}
                                                         ,
                                                         'limit': {"$sum": 1}}}]))
        gui_limit = gui_setting_collection.find_one({"gui_no": changed_items.get("gui_no")})

        if limit[0]['limit'] + 1 > gui_limit['el_limit']:
            return update(), 412

        for key, value in changed_items.items():
            el_check[key] = value
            change_list.append(key)
        if el_check2.get('cell_type') != changed_items.get('cell_type') or el_check2.get('cell_amount') != \
                changed_items.get('cell_amount') or el_check2.get('cell_shape') != changed_items.get('cell_shape'):
            el_check['thresholds'] = set_set(el_check.get('cell_amount'))
        changes = '_'.join(change_list)
        el_check["update_time"] = t
        el_config_collection.replace_one({"el_no": info["el_no"]}, el_check)
        user_log_collection.insert_one(
            {'admin_id': admin_check['_id'], 'admin_name': info["admin_name"], 'el_id': el_check.get('_id'),
             'el_no': info["el_no"], 'time': info['time'],
             'action': "%s_change_el_config:%s_%s" % (info["admin_name"], info["el_no"], changes)})
        logger.info('el_config_modify')
        return update(), 200
    else:
        return update(), 422


def el_string_config_modify(info: dict):
    t = time.time()
    change_list = list()
    string_line = info.get('string_line')
    admin_name = info.get('admin_name')
    info_time = info.get('time')
    changed_items: dict = info.get('changed_items')
    if not all([string_line, admin_name, changed_items, info_time]):
        logger.error('incomplete params')
        return update(), 400
    el_check = el_string_collection.find_one({'string_line': string_line})
    admin_check = user_collection.find_one({'user_name': admin_name, 'activate': 1})
    if el_check and admin_check:
        if el_check.get('update_time') == changed_items.get('update_time'):
            for key, value in changed_items.items():
                el_check[key] = value
                change_list.append(key)
            changes = '_'.join(change_list)
            el_check['update_time'] = t
            el_string_collection.replace_one({'string_line': string_line}, el_check)
            context = {
                'admin_id': admin_check['_id'],
                'admin_name': admin_name,
                'el_id': el_check.get('_id'),
                'string_line': string_line,
                'time': info_time,
                'action': "%s_change_el_string:%s_%s" % (admin_name, string_line, changes)
            }
            user_log_collection.insert_one(context)
            logger.info('el_string_modify')
            return update(), 200
        else:
            return update(), 422
    else:
        logger.error("el_no:%s didn't exist" % (info["admin_name"]))
        return update(), 422


def el_panel_thresholds_modify(info: dict):
    t = time.time()
    change_list = list()
    el_no = info.get('el_no')
    admin_name = info.get('admin_name')
    changed_items: dict = info.get('changed_items')
    info_time = info.get('time')
    if not all([el_no, admin_name, changed_items, info_time]):
        logger.error('incomplete params')
        return update(), 400
    el_check = el_config_collection.find_one({'el_no': el_no})
    admin_check = user_collection.find_one({'user_name': admin_name, 'activate': 1})
    if el_check:
        try:
            if el_check['thresholds']['update_time'] == changed_items['thresholds']['update_time']:
                for key, value in changed_items.items():
                    el_check[key] = value
                    change_list.append(key)
                changes = '_'.join(change_list)
                el_check['thresholds']['update_time'] = t
                el_config_collection.replace_one({'el_no': el_no}, el_check)
                user_log_collection.insert_one(
                    {'admin_id': admin_check['_id'], 'admin_name': admin_name, 'el_id': el_check['_id'],
                     'el_no': el_no, 'time': info_time,
                     'action': "%s_change_el_config:%s_%s" % (admin_name, el_no, changes)})
                logger.info('thresholds_modify')
                return update(), 200
        except Exception as e:
            logger.error(str(e))
            return update(), 422
    else:
        logger.error("el_no:%s didn't exist" % admin_name)
        return update(), 422


def gui_config_modify(info: dict):
    t = time.time()
    change_list = list()
    gui_no = info.get('gui_no')
    admin_name = info.get('admin_name')
    changed_items: dict = info.get('changed_items')
    info_time = info.get('time')
    if not all([gui_no, admin_name, changed_items, info_time]):
        logger.error('incomplete params')
        return update(), 400
    gui_check = gui_setting_collection.find_one({'gui_no': gui_no})
    admin_check = user_collection.find_one({"user_name": info["admin_name"], "activate": 1})
    if gui_check:
        try:
            if gui_check["update_time"] == info["changed_items"]["update_time"]:
                limit = list(el_config_collection.aggregate([
                    {'$match': {'gui_no': gui_no}},
                    {'$group': {
                        '_id': '$gui_no',
                        'limit': {'$sum': 1}
                    }}]))
                if limit[0]['limit'] > int(changed_items['el_limit']):
                    return update(), 412
                for key, value in changed_items.items():
                    gui_check[key] = value
                    change_list.append(key)
                changes = '_'.join(change_list)
                gui_check['update_time'] = t
                gui_setting_collection.replace_one({"gui_no": gui_no}, gui_check)
                user_log_collection.insert_one(
                    {'admin_id': admin_check['_id'], 'admin_name': admin_name, 'gui_id': gui_check['_id'],
                     'gui_no': gui_no, 'time': info_time,
                     'action': "%s_change_gui_config:%s_%s" % (admin_name, gui_no, changes)})
                logger.info('gui_config_modify')
                return update(), 200
        except Exception as e:
            logger.error(str(e))
            return update(), 400
    else:
        logger.error("gui_no:%s didn't exist" % (info["admin_name"]))
        return update(), 422


def permission_modify(info: dict):
    t = time.time()
    # change_list = list()
    admin_name = info.get('admin_name')
    changed_items = info.get('changed_items')
    info_time = info.get('time')
    if not all([admin_name, changed_items, info_time]):
        logger.error('incomplete params')
        return update(), 400
    admin_check: dict = user_collection.find_one({'user_name': admin_name, 'activate': 1})
    if admin_check.get('type') != 'yc_admin':
        return 'permission denied', 423
    for i in changed_items:
        change_list = list()
        try:
            permission_check = permission_collection.find_one({'type': i['type']})
            if permission_check['update_time'] == i['update_time']:
                for key, value in i:
                    permission_check[key] = value
                    change_list.append(key)
                changes = '_'.join(change_list)
                permission_check['update_time'] = t
                permission_collection.replace_one({'type': i['type']}, permission_check)
                user_log_collection.insert_one({'admin_id': admin_check['_id'], 'admin_name': admin_name,
                                                'type_id': permission_check['_id'], 'type': i["type"],
                                                'time': info_time,
                                                'action': "%s_change_permission_config:%s_%s" % (
                                                    admin_name, i["type"], changes)})
                logger.info('permission_modify')
            else:
                return update(), 422
        except Exception as e:
            logger.error(str(e))
            return update(), 400

    return update(), 200


def mes_defects_update(info: dict):
    barcode = info.get('barcode')
    create_time = info.get('create_time')
    mes_defects = info.get('mes_defects')
    if not all([barcode, create_time, mes_defects]):
        logger.error('incomplete params')
        return 'incomplete params', 400
    panel_check = panel_collection.find_one({'barcode': barcode, 'create_time': create_time})
    if not panel_check:
        return 'no such panel', 422
    panel_check['mes_defects'] = mes_defects
    panel_collection.replace_one({'barcode': barcode, 'create_time': create_time}, panel_check)
    logger.info("mes_defects_update{%s}" % info["barcode"])
    return '1', 200


def user_add(info: dict):
    t = time.time()
    user_name = info.get('user_name')
    user_pw = info.get('user_pw')
    admin_name = info.get('admin_name')
    user_type = info.get('type')
    info_time = info.get('time')
    if not all([user_name, user_pw, admin_name, user_type, info_time]):
        logger.error('incomplete params')
        return update(), 400
    admin_check = user_collection.find_one({'user_name': user_name, 'activate': 1})
    if not admin_check:
        logger.error("admin user:%s didn't exist" % admin_name)
        return "admin user didn't exist", 400
    if admin_check['type'] != 'super_admin' and admin_check['type'] != 'yc_admin':
        logger.error("permission denied %s" % admin_name)
        return update(), 423
    user_check = user_collection.find_one({'user_name': user_name, 'activate': 1})
    if user_check:
        return 'user exists', 413
    user_collection.insert_one({"user_name": user_name, "user_pw": user_pw, "activate": 1,
                                "type": user_type, "update_time": t})
    user_log_collection.insert_one(
        {'admin_id': admin_check["_id"], 'admin_name': admin_name, 'time': info_time,
         'action': "%s_add_user_%s" % (admin_name, user_name)})
    logger.info("user_add{%s}" % user_name)
    return update(), 200


def user_delete(info: dict):
    t = time.time()
    user_name = info.get('user_name')
    admin_name = info.get('admin_name')
    info_time = info.get('time')
    if not all([user_name, admin_name, info_time]):
        logger.error('incomplete params')
        return update(), 400
    admin_check = user_collection.find_one({'user_name': user_name, 'activate': 1})
    if not admin_check:
        logger.error("admin user:%s didn't exist" % admin_name)
        return "admin user didn't exist", 400
    if admin_check['type'] != 'super_admin' and admin_check['type'] != 'yc_admin':
        logger.error("permission denied %s" % admin_name)
        return update(), 423
    user_check = user_collection.find_one({'user_name': user_name, 'activate': 1})
    if user_check['type'] == 'super_admin' and admin_check['type'] == 'super_admin':
        logger.error("permission denied %s" % (info["admin_name"]))
        return update(), 423
    user_check['activate'] = time.time()
    user_check['update_time'] = t
    user_collection.replace_one({'user_name': user_name, 'activate': 1}, user_check)
    user_log_collection.insert_one(
        {'user_id': user_check['_id'], 'admin_id': admin_check['_id'], 'admin_name': admin_name,
         'time': info_time, 'action': "%s_del_user_%s" % (admin_name, user_name)})
    logger.info("user_del_%s" % (info["user_name"]))
    return update(), 200


def user_modify(info: dict):
    t = time.time()
    change_list = list()
    admin_name = info.get('admin_name')
    user_name = info.get('user_name')
    changed_items: dict = info.get('changed_items')
    info_time = info.get('time')
    cg_user_name = changed_items.get('user_name')
    cg_update_time = changed_items.get('update_time')
    if not all([admin_name, user_name, changed_items, info_time, cg_user_name, cg_update_time]):
        logger.error('incomplete params')
        return update(), 400
    admin_check = user_collection.find_one({'user_name': admin_name, 'activate': 1})
    if not admin_check:
        logger.error("user:%s didn't exist" % admin_name)
        return update(), 422
    if admin_check['type'] != 'super_admin' and admin_check['type'] == 'yc_admin':
        logger.error("permission denied %s" % (info["admin_name"]))
        return update(), 423
    user_check = user_collection.find_one({'user_name': user_name, 'activate': 1})
    if not user_check:
        logger.error("user:%s didn't exist" % user_name)
        return update(), 422
    dup = user_collection.find_one({'user_name': cg_user_name, 'activate': 1})
    if dup:
        return update(), 412
    if user_check['update_time'] == cg_update_time:
        for key, value in changed_items.items():
            user_check[key] = value
            change_list.append(key)
        changes = '_'.join(change_list)
        user_check['update_time'] = t
        user_collection.replace_one({"_id": user_check["_id"], "activate": 1}, user_check)
        user_log_collection.insert_one({'admin_id': admin_check['_id'], 'user_name': user_name,
                                        'user_id': user_check['_id'], 'admin_name': admin_name,
                                        'time': info_time, 'action': "%s_change_user:%s_%s" % (
                admin_name, user_name, changes)})
        logger.info("user_modify_%s" % user_name)
        return update(), 200
    else:
        return update(), 422


def user_password_change(info: dict):
    admin_name = info.get('admin_name')
    user_name = info.get('user_name')
    changed_items: dict = info.get('changed_items')
    info_time = info.get('time')
    user_pw = info.get('user_pw')
    cg_update_time = changed_items.get('update_time')
    if not all([admin_name, user_name, changed_items, info_time, user_pw, cg_update_time]):
        logger.error('incomplete params')
        return update(), 400
    admin_check = user_collection.find_one({'user_name': admin_name, 'activate': 1})
    user_check = user_collection.find_one({'user_name': user_name, 'activate': 1})
    if not (admin_check and user_check):
        return update(), 422
    if user_check['update_time'] == cg_update_time:
        user_check['user_pw'] = user_pw
        user_collection.replace_one({'user_name': user_name, 'activate': 1}, user_check)
        user_log_collection.insert_one(
            {'user_id': admin_check['_id'], 'user_name': admin_name, 'time': info_time,
             'action': "%s_password_change{%s}" % (admin_name, user_name)})
        logger.info("password_change{%s}" % user_name)
        return '1', 200
    else:
        return update(), 422


def limit(amount, create_time):
    t = time.localtime(time.time())
    time1 = time.mktime(time.strptime(time.strftime('%Y-%m-%d 00:00:00', t), '%Y-%m-%d %H:%M:%S'))
    time2 = time.mktime(time.strptime(time.strftime('%Y-%m-%d 23:59:59', t), '%Y-%m-%d %H:%M:%S'))
    data = panel_collection.find({create_time: {'$gte': time1, '$lt': time2}}).count()
    if data >= amount:
        return False
    else:
        return True


def panel_add(info: dict):
    barcode = info.get('barcode')
    create_time = info.get('create_time')
    el_no = info.get('el_no')
    mes_defects = info.get('mes_defects')
    cell_type = info.get('cell_type')
    cell_shape = info.get('cell_shape')
    cell_amount = info.get('cell_amount')
    display_mode = info.get('display_mode')
    ai_result = info.get('ai_result')
    ai_defects = info.get('ai_defects')
    gui_result = info.get('gui_result')
    gui_defects = info.get('gui_defects')
    origin_defects = info.get('origin_defects')
    ap_result = info.get('ap_result')
    ap_defects = info.get('ap_defects')
    if not all([
        barcode, create_time, el_no, mes_defects, cell_type, cell_shape,
        cell_amount, display_mode, ai_result, gui_result, ap_result
    ]):
        logger.error('incomplete params')
        return 'incomplete params', 400

    if not isinstance(mes_defects, str):
        logger.error('mes_defects should be dict')
        return 'mes_defects should be dict', 411
    if not isinstance(barcode, str):
        logger.error('barcode should be str')
        return 'barcode should be str', 411
    if cell_type not in CELL_TYPE_COLLECTION:
        logger.error('cell_type wrong')
        return 'cell_type wrong', 412
    if cell_shape not in CELL_SHAPE_COLLECTION:
        logger.error('cell_shape wrong')
        return 'cell_shape wrong', 412
    if cell_amount not in [60, 72, 120, 144, 156]:
        logger.error('cell_amount wrong')
        return 'cell_amount wrong', 412
    if not isinstance(el_no, str):
        logger.error('el_no should be str')
        return 'el_no should be str', 411
    if not isinstance(create_time, float):
        logger.error('create_time should be float')
        return 'create_time should be float', 411
    if display_mode not in [0, 1, 2]:
        logger.error('display_mode should be 0 or 1 or 2')
        return 'display_mode should be 0 or 1 or 2', 412
    if ai_result not in AI_RESULT:
        logger.error('ai_result should be %s' % (','.join(AI_RESULT)))
        return 'ai_result should be %s' % (','.join(AI_RESULT)), 412
    if ai_defects:
        if not isinstance(ai_defects, dict):
            logger.error('ai_defects should be dict')
            return 'ai_defects should be dict', 411
        for k in ai_defects.keys():
            if k not in DEFECT_TYPE_COLLECTION:
                logger.error('ai_defects wrong')
                return 'ai_defects wrong', 412
    if gui_result not in GUI_RESULT:
        logger.error('gui_result should be %s' % (','.join(GUI_RESULT)))
        return 'gui_result should be %s' % (','.join(GUI_RESULT)), 412
    if gui_defects:
        if not isinstance(gui_defects, dict):
            logger.error('gui_defects should be dict')
            return 'gui_defects should be dict', 411
        for k in gui_defects.keys():
            if k not in DEFECT_TYPE_COLLECTION:
                logger.error('gui_defects wrong')
                return 'gui_defects wrong', 411
    if not origin_defects:
        origin_defects = dict()
    if ap_result not in AI_RESULT:
        logger.error('ap_result should be %s' % (','.join(AI_RESULT)))
        return 'ap_result should be %s' % (','.join(AI_RESULT)), 412
    if ap_defects:
        if not isinstance(ap_defects, dict):
            logger.error('ap_defects should be dict')
            return 'ap_defects should be dict', 411
        for k in ap_defects.keys():
            if k not in DEFECT_TYPE_COLLECTION:
                logger.error('ap_defects wrong')
                return 'ap_defects wrong', 412

    defects = list()
    status = dict()
    status['EL_AI'] = ai_result
    status['EL_OP'] = gui_result
    status['AP_OP'] = ap_result
    if ai_defects:
        if not gui_defects:
            for key, values in ai_defects.items():
                for value in values:
                    defects.append({'type': key, 'position': value, 'by': 'AI', 'status': 'true'})
        else:
            for key, values, in ai_defects.items():
                for value in values:
                    gui_defects_list: list = gui_defects.get(key)
                    if gui_defects_list and (value in gui_defects_list):
                        defects.append({'type': key, 'position': value, 'by': 'AI', 'status': 'true'})
                        defects.append({'type': key, 'position': value, 'by': 'OP', 'status': 'true'})
                        gui_defects_list.remove(value)
                    else:
                        defects.append({'type': key, 'position': value, 'by': 'AI', 'status': 'false'})

    if gui_defects:
        for key, values in gui_defects.items():
            for value in values:
                defects.append({'type': key, 'position': value, 'by': 'OP', 'status': 'true'})

    panel_check = panel_collection.find_one(
        {"barcode": barcode, "create_time": create_time, "el_no": el_no})
    if limit(PANEL_LIMIT, 'create_time'):
        if panel_check:
            panel_collection.replace_one(panel_check, {
                'barcode': barcode,
                'cell_type': cell_type,
                'cell_amount': cell_amount,
                'cell_shape': cell_shape,
                'display_mode': display_mode,
                'el_no': el_no,
                'create_time': create_time,
                'origin_defects': origin_defects,
                'defects': defects,
                'status': status
            })
        else:
            panel_collection.insert_one({
                "mes_defects": mes_defects,
                "ap_defects": ap_defects,
                'barcode': barcode,
                'cell_type': cell_type,
                'cell_amount': cell_amount,
                'cell_shape': cell_shape,
                'display_mode': display_mode,
                'el_no': el_no,
                'create_time': create_time,
                'origin_defects': origin_defects,
                'defects': defects,
                'status': status
            })
    else:
        logger.error('panel limited')
        return "too much panels", 400
    logger.info('add panel')
    return '1', 200


def string_add(info: dict):
    image_id = info.get('image_id')
    create_time = info.get('create_time')
    string_line = info.get('string_line')
    cell_type = info.get('cell_type')
    cell_shape = info.get('cell_shape')
    cell_amount = info.get('cell_amount')
    result = info.get('result')
    defects = info.get('defects')
    insert_time = time.time()

    if not all([image_id, cell_type, cell_shape, cell_amount, string_line]):
        logger.error('incomplete params')
        return 'incomplete params', 400

    if not isinstance(image_id, str):
        logger.error('image_id should be str')
        return 'image_id should be str', 411
    if cell_type not in CELL_TYPE_COLLECTION:
        logger.error('cell_type wrong')
        return 'cell_type wrong', 412
    if cell_shape not in CELL_SHAPE_COLLECTION:
        logger.error('cell_shape wrong')
        return 'cell_shape wrong', 412
    if cell_amount not in CELL_AMOUNT_COLLECTION:
        logger.error('cell_amount wrong')
        return 'cell_amount wrong', 412
    if not isinstance(string_line, str):
        logger.error('string_line should be str')
        return 'string_line should be str', 411
    if defects:
        if not isinstance(defects, dict):
            logger.error('defects should be dict')
            return 'defects should be dict', 411
        for key in defects.keys():
            if key not in DEFECT_TYPE_COLLECTION:
                logger.error('defects wrong')
                return 'defects wrong', 412

    if limit(PANEL_LIMIT, 'insert_time'):
        el_string_collection.replace_one(
            {
                "image_id": image_id,
                "create_time": create_time,
                "string_line": string_line
            }, {
                'image_id': image_id,
                'result': result,
                'cell_type': cell_type,
                'cell_amount': cell_amount,
                'cell_shape': cell_shape,
                'string_line': string_line,
                'create_time': create_time,
                'defects': defects,
                'insert_time': insert_time,
            }, True)
    else:
        logger.error('panel limited')
        return "too much panels", 400


if __name__ == '__main__':
    print(repair({'barcode': 874253}))
