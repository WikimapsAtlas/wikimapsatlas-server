# REFERENCE
# http://flask.pocoo.org/docs/0.10/quickstart/#a-minimal-application
# https://pythonhosted.org/Flask-SQLAlchemy/
# http://zetcode.com/db/postgresqlpythontutorial/
# http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
# http://blog.luisrei.com/articles/flaskrest.html

# DEPENDENCIES
# pip install -U psycopg2 flask flask-restful pyyaml

from utils import psycopg2,psycopg_connect_atlas
from models import Hasc
from wikiatlas import Gid
import json, utils
import time
import logging

from flask import Flask, jsonify, make_response, Response, request
from flask.ext.cors import CORS, cross_origin
from flask.ext.restful import Resource, Api

app = Flask(__name__)
api = Api(app)
# Enable cross domain requests
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type', 'X-Requested-With'

# API Index
@app.route('/', methods=['GET'])
def api_index():
    return app.send_static_file('index.html')

@app.route('/v1/', methods=['GET'])
def api_v1():
    return app.send_static_file('v1.html')


@app.route('/v1/index/', methods=['GET'])
def list_countries():
    return utils.atlas2json("SELECT hasc, name, ST_Box2D(geom) FROM adm0_area;").replace("BOX(","").replace(")","").replace("st_box2d","bbox")

@app.route('/v1/index/<hasc>', methods=['GET'])
def list_subunits(hasc):
    H = Hasc(hasc)
    return H.subunits()

@app.route('/v1/bbox/<hasc>', methods=['GET'])
def generate_bbox(hasc):
    H = Hasc(hasc)
    return H.bbox()

@app.route('/v1/center/<hasc>', methods=['GET'])
def generate_centroid(hasc):
    H = Hasc(hasc)
    return H.center()

@app.route('/v1/near/<hasc>', methods=['GET'])
def find_nearby_areas(hasc):
    H = Hasc(hasc)
    return H.near()

@app.route('/v1/data/geojson/<hasc>', methods=['GET'])
def generate_geojson(hasc):
    H = Hasc(hasc)
    
    return Response(H.json("geojson"),  mimetype='application/json')
    
#@app.route('/v1/data/<hasc_code>', methods=['GET'])
#def generate_topojson(hasc_code):
#    H = Hasc(hasc_code)    
#    return H.json()

@app.route('/v1/data', methods=['POST'])
@cross_origin()
def data():
    """Data method"""
    G = Gid(request.json)
    return G.json()
#    return L.json(request.json['layer'], request.json['topology'])

# configure Flask logging
from logging import FileHandler
logger = FileHandler('error.log')
app.logger.setLevel(logging.INFO)
app.logger.addHandler(logger)
 
# log Flask events
app.logger.debug(u"Flask server started " + time.asctime())
@app.after_request
def write_access_log(response):
    app.logger.debug(u"%s %s -> %s" % (time.asctime(), request.path, response.status_code))
    return response

@app.errorhandler(500)
def internal_error(exception):
    app.logger.exception(exception)
    return response
        
# 404 Error handler
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(debug=False)