#!/bin/bash
# Load GIS data sources into a postgis database

# v0.1: by Arun Ganesh

# Database settings
USER=postgres
HOST=localhost
PORT=5432

# GIS data sources
DATA_PATH=~/Documents/GIS/data				# Folder where your data is download

## Natural Earth Data: dbname=ne download=www.naturalearthdata.com 
NATURALEARTH_PATH=$DATA_PATH/natural_earth_vector	# Unzipped folder

mkdir -p $DATA_PATH/sql
cd $DATA_PATH
shp2pgsql -W LATIN1 -srid=4326 $NATURALEARTH_PATH/110m_cultural/ne_110m_admin_0_countries.shp 110m_admin_0_countries ne > sql/110m_admin_0_countries.sql
shp2pgsql -W LATIN1 $NATURALEARTH_PATH/110m_cultural/ne_110m_admin_0_boundary_lines_land.shp 110m_admin_0_boundary_lines_land.shp ne > sql/110m_admin_0_boundary_lines_land.sql
psql $USER -d ne -h $HOST –p $PORT  -f sql/110m_admin_0_countries.sql,sql/110m_admin_0_boundary_lines_land.sql