#!/usr/bin/env python
# coding: utf-8
#Makes wikimaps atlas database

# Database settings
host = "localhost"
port = "5432"
user = "postgres"
psql_user = "psql -U " + user


# Install dependencies: sudo easy_install psycopg2 pyyaml
import subprocess	# for making system calls
import psycopg2     # for communicating with postgres 
import yaml         # for reading yaml config file

def bash(command):
    "Runs shell command"
    subprocess.call(command, shell=True)
    return


def psql_command(command):
    "Runs a postgres command in the shell"
    psql_command = psql_user + " -c \""+command+";\""
    bash(psql_command)
    return

def psql_sql(sql_file):
    "Runs a postgres SQL file"
    psql_sql = psql_user + " -d wikimaps_atlas -f "+sql_file
    bash(psql_sql)
    return
    
    
def create_database(name):
    "Drop and create a new database"
    psql_command("drop database "+name)
    psql_command("create database "+name)
    return
    
    
def create_atlas():
    "Creates fresh wikimaps database"
    with open('db/layers.yaml', 'r') as f:
        "Load atlas data configuration"
        atlas_data = yaml.load(f) 
        wikimaps_atlas = atlas_data["database_name"]
        
    create_database(wikimaps_atlas)  
    # Add PostGIS extensions
    psql_sql("/usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql")
    psql_sql("/usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql")
    return wikimaps_atlas

def load_map_data():
    "Load GIS data into database"
    
    with open('db/layers.yaml', 'r') as f:
        "Load atlas data configuration"
        atlas_data = yaml.load(f)
    
     # Load Atlas db
    for datasource in atlas_data["datasource"]:
        for layer in datasource["layer"]:
            path = atlas_data["datapath"]+datasource["path"]+layer["path"]
            query = "shp2pgsql -s 4326 -W LATIN1 -d "+path+" "+layer["table_name"]+" "+wikimaps_atlas+" > temp.sql | psql "+user+" -h "+host+" –p "+port+" -d "+wikimaps_atlas+" -f temp.sql"
            bash(query)
            print query
    return
                    

def build_atlas():
    "Builds the atlas database"
    with open('db/layers.yaml', 'r') as f:
        "Load atlas data configuration"
        atlas_data = yaml.load(f) 
            
    # Connect to atlas
    atlas = psycopg2.connect("dbname=wikimaps_atlas user=postgres")
    atlas_cur = atlas.cursor()

    ## Create atlas.adm0
    atlas_cur.execute("""
    CREATE TABLE adm0 (
        name varchar(80) NOT NULL,	-- country name
        start_date date,		-- date of formation
        end_date date,          
        next_name varchar(80),       
        previous_name varchar(80),
        wikidata_item varchar(16)	-- wikidata item code http://wikidata.org
    );
    """)

    ## Load list of country names to atlas.adm0
    adm0_names= open("db/adm0_names.txt")
    atlas_cur.copy_from(adm0_names, 'adm0', columns=("name",))
    atlas.commit()
    adm0_names.close()

    ## Join attributes from naturalearthdata shapefiles
    ### Connect to ne db
    ne = psycopg2.connect("dbname=atlas user=postgres")
    ne_cur = atlas.cursor()

    atlas_cur.execute("SELECT * from adm0;")
    print ne_cur.fetchall()

    atlas_cur.close
    atlas.close

def main():
    wikimaps_atlas = create_atlas()
    #load_map_data()
    return
main()