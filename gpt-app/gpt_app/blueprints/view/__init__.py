from flask import Blueprint,make_response
import functools

view_app = Blueprint('view_app', __name__)


from . import routes