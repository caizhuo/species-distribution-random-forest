# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Pre-process Predictor Raster for Random Forest Model
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Created on: 2016-11-29
# Usage: Must be executed as an ArcPy Script.
# Description: This tool processes an input raster for use as a predictive variable in a Random Forest model.
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy, os
from arcpy.sa import *

# Set overwrite option
arcpy.env.overwriteOutput = True

# Define input point occurrence dataset
Input_Raster = arcpy.GetParameterAsText(0)

# Define area of interest
Area_Of_Interest = arcpy.GetParameterAsText(1)

# Define location of a workspace folder
Workspace = arcpy.GetParameterAsText(2)

# Define resampling technique
Data_Type = arcpy.GetParameterAsText(3)

#Define output ASCII file
Output_Raster = arcpy.GetParameterAsText(4)

# Define intermediate files for user selected workspace
Raster_Project = os.path.join(Workspace, "Ras_Pro")
root = os.path.splitext(Output_Raster)[0]
Output_Raster = root + ".img"
Info = os.path.join(Workspace, "info")
ArcDir = os.path.join(Info, "arc.dir")

# Determine Projection of Area of Interest
Projection = arcpy.Describe(Area_Of_Interest).spatialReference

# Determine cell size of Area of Interest
Cell_Size = arcpy.GetRasterProperties_management(Area_Of_Interest, "CELLSIZEX")

# Reproject raster to match Area of Interest
arcpy.AddMessage("Reprojecting raster...")
if Data_Type == "Continuous":
    Resampling_Technique = "BILINEAR"
    arcpy.env.snapRaster = Area_Of_Interest
    arcpy.ProjectRaster_management(Input_Raster, Raster_Project, Projection, Resampling_Technique, Cell_Size)
elif Data_Type == "Discrete":
    Resampling_Technique = "NEAREST"
    arcpy.env.snapRaster = Area_Of_Interest
    arcpy.ProjectRaster_management(Input_Raster, Raster_Project, Projection, Resampling_Technique, Cell_Size)
else:
    arcpy.AddError("The data type is not recognized. Please select continuous or discrete.")

# Extract projected raster to the area of interest
arcpy.AddMessage("Extracting raster to area of interest...")
arcpy.env.snapRaster = Area_Of_Interest
outExtract = ExtractByMask(Raster_Project, Area_Of_Interest)
arcpy.AddMessage("Preparing output raster...")
if Data_Type == "Continuous":
    arcpy.CopyRaster_management(outExtract, Output_Raster, "", "", "", "NONE", "NONE", "32_BIT_FLOAT", "NONE", "NONE")
elif Data_Type == "Discrete":
    arcpy.CopyRaster_management(outExtract, Output_Raster, "", "", "", "NONE", "NONE", "16_BIT_SIGNED", "NONE", "NONE")

# Delete intermediate data
arcpy.Delete_management(Raster_Project)
if os.path.exists(ArcDir) == True:
    os.remove(ArcDir)
    os.rmdir(Info)