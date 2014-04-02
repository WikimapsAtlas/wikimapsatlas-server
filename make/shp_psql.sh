#!/bin/bash
# Load GIS data sources into a postgis database

# v0.1: by Arun Ganesh

# Database settings
USER=postgres
HOST=localhost
PORT=5432

# GIS data sources
DATA_PATH=~/Documents/GIS/data				# Folder where your data is download
SQL_PATH=$DATA_PATH/sql

## Natural Earth Data: dbname=ne download=www.naturalearthdata.com 
NATURALEARTH=$DATA_PATH/natural_earth_vector	# Unzipped folder


while read layer
do
echo "Processing $NATURALEARTH$/110m_cultural/$layer"
echo "Generating SQL"
shp2pgsql -s 4326 -W LATIN1 -d $NATURALEARTH$layer.shp $layer ne > $NATURALEARTH$layer.sql | psql $USER -h $HOST –p $PORT -d ne -f $NATURALEARTH$layer.sql

echo "Writing to postgres database: ne"


done < layers_ne.txt



#psql $USER -d ne -h $HOST –p $PORT  -f sql/110m_admin_0_countries.sql
#psql $USER -d ne -h $HOST –p $PORT  -f sql/110m_admin_0_boundary_lines_land.sql
