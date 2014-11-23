# Common utility functions and variables for working with the local system

# Install dependencies: sudo easy_install psycopg2 pyyaml
import subprocess	# for making system calls
import psycopg2     # for communicating with postgres 
import psycopg2.extras
import yaml         # for reading yaml config file
import json
import os.path

# Local settings
from settings import *

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

def psql_atlas(query):
    "Executes a query on the atlas database"
    
    # Connect to atlas
    atlas = psycopg2.connect(psycopg_connect_atlas)
    atlas_cur = atlas.cursor()
    atlas_cur.execute(query)
    atlas.commit()
    
    # Close the connection
    atlas_cur.close()
    atlas.close()
    return

# Run a postgis2geojson command
# using https://github.com/jczaplew/postgis2geojson
def postgis2geojson(table,output,options=""):
    bash("python ../postgis2geojson/postgis2geojson.py -d wikimaps_atlas -u postgres -g the_geom --topojson -t "+table+" -o "+output+" "+options)