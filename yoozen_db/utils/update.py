import json
from ..basic.db import (
    user_collection, permission_collection,
    el_string_collection, gui_setting_collection, el_config_collection
)


def update():
    result = dict()
    result['users'] = list(user_collection.find({'type': {'$ne': 'yc_admin'}, 'activate': 1},
                                                {'_id': 0, 'user_pw': 0, 'activate': 0}))
    result['permission_mng'] = list(permission_collection.find({}, {'_id': 0}))
    result['line_setting'] = list(el_config_collection.find({}, {'_id': 0}))
    result['string_setting'] = list(el_string_collection.find({}, {'_id': 0}))
    result['gui_setting'] = list(gui_setting_collection.find({}, {'_id': 0}))

    return json.dumps(result)
