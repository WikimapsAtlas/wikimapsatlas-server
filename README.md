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
## Configure make-module
Create symlinks for the data and output directories
```
cd wikimapsatlas-server
ln -s ../data/download make-modules/data
ln -s ../data/ make-modules/output
```

# Dependencies
## Node packages
```
npm install topojson
```

# Deployment
## Creating python virtual environment
virtualenv .
source bin/activate'
pip install -r ../requirements.txt

## Server config
See https://wikitech.wikimedia.org/wiki/User:Pathoschild/Getting_started_with_Flask

### FCGI
vi ~/.lighttpd.conf 
```
fastcgi.server += ( "/wikiatlas2014/api" =>
    ((
        "socket" => "/tmp/wikiatlas2014-fcgi.sock",
        "bin-path" => "/data/project/wikiatlas2014/wikimapsatlas-server/api/app.fcgi",
        "check-local" => "disable",
        "max-procs" => 1,
    ))
)

url.redirect = ( "^/wikiatlas2014/api$" => "/wikiatlas2014/api/" )

debug.log-request-handling = "enable"

```

## PostGIS config
'''
vi api/setting.py
'''

'''
host = "localhost"
port = "5432"
user = "postgres"
password = "postgres"
database = "wikimaps_atlas"
geometry = "geom"
'''

## Data config
cd wikimapsatlas-server
symlink data

## Updating server
cd wikimapsatlas-server
git pull

## Server logs
```
vi ~/error-atlas.log
'''


