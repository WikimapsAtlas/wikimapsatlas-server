make-data-json
=========

Makefiles to process GIS data to json/topojson for Wikimaps Atlas.

# Workflow

* Create postgres database with postgis extensions
* Load GIS data shapefiles into database 
* Run spatial queries on database to generate new shapefiles
* Optimize shapefiles as topojson
