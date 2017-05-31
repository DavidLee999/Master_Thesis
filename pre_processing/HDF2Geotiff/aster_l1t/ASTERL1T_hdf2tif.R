#-------------------------------------------------------------------------------
# Open ASTER L1T HDF-EOS and Export as GeotIFF Tool
# How To Tutorial
# This tool imports ASTER L1T HDF-EOS files, georeferences, and  exports as 
# GeoTIFF files.
#-------------------------------------------------------------------------------
# Author: Cole Krehbiel
# Contact: LPDAAC@usgs.gov  
# Organization: Land Processes Distributed Active Archive Center
# Date last modified: 03-06-2017
#-------------------------------------------------------------------------------
# DESCRIPTION:
# This script takes an ASTER L1T HDF-EOS file (.hdf) as an input and outputs 
# georeferenced tagged image file format (GeoTIFF) files for each of the VNIR,
# SWIR, and TIR science datasets contained in the original ASTER L1T file.

# Results from this tutorial are output in Universal Transverse Mercator (UTM)
# with WGS84 as GeoTIFF files. The output GeoTIFFs for each band include:
#  1. Original_AST_L1T_Filename_ImageDataband#.tif
# Data is At-Sensor radiance stored as Digital Numbers(DN).The script will batch 
# process ASTER L1T files if more than 1 is located in the working directory.
# Output file directory will be 'inputfiledirectory'+'/output/'

# This tool was specifically developed for ASTER L1T HDF-EOS files and should 
# only be used for those data products.
#-------------------------------------------------------------------------------
# PREREQUISITES:
#  Discaimer: This script was tested in the following environments:
# -  R: Version 3.3.0 (Anaconda 4.1.1) on Windows OS
# -  Geospatial Data Abstraction Library (GDAL): Version 2.0.0 and 2.1.0

# R Libraries:
# rgdal - 1.1.10
# raster - 2.5.2
# gdalUtils - 2.0.1.7
# tiff - 0.1.5
#-------------------------------------------------------------------------------
# ADDITIONAL INFORMATION:
# LP DAAC ASTER L1T Product Page: 
# https://lpdaac.usgs.gov/dataset_discovery/aster/aster_products_table/ast_l1t
# LP DAAC ASTER L1T User Guide: 
# https://lpdaac.usgs.gov/sites/default/files/public/product_documentation/
# aster_l1t_users_guide.pdf

# Search for other tools at https://lpdaac.usgs.gov/
#-------------------------------------------------------------------------------
# PROCEDURES:
# 1.	Copy/clone ASTERL1T_hdf2tif.R from LP DAAC Recipes & Tutorials Repository
# 2.	Download ASTER L1T data from the LP DAAC to a local directory
# 3.	Start an R session and open ASTERL1T_hdf2tif.R
# 4.	Change in_dir <- ' '  to dir where the AST L1T HDF files are on system
# 5.	Run entire script
#-------------------------------------------------------------------------------
#         IMPORTANT:
# User needs to change the 'in_dir' (working directory) below, denoted by #***

# Load necessary packages into R
library(rgdal)
library(raster)
library(gdalUtils)
library(tiff)

require(rgdal)
#-------------------------------------------------------------------------------
#|                    Batch Process files from directory:                      |
#-------------------------------------------------------------------------------
# Set input/current working directory, user NEEDS to change to directory where 
# files will be downloaded to.
in_dir <- '/PATH_TO_INPUT_FILE/' #***Change
setwd(in_dir)

# Create and set output directory
out_dir <- paste(in_dir, 'output/', sep='')
suppressWarnings(dir.create(out_dir))

