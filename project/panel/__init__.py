from flask import Blueprint

api = Blueprint('panel', __name__)
from . import test
