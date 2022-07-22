# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 16:16:10 2022
@author:        GTeague
Purpose:        Cleaning multiple GWIS geodatabases to combine into master
Requirements:   Python 3, ArcGIS software
Notes:          Prior to using this tool, you must manually inspect, remove, 
                and correct any features (e.g. Hyperlink IDs) that will be 
                duplicates/missing as this tool cannot do subjective editing
Project:        FW7563 - Shingle Creek Watershed Model Refinement
GWIS Tips:      After to transitioning to GWIS 2.1 and making necessary feature
                deletions where overlapping make sure GWIS HyperlinkID field is
                correctly populated. GWIS will set ID to null even though
                there are still features referencing it. Script will break on 
                hyperlink ID dictionary to identify issues
"""

# Import relevant libraries
import os
import arcpy
#import shutil

# Get working directory
working_dir = os.getcwd()

# GIS directory
GIS_dir = os.path.dirname(working_dir)

# Directory where cleaned GWIS 2.1 databases are
GWIS_input = os.path.join(GIS_dir, 'GDB', 'GWIS_2.1_Cleaned') 

# Directory of python working GDBs
GWIS_working = os.path.join(GIS_dir, 'GDB', 'GWIS_2.1_Python') 

# Directory where merged GWIS 2.1 database will go
GWIS_output = os.path.join(GIS_dir, 'GDB', 'GWIS_2.1_Combined') 

# Get list of geodatabases to copy:
GWIS_cleaned_list = os.listdir(GWIS_input)
             
#Copy input geodaabases to working to not mess up original cleaned version (again)
for gdb in GWIS_cleaned_list:
    working_gdb_input = os.path.join(GWIS_input, gdb)
    gdb_python = gdb.replace('Cleaned','Python')
    working_gdb = os.path.join(GWIS_working,gdb_python)
    if arcpy.Exists(working_gdb):
        arcpy.Delete_management(working_gdb)
    arcpy.Copy_management(working_gdb_input, working_gdb)

# Get list of geodatabases to combine:
GWIS_python_list = os.listdir(GWIS_working)

hyperlinkID_end = 0
##Loop through geodatabases
for input_gdb in GWIS_python_list: #['BB_GWIS_2.1_Cleaned.gdb','BSL_GWIS_2.1_Cleaned.gdb']: 
    print ('Looping through GDB -', input_gdb)
    
    # Get list of hyperlink IDs
    hyperlink_table = os.path.join(GWIS_working, input_gdb, 'HYPERLINK')
    hyperlinkID_list = []
    with arcpy.da.UpdateCursor(hyperlink_table, 'HYPERLINK_ID') as cursor:
        for row in cursor:
            # Count number of hyperlink IDs and get a list of valueslink ID
            if row[0] != None:
                hyperlinkID_list.append(row[0])
                
    # Create a dictionary of hyperlink IDs
    print ('\t', 'Creating a dictionary of HyperlinkIDs')
    hyperlinkID_start = hyperlinkID_end + 1
    hyperlinkID_end = hyperlinkID_start + len(set(hyperlinkID_list))
    hyperlinkID_dict = dict(zip(set(hyperlinkID_list), range(hyperlinkID_start, hyperlinkID_end)))  
                   
    # HYPERLINK table - Update Hyperlink ID & path to account for GWIS data source
    print ('\t', 'Updates to HYPERLINK table - HYPERLINK_ID, STORAGE_PATH_ADDR, STORAGE_FULL_PATH_ADDR')
    fields = ['HYPERLINK_ID', 'STORAGE_PATH_ADDR', 'STORAGE_FULL_PATH_ADDR']
    with arcpy.da.UpdateCursor(hyperlink_table, fields) as cursor:
        for row in cursor:
            #HyperlinkID
            if row[0] != None:
                row[0] = hyperlinkID_dict[row[0]]
            # STORAGE_PATH_ADDR and STORAGE_FULL_PATH_ADDR
            # Bonnie Brook
            if input_gdb == 'BB_GWIS_2.1_Python.gdb':
                string_split = row[1].split('\\')
                string_split_2 = row[2].split('\\')
                if len(string_split) > 1: 
                    if string_split[1] == 'Survey':
                        string_split.insert(1,'Supporting_Data\BB')
                        row[1] = '\\'.join(string_split)
                        string_split_2.insert(1,'Supporting_Data\BB')
                        row[2] = '\\'.join(string_split_2)
                    elif string_split[1] == 'Supporting_Data':
                        string_split.insert(2,'BB')
                        row[1] = '\\'.join(string_split)
                        string_split_2.insert(2,'BB')
                        row[2] = '\\'.join(string_split_2)
                    elif string_split[3] == 'Survey':
                        string_split[2] = 'BB'
                        row[1] = '\\'.join(string_split)
                        string_split_2[2] = 'BB'
                        row[2] = '\\'.join(string_split_2)
                    else:
                        row[1] = row[1]
                        row[2] = row[2]
            # Lakes C, B, & T
            if input_gdb == 'CBT_GWIS_2.1_Python.gdb':
                string_split = row[1].split('\\')
                string_split_2 = row[2].split('\\')
                if string_split[1] == 'Survey':
                    string_split.insert(1,'Supporting_Data\CBT')
                    row[1] = '\\'.join(string_split)
                    string_split_2.insert(1,'Supporting_Data\CBT')
                    row[2] = '\\'.join(string_split_2)
                elif string_split[1] == 'Supporting_Data':
                    string_split.insert(2,'CBT')
                    row[1] = '\\'.join(string_split)
                    string_split_2.insert(2,'CBT')
                    row[2] = '\\'.join(string_split_2)
                else:
                    row[1] = row[1]
                    row[2] = row[2]
            # Big Sand Lake
            if input_gdb == 'BSL_GWIS_2.1_Python.gdb':
                if row[1] != None:
                    string_split = row[1].split('\\')
                    string_split_2 = row[2].split('\\')
                    if len(string_split) > 1: 
                        if string_split[1] == 'Survey':
                            string_split.insert(1,'Supporting_Data\BSL')
                            row[1] = '\\'.join(string_split)
                            string_split_2.insert(1,'Supporting_Data\BSL')
                            row[2] = '\\'.join(string_split_2)
                        elif string_split[1] == 'Supporting_Data':
                            string_split.insert(2,'BSL')
                            row[1] = '\\'.join(string_split)
                            string_split_2.insert(2,'BSL')
                            row[2] = '\\'.join(string_split_2)
                        else:
                            row[1] = row[1]
                            row[2] = row[2]
            # Westside
            if input_gdb == 'Westside_GWIS_2.1_Python.gdb':
                string_split = row[1].split('\\')
                string_split_2 = row[2].split('\\')
                
                #NOTE: Cannot find several data sources referenced
                if len(string_split) < 3: 
                    string_split.insert(1,'Supporting_Data\Westside')
                    row[1] = '\\'.join(string_split)
                    string_split_2.insert(1,'Supporting_Data\Westside')
                    row[2] = '\\'.join(string_split_2)        
                elif string_split[2] == 'Geodata_Survey' or string_split[1] == 'OC_Survey' or string_split[1] == 'SSMC_WM_Pond_Survey':
                    string_split[1] = 'Supporting_Data\Westside\Survey'
                    row[1] = '\\'.join(string_split)
                    string_split_2[1] = 'Supporting_Data\Westside\Survey'
                    row[2] = '\\'.join(string_split_2)
                elif string_split[2] == 'OC_Stormwater_Studies':
                    string_split[1] = 'Supporting_Data\Westside\Researched_Data\Studies'
                    row[1] = '\\'.join(string_split)
                    string_split_2[1] = 'Supporting_Data\Westside\Researched_Data\Studies'
                    row[2] = '\\'.join(string_split_2)
                elif string_split[2] == 'ERP_SFWMD' or string_split[1] == 'ERP_SJRWMD':
                    string_split[1] = 'Supporting_Data\Westside\Researched_Data\Permit'
                    row[1] = '\\'.join(string_split)
                    string_split_2[1] = 'Supporting_Data\Westside\Researched_Data\Permit'
                    row[2] = '\\'.join(string_split_2)
                else:
                    string_split[1] = 'Supporting_Data\Westside\Researched_Data\Plans'
                    row[1] = '\\'.join(string_split)
                    string_split_2[1] = 'Supporting_Data\Westside\Researched_Data\Plans'
                    row[2] = '\\'.join(string_split_2)
            # Lake Hiawasssee
            if input_gdb == 'LHW_GWIS_2.1_Python.gdb':
                string_split = row[1].split('\\')
                string_split_2 = row[2].split('\\')
                if string_split[1] == 'Survey':
                    string_split.insert(1,'Supporting_Data\LHW')
                    row[1] = '\\'.join(string_split)
                    string_split_2.insert(1,'Supporting_Data\LHW')
                    row[2] = '\\'.join(string_split_2)
                elif string_split[1] == 'Supporting_Data':
                    string_split.insert(2,'LHW')
                    row[1] = '\\'.join(string_split)
                    string_split_2.insert(2,'LHW')
                    row[2] = '\\'.join(string_split_2)
                else:
                    row[1] = row[1]
                    row[2] = row[2]
            # Shingle Creek Migration (2011)
            if input_gdb == 'Shingle_GWIS_2.1_Python.gdb':
                string_split = row[1].split('\\')
                string_split_2 = row[2].split('\\')
                if string_split[1] == 'Survey':
                    string_split.insert(1,'Supporting_Data\SC')
                    row[1] = '\\'.join(string_split)
                    string_split_2.insert(1,'Supporting_Data\SC')
                    row[2] = '\\'.join(string_split_2)
                elif string_split[1] == 'Supporting_Data':
                    string_split.insert(2,'SC')
                    row[1] = '\\'.join(string_split)
                    string_split_2.insert(2,'SC')
                    row[2] = '\\'.join(string_split_2)
                elif string_split[1] == 'Hyperlink':
                    string_split[1] = 'Supporting_Data\SC\Researched_Data'
                    row[1] = '\\'.join(string_split)
                    string_split_2[1] = 'Supporting_Data\SC\Researched_Data'
                    row[2] = '\\'.join(string_split_2)
                else:
                    row[1] = row[1]
                    row[2] = row[2]
            # Shingle Creek TBG Update (2021)
            if input_gdb == 'ShingleCreek_GWIS_TBG_Python.gdb':
                string_split = row[1].split('\\')
                string_split_2 = row[2].split('\\')
                if string_split[3] == 'Survey':
                    string_split[1] = 'Supporting_Data'
                    string_split[2] = 'SC'
                    row[1] = '\\'.join(string_split)
                    string_split_2[1] == 'Supporting_Data'
                    string_split_2[2] = 'SC'
                    row[2] = '\\'.join(string_split_2)
                elif string_split[3] == 'Supporting_Data':
                    string_split.insert(4,'SC')
                    string_split.remove('3_GIS')
                    del string_split[0]
                    row[1] = '\\'.join(string_split)
                    string_split_2.insert(4,'SC')
                    string_split_2.remove('3_GIS')
                    del string_split_2[0]
                    row[2] = '\\'.join(string_split_2)
                elif string_split[3] == 'Raster':
                    string_split.remove('3_GIS')
                    del string_split[0]
                    row[1] = '\\'.join(string_split)
                    string_split_2.remove('3_GIS')
                    del string_split_2[0]
                    row[2] = '\\'.join(string_split_2)
                else:
                    row[1] = row[1]
                    row[2] = row[2]
            cursor.updateRow(row)
    
    # Feature classes w/ Hyperlink IDs - Update hyperlink ID
    print ('\t', 'Updates to Features with HyperlinkIDs - HYDROJUNCTION, HYDROEDGE, HYDRAULIC_ELEMENT_POINT')
    hyperlinkID_fc_list = ['HYDROJUNCTION', 'HYDROEDGE','HYDRAULIC_ELEMENT_POINT']
    fields = ['HYPERLINK_ID']
    for fc in hyperlinkID_fc_list:
        if fc == 'HYDRAULIC_ELEMENT_POINT':
            hyperlinkID_fc = os.path.join(GWIS_working, input_gdb,'Watershed',fc)
        else:
            hyperlinkID_fc = os.path.join(GWIS_working, input_gdb,'HydroNetwork',fc)
        edit = arcpy.da.Editor(os.path.join(GWIS_working, input_gdb))
        edit.startEditing(False, True)
        edit.startOperation()
        with arcpy.da.UpdateCursor(hyperlinkID_fc, fields) as cursor:
            for row in cursor:
                #HyperlinkID
                if row[0] != None:
                    row[0] = hyperlinkID_dict[row[0]]
                cursor.updateRow(row)
        edit.stopEditing(True)     
                    
print ('Done!')
