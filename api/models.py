import utils
import os, yaml, json
import psycopg2

class Wikimaps_Atlas:
    """Database object"""
    
    
class Hasc:
    """ Heirarchal Administrative Subdivision Code """
    """ http://en.wikipedia.org/wiki/Hierarchical_administrative_subdivision_codes """
    
    def __init__(self, code):
        self.code = code
        
        # Convert the hasc code into a path by replacing "." with "/" (IND.TN.MD > IND/TN/MD/)
        self.data_dir = code.replace(".","/")+"/"

        # Calculate admin level of the requested area 
        self.adm_level = self.code.count(".")
        
        # Set the relevant shape table for the area
        self.adm_area_table = "adm" + str(self.adm_level) + "_area"
    
    def json(self, json_format="topojson", query=""): 
        """ Generate a topojson and geojson file for the area and return the appropriate format 
        Naming format:
        <hasc.code> / <layer><adm_lvl>
        """
        
        # Construct file paths
        file_name = "adm" + str(self.adm_level)     # adm0 | adm1
        file_dir = "../data/json/" + self.data_dir       # ../data/json/IN/MD/
        file_path = file_dir + file_name            # ../data/json/IN/MD/adm2
        target_file = file_path+"."+json_format         # ../data/json/IN/MD/adm2.topojson

        # If target file does not exist
        if not os.path.exists(target_file):
            
            # Create a new directory if it does not exist
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
                
            # Now generate the files
            utils.postgis2geojson(self.adm_area_table,file_path,"-w \"hasc LIKE '{}'\"".format(self.code) )

        # Read generated file
        with open(target_file, 'r') as f:
            try:
                return json.dumps(json.load(f))
            finally:
                f.close()
    
    
    
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