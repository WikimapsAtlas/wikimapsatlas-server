#!/data/project/wikiatlas2014/wikimapsatlas-server/api/bin/python

# Cloned from https://wikitech.wikimedia.org/wiki/User:Pathoschild/Getting_started_with_Flask
# HELP http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvii-deployment-on-linux-even-on-the-raspberry-pi

from flup.server.fcgi import WSGIServer
from flask import Flask, request

from api import app

# register 'hello world' page
@app.route("/")
def hello():
        return "Welcome the the Wikimaps Atlas API"
 
# start server
if __name__ == '__main__':
    WSGIServer(app).run()