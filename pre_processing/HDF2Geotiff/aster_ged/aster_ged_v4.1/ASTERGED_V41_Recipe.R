#------------------------------------------------------------------------------
# ASTER GED V4.1 HDF5 Import, Georeference, and Export as GeoTIFF Tool
# How to Georeference ASTER GED v4.1 HDF5 Files
# Tool imports ASTER GED V4.1 HDF5, georeferences, and exports geoTIFFs.
#------------------------------------------------------------------------------
# Author: Cole Krehbiel
# Contact: LPDAAC@usgs.gov  
# Organization: Land Processes Distributed Active Archive Center
# Date last modified: 12-21-2016
#------------------------------------------------------------------------------
# OBJECTIVE:
# The Advanced Spaceborne Thermal Emission and Reflection Radiometer (ASTER) 
# Global Emissivity Dataset (GED) Version 4.1 (AG5KMMOH.041) provide monthly 
# emissivity for ASTER bands 10-14 globally at 0.05° spatial resolution, 
# delivered in HDF5 file format. However, when the files are opened
# in software packages such as ENVI/IDL, ArcMap, or QGIS, they are lacking a 
# coordinate reference system (CRS) needed to georeference the data.

# The objective of this tool is to add a CRS to the ASTER  GED v4.1 HDF5
# files. To do this, the ASTER GED v4.1 HDF5 files (downloaded from 
# https://lpdaac.usgs.gov/data_access/data_pool) are opened in the R statistical
# software program (https://www.r-project.org/) using the ASTERGED_V41_Recipe.R 
# script.This tool was developed using R version 3.3. The tool converts the data
# matrices into raster layers that include a CRS, and are exported as geoTIFFs.
# All geoTIFFs are output into Geographic (Lat/Lon) WGS-84 projection. 
# For the 'Emissivity' and 'EmissivityUncertainty' layers, which include data 
# for ASTER TIR bands 10-14, the multiband geotiffs are ordered as follows:
# band 1 = ASTER b10
# band 2 = ASTER b11
# band 3 = ASTER b12
# band 4 = ASTER b13
# band 5 = ASTER b14

# This tool was specifically developed for ASTER GED v4.1 HDF5 
# files and should only be used for the aforementioned data product.
#------------------------------------------------------------------------------
# PREREQUISITES
# R statistical software program version 3.3

#         IMPORTANT:
# If first time using this tool: Need to install Bioconductor Packages
# Unmark and run The commands below (labeled as #####) to download Bioconductor.

##### source('https://bioconductor.org/biocLite.R')
##### biocLite()
# Next, download the 'rhdf5' package from Bioconductor
##### biocLite('rhdf5')

# CRAN Packages required: 
#'rgdal' and 'raster' 
#------------------------------------------------------------------------------
# ESTIMATED TIME TO COMPLETE
# On average, this tool should run between 1-3 minutes per iteration once the 
# prerequisite requirements have been satisfied.
#------------------------------------------------------------------------------
# ADDITIONAL INFORMATION
# See the ASTER GED v4.1 HDF5 to GeoTIFF Data Recipe, available at 
# https://lpdaac.usgs.gov/ for more information.
# For more information on how to set up Bioconductor, visit: 
# https://www.bioconductor.org/install/
# This tool will batch process ASTER GED v4.1 HDF5 files if more than 1
# is located in the working directory.
#------------------------------------------------------------------------------
# RELATED DATA RECIPES
# ASTERGED_V3_Recipe.R: Tool that georeferences ASTER GED v3 HDF5 data
# ASTERGED_V3_Recipe.py: Tool that georeferences ASTER GED v3 HDF5 data
# ASTERGED_V41_Recipe.py: Tool that georeferences ASTER GED v4.1 HDF5 data
# The tools listed above can all be found at https://lpdaac.usgs.gov/
#------------------------------------------------------------------------------
# LABELS
# LP DAAC, R, ASTER GED, Emissivity, HDF5, geoTIFF
#------------------------------------------------------------------------------
# PROCEDURES:

#         IMPORTANT:
# User will need to change the current working directory (in_dir) line below, 
# denoted by #***.

# Load necessary packages into R
library(rhdf5)
library(rgdal)
library(raster)

