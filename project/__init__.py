from flask import Flask
from config import config_map
from project.utils.commons import ReConverter

# client = None
# db = None


def create_app(config_name):
    app = Flask(__name__)
    config_class = config_map.get(config_name)
    app.config.from_object(config_class)

    # global client, db
    # client = MongoClient(config_class.PYMONGO_DATABASE_URL, serverSelectionTimeoutMS=5)
    # db = client['tttt']

    app.url_map.converters['re'] = ReConverter

    from project.db import admin, gui, panel
    app.register_blueprint(admin.app, url_prefix='/admin')
    app.register_blueprint(gui.app, url_prefix='/gui')
    app.register_blueprint(panel.api)

    return app


if __name__ == '__main__':
    appp = create_app('develop')
    appp.run(host='0.0.0.0')
