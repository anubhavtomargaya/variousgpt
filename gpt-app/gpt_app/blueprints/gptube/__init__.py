from flask import Blueprint,make_response
import functools

gpt_app = Blueprint('gptube', __name__)


from . import routes