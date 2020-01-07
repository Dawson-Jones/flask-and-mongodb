from project import create_app
from flask_script import Manager

app = create_app('develop')
manager = Manager(app)

if __name__ == '__main__':
    manager.run()
    # app.run(debug=True, host="0.0.0.0")
