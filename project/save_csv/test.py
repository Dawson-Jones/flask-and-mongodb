from project.save_csv import api


@api.route('/')
def index():
    return 'hello, world'


@api.route('/<re(r".*"):name>')
def html(name):
    return f'hello, {name}'
