import json
from pathlib import Path
# export PYTHONPATH=/home/anubhavsinghtomar/Anubhav/Anubhav/my-projects/variousgpt/gpt-app$PYTHONPATH
ACCESS_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'
# "https://oauth2.googleapis.com/token"
AUTHORIZATION_URL ='https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent'
# "https://accounts.google.com/o/oauth2/auth"
AUTHORIZATION_SCOPE =["https://www.googleapis.com/auth/gmail.readonly","https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"]
# 'openid email profile'
# ['https://www.googleapis.com/auth/gmail.readonly','openid','email']

AUTH_REDIRECT_URI ="http://localhost:5000/google/auth"
AUTH_REDIRECT_URI_HTTPS ="https://wallartlabs.tech/google/auth"
#  os.environ.get("FN_AUTH_REDIRECT_URI", default=False)
BASE_URI =   "http://localhost:5000/"
BASE_REDIRECT_URI =   "http://localhost:5000/fetch"
# os.environ.get("FN_BASE_URI", default=False)
with open(Path(Path(__file__).parent.resolve(), 'env.json')) as f:
    env = json.load(f)

CLIENT_ID = env.get('CLIENT_ID')
# os.environ.get("FN_CLIENT_ID", default=False)
CLIENT_SECRET = env.get('CLIENT_SECRET')
OPENAI_KEY = env.get('OPENAI_KEY')
# os.environ.get("FN_CLIENT_SECRET", default=False)

########## ------------------------------- ############

CONFIG_FILE = 'config.json'
DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_SYSTEM_CONTENT =  "You will be provided with unstructured data, and your task is to parse it into CSV format."
XPFLASK_SYSTEM_CONTENT = """you are a coding assistant that knows everything about python, specialising in web services. Flask is you favourite framework. 
                            you have scaled flask apps to millions of users using nginx and uvicorn in the past. Upon asking any questions you give answers in steps, 
                            breaking down the problem into parts and then defining proper directory structure for proejcts, maintaining config and enums to make it easy
                            for development. You use state of the art best practices to utilise python functionality at best. Learning from your years of experience in
                            seeing python mature over the years since python 2.7
                         """
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 64
DEFAULT_TOP_P = 1

# -- ----- --- - 

JINA_READER_PREFIX  =  "https://r.jina.ai/"
JINA_SEARCH_PREFIX  =  "https://s.jina.ai/"