require(rgdal)

# Set current working directory
in_dir <- '/PATH_TO_INPUT_FILE(S)_FOLDER'  #***Change
setwd(in_dir)

# Create and set output directory
out_dir <- paste(in_dir, 'output/', sep = '')
suppressWarnings(dir.create(out_dir))

# Create a list of ASTER GED v4 HDF5 files in the directory
filelist_h5 <- list.files(pattern = 'ASTER_GEDv4.1_A.*h5$')

# set up extent for output rasters
y_min <- -90
y_max <- 90
x_max <- 180
x_min <- -180
raster_dims <- extent(x_min, x_max, y_min, y_max)

# Names for the ASTER GED datasets
sd_names <- c('Emissivity', 'EmissivityUncertainty', 'NDVI', 'QualityFlag',
              'Snow')

# Points to the location of each dataset within the HDF5 file
sd_location <- c('/SDS/Emissivity', '/SDS/EmissivityUncertainty', '/SDS/NDVI',
                 '/SDS/QualityFlag')

# Coordinate Reference System
crs_string <- '+proj=longlat +lat_1=90.000000 +lon_1=-180.000000 +datum=WGS84'
#------------------------------------------------------------------------------
# Loop processing for each HDF5 file in working directory
for (i in 1:length(filelist_h5)){
  
  # name the h5 file
  aster_file <- filelist_h5[i]
  
  # maintains the original filename
  file_name <- strsplit(aster_file, '.h5')
  
  # Loops processing for each SDS in the ASTER GED h5 file 
  for (j in 1:4){
    
    # reads in the SDS
    sds <- h5read(aster_file, sd_location[j])
    
    # If j = 1 or 2, (Emis or Emis Uncertainty) convert all 5 layers to raster 
    if (j < 2.5){
      # Transpose layers
      sds_1 <- t(sds[, , 1])
      sds_2 <- t(sds[, , 2])
      sds_3 <- t(sds[, , 3])
      sds_4 <- t(sds[, , 4])
      sds_5 <- t(sds[, , 5])
      rm(sds)
      
      # Convert layers to raster
      sds_1 <- raster(sds_1, crs = crs_string)
      sds_2 <- raster(sds_2, crs = crs_string)
      sds_3 <- raster(sds_3, crs = crs_string)
      sds_4 <- raster(sds_4, crs = crs_string)
      sds_5 <- raster(sds_5, crs = crs_string)
      
      # Assign extent to each raster layer
      extent(sds_1) <- raster_dims
      extent(sds_2) <- raster_dims
      extent(sds_3) <- raster_dims
      extent(sds_4) <- raster_dims
      extent(sds_5) <- raster_dims
      
      # Creates multiband raster file
      sds_brick <- brick(sds_1,sds_2,sds_3,sds_4,sds_5)
      rm(sds_1)
      rm(sds_2)
      rm(sds_3)
      rm(sds_4)
      rm(sds_5)
      # If j = 3 or 4 (NDVI or QualityFlag), convert the single layer to raster  
    }else{
      
      # Transpose the dataset
      sds <- t(sds)
      
      sds_brick <- raster(sds, crs = crs_string)
      rm(sds)
      
      # Assign extent to each raster layer
      extent(sds_brick) <- raster_dims
    }
    if (j == 3){
      # Generates output filename using the original aster name and the SDS name
      out_name <- paste(out_dir, file_name, '_', sd_names[j], '.tif', sep='')
      
      # Exports the raster layer file (GeoTIFF format) to the output directory
    writeRaster(sds_brick, filename=out_name,  options='INTERLEAVE=BAND',
                  format='GTiff', datatype='INT2U', overwrite=TRUE)
      rm(sds_brick)
    }else{
      # Generates output filename using the original aster name and the SDS name
      out_name <- paste(out_dir, file_name, '_', sd_names[j], '.tif', sep='')
      
      # Exports the raster layer file (GeotIFF format) to the output directory
      writeRaster(sds_brick, filename=out_name,  options='INTERLEAVE=BAND',
                  format='GTiff', datatype='INT1U', overwrite=TRUE)
      rm(sds_brick)
    }
  }
}
#------------------------------------------------------------------------------
