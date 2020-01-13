from flask import Blueprint

app = Blueprint('user', __name__)
from . import user, threshold
