#!/usr/bin/env python
# coding: utf-8
#Makes wikimaps atlas database

# Database settings
host = "localhost"
port = "5432"
user = "postgres"
psql_user = "psql -U " + user
atlas_db = "wikimaps_atlas" # Default database name
psycopg_connect_atlas= "dbname="+atlas_db+" user="+user

# Install dependencies: sudo easy_install psycopg2 pyyaml
import subprocess	# for making system calls
import psycopg2     # for communicating with postgres 
import yaml         # for reading yaml config file

def bash(command):
    "Runs shell command"
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
    
    
def create_database(name):
    "Drop and create a new database"
    
    return
    
    
def create_atlas():
    "Creates fresh wikimaps database"
    
    psql_bash("drop database "+atlas_db)
    psql_bash("create database "+atlas_db) 
    # Add PostGIS extensions
    psql_sql("/usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql")
    psql_sql("/usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql")
    return

def load_map_data():
    "Load GIS data into database"
    
    with open('db/layers.yaml', 'r') as f:
        "Load atlas data configuration"
        atlas_data = yaml.load(f)
    
     # Load shapefile layers into Atlas db using shp2pgsql
    for datasource in atlas_data["datasource"]:
        for layer in datasource["layer"]:
            path = atlas_data["datapath"]+datasource["path"]+layer["path"]
            query = "shp2pgsql -s 4326 -W LATIN1 -d "+path+" "+layer["table_name"]+" "+atlas_db+" > temp.sql | psql "+user+" -h "+host+" –p "+port+" -d "+atlas_db+" -f temp.sql"
            bash(query)
            print("Loaded "+datasource["path"]+" successfuly")
    return
                    
def create_atlas_tables():
    
    # Connect to atlas
    atlas = psycopg2.connect(psycopg_connect_atlas)
    atlas_cur = atlas.cursor()

    ## Create atlas.master
    atlas_cur.execute("""
    DROP TABLE master;
    CREATE TABLE master(
        name varchar(20), 
        scale varchar(20), 
        data_table varchar(30), 
        data_key varchar(30),
        shape_table varchar(30), 
        shape_key varchar(30)
    );
    """)
    
    ## Create atlas.adm0
    atlas_cur.execute("""
    DROP TABLE adm0;
    CREATE TABLE adm0(
        id varchar(3), -- en.wikipedia.org/wiki/ISO_3166-1_numeric
        id_ varchar(8), -- previous id
        _id varchar(8), -- next id
        id_a3 varchar(6), -- en.wikipedia.org/wiki/ISO_3166-1_alpha-3
        name varchar(80) NOT NULL,	-- adm0 name
        region_name varchar(40),	-- atlas region name
        date date,      -- date of formation
        _date date,		-- end date
        wikidata_id varchar(16)	-- wikidata item code http://wikidata.org
    );
    """)
    
    atlas_cur.close()
    atlas.commit()
    atlas.close()
    return
    
def build_atlas():
    "Builds the atlas database"
            
    # Connect to atlas
    atlas = psycopg2.connect(psycopg_connect_atlas)
    atlas_cur = atlas.cursor()
    
    ## Load list of country names to atlas.adm0
    adm0_names= open("db/adm0_names.txt")
    atlas_cur.copy_from(adm0_names, 'adm0', columns=("name",))
    atlas.commit()
    adm0_names.close()

    # Join values from shapefiles
    atlas_cur.execute("""
    UPDATE adm0
    INNER JOIN wikimaps_atlas.ne_adm0_polygon_l AS ne
    ON adm0.id = ne.iso_n3;
    """)
    atlas.commit()
    
    atlas_cur.close
    atlas.close

def main():
    #create_atlas()
    #load_map_data()
    create_atlas_tables()
    build_atlas()
    return
main()