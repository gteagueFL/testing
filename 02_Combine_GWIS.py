# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 16:16:10 2022
@author:        GTeague
Purpose:        Combining multiple GWIS geodatabases
Requirements:   Python 3, ArcGIS software
Notes:          Prior to using this tool, you must run 01_Input_GWIS_Cleanup.py
                or ensure your GWIS gdbs are correctly formatted
Project:        FW7563 - Shingle Creek Watershed Model Refinement
Upgrades needed: Assign HydroID
"""

# Import relevant libraries
import os
import arcpy
#import shutil

# Get working directory
working_dir = os.getcwd()

# GIS directory
GIS_dir = os.path.dirname(working_dir)

# Directory of python working GDBs
GWIS_working = os.path.join(GIS_dir, 'GDB', 'GWIS_2.1_Python') 

# Directory where merged GWIS 2.1 database will go
GWIS_output = os.path.join(GIS_dir, 'GDB', 'GWIS_2.1_Combined') 

# Create Master geodatabase
primary_gdb_template = 'GWIS_v2.1_20200303_OrangeCounty_2.gdb'
#primary_gdb_output = 'GWIS_2.1_Combined_Shingle.gdb'
#primary_gdb_output = 'GWIS_2.1_Combined_NoShingle.gdb'
primary_gdb_output = 'GWIS_2.1_Combined.gdb'
primary_gdb_template_path = os.path.join(GWIS_output, primary_gdb_template)
primary_gdb_output_path = os.path.join(GWIS_output, primary_gdb_output)
if arcpy.Exists(primary_gdb_output_path):
    arcpy.Delete_management(primary_gdb_output_path)
arcpy.Copy_management(primary_gdb_template_path, primary_gdb_output_path)

# Get list of geodatabases to combine:
GWIS_python_list = os.listdir(GWIS_working)
GWIS_python_list_shingle = ['Shingle_GWIS_2.1_Python.gdb','ShingleCreek_GWIS_TBG_Python.gdb']
GWIS_python_list_noshingle = [ele for ele in GWIS_python_list if ele not in GWIS_python_list_shingle]
GWIS_python_list_combined = ['GWIS_2.1_Combined_NoShingle.gdb', 'GWIS_2.1_Combined_Shingle.gdb']

# Get list of all features & tables in GWIS
features_list = []
for path, datasets, features in arcpy.da.Walk(primary_gdb_output_path, 
                                              datatype=['FeatureDataset', 'FeatureClass', 'Table']):
    if path == primary_gdb_output_path:
        datasets_list = datasets
    features_list.append(features)
append_dict = dict(zip(datasets_list, features_list[1:]))

#Loop through geodatabases
#for input_gdb in GWIS_python_list_shingle:
#for input_gdb in GWIS_python_list_noshingle:
for input_gdb in GWIS_python_list_combined:
    print ('Looping through GDB -', input_gdb)
                       
    # Append to Master GDB
    print ('\t', 'Append Hydronetwork and related tables to Master GDB (Feature Dataset - Feature Class)')    
    # Set parameters for append
    schemaType = 'NO_TEST'
    fieldMappings = ''
    subtype = ''
    if input_gdb == 'ShingleCreek_GWIS_TBG_Python.gdb':  
        # Loop through features/tables in main geodatabase
        print ('\t', '\t', 'Main Features & Tables')
        for feature in features_list[0]:
            print ('\t', '\t', '\t', 'Main features & tables - ', feature)
            # Set input location
            hydronetwork_input = os.path.join(GWIS_working, input_gdb, feature)
            # Set output location
            hydronetwork_output =  os.path.join(primary_gdb_output_path, feature)
            # Append data
            if feature != 'ICPR_ModelNetwork_BUILDERR' and feature != 'SWF_HydroNetwork_BUILDERR' and feature != 'HEP_GeometricNetwork_BUILDERR' and feature != 'ADDL_MODEL_DATA':
                arcpy.Append_management(hydronetwork_input, hydronetwork_output, schemaType, fieldMappings, subtype)    
    
        # Loop through feature datasets
        for dataset in datasets_list:
            print ('\t', '\t', 'Feature Dataset -', dataset)
            # Loop through features/datasets in feature dataset
            for feature in append_dict[dataset]:
                print ('\t', '\t', '\t', 'Feature Dataset features & tables -', feature)
                # Set input location
                feature_input = os.path.join(GWIS_working, input_gdb, dataset, feature)
                # Set output location
                feature_output =  os.path.join(primary_gdb_output_path, dataset, feature)
                # Append data
                if feature != 'SWF_HydroNetwork_Junctions' and feature != 'PW_ContribArea':
                     arcpy.Append_management(feature_input, feature_output, schemaType, fieldMappings, subtype)   
    else:
        # Loop through features/tables in main geodatabase
        print ('\t', '\t', 'Main Features & Tables')
        for feature in features_list[0]:
            print ('\t', '\t', '\t', 'Main features & tables - ', feature)
            # Set input location
#            hydronetwork_input = os.path.join(GWIS_working, input_gdb, feature)
            hydronetwork_input = os.path.join(GWIS_output, input_gdb, feature)
            # Set output location
            hydronetwork_output =  os.path.join(primary_gdb_output_path, feature)
            # Append data
            arcpy.Append_management(hydronetwork_input, hydronetwork_output, schemaType, fieldMappings, subtype)    
    
        # Loop through feature datasets
        for dataset in datasets_list:
            print ('\t', '\t', 'Feature Dataset -', dataset)
            # Loop through features/datasets in feature dataset
            for feature in append_dict[dataset]:
                print ('\t', '\t', '\t', 'Feature Dataset features & tables -', feature)
                # Set input location
#                feature_input = os.path.join(GWIS_working, input_gdb, dataset, feature)
                feature_input = os.path.join(GWIS_output, input_gdb, dataset, feature)
                # Set output location
                feature_output =  os.path.join(primary_gdb_output_path, dataset, feature)
                # Append data
                arcpy.Append_management(feature_input, feature_output, schemaType, fieldMappings, subtype)   
                     
print ('Done!')

###############################################################################
# Upgrades Needed:
## Assign new HydroIDs to Hydronetwork features to prevent duplication from source GWIS
## archydro.assignhydroid() giving error and ArcHydro tools assign hydro id in ArcMap not working - duplicating IDs
## Arc Hydro toolbox in ArcPRO working        
#