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
import json, utils

from flask import Flask, jsonify, make_response
from flask.ext.restful import Resource, Api

app = Flask(__name__)
api = Api(app)


# API Index
@app.route('/v1/')
def api_root():
    text = '''
    <h1>Wikiatlas API</h1>
    <h2>api/v1</h2>

    <ul>
    <li> <pre>/world</pre> List available countries with 2 letter ISO code</li>
    <li> <pre>/world/<country_name|iso_a2></pre> List administrative subunuts within country with hasc codes</li>
    <li> <pre>/bbox/<country_name|iso_a2|hasc></pre> Return bounding box of country name or iso or hasc code</li>
    <li> <pre>/iso2/<country_name|iso3></pre> Return ISO_a2 from hasc or iso_a3 code or country name</li>
    <li> <pre>/topojson/<iso_a2|hasc>/adm|natural|highway|railway|place|waterway</pre> Return topojson data for requested admin area</li>
    </ul>
    '''
    return textwrap.dedent(text).strip()

# Return list of adm0 areas
@app.route('/v1/world/', methods=['GET'])
def list_adm0_areas():
    return utils.atlas2json("SELECT hasc,name FROM adm0_area;")

# Return list of adm1 areas for a given adm0 area
@app.route('/v1/world/<hasc>', methods=['GET'])
def list_adm1_areas(hasc):
    H = Hasc(hasc)
    return H.subunits()

# Return bbox of adm area
@app.route('/v1/bbox/<hasc>', methods=['GET'])
def generate_adm_bbox(hasc):
    H = Hasc(hasc)
    return H.bbox()

# Return geojson data of requested area
@app.route('/v1/geojson/<hasc>', methods=['GET'])
def generate_geojson(hasc):
    H = Hasc(hasc)
    return H.json("geojson","")
    
# Return topojson data of requested area
@app.route('/v1/topojson/<hasc_code>', methods=['GET'])
def generate_topojson(hasc_code):
    H = Hasc(hasc_code)    
    return H.json("topojson","")

# 404 Error handler
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(debug=True)