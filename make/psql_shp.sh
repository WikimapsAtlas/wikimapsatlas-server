#!/bin/bash

# Query 
pgsql2shp -u postgres -h localhost -p 5432 -g way -f ~/Documents/GIS/test.shp osm "SELECT * FROM planet_osm_line where ref LIKE '%NH%'"

