#------------------------------------------------------------------------------
# ASTER GED Version 3 HDF5 Import, Georeference, and Export as GeotIFF Tool
# How to Georeference ASTER GED v3 HDF5 Files
# This tool imports ASTER GED Version 3 HDF5, georeferences, and  exports 
# files as geoTIFFs.
#------------------------------------------------------------------------------
# Author: Cole Krehbiel
# Contact: LPDAAC@usgs.gov  
# Organization: Land Processes Distributed Active Archive Center
# Date last modified: 12-21-2016
#------------------------------------------------------------------------------
# OBJECTIVE:
# The Advanced Spaceborne Thermal Emission and Reflection Radiometer (ASTER) 
# Global Emissivity Dataset (GED) Version 3 (AG100, AG1km)
# provide land surface temperature and emissivity for ASTER bands 10-14 globally
# in 1° x 1°tiles at 100 m and 1 km spatial resolution, delivered in HDF5 file 
# formats. The values are computed from all clear-sky observations 
# from ASTER scenes acquired from 2000-2008. However, when the files are opened
# in software packages such as ENVI/IDL, ArcMap, or QGIS, they are lacking a 
# coordinate reference system (CRS) needed to georeferenced the data.

# The objective of this tool is to add a CRS to the ASTER  GED v3 HDF5 files.
# To do this, the ASTER  GED v3 HDF5 files (downloaded from 
# https://lpdaac.usgs.gov/data_access/data_pool) are opened in the R statistical
# software program (https://www.r-project.org/) using the ASTERGED_V3_Recipe.R 
# script.This tool was developed using R version 3.3.The tool converts the data 
# matrices into raster layers that include a CRS, and are exported as geoTIFFs. 
# All geoTIFFs are output into Geographic (Lat/Lon) WGS-84 projection. For the 
# 'Emissivity_Mean' and 'Emissivity_SDev' layers, 
# which include data for ASTER TIR bands 10-14, the multiband geoTIFFs are 
# ordered as follows:
# band 1 = ASTER b10
# band 2 = ASTER b11
# band 3 = ASTER b12
# band 4 = ASTER b13
# band 5 = ASTER b14

# This tool was specifically developed for ASTER  GED v3 HDF5 files and
# should only be used for the aforementioned data products.
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
# 'rgdal' and 'raster' 
#------------------------------------------------------------------------------
# ESTIMATED TIME TO COMPLETE
# On average, this tool should run < 1 minute per iteration once the 
# prerequisite requirements have been satisfied.
#------------------------------------------------------------------------------
# ADDITIONAL INFORMATION
# See the ASTER GED v3 HDF5 to GeoTIFF Data Recipe, available at 
# https://lpdaac.usgs.gov/ for more information.

# For more information on how to set up Bioconductor, 
# visit: https://www.bioconductor.org/install/

# This tool will batch process ASTER GED v3 HDF5 files if more than 1 is
# located in the working directory.
#------------------------------------------------------------------------------
# RELATED DATA RECIPES
# ASTERGED_V41_Recipe.R is a tool that georeferences ASTER GED v4.1 HDF5 data

# ASTERGED_V3_Recipe.py is a Python tool that georeferences ASTER GED v3 
# HDF5 data

# ASTERGED_V41_Recipe.py is a Python tool that georeferences ASTER GED v4.1 
# HDF5 data

# The tools listed above can all be found at https://lpdaac.usgs.gov/
#------------------------------------------------------------------------------
# LABELS
# LP DAAC, R, ASTER GED, Emissivity, HDF5, geoTIFF
#------------------------------------------------------------------------------
# PROCEDURES:

#         IMPORTANT:
# The user will need to change the current working directory (in_dir) line below, 
# denoted by #***.

# Load Packages into R
library(rhdf5)
library(rgdal)
library(raster)

require(rgdal)

# Set current working directory
in_dir <- '/PATH_TO_INPUT_FILE(S)_FOLDER' #***Change
setwd(in_dir)

# Create and set output directory
out_dir <- paste(in_dir, 'output/', sep = '')
suppressWarnings(dir.create(out_dir))

# Create a list of ASTER GED v3 HDF5 files in the directory
filelist_h5 <- list.files(pattern = 'AG1.*.v003.*h5$')

# Names for the ASTER GED datasets
sd_names <- c( 'Emissivity_Mean', 'Emissivity_SDev', 'Temperature_Mean', 
               'Temperature_SDev', 'NDVI_Mean', 'NDVI_SDev', 'Land_Water_Map', 
               'Num_Observations', 'Geolocation_Latitude', 
               'Geolocation_Longitude', 'ASTER_GDEM' )

