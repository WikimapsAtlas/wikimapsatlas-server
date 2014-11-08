#!/usr/bin/env python
# coding: utf-8
#Makes wikimaps atlas database

# Workflow

# Database settings
host = "localhost"
port = "5432"
user = "postgres"
psql_user = "psql -U " + user
atlas_db = "wikimaps_atlas" # Default database name
psycopg_connect_atlas= "dbname="+atlas_db+" user="+user
atlas_connect_ogr2ogr= "'host="+host+" user="+user+" dbname=wikimaps_atlas'"

# Install dependencies: sudo easy_install psycopg2 pyyaml
import subprocess	# for making system calls
import psycopg2     # for communicating with postgres 
import psycopg2.extras
import yaml         # for reading yaml config file

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
    DROP TABLE atlas_join;
    CREATE TABLE atlas_join(
        id varchar(10), 
        name varchar(30), 
        data_table varchar(30),
        shape_table varchar(30)
    );
     DROP TABLE atlas_type;
    CREATE TABLE atlas_type(
        id varchar(10), 
        name varchar(50), 
        data_table varchar(30),
        shape_table varchar(30)
    );
    """)
    atlas.commit()
    
    atlas_cur.execute("""
    INSERT INTO atlas_join
        (id, name, data_table, shape_table)
    VALUES (
        'adm0-a',
        'Admin Level 0 Boundaries',
        'adm0.name',
        'adm0_area.admin'
    ),
    (
        'adm1-a',
        'Admin Level 1 Boundaries',
        'adm1.name',
        'adm1_area.admin'
    );    
    """)
    atlas.commit()
    
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
    atlas.commit()
    
    atlas_cur.close()
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
    
    atlas_cur.close
    atlas.close
    return


def export_atlas():
    "Output atlas data files and makefiles"
    
    with open('db/export.yaml', 'r') as f:
        "Load atlas export configuration"
        export_config = yaml.load(f)
    
    export_folder(export_config,export_config["base_path"])
    return
    

def export_folder(folder_config,path):
    "Export a folder with relevant json files"
 
    # Connect to atlas
    atlas = psycopg2.connect(psycopg_connect_atlas)
    atlas_cur = atlas.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    ## Load list of country names to atlas.adm0
    atlas_cur.execute("SELECT name from adm0;")
    countries = atlas_cur.fetchall()
    atlas.close()
    
    # Create folder
    adm0_names= open("db/adm0_iso_a3.txt")
    for i in adm0_names:
        iso_a3=i.rstrip('\n')
        
        # Generate country outline
        #bash("ogr2ogr -f 'GeoJSON' "+path+iso_a3+".adm0.geojson PG:"+atlas_connect_ogr2ogr+" -sql \"select * from adm0_area where iso_a3='"+iso_a3+"'\"")
        # Covert to topojson
        #bash("topojson -o ../../wikimapsatlas.github.io/atlas/"+iso_a3+".adm0.topojson "+path+iso_a3+".adm0.geojson")
        
        # Generate admin1 units per country
        bash("ogr2ogr -f 'GeoJSON' "+path+iso_a3+".adm1.geojson PG:"+atlas_connect_ogr2ogr+" -sql \"select * from adm1_area where sr_adm0_a3='"+iso_a3+"'\"")
        
        # Covert geojson to topojson and move to atlas website repo
        # See https://github.com/mbostock/topojson/wiki/Command-Line-Reference
        # Natural Earth Admin1 properties
        # id : Unique id used to reference the shape from the database. In the format "iso_a2-shape_number"
        # name : International name in Latin alphabet
        # hasc : Heirarchial Administrative Subdivision Code used for building spatial relationships with parent and child regions
        # type_en : Word describing the type of the feature
        # scalerank : Integer denoting the relative importance of the feature. 1 is the highest importance on a global level
        # note : Free text that is displayed as a footnote
        simplify = "--quantization 1e4 --simplify 0.00000001"
        properties = "--id-property adm1_code -p name,scalerank,admin,type_en,hasc=code_hasc,provnum_ne,note "
        bash("topojson -o ../../wikimapsatlas.github.io/atlas/"+iso_a3+".adm1.topojson "+path+iso_a3+".adm1.geojson "+properties+simplify)
        
        
    # Recursively generate subfolders
    try:
        for i in folder_config["folder"]:
            print "Generating folder: ",i["map_location"],"\n"
            if i.has_key("folder"):
                export_folder(i,path)
    except KeyError:
        return
    

def main():
    #create_atlas()
    #load_map_data()
    create_atlas_tables()
    build_atlas()
    export_atlas()
    return
main()