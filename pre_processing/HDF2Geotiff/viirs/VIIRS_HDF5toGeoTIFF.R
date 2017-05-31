#-------------------------------------------------------------------------------
# VIIRS HDF-EOS5 Import, Georeference, and Export as GeoTIFF Tool
# How to Reformat and Georeference VIIRS Surface Reflectance HDF-EOS5 Files 
# Tool imports VIIRS HDF5, georeferences, and exports geoTIFFs
#
# Authors: Cole Krehbiel1 and Aaron Friesz1
# 1 Innovate!, Inc., contractor to the U.S. Geological Survey, Earth Resources
# Observation and Science (EROS) Center, Sioux Falls, South Dakota, USA. Work 
# performed under USGS contract G15PD00766 for LP DAAC2.
# 2 LP DAAC Work performed under NASA contract NNG14HH33I.

# Contact: 
# Phone: 866-573-3222
# E-mail: LPDAAC@usgs.gov 

# Organization: Land Processes Distributed Active Archive Center
# Date last modified: 03-20-2017
#-------------------------------------------------------------------------------
# OBJECTIVE:  
# This tutorial demonstrates how R and Python scripts can be used to open 
# Visible Infrared Imaging Radiometer Suite (VIIRS) Hierarchical Data Format 
# version 5 (HDF-EOS5, .h5) surface reflectance files, correctly define the 
# coordinate reference system (CRS), and export each science dataset as GeoTIFF 
# files that can be loaded with spatial reference into GIS and Remote Sensing 
# software programs. Both the R and Python scripts will batch process all VIIRS 
# HDF-EOS5 surface reflectance (VNP09) files contained in the input directory.

# The Land Processes Distributed Active Archive Center (LP DAAC) has begun 
# distributing four VIIRS surface reflectance products. The VIIRS surface 
# reflectance collection is archived in HDF-EOS5 format. There is a known issue 
# that prevents users from viewing the data in its correct spatial orientation 
# when using common image processing software programs. When brought into a GIS 
# or Remote Sensing software program, the VNP09 HDF-EOS5 files are displayed 
# without a CRS. The scripts provided here correct this issue. 

# For specific information on the four VIIRS surface reflectance products, 
# see the additional information section below.  VIIRS surface reflectance files 
# can be downloaded from the LP DAAC Data Pool.  Results from this tutorial are 
# output in the native coordinate reference system for each specific VIIRS VNP09 
# product as GeoTIFF files for each science dataset contained in the input file.

# The output naming convention for each band is:
# VNP09[specific prod].AYYYYDOY.h##v##.001_[process date]_sciencedatasetname.tif

# This tool was specifically developed for VIIRS HDF-EOS5 Surface Reflectance
# files and should only be used for the data products listed below:
# VNP09A1
# VNP09GA
# VNP09H1
# VNP09CMG
#-------------------------------------------------------------------------------
# PREREQUISITES:
# This script has been tested with the specifications listed below.
# - Windows 7 64-bit OS
# - R (Version 3.3):
#   . Geospatial Data Abstraction Library (GDAL) Version 1.11.1
# - Libraries
#   .	rhdf5
#   .	rgdal
#   .	raster
#   .	gdalUtils
#   .	tiff
#
# IMPORTANT:
# If first time using this tool: Need to install Bioconductor Packages
# Unmark and run The commands below (labeled as #####) to download Bioconductor.

##### source('https://bioconductor.org/biocLite.R')
##### biocLite()
# Next, download the 'rhdf5' package from Bioconductor
##### biocLite('rhdf5')
#-------------------------------------------------------------------------------
# PROCEDURES:
# VIIRS_HDF5toGeoTIFF.R (URL to R Script)
# 1.Download VIIRS VNP09 HDF-EOS5 data and the VIIRS_HDF5toGeoTIFF.R script from
# the LP DAAC to a local directory
# 2. Start an R session and open VIIRS_HDF5toGeoTIFF.R
# 3. Change in_dir <- ' '  to the directory where the VIIRS HDF-EOS5 files are 
# stored on your system
# 4. Run entire script
#-------------------------------------------------------------------------------
# ADDITIONAL INFORMATION
# For more information on how to set up Bioconductor, visit: 
# https://www.bioconductor.org/install/

