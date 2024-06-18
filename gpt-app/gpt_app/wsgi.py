
""" Use this file to run the server for development.
        wdir :
             cd small-auth-app
    
    In production, use `gunicorn` 

        cd variousgpt/gpt-app
        (.venv) gunicorn  -w 4 -b 0.0.0.0:5000 "gpt_app.wsgi:app"
    """

from gpt_app.flask_app import create_app

app = create_app() 

        

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host='0.0.0.0',port=5000,debug=True)
    # app.run(debug=True)

