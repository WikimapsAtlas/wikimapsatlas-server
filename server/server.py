# Wikiatlas Flask Server
#sudo pip install flask
# pip install -U psycopg2
# pip install Flask-SQLAlchemy

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_pyfile(config.py)
db = SQLAlchemy(app)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run()