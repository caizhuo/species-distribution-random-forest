# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Random Forest Model Analysis
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Created on: 2017-01-22
# Usage: Must be executed as an R Script. Script is set up to integrate with python but can be modified to run from an R command interface.
# Description: This tool provides a Random Forest model with variable selection and best model fit determined using data-driven approaches.
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

# Interpret arguments passed from python.
Predictor_Folder_Current <- as.vector(Arguments[,1])
Species_Shapefile <- as.vector(Arguments[,2])
Output_Raster_Current <- as.vector(Arguments[,3])
Bootstrap <- as.numeric(as.vector(Arguments[,4]))
Permutations <- as.numeric(as.vector(Arguments[,5]))

# Create current raster stack for model fit and current distribution.
cat("Creating raster stack for current predictor variables...\n")
Raster_List_Current <- list.files(Predictor_Folder_Current, pattern="img$", full.names = TRUE)
Raster_Stack_Current <- stack(Raster_List_Current)

# Convert shapefile into spatial data frame and extract raster data.
cat("Creating species data frame...\n")
Species_Data <- readOGR(dsn = Species_Shapefile)
Species_Data@data <- data.frame(Species_Data@data, extract(Raster_Stack_Current, Species_Data))

# Convert species presence to factor
Species_Data@data$Present <- as.factor(Species_Data@data$Present)

# Create model kappa function
Kappa_Function <- function(actual, model) {
  Table <- table(actual=actual,predicted=predict(model,OOB=TRUE))
  A <- Table[2,2]
  B <- Table[1,2]
  C <- Table[2,1]
  D <- Table[1,1]
  Kappa_Value <- ((A+D)-(((A+C)*(A+B)+(B+D)*(C+D))/(A+B+C+D)))/((A+B+C+D)-
    (((A+C)*(A+B)+(B+D)*(C+D))/(A+B+C+D)))
  return(Kappa_Value)
}

# Perform 100 iterations of variable selection and model fit to find three best performing models based on model kappa.
cat("Starting model fit iteration 1 of 100...\n")
Kappa_List <- numeric()
Variables <- rf.modelSel(x = Species_Data@data[, 2:ncol(Species_Data@data)], y = Species_Data@data[, "Present"], imp.scale = "mir", ntree = Bootstrap, r = c(0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1))
Selected <- Variables$selvars
Fit <- randomForest(x = Species_Data@data[, Selected], y = Species_Data@data[, "Present"], ntree = Bootstrap, importance = TRUE, norm.votes = TRUE, proximity = TRUE)
Model_Kappa <- Kappa_Function(Species_Data@data[, "Present"], Fit)
Kappa_List <- c(Kappa_List, Model_Kappa)
Kappa_Sorted <- sort(unique(Kappa_List), decreasing = TRUE)
Variables_1 <- Variables
Selected_1 <- Selected
Fit_1 <- Fit
Model_Kappa_1 <- Model_Kappa
Variables_2 <- Variables
Selected_2 <- Selected
Fit_2 <- Fit
Model_Kappa_2 <- Model_Kappa
Variables_3 <- Variables
Selected_3 <- Selected
Fit_3 <- Fit
Model_Kappa_3 <- Model_Kappa
for (Count in 2:100) {
  cat(paste("Starting model fit iteration ", Count, " of 100...\n", sep=""))
  Variables <- rf.modelSel(x = Species_Data@data[, 2:ncol(Species_Data@data)], y = Species_Data@data[, "Present"], imp.scale = "mir", ntree = Bootstrap, r = c(0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1))
  Selected <- Variables$selvars
  Fit <- randomForest(x = Species_Data@data[, Selected], y = Species_Data@data[, "Present"], ntree = Bootstrap, importance = TRUE, norm.votes = TRUE, proximity = TRUE)
  Model_Kappa <- Kappa_Function(Species_Data@data[, "Present"], Fit)
  Kappa_List <- c(Kappa_List, Model_Kappa)
  Kappa_Sorted <- sort(unique(Kappa_List), decreasing = TRUE)
  if (Model_Kappa >= Kappa_Sorted[1]) {
    Variables_1 <- Variables
    Selected_1 <- Selected
    Fit_1 <- Fit
    Model_Kappa_1 <- Model_Kappa
  } else if ((Model_Kappa >= Kappa_Sorted[2]) & (Model_Kappa < Kappa_Sorted[1])) {
    Variables_2 <- Variables
    Selected_2 <- Selected
    Fit_2 <- Fit
    Model_Kappa_2 <- Model_Kappa
  } else if ((Model_Kappa >= Kappa_Sorted[3]) & (Model_Kappa < Kappa_Sorted[2])) {
    Variables_3 <- Variables_3
    Selected_3 <- Selected
    Fit_3 <- Fit
    Model_Kappa_3 <- Model_Kappa
  }
}

