# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Generate random forest distribution raster
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Created on: 2016-11-21
# Usage: Must be executed as an R Script.
# Description: This tool provides a simple Random Forests model.
# ---------------------------------------------------------------------------

# Install required libraries if they are not already installed.
Required_Packages <- c("randomForest", "rfUtilities", "sp", "raster", "rgdal", "stringr", "ROCR")
New_Packages <- Required_Packages[!(Required_Packages %in% installed.packages()[,"Package"])]
if (length(New_Packages) > 0) {
  install.packages(New_Packages)
}

# Import required libraries: randomForest, rfUtilities, sp, raster, rgdal, stringr, ROCR.
library(randomForest)
library(rfUtilities)
library(sp)
library(raster)
library(rgdal)
library(stringr)
library(ROCR)

# Set seed
set.seed(415)

# Set workspace folder from command line input.
Workspace <- commandArgs(trailingOnly = TRUE)
setwd(Workspace)

# Import arguments passed by python.
Arguments <- read.table("Arguments.txt", header = FALSE)

# Set path to raster folder and generate raster stack from arguments passed by python.
Raster_Folder <- as.vector(Arguments[,1])
cat("Creating raster stack...\n")
Raster_List <- list.files(Raster_Folder, pattern="img$", full.names = TRUE)
Raster_Stack <- stack(Raster_List)

# Select species data from arguments passed by python.
Species_Shapefile <- as.vector(Arguments[,2])

# Define output raster from arguments passed by python.
Output_Text <- as.vector(Arguments[,3])

# Convert shapefile into spatial data frame and extract raster data.
cat("Creating species data frame...\n")
Species_Data <- readOGR(dsn = Species_Shapefile)
Species_Data@data <- data.frame(Species_Data@data, extract(Raster_Stack, Species_Data))

# Test for multiple colinearity in environmental variables with p value assigned based on number of variables.
cat("Performing colinearity tests...\n")
Raster_Number <- as.numeric(length(Raster_List))
if (Raster_Number < 20) {
  p_value <- 0.0000001
} else if (Raster_Number >= 20) {
  p_value <- 0.05
}
Collinearity <- multi.collinear(Species_Data@data, p = p_value)

# Remove variables one at a time to ensure that each variable identified as colinear is a true multiple colinearity.
if (length(Collinearity) != 0) {
  Collinear_List <- c(Collinearity)
  for (l in Collinearity) {
    Collinearity_Iteration <- multi.collinear(Species_Data@data[,-which(names(Species_Data@data)==l)], p = p_value)
    Collinear_List <- c(Collinear_List, Collinearity_Iteration)
  }
  # Generate list of variables to remove because of true multiple colinearity.
  Collinear_Remove <- character()
  for (l in Collinearity) {
    Word_Count <- as.numeric(sum(str_count(Collinear_List, l)))
    if (Word_Count == as.numeric(length(Collinearity))) {
      Collinear_Remove <- c(Collinear_Remove, l)
    }
  }
} else if (length(Collinearity) == 0) {
  Collinear_Remove <- "No multicollinear variables identified"
}

# Output list of collinear variables to text
sink("R_Text.txt")
cat(as.vector(Collinear_Remove))
sink()