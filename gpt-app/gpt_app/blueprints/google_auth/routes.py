

from authlib.client import OAuth2Session
from flask import current_app, url_for, redirect
import flask 
import ast
import json 

from gpt_app.common.session_manager import set_auth_state,set_auth_token, clear_auth_session,\
                                          get_next_url,is_logged_in,set_google_id, \
                                          set_user_email
from gpt_app.common.constants import AUTH_REDIRECT_URI, AUTH_REDIRECT_URI_HTTPS, CLIENT_ID,CLIENT_SECRET,AUTHORIZATION_SCOPE,AUTHORIZATION_URL,ACCESS_TOKEN_URI,BASE_URI
print("CLIENT_ID",CLIENT_ID)
from .auth import get_user_info


from . import google_auth, no_cache



@google_auth.route('/login',methods=['GET','POST'])
@no_cache
def login():

        
    if is_logged_in():
        return "Already logged in, proceed to api/v1/mailbox"
    # redirect(url_for('index'))
    current_app.logger.info("RUNNING LOGIN")
    current_app.logger.info('building session')
    print("auth url")
    print(url_for('google_auth.google_auth_redirect',
                                            _external=True))
    print('url base',AUTH_REDIRECT_URI_HTTPS)
    session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
                            scope=AUTHORIZATION_SCOPE,
                            redirect_uri=AUTH_REDIRECT_URI_HTTPS,
                            _external=True)
                            #   url_for('google_auth.google_auth_redirect',
                                                #  _external=True)) #no need to use 

    uri, state = session.create_authorization_url(AUTHORIZATION_URL)
    current_app.logger.debug("state %s",state )
    current_app.logger.debug("uri %s",uri)
    set_auth_state(state)

    return flask.redirect(uri, code=302)

@google_auth.route('/auth')
@no_cache
def google_auth_redirect():
    # current_app.logger.info("keys!! %s",flask.session.keys())
    req_state = flask.request.args.get('state', default=None, type=None)
    current_app.logger.debug('req state!!: %s',req_state)
    # if req_state != flask.session[AUTH_STATE_KEY]:
    #     response = flask.make_response('Invalid state parameter', 401)
    #     return response
    try:
        current_app.logger.info('creating session')
        session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
                                scope=AUTHORIZATION_SCOPE,
                                state=req_state,
                                redirect_uri=
                                        AUTH_REDIRECT_URI_HTTPS)
    except Exception as e:
        return flask.jsonify(e)
    current_app.logger.debug(' session built')
        
    oauth2_tokens = session.fetch_access_token(
                        ACCESS_TOKEN_URI,            
                        authorization_response=flask.request.url)

    current_app.logger.debug('oath tokens!! : %s',oauth2_tokens)
    set_auth_token(oauth2_tokens)
    default_login_url = url_for('google_auth.etc',data=oauth2_tokens)

    next_url = get_next_url()
    current_app.logger.info(' next url %s',next_url) 
    if next_url:

        current_app.logger.info(' next url %s',next_url) 
        # clear_next_url()
        return flask.redirect(next_url, code=307)
    else: 
        return flask.redirect(default_login_url, code=307)
    

@google_auth.route('/logout')
@no_cache
def logout():
    # flask.session.pop(AUTH_TOKEN_KEY, None)
    # flask.session.pop(AUTH_STATE_KEY, None)
    clear_auth_session()
    
    return flask.redirect(BASE_URI, code=302)

from gpt_app.common.supabase_handler import check_user_exist, save_user
@google_auth.route('/etc')
def etc():
    
    d=flask.request.args['data']
   
    current_app.logger.info('body: %s',d)
    d = ast.literal_eval(d)
    current_app.logger.info('body: %s',d)
    current_app.logger.info('type: %s',type(d))
    if is_logged_in():
        user_info = get_user_info()
        name=user_info['name']
        user = check_user_exist(user_info['email'])
        if user:
            print('user exist')
            # get last login
            pass 
        else:
            print('saving user ')
            if not save_user(email=user_info['email'],
                      name=name,
                      google_id=user_info['id']):
                raise Exception("Unable to save user to database ")
            else:

                current_app.logger.info("user saved %s",user_info)
        # expiresat=d['expires_at']
        # val=d['access_token'][0:6]
        set_google_id(user_info['id'])
        set_user_email(user_info['email'])
        # curr_pth = pathlib.Path(__file__).resolve().parent
        # tkdir = pathlib.Path('temp','etc')
        # filename=f'token_{name}_{val}_{expiresat}_.json'
      
        # filepath = pathlib.Path(curr_pth,tkdir,filename)
        # with open(filepath,'w') as f:
            # print(json.dump(dew,f))
        
        ###check if not able to save file in ec2

        return flask.redirect(url_for('view_app.index'))
        # return '<div>You are currently logged in as ' + user_info['given_name'] + '<div><pre>' + json.dumps(user_info, indent=4) + "</pre>"
    # flask.redirect(BASE_URI, code=302)
    else:
        # return render_template("index.html")

        return flask.jsonify("ERORROR )")