# Points to the location of each dataset within the ASTER GED HDF5 v3 file
sd_location <- c( '/Emissivity/Mean', '/Emissivity/SDev', '/Temperature/Mean',
                  '/Temperature/SDev', '/NDVI/Mean', '/NDVI/SDev',
                  '/Land Water Map/LWmap', '/Observations/NumObs',
                  '/Geolocation/Latitude', '/Geolocation/Longitude',
                  '/ASTER GDEM/ASTGDEM')

# Coordinate Reference System
crs_string <- '+proj=longlat +lat_1=90.000000 +lon_1=-180.000000 +datum=WGS84'
#------------------------------------------------------------------------------
# Loops processing for each ASTER GED v3 HDF5 file in working directory
for (i in 1:length(filelist_h5)){
   
  # Read the Lat and Lon Datasets in order  to set up extent for output rasters
  y_min <- min(h5read(filelist_h5[i], 'Geolocation/Latitude'))
  y_max <- max(h5read(filelist_h5[i], 'Geolocation/Latitude'))
  x_max <- max(h5read(filelist_h5[i], 'Geolocation/Longitude'))
  x_min <- min(h5read(filelist_h5[i], 'Geolocation/Longitude'))
  raster_dims <- extent(x_min, x_max, y_min, y_max)
  
  # Name the ASTER GED v3 HDF5 file
  aster_file <- filelist_h5[i]
  
  # maintain the original filename for output geotiff
  file_name <- strsplit(aster_file, '.h5')
  #------------------------------------------------------------------------------
  # Loops processing for each SDS in the ASTER GED v3 HDF5 file 
  for (j in 1:length(sd_location)){
    
    # read in the SDS
    sds <- h5read(aster_file, sd_location[j])
    
    # If j = 1 or 2, (Emis or Emis Uncertainty), convert all 5 layers to raster 
    if (j<2.5){
      
      # Transpose layers
      sds_1 <- t(sds[, , 1])
      sds_2 <- t(sds[, , 2])
      sds_3 <- t(sds[, , 3])
      sds_4 <- t(sds[, , 4])
      sds_5 <- t(sds[, , 5])
      
      # Convert layers to raster
      sds_1 <- raster(sds_1, crs = crs_string)
      sds_2 <- raster(sds_2, crs = crs_string)
      sds_3 <- raster(sds_3, crs = crs_string)
      sds_4 <- raster(sds_4, crs = crs_string)
      sds_5 <- raster(sds_5, crs = crs_string)
      
      # Remove input SDS
      rm(sds)
      
      # Assign extent to each raster layer
      extent(sds_1) <- raster_dims
      extent(sds_2) <- raster_dims
      extent(sds_3) <- raster_dims
      extent(sds_4) <- raster_dims
      extent(sds_5) <- raster_dims
      
      # Create multiband raster file
      sds_brick <- brick(sds_1, sds_2, sds_3, sds_4, sds_5)
      rm(sds_1)
      rm(sds_2)
      rm(sds_3)
      rm(sds_4)
      rm(sds_5)
      
      # Convert single layer to raster  
    }else{
      
      # Transpose the dataset
      sds <- t(sds)
      
      # Convert Matrix to raster
      sds_brick <- raster(sds, crs = crs_string)
      rm(sds)
      
      # Assign extent to raster layer
      extent(sds_brick) <- raster_dims
    }
    # NDVI needs to be exported as 'INT4S', all others are exported as 'INT2S'
    if (j == 3){
      
      # Generate output filename using the original aster name and the SDS name
      out_name <- paste(out_dir, file_name, '_', sd_names[j], '.tif', sep = '')
      
      # export the raster layer file (Geotiff format) to the output directory
      writeRaster(sds_brick, filename = out_name,  options = 'INTERLEAVE=BAND',
                  format = 'GTiff', datatype = 'INT4S', overwrite = TRUE)
      
      # Remove the raster layer
      rm(sds_brick)
      
    }else if (j > 8.5 & j < 10.5){ 
      # Generate output filename using the original aster name and the SDS name
      out_name <- paste(out_dir, file_name, '_', sd_names[j], '.tif', sep = '')
      
      # export the raster layer file (Geotiff format) to the output directory
      writeRaster(sds_brick, filename = out_name,  options = 'INTERLEAVE=BAND',
                  format = 'GTiff', datatype = 'FLT4S', overwrite = TRUE)
      
      # Remove the raster layer
      rm(sds_brick)
    }else{ 
      # Generate output filename using the original aster name and the SDS name
      out_name <- paste(out_dir, file_name, '_', sd_names[j], '.tif', sep = '')
      
      # export the raster layer file (Geotiff format) to the output directory
      writeRaster(sds_brick, filename = out_name,  options = 'INTERLEAVE=BAND',
                  format = 'GTiff', datatype = 'INT2S', overwrite = TRUE)
      
      # Remove the raster layer
      rm(sds_brick)
    }
  }
}
#------------------------------------------------------------------------------