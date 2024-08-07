""" 
Using application factory, i.e. create_app() contains all the steps involved in
creating the flask application. due to which some routes are also inside this 
function. They can be added as a blueprint but I am using these as tools while 
developement. Run this with wsgi.py" 
"""
# from common import fh
from flask import Flask, jsonify,redirect, render_template, url_for
from flask_cors import CORS
from gpt_app.common.session_manager import set_auth_state,set_auth_token, clear_auth_session, get_next_url,is_logged_in
from gpt_app.blueprints.gptube import gpt_app
from gpt_app.blueprints.google_auth import google_auth
from gpt_app.blueprints.view import view_app
from gpt_app.common.session_manager import *


import logging
logging.basicConfig(level=logging.INFO)  

def create_app():
    
    app = Flask(__name__)
    app.config['PREFERRED_URL_SCHEME'] = 'https'
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

    app.register_blueprint(view_app, url_prefix='/view')
    app.logger.info('Flask bp registerd, %s',"/view")

    @app.route('/session',methods=['GET'])
    def session_debugger():
        # if not is_logged_in():pass
            # return redirect(url_for('login'))
        # Render the home page with a table or dashboard
        # else:
            return jsonify(get_session_items())
        # return redirect(url_for('login'))  
    google_auth_page = 'google_auth.login'
    # print("url_for(google_auth_page)")
    # print(url_for(google_auth_page))
    default_home_page = 'view_app.index'
    default_error_page = """<body >  
                                <p>Oops... Login first</p>
                                <br>
                                <div style="text-align: center;"> 
                                    <h1 style="color: #ffaaaa; font-size: 3em;">:(</h1>
                                    <a href="{login}"> LOGIN </a>
                                </div>
                            </body>"""
   
    
    ## added this route for startup help
    @app.route('/') 
    def index():
        sth = """ <p> - /google for google auth, fetching token for user & permissions etc. </br>
                    - /session route at __main__ for docs </br> 
                    - /api/v1/gptube - app to serve the content with apis.
                    - /view/ - app to mimic front end client
    """
        if is_logged_in():
            return redirect(url_for(default_home_page))
        else:
             return default_error_page.format(login=url_for(google_auth_page))

    return app

app = create_app()