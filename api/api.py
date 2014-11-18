# REFERENCE
# http://flask.pocoo.org/docs/0.10/quickstart/#a-minimal-application
# https://pythonhosted.org/Flask-SQLAlchemy/
# http://zetcode.com/db/postgresqlpythontutorial/
# http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
# http://blog.luisrei.com/articles/flaskrest.html

# DEPENDENCIES
#sudo pip install flask flask-restful
# pip install -U psycopg2

# Install dependencies: sudo easy_install psycopg2 pyyaml
import subprocess	# for making system calls
import psycopg2     # for communicating with postgres 
import psycopg2.extras
import yaml         # for reading yaml config file
import json
import textwrap
import os.path

from flask import Flask, jsonify, make_response
from flask.ext.restful import Resource, Api

app = Flask(__name__)
api = Api(app)

# Local settings
import settings
host = settings.host
port = settings.port
user = settings.user
password = settings.password

# Useful variables
psql_user = "psql -U " + user
atlas_db = "wikimaps_atlas" # Default database name
psycopg_connect_atlas= "dbname="+atlas_db+" user="+user
atlas_connect_ogr2ogr= "'host="+host+" user="+user+" dbname=wikimaps_atlas'"


def bash(command):
    "Runs shell command"
    print "bash: ",command
    subprocess.call(command, shell=True)
    return


def psql_bash(command):
    "Runs a postgres command in the shell"
    psql_command = psql_user + " -c \""+command+";\""
    bash(psql_command)
    return

def psql_sql(sql_file):
    "Runs a postgres SQL file"
    psql_sql = psql_user + " -d "+atlas_db+" -f "+sql_file
    bash(psql_sql)
    return

# API Index
@app.route('/api/v1/')
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
@app.route('/api/v1/world/', methods=['GET'])
def list_adm0_areas():
    atlas = psycopg2.connect(psycopg_connect_atlas)
    atlas_cur = atlas.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    ## Load list of country names to atlas.adm0
    atlas_cur.execute("SELECT sovereignt,iso_a2 FROM adm0_area;")
    countries = atlas_cur.fetchall()
    atlas.close()
    return json.dumps(countries)

# Return list of adm1 areas for a given adm0 area
@app.route('/api/v1/world/<adm0_area>', methods=['GET'])
def list_adm1_areas(adm0_area):
    atlas = psycopg2.connect(psycopg_connect_atlas)
    atlas_cur = atlas.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    atlas_cur.execute("SELECT name,code_hasc FROM adm1_area WHERE admin LIKE '"+ adm0_area +"' OR iso_a2 LIKE '"+ adm0_area +"';")
    countries = atlas_cur.fetchall()
    atlas.close()
    return json.dumps(countries)

# Return bbox of adm area
@app.route('/api/v1/bbox/<adm_area>', methods=['GET'])
def generate_adm_bbox(adm_area):
    atlas = psycopg2.connect(psycopg_connect_atlas)
    atlas_cur = atlas.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    ## If adm_area is a hasc code, lookup the adm1 table
    if "." in adm_area :
        atlas_cur.execute("SELECT ST_Box2D(the_geom) FROM adm1_area WHERE name LIKE '"+ adm_area +"' OR code_hasc LIKE '"+ adm_area +"';")
    else:
        atlas_cur.execute("SELECT ST_Box2D(the_geom) FROM adm0_area WHERE sovereignt LIKE '"+ adm_area +"' OR iso_a2 LIKE '"+ adm_area +"';")
    countries = atlas_cur.fetchall()
    atlas.close()
    return json.dumps(countries)

# Return geojson data of requested area
@app.route('/api/v1/geojson/<path:adm_area>', methods=['GET'])
def generate_geojson(adm_area):
    atlas = psycopg2.connect(psycopg_connect_atlas)
    atlas_cur = atlas.cursor(cursor_factory=psycopg2.extras.DictCursor)

    ## If adm_area is a hasc code, lookup the adm1 table
    if "." in adm_area :
        atlas_cur.execute("SELECT ST_AsGeoJson(the_geom) FROM adm1_area WHERE name LIKE '"+ adm_area +"' OR code_hasc LIKE '"+ adm_area +"';")
    else:
        atlas_cur.execute("SELECT ST_AsGeoJson(the_geom) FROM adm0_area WHERE sovereignt LIKE '"+ adm_area +"' OR iso_a2 LIKE '"+ adm_area +"';")
    countries = atlas_cur.fetchall()
    atlas.close()
    return json.dumps(countries)


class Hasc:
    """ Heirarchal Administrative Subdivision Code """
    """ http://en.wikipedia.org/wiki/Hierarchical_administrative_subdivision_codes """
    
    def __init__(self, code):
        self.code = code
        
        # Convert the hasc code into a path by replacing "." with "/" (IND.TN.MD > IND/TN/MD/)
        self.data_dir = code.replace(".","/")+"/"

        # Calculate admin level of the requested area 
        self.adm_level = self.code.count(".")
        
        # Set the relevant shape table for the area
        self.adm_area_table = "adm" + str(self.adm_level) + "_area"
    
    def topojson(self, query): 
        """ Generate a topojson and geojson file for the area """
        
        # Construct file paths
        file_name = "adm" + str(self.adm_level)     # adm0 | adm1
        file_dir = "../data/" + self.data_dir       # ../data/IN/MD/
        file_path = file_dir + file_name            # ../data/IN/MD/adm2
        target_file = file_path+".topojson"         # ../data/IN/MD/adm2.topojson

        # If target file does not exist
        if not os.path.exists(target_file):
            
            # Create a new directory if it does not exist
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
                
            # Now generate the files
            postgis2geojson(self.adm_area_table,file_path,"-w \"iso_a2 LIKE '"+self.code+"'\"" )

        # Read generated file
        with open(target_file, 'r') as f:
            try:
                return json.dumps(json.load(f))
            finally:
                f.close()
                
# Run a postgis2geojson command
# using https://github.com/jczaplew/postgis2geojson
def postgis2geojson(table,output,options=""):
    bash("python ../postgis2geojson/postgis2geojson.py -d wikimaps_atlas -u postgres -g the_geom --topojson -t "+table+" -o "+output+" "+options)
    
# Return topojson data of requested area
@app.route('/api/v1/topojson/<hasc_code>', methods=['GET'])
def generate_topojson(hasc_code):
    H = Hasc(hasc_code)    
    return H.topojson("")

# 404 Error handler
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(debug=True)