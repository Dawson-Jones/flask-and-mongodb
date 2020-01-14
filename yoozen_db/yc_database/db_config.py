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

    # def el_string_config_check(self, info: dict):
    #     string_line = info.get('string_line')
    #     if not string_line:
    #         logger.error('incomplete params')
    #         return 'incomplete params', 421, {'Content-Type': 'application/json'}
    #     el_check = self.el_string_collection.find_one({'string_line': string_line}, {'_id': 0})
    #     if not el_check:
    #         return 'null', 400, {'Content-Type': 'application/json'}
    #     logger.info('el_string_config_check')
    #     return json.dumps(el_check), 200, {'Content-Type': 'application/json'}

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

        if el_check and el_check.get("update_time") == changed_items.get("update_time"):
            limit = list(self.el_config_collection.aggregate([
                {'$match': {'gui_no': changed_items.get("gui_no")}},
                {"$group": {'_id': '$gui_no', 'limit': {"$sum": 1}}}
            ]))
            # print(limit)  # [{'_id': {'_id': 'op0'}, 'limit': 2}]
            gui_limit = self.gui_setting_collection.find_one({"gui_no": changed_items.get("gui_no")})

            if limit and limit[0]['limit'] >= gui_limit['el_limit']:
                return update(), 412, {'Content-Type': 'application/json'}
            changed_before = dict()
            changed_after = dict()
            for key, value in changed_items.items():
                if (pre_data := el_check.get(key)) != value:
                    changed_before[key] = pre_data
                    changed_after[key] = value
                    el_check[key] = value
            if el_check2.get('cell_type') != changed_items.get('cell_type') or el_check2.get('cell_amount') != \
                    changed_items.get('cell_amount') or el_check2.get('cell_shape') != changed_items.get('cell_shape'):
                el_check['thresholds'] = self.__set_set(el_check.get('cell_amount'))
            el_check["update_time"] = t
            self.el_config_collection.replace_one({"el_no": el_no}, el_check)
            self.user_log_collection.insert_one({
                'id': {
                    'admin_id': admin_check['_id'],
                    'el_id': el_check.get('_id'),
                },
                'operator': admin_name,
                'el_no': el_no,
                'time': info['time'],
                'action': "change el_config",
                'changed_before': changed_before,
                'changed_after': changed_after
            })
            logger.info('el_config_modify')
            return update(), 200, {'Content-Type': 'application/json'}
        else:
            return update(), 422, {'Content-Type': 'application/json'}

    # def el_string_config_modify(self, info: dict):
    #     t = time.time()
    #     change_list = list()
    #     string_line = info.get('string_line')
    #     admin_name = info.get('admin_name')
    #     info_time = info.get('time')
    #     changed_items = info.get('changed_items')
    #     if not all([string_line, admin_name, changed_items, info_time]):
    #         logger.error('incomplete params')
    #         return update(), 400, {'Content-Type': 'application/json'}
    #     el_check = self.el_string_collection.find_one({'string_line': string_line})
    #     admin_check = self.user_collection.find_one({'user_name': admin_name, 'activate': 1})
    #     if el_check and admin_check:
    #         if el_check.get('update_time') == changed_items.get('update_time'):
    #             for key, value in changed_items.items():
    #                 el_check[key] = value
    #                 change_list.append(key)
    #             changes = '_'.join(change_list)
    #             el_check['update_time'] = t
    #             self.el_string_collection.replace_one({'string_line': string_line}, el_check)
    #             context = {
    #                 'admin_id': admin_check['_id'],
    #                 'admin_name': admin_name,
    #                 'el_id': el_check.get('_id'),
    #                 'string_line': string_line,
    #                 'time': info_time,
    #                 'action': "change el_string"
    #             }
    #             self.user_log_collection.insert_one(context)
    #             logger.info('el_string_modify')
    #             return update(), 200, {'Content-Type': 'application/json'}
    #         else:
    #             return update(), 422, {'Content-Type': 'application/json'}
    #     else:
    #         logger.error("el_no:%s didn't exist" % (info["admin_name"]))
    #         return update(), 422, {'Content-Type': 'application/json'}

    def el_panel_thresholds_modify(self, info: dict):
        """
        aa = {
            "time": 1578906466.346,
            "admin_name": "super admin",
            "el_no": "PreA1",
            "el_url": "192.168.1.21:8080",
            "changed_items": {
                "el_no": "PreA1",
                "el_url": "192.168.1.21:8080",
                "gui_no": "op0",
                "gui_url": "192.168.1.9:3000",
                "cell_type": "mono",
                "cell_amount": 144,
                "cell_shape": "half",
                "display_mode": 2,
                "busbar": 5,
                "threshold_switch": 1,
                "thresholds": {
                    "ds": {"rules": [], "welding_point": 0},
                    "bb": [],
                    "lsh": [],
                    "ash": [],
                    "sh": {},
                    "vl": [],
                    "cs": {
                        "cell_set": [{
                            "name": "0",
                            "cs_rules": [
                                {"min_cell_per_string": 0,
                                 "min_cell_per_panel": 0,
                                 "position_2": 99,
                                 "area_1": 100,
                                 "area_3": 100,
                                 "position_1": 1,
                                 "result": "NG",
                                 "area_2": 70,
                                 "gray_scale_level": 0}],
                            "set": [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4],
                                    [0, 5], [0, 6], [0, 7], [0, 8], [0, 9],
                                    [0, 10], [0, 11], [0, 12], [0, 13],
                                    [0, 14],
                                    [0, 15], [0, 16], [0, 17], [0, 18],
                                    [0, 19],
                                    [0, 20], [0, 21], [0, 22], [0, 23],
                                    [1, 0],
                                    [1, 1], [1, 2], [1, 3], [1, 4], [1, 5],
                                    [1, 6], [1, 7], [1, 8], [1, 9], [1, 10],
                                    [1, 11], [1, 12], [1, 13], [1, 14],
                                    [1, 15],
                                    [1, 16], [1, 17], [1, 18], [1, 19],
                                    [1, 20],
                                    [1, 21], [1, 22], [1, 23], [2, 0], [2, 1],
                                    [2, 2], [2, 3], [2, 4], [2, 5], [2, 6],
                                    [2, 7], [2, 8], [2, 9], [2, 10], [2, 11],
                                    [2, 12], [2, 13], [2, 14], [2, 15],
                                    [2, 16],
                                    [2, 17], [2, 18], [2, 19], [2, 20],
                                    [2, 21],
                                    [2, 22], [2, 23], [3, 0], [3, 1], [3, 2],
                                    [3, 3], [3, 4], [3, 5], [3, 6], [3, 7],
                                    [3, 8], [3, 9], [3, 10], [3, 11], [3, 12],
                                    [3, 13], [3, 14], [3, 15], [3, 16],
                                    [3, 17],
                                    [3, 18], [3, 19], [3, 20], [3, 21],
                                    [3, 22],
                                    [3, 23], [4, 0], [4, 1], [4, 2], [4, 3],
                                    [4, 4], [4, 5], [4, 6], [4, 7], [4, 8],
                                    [4, 9], [4, 10], [4, 11], [4, 12],
                                    [4, 13],
                                    [4, 14], [4, 15], [4, 16], [4, 17],
                                    [4, 18],
                                    [4, 19], [4, 20], [4, 21], [4, 22],
                                    [4, 23],
                                    [5, 0], [5, 1], [5, 2], [5, 3], [5, 4],
                                    [5, 5], [5, 6], [5, 7], [5, 8], [5, 9],
                                    [5, 10], [5, 11], [5, 12], [5, 13],
                                    [5, 14],
                                    [5, 15], [5, 16], [5, 17], [5, 18],
                                    [5, 19],
                                    [5, 20], [5, 21], [5, 22], [5, 23]]},
                            {"name": "1", "cs_rules": [], "set": []},
                            {"name": "2", "cs_rules": [], "set": []},
                            {"name": "3", "cs_rules": [], "set": []},
                            {"name": "4", "cs_rules": [], "set": []},
                            {"name": "5", "cs_rules": [], "set": []}],
                        "cc": []},
                    "mr": {
                        "dark": [{"min_cell_per_string": 0, "min_cell_per_panel": 0, "result": "NG", "tolerance": 50}],
                        "bright": [{
                            "min_cell_per_panel": 0,
                            "result": "NG", "tolerance": 70,
                            "min_cell_per_string": 0
                        }]},
                    "cr": {
                        "corner_detection": 0,
                        "cell_set": [
                            {"name": "0", "v_cr": [
                                {"min_dft_per_cell": 0, "min_cell_per_panel": 0, "result": "NG",
                                 "min_len": 8, "min_cell_per_string": 0}], "l_cr": [
                                {"min_dft_per_cell": 0, "min_cell_per_panel": 0, "result": "NG",
                                 "min_len": 12, "min_cell_per_string": 0}],
                             "set": [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7], [0, 8],
                                     [0, 9], [0, 10], [0, 11], [0, 12], [0, 13], [0, 14], [0, 15], [0, 16],
                                     [0, 17], [0, 18], [0, 19], [0, 20], [0, 21], [0, 22], [0, 23], [1, 0],
                                     [1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [1, 7], [1, 8], [1, 9],
                                     [1, 10], [1, 11], [1, 12], [1, 13], [1, 14], [1, 15], [1, 16], [1, 17],
                                     [1, 18], [1, 19], [1, 20], [1, 21], [1, 22], [1, 23], [2, 0], [2, 1],
                                     [2, 2], [2, 3], [2, 4], [2, 5], [2, 6], [2, 7], [2, 8], [2, 9],
                                     [2, 10], [2, 11], [2, 12], [2, 13], [2, 14], [2, 15], [2, 16], [2, 17],
                                     [2, 18], [2, 19], [2, 20], [2, 21], [2, 22], [2, 23], [3, 0], [3, 1],
                                     [3, 2], [3, 3], [3, 4], [3, 5], [3, 6], [3, 7], [3, 8], [3, 9],
                                     [3, 10], [3, 11], [3, 12], [3, 13], [3, 14], [3, 15], [3, 16], [3, 17],
                                     [3, 18], [3, 19], [3, 20], [3, 21], [3, 22], [3, 23], [4, 0], [4, 1],
                                     [4, 2], [4, 3], [4, 4], [4, 5], [4, 6], [4, 7], [4, 8], [4, 9],
                                     [4, 10], [4, 11], [4, 12], [4, 13], [4, 14], [4, 15], [4, 16], [4, 17],
                                     [4, 18], [4, 19], [4, 20], [4, 21], [4, 22], [4, 23], [5, 0], [5, 1],
                                     [5, 2], [5, 3], [5, 4], [5, 5], [5, 6], [5, 7], [5, 8], [5, 9],
                                     [5, 10], [5, 11], [5, 12], [5, 13], [5, 14], [5, 15], [5, 16], [5, 17],
                                     [5, 18], [5, 19], [5, 20], [5, 21], [5, 22], [5, 23]], "x_cr": []},
                            {"name": "1", "v_cr": [], "l_cr": [], "set": [], "x_cr": []},
                            {"name": "2", "v_cr": [], "l_cr": [], "set": [], "x_cr": []},
                            {"name": "3", "v_cr": [], "l_cr": [], "set": [], "x_cr": []},
                            {"name": "4", "v_cr": [], "l_cr": [], "set": [], "x_cr": []},
                            {"name": "5", "v_cr": [], "l_cr": [], "set": [], "x_cr": []}],
                        "cc": []
                    },
                    "update_time": 1571117012.98997},
                "cr_module": 1,
                "cs_module": 1,
                "mr_module": 1,
                "bc_module": 1,
                "br_module": 1,
                "bb_module": 0,
                "ds_module": 0,
                "lsh_module": 0,
                "ash_module": 0,
                "vl_module": 0,
                "update_time": 0
            }
        }
        """
        t = time.time()
        el_no = info.get('el_no')
        admin_name = info.get('admin_name')
        changed_items = info.get('changed_items')
        info_time = info.get('time')
        if not all([el_no, admin_name, changed_items, info_time]):
            logger.error('incomplete params')
            return update(), 400, {'Content-Type': 'application/json'}
        el_check = self.el_config_collection.find_one({'el_no': el_no})
        admin_check = self.user_collection.find_one({'user_name': admin_name, 'activate': 1})
        if not el_check:
            logger.error("el_no:%s didn't exist" % admin_name)
            return update(), 422, {'Content-Type': 'application/json'}
        try:
            if el_check['thresholds']['update_time'] == changed_items['thresholds']['update_time']:
                changed_before = dict()
                changed_after = dict()
                for key, value in changed_items.items():
                    if (pre_data := el_check.get(key)) != value:
                        changed_before[key] = pre_data
                        changed_after[key] = value
                        el_check[key] = value
                el_check['thresholds']['update_time'] = t
                self.el_config_collection.replace_one({'el_no': el_no}, el_check)
                self.user_log_collection.insert_one({
                    'id': {
                        'admin_id': admin_check['_id'],
                        'el_id': el_check['_id']
                    },
                    'operator': admin_name,
                    'el_no': el_no,
                    'time': info_time,
                    'action': "change_el config",
                    'changed_before': changed_before,
                    'changed_after': changed_after,
                })
                logger.info('thresholds_modify')
                return update(), 200, {'Content-Type': 'application/json'}
        except Exception as e:
            logger.error(str(e))
            return update(), 422, {'Content-Type': 'application/json'}

    def gui_config_modify(self, info: dict):
        t = time.time()
        gui_no = info.get('gui_no')
        admin_name = info.get('admin_name')
        changed_items = info.get('changed_items')
        info_time = info.get('time')
        if not all([gui_no, admin_name, changed_items, info_time]):
            logger.error('incomplete params')
            return update(), 400, {'Content-Type': 'application/json'}
        gui_check = self.gui_setting_collection.find_one({'gui_no': gui_no})
        admin_check = self.user_collection.find_one({"user_name": info["admin_name"], "activate": 1})
        if not gui_check:
            logger.error("gui_no:%s didn't exist" % (info["admin_name"]))
            return update(), 422, {'Content-Type': 'application/json'}
        try:
            if gui_check["update_time"] != changed_items["update_time"]:
                return update(), 422, {'Content-Type': 'application/json'}

            limit = list(self.el_config_collection.aggregate([
                {'$match': {'gui_no': gui_no}},
                {'$group': {'_id': '$gui_no', 'limit': {'$sum': 1}}}
            ]))
            if limit[0]['limit'] > int(changed_items['el_limit']):
                return update(), 412, {'Content-Type': 'application/json'}
            changed_before = dict()
            changed_after = dict()
            for key, value in changed_items.items():
                if (pre_data := gui_check.get(key)) != value:
                    changed_before[key] = pre_data
                    changed_after[key] = value
                    gui_check[key] = value
            gui_check['update_time'] = t
            self.gui_setting_collection.replace_one({"gui_no": gui_no}, gui_check)
            self.user_log_collection.insert_one({
                'id': {
                    'admin_id': admin_check['_id'],
                    'gui_id': gui_check['_id']
                },
                'operator': admin_name,
                'gui_no': gui_no,
                'time': info_time,
                'action': "change gui_config",
                'changed_before': changed_before,
                'changed_after': changed_after
            })
            logger.info('gui_config_modify')
            return update(), 200, {'Content-Type': 'application/json'}
        except Exception as e:
            logger.error(str(e))
            return update(), 400, {'Content-Type': 'application/json'}
