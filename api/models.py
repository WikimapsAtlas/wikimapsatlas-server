from local import *

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
        file_dir = "../data/" + self.data_dir       # ../data/IN/MD/
        file_path = file_dir + file_name            # ../data/IN/MD/adm2
        target_file = file_path+"."+json_format         # ../data/IN/MD/adm2.topojson

        # If target file does not exist
        if not os.path.exists(target_file):
            
            # Create a new directory if it does not exist
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
                
            # Now generate the files
            postgis2geojson(self.adm_area_table,file_path,"-w \"iso_a2 LIKE '"+self.code+"'\"" )

        # Read generated file
        with open(target_file, 'r') as f:
            try:
                return json.dumps(json.load(f))
            finally:
                f.close()