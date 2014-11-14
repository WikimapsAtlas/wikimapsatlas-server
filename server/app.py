# Wikiatlas API
# /api/v1

# METHODS
# GET
# /world List available countries with 2 letter ISO code
# /world/<country_name|iso_a2> List administrative subunuts within country with hasc codes
# /bbox/<country_name|iso_a2|hasc> Return bounding box of country name or iso or hasc code
# /iso2/<country_name|iso3> Return ISO_a2 from hasc or iso_a3 code or country name
# /topojson/<iso_a2|hasc>/adm|natural|highway|railway|place|waterway Return topojson data for requested admin area

# REFERENCE
# http://flask.pocoo.org/docs/0.10/quickstart/#a-minimal-application
# https://pythonhosted.org/Flask-SQLAlchemy/
# http://zetcode.com/db/postgresqlpythontutorial/
# http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask

# DEPENDENCIES
#sudo pip install flask
# pip install -U psycopg2
# Database settings
host = "localhost"
port = "5432"
user = "postgres"
password = ""
psql_user = "psql -U " + user
atlas_db = "wikimaps_atlas" # Default database name
psycopg_connect_atlas= "dbname="+atlas_db+" user="+user
atlas_connect_ogr2ogr= "'host="+host+" user="+user+" dbname=wikimaps_atlas'"

# Install dependencies: sudo easy_install psycopg2 pyyaml
import subprocess	# for making system calls
import psycopg2     # for communicating with postgres 
import psycopg2.extras
import yaml         # for reading yaml config file
import json

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

#!flask/bin/python
from flask import Flask, jsonify, make_response

app = Flask(__name__)

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

#def atlas_query_by_code

# Return topojson data of requested area
@app.route('/api/v1/topojson/<path:adm_area>', methods=['GET'])
def generate_topojson(adm_area):
    atlas = psycopg2.connect(psycopg_connect_atlas)
    atlas_cur = atlas.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    
#        countries = atlas_query_by_code("ST_Box2D(the_geom)",hasc_code)

    ## If adm_area is a hasc code, lookup the adm1 table
    if "." in adm_area :
        atlas_cur.execute("SELECT ST_AsTopoJSON(the_geom) FROM adm1_area WHERE name LIKE '"+ adm_area +"' OR code_hasc LIKE '"+ adm_area +"';")
    else:
        atlas_cur.execute("SELECT ST_Box2D(the_geom) FROM adm0_area WHERE sovereignt LIKE '"+ adm_area +"' OR iso_a2 LIKE '"+ adm_area +"';")
    countries = atlas_cur.fetchall()
    atlas.close()
    return json.dumps(adm_area)

# 404 Error handler
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(debug=True)