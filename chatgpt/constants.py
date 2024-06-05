OPENAI_KEY= 'OPENAI_KEY'
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