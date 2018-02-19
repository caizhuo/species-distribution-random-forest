# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Random Forest Model Pre/Post-Processing
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Created on: 2017-01-22
# Usage: Must be executed as an ArcPy Script.
# Description: This tool provides a Random Forest species distribution model that runs from ArcGIS for a single current or historic timeframe.
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy, os, subprocess

# Set overwrite option
arcpy.env.overwriteOutput = True

# Define folder of environmental raster datasets
Predictor_Folder_Current = arcpy.GetParameterAsText(0)

# Define input species presence/absence points
Species_Shapefile = arcpy.GetParameterAsText(1)

# Define output raster
Output_Raster_Current = arcpy.GetParameterAsText(2)

# Define output probability threshold file
Probability_Threshold = arcpy.GetParameterAsText(3)

# Define location of RScript.exe
RScript_Program = arcpy.GetParameterAsText(4)

# Define location of R Script
RandomForest_Script = arcpy.GetParameterAsText(5)

# Set number of bootstrap replicates
Bootstrap = arcpy.GetParameterAsText(6)

# Set number of validation permutations
Permutations = arcpy.GetParameterAsText(7)

# Setup workspace
Workspace = os.path.split(Output_Raster_Current)[0]
Plots_Folder = os.path.join(Workspace, "plots")
VariableCurves = os.path.join(Plots_Folder, "variablecurves")
if os.path.exists(Plots_Folder) == False:
    os.makedirs(Plots_Folder)
if os.path.exists(VariableCurves) == False:
    os.makedirs(VariableCurves)

# Define intermediate files for user selected workspace
Arguments = os.path.join(Workspace, "Arguments.txt")

# Prepare argument for predictor folder path
arcpy.AddMessage("Compiling R script...")
Predictor_Folder_Path_Current = str(Predictor_Folder_Current)
Predictor_Folder_Path_Current = "'" + Predictor_Folder_Path_Current + "'"

# Prepare argument for species shapefile path
Species_Shapefile_Path = str(Species_Shapefile)
Species_Shapefile_Path = "'" + Species_Shapefile_Path + "'"

# Prepare argument for current 64-bit distribution raster output
Output_Name_Current = os.path.split(Output_Raster_Current)[1]
Output_Name_Current = os.path.splitext(Output_Name_Current)[0]
Filename_Current = Output_Name_Current + "_64bit.img"
Output_Raster_64_Current = os.path.join(Workspace, Filename_Current)
Output_Raster_64_Current_Path = str(Output_Raster_64_Current)
Output_Raster_64_Current_Path = "'" + Output_Raster_64_Current_Path + "'"

#Prepare argument for workspace
Workspace_Path = str(Workspace)

# Write arguments to text file
text_file = open(Arguments, "w")
text_file.write(Predictor_Folder_Path_Current + " " + Species_Shapefile_Path + " " + Output_Raster_64_Current_Path + " " + Bootstrap + " " + Permutations)
text_file.close()

# Send process to R
arcpy.AddMessage("Starting R...")
cmd = RScript_Program + " " + RandomForest_Script + " " + Workspace
arcpy.AddMessage(cmd)
subprocess.call(cmd)

# Define projection for current output
arcpy.AddMessage("Post-processing output raster...")
Projection = arcpy.Describe(Species_Shapefile).spatialReference
arcpy.DefineProjection_management(Output_Raster_64_Current, Projection)

# Copy raster to final output as a 32 bit float
arcpy.CopyRaster_management(Output_Raster_64_Current, Output_Raster_Current, "", "", "-3.402823e+038", "NONE", "NONE", "32_BIT_FLOAT", "NONE", "NONE")

# Read cross validation results into variable
CV_File = os.path.join(Workspace, "CrossValidation_Kappa.txt")
CV_Open = open(CV_File, "r")
CV_Lines = CV_Open.readlines()
CV_Open.close()

# Read AUC results into variable
AUC_File = os.path.join(Workspace, "AUC.txt")
AUC_Open = open(AUC_File, "r")
AUC_Value = AUC_Open.readlines()
AUC_Open.close()

# Read occurrence threshold results into variable
Threshold_File = os.path.join(Workspace, "OccurrenceThreshold.txt")
Threshold_Open = open(Threshold_File, "r")
Threshold = Threshold_Open.readlines()
Threshold_Open.close()

# Create probability threshold text file
Probability_Line = Threshold[7]
Probability_Str = Probability_Line[68] + Probability_Line[69] + Probability_Line[70] + Probability_Line[71]
Probability_Flt = float(Probability_Str)
Probability_Open = open(Probability_Threshold, "w")
Probability_Open.write(str(Probability_Flt))
Probability_Open.close()

