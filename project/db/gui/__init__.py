from flask import Blueprint

app = Blueprint('gui', __name__)
from . import gui
