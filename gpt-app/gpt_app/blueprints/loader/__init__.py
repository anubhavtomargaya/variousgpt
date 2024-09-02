from flask import Blueprint,make_response
import functools

loader_app = Blueprint('loader', __name__)


from . import routes