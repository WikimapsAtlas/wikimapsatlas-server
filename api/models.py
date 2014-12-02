import utils
import os, yaml, json

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
    
    def json(self, json_format, query): 
        """ Generate a topojson and geojson file for the area and return the appropriate format """
        
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
            utils.postgis2geojson(self.adm_area_table,file_path,"-w \"code_hasc LIKE '"+self.code+"'\"" )

        # Read generated file
        with open(target_file, 'r') as f:
            try:
                return json.dumps(json.load(f))
            finally:
                f.close()
                
                
                
class Datasource:
    """A vector or raster source to be used in the Wikimaps Atlas Database"""
    
    def __init__(self, config, download_dir):
        self.config = config
        self.download_dir = download_dir
        self.dir = download_dir + self.config["dir"]
        self.filepath = download_dir + self.config["download_url"].rsplit('/', 1)[-1]
        self.srs = self.config["srs"]
        
        
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
        with open("data_loader/"+self.config["layer_config"], 'r') as f:
            config = yaml.load(f)

            for layer in config["layers"]:
                shapefile = self.dir+layer["file"]
                self.shp2pgsql(shapefile, layer['table'])    
        
                # Alter the table if needed
                try:
                    query = layer["alter"].format(table=layer['table'])
                    utils.psycopg_atlas(query)
                except:
                    pass
    
    
    def unzip(self):
        """Unpack the source"""
        utils.bash("unzip "+self.filepath+" -d "+self.dir)

        
    def shp2pgsql(self, shapefile, table):
        """Load shapefiles into a postgres database"""
        
        print "Opening {shapefile}".format(shapefile=shapefile)
        query = "shp2pgsql -s {srs} -W LATIN1 {shapefile} {table} > temp.sql".format(srs=self.srs,shapefile=shapefile,table=table)
        utils.bash(query)
        print "Sql schema generated"
    
        # Load the sql
        utils.psycopg_atlas(open('temp.sql', 'r').read())
        print "Loaded schema into database"
        