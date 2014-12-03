#!/wikimapsatlas-server/api/bin/python

# Cloned from https://wikitech.wikimedia.org/wiki/User:Pathoschild/Getting_started_with_Flask
# HELP http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvii-deployment-on-linux-even-on-the-raspberry-pi

from flask import Flask, request
import time
import logging

from api import app

# create Flask application
app = Flask(__name__)

# configure Flask logging
from logging import FileHandler
logger = FileHandler('error.log')
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(logger)
 
# log Flask events
app.logger.debug(u"Flask server started " + time.asctime())
@app.after_request
def write_access_log(response):
    app.logger.debug(u"%s %s -> %s" % (time.asctime(), request.path, response.status_code))
    return response
 
# start server
if __name__ == '__main__':
    WSGIServer(app).run()