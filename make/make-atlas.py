#!/usr/bin/env python
#Makes wikimaps atlas database

# Install dependencies: sudo easy_install psycopg2 pyyaml
import subprocess	# for making system calls
import psycopg2 	# for communicating with postgres 
import yaml		# for reading yaml config file


# Create atlas db
subprocess.call("psql -U postgres -c \"drop database atlas;\"", shell=True)
subprocess.call("psql -U postgres -c \"create database atlas;\"", shell=True)

# Create ne db
subprocess.call("psql -U postgres -c \"drop database ne;\"", shell=True)
subprocess.call("psql -U postgres -c \"create database ne;\"", shell=True)
subprocess.call("psql -U postgres -d ne -f /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql", shell=True)
subprocess.call("psql -U postgres -d ne -f /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql", shell=True)

# Connect to atlas
atlas = psycopg2.connect("dbname=atlas user=postgres")
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
adm0_names= open("adm0_names.txt")
atlas_cur.copy_from(adm0_names, 'adm0', columns=("name",))
atlas.commit()
adm0_names.close()

## Join attributes from naturalearthdata shapefiles
### Connect to ne db
ne = psycopg2.connect("dbname=atlas user=postgres")
ne_cur = atlas.cursor()

atlas_cur.execute("SELECT * from adm0;")
print atlas_cur.fetchall()

atlas_cur.close
atlas.close


#./create_tables.sh


