# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Check variable multicollinearity
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Created on: 2017-01-06
# Usage: Must be executed as an ArcPy Script.
# Description: This tool provides a check for multicollinearity in a set of variables per a given presence-absence dataset based on qr matrix decomposition.
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy, os, subprocess

# Set overwrite option
arcpy.env.overwriteOutput = True

# Define folder of environmental raster datasets
Raster_Folder = arcpy.GetParameterAsText(0)

# Define input species presence/absence points
Species_Points = arcpy.GetParameterAsText(1)

# Define output raster
Output_Text = arcpy.GetParameterAsText(2)

# Define location of RScript.exe
RScript = arcpy.GetParameterAsText(3)

# Define location of R Script
R_Script = arcpy.GetParameterAsText(4)

# Setup workspace
Workspace, Output_Name = os.path.split(Output_Text)

# Define intermediate files for user selected workspace
Species_Shapefile = os.path.join(Workspace, "Species_Points.shp")
Arguments = os.path.join(Workspace, "Arguments.txt")

# Copy species points to workspace as a shapefile
arcpy.CopyFeatures_management(Species_Points, Species_Shapefile)

# Prepare arguments
arcpy.AddMessage("Compiling R script...")
Raster_Folder_Path = str(Raster_Folder)
Species_Shapefile_Path = str(Species_Shapefile)
Output_Text_Path = str(Output_Text)
Workspace_Path = str(Workspace)
Raster_Folder_Path = "'" + Raster_Folder_Path + "'"
Species_Shapefile_Path = "'" + Species_Shapefile_Path + "'"
Output_Text_Path = "'" + Output_Text_Path + "'"

# Write arguments to text file
text_file = open(Arguments, "w")
text_file.write(Raster_Folder_Path + " " + Species_Shapefile_Path + " " + Output_Text_Path)
text_file.close()

# Send process to R
arcpy.AddMessage("Starting R...")
cmd = RScript + " " + R_Script + " " + Workspace
arcpy.AddMessage(cmd)
subprocess.call(cmd)

# Rename R Text to Output Text
R_Text = os.path.join(Workspace, "R_Text.txt")
R_Text_Open = open(R_Text, "r")
R_Text_Lines = R_Text_Open.readlines()
R_Text_Open.close()
Output_Text_Open = open(Output_Text, "w")
Output_Text_Open.write(str(R_Text_Lines))
Output_Text_Open.close()

# Delete intermediate data
arcpy.Delete_management(Species_Shapefile)
os.remove(Arguments)
os.remove(R_Text)
DirPath = os.path.split(R_Script)[0]
Info = os.path.join(DirPath, "info")
ArcDir = os.path.join(Info, "arc.dir")
if os.path.exists(ArcDir) == True:
    os.remove(ArcDir)
    os.rmdir(Info)
R_History = os.path.join(Workspace, ".Rhistory")
if os.path.exists(R_History) == True:
    os.remove(R_History)
XML = os.path.join(Output_Text, "txt.xml")
if os.path.exists(XML) == True:
    os.remove(XML)
