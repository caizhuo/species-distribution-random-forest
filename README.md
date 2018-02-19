# random-forest-distribution-toolbox
Python- and R-based ArcGIS toolbox for mapping species distributions using a variable-optimized random forest model.

## Getting Started

These instructions will enable you to run the Random Forest Distribution Modeling Toolbox in ArcGIS Pro or Desktop.

### Prerequisites
1. ArcGIS Pro 2.0 or higher AND/OR ArcGIS Desktop 10.4.1 with 64-bit Background Processing if using ArcGIS Desktop
2. R 3.4.2 or higher

### Installing

Download this repository and unzip it to a folder on a drive accessible to your computer. Local drives may perform better than network drives.

Open ArcGIS Pro or ArcMap:
* In ArcGIS Pro, open the catalog tab, right click on the toolbox folder, select add toolbox, and navigate to the location of the downloaded/unzipped toolbox.
* In ArcMap, open the toolbox tab, right click, select add toolbox, and navigate to the location of the downloaded/unzipped toolbox.

*You must have R installed to a local drive prior to use of this tool. Packages do not need to be pre-installed. The first time you run this tool, all necessary packages will be automatically downloaded and installed.*

*The toolbox and the script folder must remain in the same parent folder or the location of the script will have to be modified in the toolbox.*

## Usage

### Workflow
A suggested workflow is to create an area of interest, a set of presence-absence points, and a suite of predictor rasters. Then use the tools in this toolbox to do the following:
1. Pre-process Predictor Raster: for every predictor raster, this tool must be run to align grids, standardize cell size, and ensure uniform extent. Failure to do so will result in model failure during predict steps.
2. Check Variable Multicollinearity: Run with the presence-absence points and suite of potential predictor rasters to identify collinear variables that should be considered for removal. The model will work without removing collinear variables and there are some circumstances where it is better that one or multiple be retained.
3. Random Forest Model OR Random Forest Model and Projection: Trains a model based on the input presence-absence points and predictor rasters. Model selects best-performing suite of predictor variables based on cross-validation kappa. Input rasters are used to create spatial predictions.
4. Convert Probability Distribution to Presence-Absence: If a binary distribution is desired, then this tool converts the predicted output probability distribution to presence-absence based on the threshold value calculated by the minimization of the difference between sensitivity and specificity.

### Pre-process Predictor Raster
* tbd

### Check Variable Multicollinearity
* tbd

### Random Forest Model
* tbd

### Random Forest Model and Projection
* tbd

### Convert Probability Distribution to Presence-Absence
* tbd

## Credits

### Built With
* ArcGIS Desktop 10.4.1
* ArcGIS Pro 2.0
* Notepad ++
* R 3.4.2
* RStudio 1.0.153

### Authors

* **Timm Nawrocki** - *Alaska Center for Conservation Science, University of Alaska Anchorage*

### Usage Requirements

If you use this tool, elements of this tool, or a derivative product, please cite the following:

Evans, J., M. Murphy, Z. Holden, and S. Cushman. 2011. Modeling Species Distribution and Change Using Random Forest. In: Drew, C., Y. Wiersma, F. Huettmann (eds.). 2011. Predictive Species and Habitat Modeling in Landscape Ecology. Springer. New York. 139-159.

Murphy, M., J. Evans, and A. Storfer. 2010. Quantifying Bufo boreas connectivity in Yellowstone National Park with landscape genetics. Ecology. 91(1). 252-261.

Reimer, J.P, T. Nawrocki, M. Aisu, and T. Gotthardt. 2016. Section H: Terrestrial Fine-Filter Conservation Elements. *In:* Trammell, E.J., T. Boucher, M.L. Carlson, N. Fresco, J.R. Fulkerson, M.L. McTeague, J.P. Reimer, and J. Schmidt (eds.). 2016. Central Yukon Rapid Ecoregional Assessment. Prepared for the Bureau of Land Management, U.S. Department of the Interior. Anchorage, Alaska.

Shaftel, R., D. Rinella, and D. Merrigan. 2016. Section J: Aquatic Fine-Filter Conservation Elements. *In:* Trammell, E.J., T. Boucher, M.L. Carlson, N. Fresco, J.R. Fulkerson, M.L. McTeague, J.P. Reimer, and J. Schmidt (eds.). 2016. Central Yukon Rapid Ecoregional Assessment. Prepared for the Bureau of Land Management, U.S. Department of the Interior. Anchorage, Alaska. 

### License

This project is private and can be used by Alaska Center for Conservation Science and collaborators.
