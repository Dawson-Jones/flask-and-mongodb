# from db_config import Config
# from db_product import Product
# from db_user import User
from yoozen_db.yc_database.db_config import Config
from yoozen_db.yc_database.db_product import Product
from yoozen_db.yc_database.db_user import User
from yoozen_db.basic.db import (
    user_collection, user_log_collection, permission_collection,
    el_config_collection, el_string_collection, gui_setting_collection,
    panel_collection
)


class YcDataBase(Config, Product, User):
    def __init__(self):
        super().__init__(
            el_config_collection,
            user_collection,
            gui_setting_collection,
            user_log_collection,
            el_string_collection,
            permission_collection,
            panel_collection)


if __name__ == '__main__':
    yc = YcDataBase()
    print(yc.el_config_display())