# Perform cross validation of three best performing model iterations based on model kappa.
cat("Cross validating best performing model (based on model kappa)...\n")
CrossValidation_1 <- rf.crossValidation(Fit_1, Species_Data@data[, Selected_1], p = 0.10, n = Permutations, ntree = Bootstrap)
CV_Kappa_1 <- mean(CrossValidation_1$cross.validation$cv.oob$kappa)
cat("Cross validating second best performing model (based on model kappa)...\n")
CrossValidation_2 <- rf.crossValidation(Fit_2, Species_Data@data[, Selected_2], p = 0.10, n = Permutations, ntree = Bootstrap)
CV_Kappa_2 <- mean(CrossValidation_2$cross.validation$cv.oob$kappa)
cat("Cross validating third best performing model (based on model kappa)...\n")
CrossValidation_3 <- rf.crossValidation(Fit_3, Species_Data@data[, Selected_3], p = 0.10, n = Permutations, ntree = Bootstrap)
CV_Kappa_3 <- mean(CrossValidation_3$cross.validation$cv.oob$kappa)

# Select best performing model based on cross validation kappa.
cat("Selecting best performing model based on cross validation kappa...\n")
Max_CV_Kappa <- max(CV_Kappa_1, CV_Kappa_2, CV_Kappa_3)
if (CV_Kappa_1 == Max_CV_Kappa) {
  Final_Variables <- Variables_1
  Final_Selected <- Selected_1
  Final_Fit <- Fit_1
  Final_Model_Kappa <- Model_Kappa_1
  Final_CrossValidation <- CrossValidation_1
  Final_CV_Kappa <- CV_Kappa_1
} else if (CV_Kappa_2 == Max_CV_Kappa) {
  Final_Variables <- Variables_2
  Final_Selected <- Selected_2
  Final_Fit <- Fit_2
  Final_Model_Kappa <- Model_Kappa_2
  Final_CrossValidation <- CrossValidation_2
  Final_CV_Kappa <- CV_Kappa_2
} else if (CV_Kappa_3 == Max_CV_Kappa) {
  Final_Variables <- Variables_3
  Final_Selected <- Selected_3
  Final_Fit <- Fit_3
  Final_Model_Kappa <- Model_Kappa_3
  Final_CrossValidation <- CrossValidation_3
  Final_CV_Kappa <- CV_Kappa_3
}
sink("FinalVars.txt")
cat(Final_Selected)
sink()

# Export kappa value.
cat("Exporting statistic values and plots...\n")
sink("CrossValidation_Kappa.txt")
cat(as.vector(summary(Final_CV_Kappa))[1])
sink()

# Calculate Area under Curve (AUC) and export Reciever Operating Characteristic (ROC) plot.
Model_Predictions <- as.vector(Final_Fit$votes[,2])
Prediction_Class <- prediction(Model_Predictions, Species_Data@data[, "Present"])
Performance_AUC <- performance(Prediction_Class, "auc")
AUC <- Performance_AUC@y.values[[1]]
Performance_ROC <- performance(Prediction_Class, "tpr", "fpr")
png(file = "plots\\RecieverOperatingCharacteristic.png")
plot(Performance_ROC, main = "Reciever Operating Characteristic")
text(0.7, 0.3, paste("Area Under Curve (AUC) = ", format(AUC, digits=5, scientific = FALSE)))
dev.off()
sink("AUC.txt")
cat(as.vector(summary(AUC))[1])
sink()

# Export graph of all variable importances.
png(file = "plots\\VariableImportance_All.png")
plot(Variables, imp = "all")
dev.off()

# Export scaled variable importance for selected variables.
p <- as.matrix(Final_Fit$importance[,3])
ord <- rev(order(p[,1], decreasing = TRUE)[1:dim(p)[1]])
png(file = "plots\\VariableImportance_Selected.png")
dotchart(p[ord,1], main = "Scaled Variable Importance", pch = 19)
dev.off()

# Export partial dependency plots for the selected variables.
par(mfrow=c(2,2))
for (i in Final_Selected) {
  png_name <- paste("plots\\variablecurves\\PartialDependency_", i, ".png", sep = "")
  png(file = png_name)
  rf.partial.prob(Final_Fit, Species_Data@data[,Final_Selected], i, "1", smooth = TRUE, raw = TRUE, rug = FALSE)
  dev.off()
}

# Calculate occurrence threshold and output value.
Independent_Data <- Species_Data@data[,-1]
Threshold_Value <- occurrence.threshold(Final_Fit, Independent_Data, class="1", type="delta.ss")
sink("OccurrenceThreshold.txt")
summary(Threshold_Value)
sink()
png(file = "plots\\Threshold_Value.png")
plot(Threshold_Value)
dev.off()

# Predict current distribution raster.
cat("Exporting current distribution raster...\n")
Raster_Variables_Current <- stack(paste(Predictor_Folder_Current, paste(rownames(Final_Fit$importance), "img", sep="."), sep="/"))
predict(Raster_Variables_Current, Final_Fit, Output_Raster_Current, type = "prob", index = 2, na.rm = TRUE, overwrite = TRUE, progress = "window")