# Read selected variables results into variable
Variables_File = os.path.join(Workspace, "FinalVars.txt")
Variables_Open = open(Variables_File, "r")
Final_Selected = Variables_Open.readlines()
Variables_Open.close()

# Write html text file
HTML_Text = os.path.join(Workspace, Output_Name_Current + ".txt")
text_file = open(HTML_Text, "w")
text_file.write("<html>\n")
text_file.write("<head>\n")
text_file.write("<meta http-equiv=\"pragma\" content=\"no-cache\">\n")
text_file.write("<meta http-equiv=\"Expires\" content=\"-1\">\n")
text_file.write("</head>\n")
text_file.write("<body>\n")
text_file.write("<div style=\"width:90%;max-width:1000px;margin-left:auto;margin-right:auto\">\n")
text_file.write("<h1 style=\"text-align:center;\">Random Forest Model Results for " + Output_Name_Current + "</h1>\n")
text_file.write(r"<br>" + "\n")
text_file.write(r"<h2>Model Accuracy</h2>" + "\n")
text_file.write("<p>The <b>Kappa</b> of the model is <b>" + CV_Lines[0] + "</b></p>\n")
text_file.write("<p>Selection of variables and model fit was optimized for maximum Kappa.</p>")
text_file.write(r"<br>" + "\n")
text_file.write("<p>The <b>AUC value</b> of the model is <b>" + AUC_Value[0] + "</b></p>\n")
text_file.write("<img style=\"display:inline-block;max-width:480px;width:100%;\" src=\"plots\\RecieverOperatingCharacteristic.png\">\n")
text_file.write(r"<br>" + "\n")
text_file.write(r"<br>" + "\n")
text_file.write(r"<h2>Probability Threshold for Occurrence</h2>" + "\n")
text_file.write("<p>" + Threshold[7] + "</p>\n")
text_file.write("<img style=\"display:inline-block;max-width:480px;width:100%;\" src=\"plots\\Threshold_Value.png\">\n")
text_file.write(r"<br>" + "\n")
text_file.write(r"<br>" + "\n")
text_file.write(r"<h2>Variable Importances for All Input Variables</h2>" + "\n")
text_file.write("<img style=\"display:inline-block;max-width:480px;width:100%;\" src=\"plots\\VariableImportance_All.png\">\n")
text_file.write(r"<br>" + "\n")
text_file.write(r"<br>" + "\n")
text_file.write(r"<h2>Variable Importances for Variables Selected for Random Forest Model</h2>" + "\n")
text_file.write("<p>The variables selected for the final model were:</p>\n")
text_file.write("<p>" + Final_Selected[0] + "</p>\n")
text_file.write("<img style=\"display:inline-block;max-width:480px;width:100%;\" src=\"plots\\VariableImportance_Selected.png\">\n")
text_file.write(r"<br>" + "\n")
text_file.write(r"<br>" + "\n")
text_file.write(r"<h2>Response Curves for Selected Variables</h2>" + "\n")
text_file.write("<div style=\"text-align:center\">\n")
for file in os.listdir(VariableCurves):
    curve_path = os.path.join("plots\\variablecurves", file)
    curve_html = "<img style=\"display:inline-block;max-width:480px;width:100%;\" src=\"" + curve_path + "\">\n"
    text_file.write(curve_html)
text_file.write("</div>\n")
text_file.write("</div>\n")
text_file.write("</body>\n")
text_file.write("</html>\n")
text_file.close()

# Rename HTML Text to HTML
HTML = os.path.join(Workspace, Output_Name_Current + "_StatisticsReport.html")
if os.path.exists(HTML) == True:
    os.remove(HTML)
os.rename(HTML_Text, HTML)

# Delete intermediate data
arcpy.Delete_management(Output_Raster_64_Current)
os.remove(Arguments)
DirPath = os.path.split(RandomForest_Script)[0]
Info = os.path.join(DirPath, "info")
ArcDir = os.path.join(Info, "arc.dir")
if os.path.exists(ArcDir) == True:
    os.remove(ArcDir)
    os.rmdir(Info)
os.remove(CV_File)
os.remove(AUC_File)
os.remove(Threshold_File)
os.remove(Variables_File)
R_Plots = os.path.join(Workspace, "Rplots.pdf")
if os.path.exists(R_Plots) == True:
    os.remove(R_Plots)
R_History = os.path.join(Workspace, ".Rhistory")
if os.path.exists(R_History) == True:
    os.remove(R_History)