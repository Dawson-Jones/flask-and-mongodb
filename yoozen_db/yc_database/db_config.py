import json
import time
from log_manager import logger
from yoozen_db.utils.update import update


class Config(object):
    def __init__(self, el_config_collection, user_collection, gui_setting_collection,
                 user_log_collection, el_string_collection, permission_collection,
                 *args, **kwargs):
        self.el_config_collection = el_config_collection
        self.user_collection = user_collection
        self.gui_setting_collection = gui_setting_collection
        self.user_log_collection = user_log_collection
        self.el_string_collection = el_string_collection
        self.permission_collection = permission_collection

    @staticmethod
    def __set_set(cell_amount):
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

    def el_config_display(self):
        el_config = list(self.el_config_collection.find({}, {"_id": 0}))
        logger.info('el_config_display')
        return json.dumps(el_config), 200, {'Content-Type': 'application/json'}

    def el_panel_config_check(self, info: dict):
        el_no = info.get('el_no')
        if not el_no:
            logger.error('incomplete params')
            return 'incomplete params', 421, {'Content-Type': 'application/json'}

        el_check = self.el_config_collection.find_one({'el_no': el_no}, {'_id': 0})
        if not el_check:
            return 'null', 400, {'Content-Type': 'application/json'}
        logger.info('el_panel_config_check')
        return json.dumps(el_check), 200, {'Content-Type': 'application/json'}

    def el_string_config_check(self, info: dict):
        string_line = info.get('string_line')
        if not string_line:
            logger.error('incomplete params')
            return 'incomplete params', 421, {'Content-Type': 'application/json'}
        el_check = self.el_string_collection.find_one({'string_line': string_line}, {'_id': 0})
        if not el_check:
            return 'null', 400, {'Content-Type': 'application/json'}
        logger.info('el_string_config_check')
        return json.dumps(el_check), 200, {'Content-Type': 'application/json'}

    def gui_config_check(self, info: dict):
        gui_no = info.get('gui_no')
        if not gui_no:
            logger.error('incomplete params')
            return 'incomplete params', 421, {'Content-Type': 'application/json'}
        gui_setting_check = self.gui_setting_collection.find_one({'gui_no': gui_no}, {'_id': 0})
        if not gui_setting_check:
            return 'null', 400, {'Content-Type': 'application/json'}
        logger.info('gui_config_check')
        return json.dumps(gui_setting_check), 200, {'Content-Type': 'application/json'}

    def el_panel_config_modify(self, info: dict):
        """
        {
          "admin_name": "dawson",
          "time": 1548056846.8,
          "el_no": "line0",
          "changed_items": {
            "cell_type": "mono",
            "display_mode": 2,
            "update_time": 0
          }
        }
        """
        change_list = list()
        t = time.time()
        el_no = info.get('el_no')
        admin_name = info.get('admin_name')
        changed_items = info.get('changed_items')

        if not all([el_no, admin_name, changed_items]):
            logger.error('incomplete params')
            return update(), 400, {'Content-Type': 'application/json'}

        el_check = self.el_config_collection.find_one({"el_no": el_no})
        el_check2 = self.el_config_collection.find_one({"el_no": el_no})
        admin_check = self.user_collection.find_one({"user_name": admin_name, "activate": 1})

        if el_check and el_check.get("update_time") == changed_items.get("update_time"):  # TODO: update_time 有什么用
            limit = list(self.el_config_collection.aggregate([
                {'$match': {'gui_no': changed_items.get("gui_no")}},
                {"$group": {'_id': {'_id': '$gui_no'}, 'limit': {"$sum": 1}}}
            ]))
            gui_limit = self.gui_setting_collection.find_one(
                {"gui_no": changed_items.get("gui_no")})  # TODO: 里面没有gui_no

            if limit[0]['limit'] + 1 > gui_limit['el_limit']:
                return update(), 412, {'Content-Type': 'application/json'}

            for key, value in changed_items.items():
                el_check[key] = value
                change_list.append(key)
            if el_check2.get('cell_type') != changed_items.get('cell_type') or el_check2.get('cell_amount') != \
                    changed_items.get('cell_amount') or el_check2.get('cell_shape') != changed_items.get('cell_shape'):
                el_check['thresholds'] = self.__set_set(el_check.get('cell_amount'))
            changes = '_'.join(change_list)
            el_check["update_time"] = t
            self.el_config_collection.replace_one({"el_no": info["el_no"]}, el_check)
            self.user_log_collection.insert_one({
                'admin_id': admin_check['_id'],
                'admin_name': info["admin_name"],
                'el_id': el_check.get('_id'),
                'el_no': info["el_no"],
                'time': info['time'],
                'action': "%s_change_el_config:%s_%s" % (info["admin_name"], info["el_no"], changes)
            })
            logger.info('el_config_modify')
            return update(), 200, {'Content-Type': 'application/json'}
        else:
            return update(), 422, {'Content-Type': 'application/json'}

    def el_string_config_modify(self, info: dict):
        t = time.time()
        change_list = list()
        string_line = info.get('string_line')
        admin_name = info.get('admin_name')
        info_time = info.get('time')
        changed_items = info.get('changed_items')
        if not all([string_line, admin_name, changed_items, info_time]):
            logger.error('incomplete params')
            return update(), 400, {'Content-Type': 'application/json'}
        el_check = self.el_string_collection.find_one({'string_line': string_line})
        admin_check = self.user_collection.find_one({'user_name': admin_name, 'activate': 1})
        if el_check and admin_check:
            if el_check.get('update_time') == changed_items.get('update_time'):
                for key, value in changed_items.items():
                    el_check[key] = value
                    change_list.append(key)
                changes = '_'.join(change_list)
                el_check['update_time'] = t
                self.el_string_collection.replace_one({'string_line': string_line}, el_check)
                context = {
                    'admin_id': admin_check['_id'],
                    'admin_name': admin_name,
                    'el_id': el_check.get('_id'),
                    'string_line': string_line,
                    'time': info_time,
                    'action': "%s_change_el_string:%s_%s" % (admin_name, string_line, changes)
                }
                self.user_log_collection.insert_one(context)
                logger.info('el_string_modify')
                return update(), 200, {'Content-Type': 'application/json'}
            else:
                return update(), 422, {'Content-Type': 'application/json'}
        else:
            logger.error("el_no:%s didn't exist" % (info["admin_name"]))
            return update(), 422, {'Content-Type': 'application/json'}

    def el_panel_thresholds_modify(self, info: dict):
        t = time.time()
        change_list = list()
        el_no = info.get('el_no')
        admin_name = info.get('admin_name')
        changed_items = info.get('changed_items')
        info_time = info.get('time')
        if not all([el_no, admin_name, changed_items, info_time]):
            logger.error('incomplete params')
            return update(), 400, {'Content-Type': 'application/json'}
        el_check = self.el_config_collection.find_one({'el_no': el_no})
        admin_check = self.user_collection.find_one({'user_name': admin_name, 'activate': 1})
        if el_check:
            try:
                if el_check['thresholds']['update_time'] == changed_items['thresholds']['update_time']:
                    for key, value in changed_items.items():
                        el_check[key] = value
                        change_list.append(key)
                    changes = '_'.join(change_list)
                    el_check['thresholds']['update_time'] = t
                    self.el_config_collection.replace_one({'el_no': el_no}, el_check)
                    self.user_log_collection.insert_one({
                        'admin_id': admin_check['_id'],
                        'admin_name': admin_name,
                        'el_id': el_check['_id'],
                        'el_no': el_no,
                        'time': info_time,
                        'action': "%s_change_el_config:%s_%s" % (admin_name, el_no, changes)
                    })
                    logger.info('thresholds_modify')
                    return update(), 200, {'Content-Type': 'application/json'}
            except Exception as e:
                logger.error(str(e))
                return update(), 422, {'Content-Type': 'application/json'}
        else:
            logger.error("el_no:%s didn't exist" % admin_name)
            return update(), 422, {'Content-Type': 'application/json'}

    def gui_config_modify(self, info: dict):
        t = time.time()
        change_list = list()
        gui_no = info.get('gui_no')
        admin_name = info.get('admin_name')
        changed_items = info.get('changed_items')
        info_time = info.get('time')
        if not all([gui_no, admin_name, changed_items, info_time]):
            logger.error('incomplete params')
            return update(), 400, {'Content-Type': 'application/json'}
        gui_check = self.gui_setting_collection.find_one({'gui_no': gui_no})
        admin_check = self.user_collection.find_one({"user_name": info["admin_name"], "activate": 1})
        if gui_check:
            try:
                if gui_check["update_time"] == info["changed_items"]["update_time"]:
                    limit = list(self.el_config_collection.aggregate([
                        {'$match': {'gui_no': gui_no}},
                        {'$group': {'_id': '$gui_no', 'limit': {'$sum': 1}}}
                    ]))
                    if limit[0]['limit'] > int(changed_items['el_limit']):
                        return update(), 412, {'Content-Type': 'application/json'}
                    for key, value in changed_items.items():
                        gui_check[key] = value
                        change_list.append(key)
                    changes = '_'.join(change_list)
                    gui_check['update_time'] = t
                    self.gui_setting_collection.replace_one({"gui_no": gui_no}, gui_check)
                    self.user_log_collection.insert_one({
                        'admin_id': admin_check['_id'],
                        'admin_name': admin_name,
                        'gui_id': gui_check['_id'],
                        'gui_no': gui_no,
                        'time': info_time,
                        'action': "%s_change_gui_config:%s_%s" % (admin_name, gui_no, changes)
                    })
                    logger.info('gui_config_modify')
                    return update(), 200, {'Content-Type': 'application/json'}
            except Exception as e:
                logger.error(str(e))
                return update(), 400, {'Content-Type': 'application/json'}
        else:
            logger.error("gui_no:%s didn't exist" % (info["admin_name"]))
            return update(), 422, {'Content-Type': 'application/json'}
