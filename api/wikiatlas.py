import utils
import os, yaml, json
import psycopg2
import models

# Wikiatlas Data Directory
atlas_data_dir = "../data/json/"

class Gid:
    """ Well Known Location Code parser"""
    
    def __init__(self, request_json ):
        "Parse the request options"
        try:
            self.g_id = request_json['gid']
        except:
            self.g_id = ""
        finally:
            # Check if g_id is set world code
            if self.g_id == '*' :
                self.location_id = ''
            else:
                self.location_id = self.g_id
            self.parse_location_id(request_json)
        
        # Set the data layer
        try:
            if request_json['layer'] == 'bbox' :
                self.data_layer = 'bbox'
        except:
            self.data_layer = 'adm'
        finally:
            self.parse_data_layer()
                
        # Fallback to topojson if not specified
        try:
            if request_json['topology'] == 'false' :
                self.json_format = 'geojson'
        except:
                self.json_format = 'topojson'
            

    def parse_location_id(self, request_json):        
        # Convert the hasc code into a data path by replacing "." with "/" (IND.TN.MD > IND/TN/MD/)
        ## For World level, just use base directory
        if self.location_id == '':
            self.data_dir = ''
        else:
            self.data_dir = self.location_id.replace(".","/")+"/"
        
        # Calculate the default admin level of the location if not available in the request
        ## This determines the level of details of the output
        try:
            self.admin_level = request_json['level']
        except:
            if self.location_id == '' :
                self.admin_level = 0
            else:
                self.admin_level = self.location_id.count(".") + 1
        
        # Set the location directory for the current code
        self.output_dir = self.construct_output_path(self.data_dir)
        
        
    def parse_data_layer(self):
        "Set the correct output file, table and query"
        
        if self.data_layer == "bbox":
            self.file_name = 'bbox'
        else:
            self.file_name = "adm" + str(self.admin_level)     # adm0 | adm1
        self.query_where = "hasc LIKE '{}%'".format(self.location_id)
        # Set the relevant shape table for the location
        self.query_table = "adm" + str(self.admin_level) + "_area"
        
        
    def construct_output_path(self, file_name):
        "Constructs the relative output path for the requested filename"
        return atlas_data_dir + self.data_dir + file_name
    
    def update_data_index(self):
        "Generate an index json file for the directory location"
        self.query2json(self.table_admin_area, "hasc LIKE '{}%'".format('*'), 'index', 'geojson', 'true')
        
        
    def json(self, query=""): 
        """ Generate a topojson and geojson file for the location_id
        """        
        return self.query2json(self.query_table, self.query_where, self.file_name)
    
    
        
    def fetch_json_data(self, target_file_name):
        "Fetch the json data from the data directory"
        with open(target_file_name + '.' + self.json_format, 'r') as f:
            try:
                return json.dumps(json.load(f))
            finally:
                f.close()
            

    def query2json(self, table, where, file_name, update = 'false'):
        "Generates a json result from the requested database query"
        
        output_file_name = self.construct_output_path( file_name )
        options = "-w \"{}\"".format(where)
        
        # If target file does not exist
        if not os.path.exists(output_file_name + '.' + self.json_format):
            
            # Create a new directory if it does not exist
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
                
            # Generate an index file for the region with list of subunits and bounding boxes
#            self.update_data_index()
        
            # Now generate the files and regenerate the index
            utils.postgis2geojson(table, output_file_name, options )
#
        return self.fetch_json_data(output_file_name)