# VIIRS Overview: https://lpdaac.usgs.gov/dataset_discovery/viirs_overview 
# VNP09A1 - VIIRS/NPP Surface Reflectance 8-Day L3 Global 1km SIN Grid Product Page
# https://ladsweb.nascom.nasa.gov/api/v1/productPage/product=VNP09A1&collection=5000&return=true 
# VNP09GA - VIIRS/NPP Surface Reflectance Daily L2G Global 1km and 500m SIN Grid Product Page
# https://ladsweb.nascom.nasa.gov/api/v1/productPage/product=VNP09GA&collection=5000&return=true 
# VNP09H1 - VIIRS/NPP Surface Reflectance 8-Day L3 Global 500m SIN Grid Product Page
# https://ladsweb.nascom.nasa.gov/api/v1/productPage/product=VNP09H1&collection=5000&return=true 
# VNP09CMG - VIIRS/NPP Surface Reflectance Daily L3 Global 0.05 Deg CMG Product Page
# https://ladsweb.nascom.nasa.gov/api/v1/productPage/product=VNP09CMG&collection=5000&return=true 

# This tool will batch process VIIRS HDF-EOS5 files if more than 1 is located in
# the input directory.
#-------------------------------------------------------------------------------
# RELATED TUTORIALS:
# How to Reformat and Georeference ASTER L1T HDF Files
# https://lpdaac.usgs.gov/user_community/user_resources/e_learning/how_reformat_and_georeference_aster_l1t_hdf_files
# How to Convert ASTER L1T Radiance to Top of Atmosphere Reflectance 
# https://lpdaac.usgs.gov/user_community/user_resources/e_learning/how_convert_aster_l1t_radiance_top_atmosphere_reflectance
# How to Convert ASTER GED V3 Science Datasets to Georeferenced GeoTIFFs using R and Python
# https://lpdaac.usgs.gov/user_resources/e_learning/how_convert_aster_ged_v3_science_datasets_georeferenced 
# How to Convert ASTER GED V4.1 Science Datasets to Georeferenced GeoTIFFs using R and Python
# https://lpdaac.usgs.gov/user_resources/e_learning/how_convert_aster_ged_v4_science_datasets_georeferenced

# The tutorials and tools listed above can all be found at:
# https://lpdaac.usgs.gov/user_resources/e_learning
#-------------------------------------------------------------------------------
# LABELS:
# Georeference, GeoTIFF, HDF-EOS5, LP DAAC, Python, R, Surface Reflectance,VIIRS
#-------------------------------------------------------------------------------
#               IMPORTANT:
# User needs to change the input directory 'in_dir' line below, denoted by #***.

# Load necessary packages into R
library(rhdf5);library(rgdal);library(raster); library(gdalUtils); library(tiff)
require(rgdal)
#-------------------------------------------------------------------------------
#|                    Batch Process files from directory:                      |
#-------------------------------------------------------------------------------
# Set input directory, user NEEDS to change to directory containing 
# VIIRS HDF-EOS5 files
in_dir <- '/PATH_TO_INPUT_FILE/' #***Change

# Create and set output directory
out_dir <- paste(in_dir, 'output/', sep = '')
suppressWarnings(dir.create(out_dir))

# Create a list of All VIIRS Surface Reflectance HDF-EOS5 files in the directory
file_list <- list.files(path = in_dir,pattern = 'VNP.*h5$')

#Build Dictionary (list) of potential output data types
dt_dict <- vector(mode="list", length=5) 
names(dt_dict) <- c("8-bit character" ,"8-bit unsigned character",
                          "16-bit integer" ,"16-bit unsigned integer" ,
                          "32-bit unsigned integer" )  
