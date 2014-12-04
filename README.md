make-data-json
=========

Makefiles to process GIS data to json/topojson for Wikimaps Atlas.

# Workflow

* Create postgres database with postgis extensions
* Load GIS data shapefiles into database 
* Run spatial queries on database to generate new shapefiles
* Optimize shapefiles as topojson

# Server Requirements

* Postgres 9.3 with PostGIS 1.5
* Python 2.7

# Installation

* Clone this repository 
* Initialize and update the submodules
```
git submodule init
git submodule update
```

# Dependencies

## Python packages
```
sudo apt-get install python-psycopg2
```

## Node packages
```
npm install topojson
```