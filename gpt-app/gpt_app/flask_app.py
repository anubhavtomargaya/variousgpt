""" 
Using application factory, i.e. create_app() contains all the steps involved in
creating the flask application. due to which some routes are also inside this 
function. They can be added as a blueprint but I am using these as tools while 
developement. Run this with wsgi.py" 
"""
# from common import fh
from flask import Flask, jsonify
from flask_cors import CORS

from gpt_app.blueprints.gptube import gpt_app
from gpt_app.blueprints.google_auth import google_auth
from gpt_app.blueprints.view import view_app
from gpt_app.common.session_manager import *


import logging
logging.basicConfig(level=logging.INFO)  

def create_app():
    app = Flask(__name__)
    # app.logger.addHandler(file_handler)
    # app.logger.addHandler(fh)
    app.logger.info('Flask app started')
    CORS(app)
    app.logger.info('Flask app CORSed')

    app.secret_key = "MYSK3Y"
    # # os.environ.get("FN_FLASK_SECRET_KEY", default=False)

    app.register_blueprint(google_auth, url_prefix='/google')
    app.logger.info('Flask bp registerd, %s',"/google")

    app.register_blueprint(gpt_app, url_prefix='/api/v1/gptube')
    app.logger.info('Flask bp registerd, %s',"/gptube")

    app.register_blueprint(view_app, url_prefix='/api/v1/view')
    app.logger.info('Flask bp registerd, %s',"/view")

    @app.route('/session',methods=['GET'])
    def session_debugger():
        # if not is_logged_in():pass
            # return redirect(url_for('login'))
        # Render the home page with a table or dashboard
        # else:
            return jsonify(get_session_items())
        # return redirect(url_for('login'))  


    
    ## added this route for startup help
    @app.route('/') 
    def index():
        sth = """ <p> - /google for google auth, fetching token for user & permissions etc. </br>
                    - /session route at __main__ for docs </br> 
                    - 
    """
        return sth
    return app

app = create_app()