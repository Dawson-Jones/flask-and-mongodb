import time
import csv
import json

from yoozen_db.utils.log_manager import logger
from yoozen_db.utils.update import update


class User(object):

    def __init__(self,
                 user_collection,
                 permission_collection,
                 el_config_collection,
                 el_string_collection,
                 gui_setting_collection,
                 user_log_collection,
                 *args, **kwargs):
        self.user_collection = user_collection
        self.permission_collection = permission_collection
        self.el_config_collection = el_config_collection
        self.el_string_collection = el_string_collection
        self.gui_setting_collection = gui_setting_collection
        self.user_log_collection = user_log_collection

    @property
    def user_display(self):
        res = dict()
        res['users'] = list(
            self.user_collection.find({'type': {'$ne': 'yc_admin'}, 'activate': 1},
                                      {'_id': 0, "user_pw": 0, "activate": 0}))
        return json.dumps(res), 200, {'Content-Type': 'application/json'}

    def user_login_operator(self, info: dict):
        user_name = info.get('user_name')
        user_pw = info.get('user_pw')
        info_time = info.get('time')
        if not all([user_name, user_pw, info_time]):
            logger.error('incomplete params')
            return 'incomplete params', 421

        user_check = self.user_collection.find_one(
            {"user_name": user_name, "user_pw": user_pw, "activate": 1})
        if user_check:
            self.user_log_collection.insert_one({
                'user_id': user_check['_id'],
                'user_name': user_name,
                'time': info_time,
                'action': 'login_%s' % user_name
            })
            logger.info("login_%s" % user_name)
            return user_check['type'], 200
        else:
            logger.error("user:%s didn't exist" % user_name)
            return 'login failed', 421

    def user_login_admin(self, info: dict):
        # with open('yoozen_db/SETUP/url.csv', 'r', newline='') as f:
        #     reader = csv.DictReader(f)
        #     for csv_url in reader:
        #         url = csv_url
        res = dict()
        user_name = info.get('user_name')
        user_pw = info.get('user_pw')
        info_time = info.get('time')
        admin_url = info.get('admin_url')
        if not all([user_name, user_pw, info_time, admin_url]):
            logger.error('incomplete params')
            return 'incomplete params', 421, {'Content-Type': 'application/json'}

        user_check = self.user_collection.find_one(
            {"user_name": user_name, "user_pw": user_pw, "activate": 1})
        if not user_check:
            logger.error("user:%s didn't exist" % user_name)
            return "user didn't exist", 421, {'Content-Type': 'application/json'}
        if user_check['type'] == 'operator':
            return "not admin", 421, {'Content-Type': 'application/json'}
        self.user_log_collection.insert_one({
            'user_id': user_check['_id'],
            'user_name': user_name,
            'time': info_time,
            'action': "login_%s" % user_name
        })

        res['type'] = user_check['type']
        # pre_url = url.get(admin_url)
        # res['previous_url'] = user_check.get("previous_url") if user_check.get('previous_url') != pre_url else ''
        # user_check['previous_url'] = pre_url
        # self.user_collection.replace_one({'user_name': user_name, 'activate': 1}, user_check)

        res['permission_mng'] = list(self.permission_collection.find({}, {'_id': 0}))
        res['line_setting'] = list(self.el_config_collection.find({}, {'_id': 0}))
        res['string_setting'] = list(self.el_string_collection.find({}, {'_id': 0}))
        res['gui_setting'] = list(self.gui_setting_collection.find({}, {'_id': 0}))
        logger.info("admin_login_%s" % user_name)
        return json.dumps(res), 200, {'Content-Type': 'application/json'}

    def user_logout(self, info: dict):
        user_name = info.get('user_name')
        info_time = info.get('time')
        if not all([user_name, info_time]):
            logger.error('incomplete params')
            return 'incomplete params', 421, {'Content-Type': 'application/json'}

        user_check = self.user_collection.find_one({'user_name': user_name, 'activate': 1})
        if user_check:
            context = {
                'user_id': user_check['_id'],
                'user_name': user_name,
                'time': info_time,
                'action': "logout_%s" % user_name
            }
            self.user_log_collection.insert_one(context)
            logger.info("logout_%s" % user_name)
            return '1', 200, {'Content-Type': 'application/json'}
        else:
            logger.error("user:%s didn't exist" % user_name)
            return "user didn't exist", 400, {'Content-Type': 'application/json'}

    def user_add(self, info: dict):
        t = time.time()
        user_name = info.get('user_name')
        user_pw = info.get('user_pw')
        admin_name = info.get('admin_name')
        user_type = info.get('type')
        info_time = info.get('time')
        if not all([user_name, user_pw, admin_name, user_type, info_time]):
            logger.error('incomplete params')
            return update(), 400, {'Content-Type': 'application/json'}
        admin_check = self.user_collection.find_one({'user_name': admin_name, 'activate': 1})
        if not admin_check:
            logger.error("admin user:%s didn't exist" % admin_name)
            return "admin user didn't exist", 400, {'Content-Type': 'application/json'}
        if admin_check['type'] != 'super_admin' and admin_check['type'] != 'yc_admin':
            logger.error("permission denied %s" % admin_name)
            return update(), 423, {'Content-Type': 'application/json'}
        user_check = self.user_collection.find_one({'user_name': user_name, 'activate': 1})
        if user_check:
            return 'user exists', 413, {'Content-Type': 'application/json'}
        self.user_collection.insert_one({"user_name": user_name, "user_pw": user_pw, "activate": 1,
                                         "type": user_type, "update_time": t})
        self.user_log_collection.insert_one({
            'admin_id': admin_check["_id"],
            'admin_name': admin_name,
            'time': info_time,
            'action': "%s_add_user_%s" % (admin_name, user_name)
        })
        logger.info("user_add{%s}" % user_name)
        return update(), 200, {'Content-Type': 'application/json'}

    def user_delete(self, info: dict):
        t = time.time()
        user_name = info.get('user_name')
        admin_name = info.get('admin_name')
        info_time = info.get('time')
        if not all([user_name, admin_name, info_time]):
            logger.error('incomplete params')
            return update(), 400, {'Content-Type': 'application/json'}
        admin_check = self.user_collection.find_one({'user_name': admin_name, 'activate': 1})
        if not admin_check:
            logger.error("admin user:%s didn't exist" % admin_name)
            return "admin user didn't exist", 400, {'Content-Type': 'application/json'}
        if admin_check['type'] != 'super_admin' and admin_check['type'] != 'yc_admin':
            logger.error("permission denied %s" % admin_name)
            return update(), 423, {'Content-Type': 'application/json'}
        user_check = self.user_collection.find_one({'user_name': user_name, 'activate': 1})
        if user_check['type'] == 'super_admin' and admin_check['type'] == 'super_admin':
            logger.error("permission denied %s" % (info["admin_name"]))
            return update(), 423, {'Content-Type': 'application/json'}
        user_check['activate'] = time.time()
        user_check['update_time'] = t
        self.user_collection.replace_one({'user_name': user_name, 'activate': 1}, user_check)
        self.user_log_collection.insert_one({
            'user_id': user_check['_id'],
            'admin_id': admin_check['_id'],
            'admin_name': admin_name,
            'time': info_time,
            'action': "%s_del_user_%s" % (admin_name, user_name)
        })
        logger.info("user_del_%s" % (info["user_name"]))
        return update(), 200, {'Content-Type': 'application/json'}

    def user_modify(self, info: dict):
        t = time.time()
        admin_name = info.get('admin_name')
        user_name = info.get('user_name')
        changed_items: dict = info.get('changed_items')
        info_time = info.get('time')
        cg_user_name = changed_items.get('user_name')
        cg_update_time = changed_items.get('update_time')
        if not all([admin_name, user_name, changed_items, info_time, cg_update_time]):
            logger.error('incomplete params')
            return update(), 400, {'Content-Type': 'application/json'}
        admin_check = self.user_collection.find_one({'user_name': admin_name, 'activate': 1})
        if not admin_check:
            logger.error("user:%s didn't exist" % admin_name)
            return update(), 422, {'Content-Type': 'application/json'}
        if admin_check['type'] != 'super_admin' and admin_check['type'] != 'yc_admin':
            logger.error("permission denied %s" % (info["admin_name"]))
            return update(), 423, {'Content-Type': 'application/json'}
        user_check = self.user_collection.find_one({'user_name': user_name, 'activate': 1})
        if not user_check:
            logger.error("user:%s didn't exist" % user_name)
            return update(), 422, {'Content-Type': 'application/json'}
        if cg_user_name and self.user_collection.find_one({'user_name': cg_user_name, 'activate': 1}):
            # if change name have be used
            return update(), 412, {'Content-Type': 'application/json'}
        change_list = list()
        if user_check['update_time'] == cg_update_time:
            for key, value in changed_items.items():
                user_check[key] = value
                change_list.append(key)
            changes = '_'.join(change_list)
            user_check['update_time'] = t
            self.user_collection.replace_one({"_id": user_check["_id"], "activate": 1}, user_check)
            self.user_log_collection.insert_one({
                'admin_id': admin_check['_id'],
                'user_name': user_name,
                'user_id': user_check['_id'],
                'admin_name': admin_name,
                'time': info_time,
                'action': "%s_change_user:%s_%s" % (admin_name, user_name, changes)
            })
            logger.info("user_modify_%s" % user_name)
            return update(), 200, {'Content-Type': 'application/json'}
        else:
            return update(), 422, {'Content-Type': 'application/json'}

    def user_password_change(self, info: dict):
        admin_name = info.get('admin_name')
        user_name = info.get('user_name')
        changed_items = info.get('changed_items')
        info_time = info.get('time')
        user_pw = info.get('user_pw')
        cg_update_time = changed_items.get('update_time')
        if not all([admin_name, user_name, changed_items, info_time, user_pw, cg_update_time]):
            logger.error('incomplete params')
            return update(), 400, {'Content-Type': 'application/json'}
        admin_check = self.user_collection.find_one({'user_name': admin_name, 'activate': 1})
        user_check = self.user_collection.find_one({'user_name': user_name, 'activate': 1})
        if not (admin_check and user_check):
            return update(), 422, {'Content-Type': 'application/json'}
        if user_check['update_time'] == cg_update_time:
            user_check['user_pw'] = user_pw
            self.user_collection.replace_one({'user_name': user_name, 'activate': 1}, user_check)
            self.user_log_collection.insert_one({
                'user_id': admin_check['_id'],
                'user_name': admin_name,
                'time': info_time,
                'action': "%s_password_change{%s}" % (admin_name, user_name)
            })
            logger.info("password_change{%s}" % user_name)
            return '1', 200, {'Content-Type': 'application/json'}
        else:
            return update(), 422, {'Content-Type': 'application/json'}

    def permission_modify(self, info):  # TODO: oxxx
        t = time.time()
        # change_list = list()
        admin_name = info.get('admin_name')
        changed_items = info.get('changed_items')
        info_time = info.get('time')
        if not all([admin_name, changed_items, info_time]):
            logger.error('incomplete params')
            return update(), 400, {'Content-Type': 'application/json'}
        admin_check = self.user_collection.find_one({'user_name': admin_name, 'activate': 1})
        if admin_check.get('type') != 'yc_admin':
            return 'permission denied', 423, {'Content-Type': 'application/json'}
        for i in changed_items:
            change_list = list()
            try:
                permission_check = self.permission_collection.find_one({'type': i['type']})
                if permission_check['update_time'] == i['update_time']:
                    for key, value in i:
                        permission_check[key] = value
                        change_list.append(key)
                    changes = '_'.join(change_list)
                    permission_check['update_time'] = t
                    self.permission_collection.replace_one({'type': i['type']}, permission_check)
                    self.user_log_collection.insert_one({
                        'admin_id': admin_check['_id'],
                        'admin_name': admin_name,
                        'type_id': permission_check['_id'],
                        'type': i["type"],
                        'time': info_time,
                        'action': "%s_change_permission_config:%s_%s" % (admin_name, i["type"], changes)
                    })
                    logger.info('permission_modify')
                else:
                    return update(), 422, {'Content-Type': 'application/json'}
            except Exception as e:
                logger.error(str(e))
                return update(), 400, {'Content-Type': 'application/json'}

        return update(), 200, {'Content-Type': 'application/json'}
