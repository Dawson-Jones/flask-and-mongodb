# from db_config import Config
# from db_product import Product
# from db_user import User
import csv
from yoozen_db.yc_database.db_config import Config
from yoozen_db.yc_database.db_product import Product
from yoozen_db.yc_database.db_user import User
from yoozen_db.basic.db import (
    user_collection, user_log_collection, permission_collection,
    el_config_collection, el_string_collection, gui_setting_collection,
    panel_collection
)


class YcDataBase(Config, Product, User):
    _instance = None
    init_flag = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if self.init_flag:
            return
        url = dict()
        super().__init__(
            el_config_collection,
            user_collection,
            gui_setting_collection,
            user_log_collection,
            el_string_collection,
            permission_collection,
            panel_collection)
        self.init_flag = True


if __name__ == '__main__':
    yc = YcDataBase()
