from flask import Blueprint,make_response
import functools

company_app = Blueprint('company_app', __name__)


from . import routes