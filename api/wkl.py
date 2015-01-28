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
            self.g_id = "*"
        finally:            
            self.locationId = self.gId
            self.parse_locationId(request_json)
            

    def parse_location_id(self, request_json):        
        # Convert the hasc code into a data path by replacing "." with "/" (IND.TN.MD > IND/TN/MD/)
        ## For World level, just use base directory
        if location_id == '*':
            self.data_dir = ''
        else:
            self.data_dir = self.Location_id.replace(".","/")+"/"
        
        # Calculate the default admin level of the location if not available in the request
        try:
            self.admin_level = request_json['level']
        except:
            self.admin_level = self.location_id.count(".")
        
        # Set the relevant shape table for the area
        self.table_admin_area = "adm" + str(self.admin_level) + "_area"
        
        # Set the location directory for the current code
        self.data_dir = self.construct_output_path('')
        
    def construct_output_path(self, file_name):
        "Constructs the relative output path for the requested filename"
        return atlas_data_dir + self.data_dir + file_name