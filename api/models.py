import utils
import os, yaml, json
import psycopg2

# Wikiatlas Data Directory
atlas_data_dir = "../data/json/"

class Atlas:
    """The Atlas object"""
    
    def __init__(self):
        world = Hasc('*')
    
    
class Hasc:
    """ Heirarchal Administrative Subdivision Code """
    """ http://en.wikipedia.org/wiki/Hierarchical_administrative_subdivision_codes """
    
    def __init__(self, code):
        self.code = code
        
        # Convert the hasc code into a data path by replacing "." with "/" (IND.TN.MD > IND/TN/MD/)
        self.hasc_dir = code.replace(".","/")+"/"
        
        # For World level, use base directory
        if code == '*':
            self.hasc_dir = ''

        # Calculate admin level of the requested area 
        self.adm_level = self.code.count(".")
        
        # Set the relevant shape table for the area
        self.adm_area_table = "adm" + str(self.adm_level) + "_area"
        
        # Set the location directory for the current code
        self.data_dir = self.output_path('')
    
    def output_path(self, file_name):
        "Constructs the relative output path for the requested filename"
        return atlas_data_dir + self.hasc_dir + file_name
    
    
    def generate_atlas_index(self):
        "Generate an index json file for the territory"
#        target_file = output_path
#        with open(self.output_path('index.json'), 'r') as f:
    
    def query2json(self, table, file_name, where, json_type = 'topojson'):
        "Generates a json result from the requested database query"
        output_file = self.output_path( file_name )
        
        options = "-w \"{}\"".format(where)
        
        # If target file does not exist
        if not os.path.exists(output_file + '.' + json_type):
            
            # Create a new directory if it does not exist
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
                
            # Generate an index file for the region with list of subunits and bounding boxes
            self.generate_atlas_index()
        
            # Now generate the files and regenerate the index
            utils.postgis2geojson(table, output_file, options )

        # Read generated file
        with open(output_file + '.' + json_type, 'r') as f:
            try:
                return json.dumps(json.load(f))
            finally:
                f.close()
        
        
    def json(self, json_format="topojson", query=""): 
        """ Generate a topojson and geojson file for the area and return the appropriate format 
        Naming format:
        <hasc.code> / <layer><adm_lvl>
        """
        
        # Construct file paths
        file_name = "adm" + str(self.adm_level)     # adm0 | adm1
        
        return self.query2json(self.adm_area_table, file_name, "hasc LIKE '{}%'".format(self.code), json_format)

    def bbox(self):
        "Return the bounding box of the area"
        return utils.atlas2json("SELECT hasc, name,ST_Box2D(geom) FROM {} WHERE hasc LIKE '{}';".format(self.adm_area_table,self.code) )
    
    def center(self):
        "Return the centroid of the area"
        return utils.atlas2json("SELECT hasc, name, ST_Y(ST_Transform(centroid(geom),4326)), ST_X(ST_Transform(centroid(geom),4326)) FROM {} WHERE hasc LIKE '{}';".format(self.adm_area_table,self.code) )
    
    def subunits(self):
        "Return the list of subunits within the area"
        return utils.atlas2json("SELECT hasc, name FROM {} WHERE hasc LIKE '{}.%';".format("adm1_area",self.code) )
        
    def near(self):
        "Return the list of nearby areas"
        query1 = """
        SELECT hasc, name, ST_Y(ST_Transform(centroid(geom),4326)), ST_X(ST_Transform(centroid(geom),4326)) FROM {} WHERE hasc LIKE '{}'; 
        """.format(self.adm_area_table,self.code)
        query2 = """
        SELECT hasc, name, ST_Y(ST_Transform(centroid(geom),4326)), ST_X(ST_Transform(centroid(geom),4326)) FROM {} WHERE hasc LIKE '{}'; 
        """.format(self.adm_area_table,self.code)
        
        return utils.atlas2json(query1 + query2)
    
class Datasource:
    """A vector or raster source to be used in the Wikimaps Atlas Database"""
    
    def __init__(self, config, download_dir):
        self.config = config
        self.name = self.config["name"]
        self.download_dir = download_dir
        self.dir = download_dir + self.config["dir"]
        self.filepath = download_dir + self.config["download_url"].rsplit('/', 1)[-1]
        self.srs = self.config["srs"]
        self.fileformat = self.config["download_url"].rsplit('.', 1)[-1]
        
        
    def download(self):
        """Download the datasource if not already downloaded"""
        if not os.path.isfile(self.filepath):
            utils.bash("wget -P "+self.download_dir+" "+self.config["download_url"])
            self.unzip()
            self.process()
        else:
            print self.filepath + " already exists"
            
            
    def load_layers(self):
        """Load the layer configuration for the datasource"""
        
        try:
            with open("data_loader/"+self.config["layer_config"], 'r') as f:
                config = yaml.load(f)

                for layer in config["layers"]:

                    shapeformat = layer["file"].rsplit('.', 1)[-1]
                    shapefile = self.dir+layer["file"]

                    if shapeformat == "shp":
                        self.shp2pgsql(shapefile, layer['table'])

                    if shapeformat == "tif":
                        self.raster2pgsql(shapefile, layer['table'])   

                    # Alter the table if needed
                    try:
                        query = layer["alter"].format(table=layer['table'])
                        utils.psycopg_atlas(query)
                    except:
                        pass
                
        except KeyError:
            print "No configuration file found for {}".format(self.name)
    
    
    def unzip(self):
        """Unpack the source"""
        utils.bash("unzip {} -d {}".fromat(self.filepath, self.dir))

        
    def shp2pgsql(self, datafile, table):
        """Load shapefiles into a postgres database"""
        
        print "Opening {shapefile}".format(shapefile=datafile)
        query = "shp2pgsql -s {srs} -W LATIN1 -g geom {shapefile} {table} > temp.sql".format(srs=self.srs, shapefile=datafile, table=table)
        utils.bash(query)
        print "Sql schema generated"
        sql2pgsql(open('temp.sql', 'r').read())
        
        
    def raster2pgsql(self, datafile, table):
        print "Opening {raster}".format(raster=datafile)
        query = "raster2pgsql -s {srs} -I -C {raster} {table} > temp.sql".format(srs=self.srs, raster=datafile, table=table)
        utils.bash(query)
        print "Sql schema generated"
        try:
            self.sql2pgsql(open('temp.sql', 'r').read())
        except psycopg2.ProgrammingError:
            print "Rasters not supported in PostGIS 1.5 Please upgrade to 2.0"
        
    def sql2pgsql(self, sql):
        utils.psycopg_atlas(sql)
        print "Loaded schema into database"