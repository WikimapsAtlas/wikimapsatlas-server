#!/wikimapsatlas-server/api/bin/python

# Cloned from https://github.com/valhallasw/gerrit-patch-uploader/blob/master/app.fcgi
# HELP http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvii-deployment-on-linux-even-on-the-raspberry-pi

from flup.server.fcgi import WSGIServer
from api import app




if __name__ == '__main__':
    WSGIServer(app).run()