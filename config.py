class Config(object):
    # 数据库
    PYMONGO_DATABASE_URL = 'mongodb://root:123456@192.168.2.52:27027'
    # PYMONGO_DATABASE_URL = 'mongodb://root:123456@192.168.1.7:27017'


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass


config_map = {
    'develop': DevelopmentConfig,
    'product': ProductionConfig
}
