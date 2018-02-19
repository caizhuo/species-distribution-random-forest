# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Convert Probability Distribution to Presence-Absence
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Created on: 2016-12-06
# Usage: Must be executed as an ArcPy Script.
# Description: This tool processes the Random Forest raw probability distribution into a boolean presence-absence output based on the probability threshold of occurrence calculated by the Random Forest tool.
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy, os
from arcpy.sa import *

# Set overwrite option
arcpy.env.overwriteOutput = True

# Define input distribution raster
Input_Distribution_Raster = arcpy.GetParameterAsText(0)

# Define probability threshold for occurrence
Threshold_File = arcpy.GetParameterAsText(1)

# Define location of output distribution raster
Output_Distribution_Raster = arcpy.GetParameterAsText(2)

# Setup workspace
Workspace, Output_Name = os.path.split(Input_Distribution_Raster)

# Define intermediate files for user selected workspace
ASCII_Table = os.path.join(Workspace, "ASCII_Remap.txt")

# Read probabilty from probability file
Threshold_Open = open(Threshold_File, "r")
Threshold = Threshold_Open.readlines()
Threshold_Open.close()
Probability = Threshold[0]

# Write ASCII remap table
text_file = open(ASCII_Table, "w")
text_file.write("0 " + Probability + " 0\n")
text_file.write(Probability + " 1 1")
text_file.close()

# Reclassify probability distribution by occurrence threshold
arcpy.AddMessage("Generating output raster...")
outReclassify = ReclassByTable(Input_Distribution_Raster, ASCII_Table, "Field1", "Field2", "Field3", "NODATA")
arcpy.CopyRaster_management(outReclassify, Output_Distribution_Raster, "", "", "-128", "NONE", "NONE", "8_BIT_SIGNED", "NONE", "NONE")
    
# Delete intermediate data
os.remove(ASCII_Table)
Schema = os.path.join(Workspace, "schema.ini")
if os.path.exists(Schema) == True:
    os.remove(Schema)
Log = os.path.join(Workspace, "log")
if os.path.exists(Log) == True:
    os.remove(Log)