dt_dict[[1]] <- "INT1U"; dt_dict[[2]] <- "INT1U"; dt_dict[[3]] <- "INT2S"; 
dt_dict[[4]] <- "INT2U"; dt_dict[[5]] <- "INT4U"
#-------------------------------------------------------------------------------
# Batch for all VIIRS files in input directory
for (i in 1:length(file_list)){
  # Maintain the original filename
  file_name <- file_list[i]
  # Search file metadata for a list of science datasets inside the file
  meta_data  <- gdalinfo(paste(in_dir, file_name, sep=""))
  sd_all <- strsplit(meta_data[grep('NAME=HDF5', meta_data)], '":/')
  dt_all <- (meta_data[grep('DESC=', meta_data)])
  rm(meta_data)
  #-----------------------------------------------------------------------------
  # Set the output CRS for the VIIRS CMG product (VNP09CMG)
  if (substr(file_name,6,8) == 'CMG'){
    # set up extent for output rasters
    y_min <- -90.0; y_max <- 90.0; x_max <- 180.0; x_min <- -180.0
    # Coordinate Reference System
    crs <- '+proj=longlat +ellps=clrk66 +no_defs'
  }else{
    # Search metadata for geolocation information for VIIRS gridded/tiled products
    struct_metadata = strsplit(h5read(paste(in_dir, file_name, sep=""),
                                        'HDFEOS INFORMATION/StructMetadata.0',read.attributes=T), "\n")
    # Grab upper left and lower right geolocation information
    ul_x <- as.numeric(strsplit(sub("\\).*", "", sub(".*\\(", "",
                                                     struct_metadata[[1]][[8]] )), ",")[[1]][[1]])
    ul_y <- as.numeric(strsplit(sub("\\).*", "", sub(".*\\(", "",
                                                     struct_metadata[[1]][[8]] )), ",")[[1]][[2]])
    lr_x <- as.numeric(strsplit(sub("\\).*", "", sub(".*\\(", "",
                                                     struct_metadata[[1]][[9]] )), ",")[[1]][[1]])
    lr_y <- as.numeric(strsplit(sub("\\).*", "", sub(".*\\(", "",
                                                     struct_metadata[[1]][[9]] )), ",")[[1]][[2]])
    # Configure and set extent properties
    y_min <- min(ul_y, lr_y)
    y_max <- max(ul_y, lr_y)
    x_max <- max(ul_x, lr_x)
    x_min <- min(ul_x, lr_x)
    
    # Coordinate Reference System
    crs <- '+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs '
    rm(struct_metadata, ul_y, ul_x, lr_y, lr_x)
    }
  #-----------------------------------------------------------------------------
  # Set Raster Dimensions
  raster_dims <- extent(x_min, x_max, y_min, y_max)
  rm(y_min, y_max, x_min, x_max)
  #-----------------------------------------------------------------------------
  for (k in 1:length(sd_all)){
    # Read input datatype for each dataset
    out_dt = dt_dict[sub("\\).*", "", sub(".*\\(", "", dt_all[k]))][[1]][[1]]
    sd <- gsub('Data_Fields','Data Fields', sd_all[[k]][[2]])
    sd_name <- strsplit(sd, 'Data Fields/')[[1]][[2]]
    sd_longname = sd_all[[k]][[1]]
    
    # read in the science dataset
    sds <- h5read(paste(in_dir, file_name, sep=""), sd)
    sds_t <- t(sds)
    rm(sds)
    # Convert array to raster and set coordinate reference system
    sds_r <- raster(sds_t, crs = crs)
    rm(sds_t)

    # Assign extent to each raster layer
    extent(sds_r) <- raster_dims
    
    # Generate output filename using the original file name and the SDS name
    out_name <- paste(out_dir, strsplit(file_name, '.h5'), '_', 
                      strsplit(sd, 'Data Fields/')[[1]][[2]], '.tif', sep='')
    # Export the raster layer file (GeoTIFF) to the output directory
    writeRaster(sds_r, filename=out_name,  options='INTERLEAVE=BAND',
                format='GTiff', datatype=out_dt, overwrite=TRUE)
    rm(sds_r,out_dt, out_name, sd, sd_longname, sd_name)
  }
  rm(dt_all, file_name, sd_all, raster_dims)
}  
#-------------------------------------------------------------------------------
