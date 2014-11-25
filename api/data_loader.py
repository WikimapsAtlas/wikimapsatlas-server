# Wikimaps Atlas Database Creator

from utilities import bash, psql_bash
from models import Datasource
import yaml
import os.path

def create_atlas():
    "Creates fresh wikimaps database"
    psql_bash("drop database "+atlas_db)
    psql_bash("create database "+atlas_db) 
    # Add PostGIS extensions
    psql_sql("/usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql")
    psql_sql("/usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql")
    return


def download_map_data():
    "Download data sources"
    with open('sources.yaml', 'r') as f:
        atlas_data = yaml.load(f)
    
        # Download and unpack datasources
        for datasource in atlas_data["datasource"]:
            bash("wget -P "+output_dir+" "+datasource["download_url"])
        
    f.close()
    return


def load_sources():
    "Load GIS data into database"
    with open('data_loader/sources.yaml', 'r') as f:
        atlas_data = yaml.load(f)
        
        download_dir = atlas_data["download_dir"]
        
        # If data dir does not exists, create a new database and the directory for the data sources
        if not os.path.exists(download_dir):
            create_atlas()
            os.makedirs(download_dir)
        
        # Load shapefile layers into Atlas db using shp2pgsql
        for datasource in atlas_data["datasource"]:
            D = Datasource(datasource, download_dir)
            D.download()
    f.close()
    return
            
def main():
#    create_atlas()
#    download_map_data()
    load_sources()
    return
main()