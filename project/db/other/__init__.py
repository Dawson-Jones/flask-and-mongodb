from flask import Blueprint

api = Blueprint('other', __name__)
from . import others