# Create a list of ASTER L1T HDF files in the directory
file_list <- list.files(pattern = 'AST_L1T_.*hdf$')
#-------------------------------------------------------------------------------
for (i in 1:length(file_list)){
  # Maintains the original filename
  file_name <- file_list[i]

  # Read in the metadata
  meta_data <- gdalinfo(file_name)

  # Define CRS
  # Define Upper left and lower right--need for x, y min/max
  # For offset (pixel size / 2), needs to be defined for 3 ASTER pixel 
  # resolutions (15, 30, 90)
  
  # Grab LR and UL values
  lr_row <- grep('LOWERRIGHTM', meta_data)
  ul_row <- grep('UPPERLEFTM', meta_data)
  lr <- substr(meta_data[lr_row[1]], 15, 50)
  ul <- substr(meta_data[ul_row[1]], 14, 50)
  clip4 <- regexpr(', ' , ul) 
  clip5 <- regexpr(', ', lr) 
  
  # Define LR and UL x and y values for 15m VNIR Data
  ul_y <- as.numeric((substr(ul, 1, (clip4 - 1)))) + 7.5
  ul_x <- as.numeric((substr(ul, (clip4 + 2), 10000))) - 7.5
  lr_y <- as.numeric((substr(lr, 1, (clip5 - 1)))) - 7.5
  lr_x <- as.numeric((substr(lr, (clip5 + 2) , 10000))) + 7.5
  
  # Define LR and UL x and y values for 30m SWIR Data
  ul_y_30m <- as.numeric((substr(ul, 1, (clip4 - 1)))) + 15
  ul_x_30m <- as.numeric((substr(ul, (clip4 + 2), 10000))) - 15
  lr_y_30m <- as.numeric((substr(lr, 1, (clip5 - 1)))) - 15
  lr_x_30m <- as.numeric((substr(lr, (clip5 + 2) , 10000))) + 15
  
  # Define LR and UL x and y values for 90m TIR Data
  ul_y_90m <- as.numeric((substr(ul, 1, (clip4 - 1)))) + 45
  ul_x_90m <- as.numeric((substr(ul, (clip4 + 2), 10000))) - 45
  lr_y_90m <- as.numeric((substr(lr, 1, (clip5 - 1)))) - 45
  lr_x_90m <- as.numeric((substr(lr, (clip5 + 2) , 10000))) + 45
  
  # Define UTM zone
  utm_row <- grep('UTMZONECODE', meta_data)
  utm_zone <- substr(meta_data[utm_row[1]], 1, 50)
  clip6 <- regexpr('=', utm_zone) 
  utm_zone <- substr(utm_zone, clip6 + 1, 50)
  
  # Configure extent properties (15m VNIR)
  y_min <- min(ul_y, lr_y); y_max <- max(ul_y, lr_y)
  x_max <- max(ul_x, lr_x); x_min <- min(ul_x, lr_x)
  
  # Configure extent properties (30m SWIR)
  y_min_30m <- min(ul_y_30m, lr_y_30m); y_max_30m <- max(ul_y_30m, lr_y_30m)
  x_max_30m <- max(ul_x_30m, lr_x_30m); x_min_30m <- min(ul_x_30m, lr_x_30m)
  
  # Configure extent properties (90m TIR)
  y_min_90m <- min(ul_y_90m, lr_y_90m); y_max_90m <- max(ul_y_90m, lr_y_90m)
  x_max_90m <- max(ul_x_90m, lr_x_90m); x_min_90m <- min(ul_x_90m, lr_x_90m)
  
  raster_dims_15m <- extent(x_min, x_max, y_min, y_max)
  raster_dims_30m <- extent(x_min_30m, x_max_30m, y_min_30m, y_max_30m)
  raster_dims_90m <- extent(x_min_90m, x_max_90m, y_min_90m, y_max_90m)
  
  # Compile Cordinate Reference System string to attach projection information
  crs_string <- paste('+proj=utm +zone=', utm_zone, ' +datum=WGS84 +units=m 
                      +no_defs +ellps=WGS84 +towgs84=0,0,0', sep = '')
  
  # Remove unneccessary variables
  rm(clip4, clip5, clip6, lr, lr_x, lr_y, meta_data, ul, ul_x, ul_y, utm_zone,
     x_min, x_max, y_min, y_max, lr_row, ul_row, utm_row)
  
  # Get a list of sds names
  sds <- get_subdatasets(file_name)
  
  # Limit loop to SDS that contain VNIR/SWIR/TIR data (14 max)
  match_vnir <- grep('VNIR_Swath', sds)
  match_swir <- grep('SWIR_Swath', sds)
  match_tir <- grep('TIR_Swath', sds)
  #-----------------------------------------------------------------------------
  if (length(match_vnir)> 0) {
    for (k in min(match_vnir):max(match_vnir)){
      # Isolate the name of the first sds
      sub_dataset<- sds[k]
      
      # Get the name of the specific SDS
      clip2 <- max(unlist((gregexpr(':', sub_dataset)))) 
      
      # Generate output name for tif
      new_file_name <- strsplit(file_name, '.hdf')
      tif_name <- paste(out_dir, new_file_name, '_', substr(sub_dataset, 
                       (clip2 + 1), 10000),'.tif', sep='')
      sd_name <- paste(new_file_name, substr(sub_dataset, (clip2 + 1), 10000),
                       sep = '_')
      sub_name <- paste(new_file_name, 'ImageData', sep = '_')
      ast_band_name <- gsub(sub_name, '', sd_name)
      
      # Extract specified SDS and export as Geotiff
      gdal_translate(file_name, tif_name, sd_index=k, output_Raster = FALSE)
      
      # Open geotiff and add projection (CRS)
      aster_file <- raster(tif_name, crs = crs_string)
      extent(aster_file) <- raster_dims_15m

      # Convert to large raster layer
      aster_file <- calc(aster_file, fun =function(x){x} )
      
      # Export the raster layer file (Geotiff format) to the output directory
      writeRaster(aster_file, filename = tif_name,  options = 'INTERLEAVE=BAND',
                  format = 'GTiff', datatype = 'INT1U', overwrite = TRUE, 
                  NAflag = 0)
      # Remove unneccessary variables
      rm(aster_file, sub_dataset, sd_name, sub_name, tif_name, new_file_name)
    }
  } 
  #-----------------------------------------------------------------------------
  if (length(match_swir) > 0) {
    for (k in min(match_swir):max(match_swir)){
    # Isolate the name of the first sds
    sub_dataset<- sds[k]
    
    # Get the name of the specific SDS
    clip2 <- max(unlist((gregexpr(':', sub_dataset)))) 
    
    # Generate output name for tif
    new_file_name <- strsplit(file_name, '.hdf')
    tif_name <- paste(out_dir, new_file_name, '_', substr(sub_dataset, 
                     (clip2 + 1), 10000),'.tif', sep='')
    sd_name <- paste(new_file_name, substr(sub_dataset, (clip2 + 1), 10000),
                     sep = '_')
    sub_name <- paste(new_file_name, 'ImageData', sep = '_')
    ast_band_name <- gsub(sub_name, '', sd_name)
    
    # Extract specified SDS and export as Geotiff
    gdal_translate(file_name, tif_name, sd_index=k, output_Raster = FALSE)
    
    # Open geotiff and add projection (CRS)
    aster_file <- raster(tif_name, crs = crs_string)
    extent(aster_file) <- raster_dims_30m
    
    # Convert to large raster layer
    aster_file <- calc(aster_file, fun =function(x){x} )
    
    # Export the raster layer file (Geotiff format) to the output directory
    writeRaster(aster_file, filename = tif_name,  options = 'INTERLEAVE=BAND',
                format = 'GTiff', datatype = 'INT1U', overwrite = TRUE, 
                NAflag = 0)
    # Remove unneccessary variables
    rm(aster_file, sub_dataset, sd_name, sub_name, tif_name, new_file_name)
    }
  }
  #-----------------------------------------------------------------------------
  if (length(match_tir) > 0) {
    for (k in min(match_tir):max(match_tir)){
    # Isolate the name of the first sds
    sub_dataset<- sds[k]
    
    # Get the name of the specific SDS
    clip2 <- max(unlist((gregexpr(':', sub_dataset)))) 
    
    # Generate output name for tif
    new_file_name <- strsplit(file_name, '.hdf')
    tif_name <- paste(out_dir, new_file_name, '_', substr(sub_dataset, 
                     (clip2 + 1), 10000),'.tif', sep='')
    sd_name <- paste(new_file_name, substr(sub_dataset, (clip2 + 1), 10000),
                     sep = '_')
    sub_name <- paste(new_file_name, 'ImageData', sep = '_')
    ast_band_name <- gsub(sub_name, '', sd_name)
    
    # Extract specified SDS and export as Geotiff
    gdal_translate(file_name, tif_name, sd_index=k, output_Raster = FALSE)
    
    # Open geotiff and add projection (CRS)
    aster_file <- raster(tif_name, crs = crs_string)
    extent(aster_file) <- raster_dims_90m

    # Convert to large raster layer
    aster_file <- calc(aster_file, fun =function(x){x} )
    
    # Export the raster layer file (Geotiff format) to the output directory
    writeRaster(aster_file, filename = tif_name,  options = 'INTERLEAVE=BAND',
                format = 'GTiff', datatype = 'INT2U', overwrite = TRUE, 
                NAflag = 0)
    # Remove unneccessary variables
    rm(aster_file, sub_dataset, sd_name, sub_name, tif_name, new_file_name)
    }
  }
  #-----------------------------------------------------------------------------
  # Remove unneccessary variables
  rm(ast_band_name, clip2, crs_string, file_name,sds, lr_x_30m, lr_x_90m, 
     lr_y_30m, lr_y_90m, match_swir, match_tir, match_vnir, raster_dims_15m, 
     raster_dims_30m, raster_dims_90m, ul_x_30m, ul_x_90m, ul_y_30m, ul_y_90m,
     x_max_30m, x_max_90m, x_min_30m, x_min_90m, y_max_30m, y_max_90m,y_min_30m,
     y_min_90m)
}
#-------------------------------------------------------------------------------