#-------------------------------------------------------------------------------
# How to Convert ASTER L1T HDF-EOS VNIR/SWIR datasets from Radiance Stored as 
# Digital Numbers to GeoTIFF files of Top of Atmosphere Reflectance

# This tool imports ASTER L1T HDF-EOS files, converts data values from DN to 
# radiance and TOA reflectance, georeferences, and  exports as GeoTIFF files.
#-------------------------------------------------------------------------------
# Author: Cole Krehbiel
# Contact: LPDAAC@usgs.gov  
# Organization: Land Processes Distributed Active Archive Center
# Date last modified: 03-06-2017
#-------------------------------------------------------------------------------
# DESCRIPTION:
# This script demonstrates how to convert ASTER L1T data from Digital Number(DN)
# to radiance (w/m2/sr/µm), and from radiance into Top of Atmosphere (TOA) 
# reflectance. 

# The script uses an ASTER L1T HDF-EOS file (.hdf) as the input and outputs 
# georeferenced tagged image file format (GeoTIFF) files for each of the VNIR 
# and SWIR science datasets contained in the original ASTER L1T file.

# Results from these tutorials are output in UTM with WGS84 datum as GeoTIFFs.
# The output GeoTIFFs for each band include:
#  1. Original_AST_L1T_Filename_ImageDataband#.tif
# Data is At-Sensor radiance stored as DN
# 2. Original_AST_L1T_Filename_ImageDataband#_radiance.tif
# Data is At-Sensor radiance that has been converted out of DN
# 3. Original_AST_L1T_Filename_ImageDataband#_reflectance.tif
# Data is TOA reflectance
# This tool will batch process ASTER L1T files if more than 1 is located in the
# working directory. Output directory will be 'inputfiledirectory'+'/output/'

# This tool was specifically developed for ASTER L1T HDF-EOS files and should 
# only be used for those data products.
-------------------------------------------------------------------------------
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
# 1.	Copy/clone ASTERL1T_DN2REF.R from LP DAAC Recipes & Tutorials Repository
# 2.	Download ASTER L1T data from the LP DAAC to a local directory
# 3.	Start an R session and open ASTERL1T_DN2REF.R
# 4.	Change in_dir <- ' '  to dir where AST L1T HDF files are stored on system
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
in_dir <- '/PATH_TO_INPUT_FILES/'  #***Change
setwd(in_dir)

# Create and set output directory
out_dir <- paste(in_dir, 'output/', sep='')
suppressWarnings(dir.create(out_dir))

# Create a list of ASTER L1T HDF files in the directory
file_list <- list.files(pattern = 'AST_L1T_.*hdf$')
#-------------------------------------------------------------------------------
# Set up calculations
# 1. DN to Radiance (Abrams, 1999)
# Radiance = (DN-1)* Unit Conversion Coefficient

# 2. Radiance to TOA Reflectance
# Reflectance_TOA = (pi*Lrad*d2)/(esuni*COS(z))

# Define the following:
# Unit Conversion Coefficient = ucc
# pi = pi
# Radiance,Lrad  = rad
# esuni = esun 
# z = solare

# Order for ucc (Abrams, 1999) is: Band 1 high, normal, low; Band 2 h, n, l; 
# b3 h, n, l (3N & 3B the same) 
# Construct a dataframe for the UCC values:
bands <- c('1', '2', '3N', '3B', '4', '5', '6', '7', '8', '9')
gain_names <- c('Band', 'High Gain', 'Normal', 'Low Gain 1', 'Low Gain 2')
ucc_vals <- matrix( c(0.676, 1.688, 2.25, 0, 0.708, 1.415, 1.89, 0, 0.423, 
                      0.862, 1.15, 0, 0.423, 0.862, 1.15, 0, 0.1087, 0.2174, 
                      0.2900, 0.2900, 0.0348, 0.0696, 0.0925, 0.4090, 0.0313,
                      0.0625, 0.0830, 0.3900, 0.0299, 0.0597, 0.0795, 0.3320,
                      0.0209,0.0417, 0.0556, 0.2450, 0.0159, 0.0318, 0.0424, 
                      0.2650), nrow = 10, ncol = 4, byrow = TRUE)
ucc <- data.frame( bands, ucc_vals )
names(ucc) <- gain_names

# Remove unneccessary variables
rm(bands,gain_names,ucc_vals)

# Thome et al (B) is used, which uses spectral irradiance values from MODTRAN
# Ordered b1, b2, b3N, b4, b5...b9
irradiance <- c(1848,1549,1114,225.4,86.63,81.85,74.85,66.49,59.85)
#-------------------------------------------------------------------------------
# Next, define functions for calculations
# Write a function to convert degrees to radians
calc_radians <- function(x) {(x * pi) / (180)}
 
# Write a function to calculate the Radiance from DN values
calc_radiance <- function(x){(x - 1) * ucc1}

# Write a function to calculate the TOA Reflectance from Radiance
calc_reflectance <- function(x){
  (pi * x * (earth_sun_dist^2)) / (irradiance1 * sin(pi * sza / 180))}
#-------------------------------------------------------------------------------
for (i in 1:length(file_list)){
  # Maintains the original filename
  file_name <- file_list[i]
  
  # grab DOY from the filename and convert to day of year
  month <- substr(file_name, 12, 13)
  day <- substr(file_name, 14, 15)
  year <- substr(file_name, 16, 19)
  date <- paste(year, month, day, sep = '-')  
  doy <- as.numeric(strftime(date, format = '%j'))
  
  # Remove unneccessary variables
  rm(month, day, year, date)
  
  # need SZA--calculate by grabbing solar elevation info 
  md  <- gdalinfo(file_name)
  sza <- md[grep('SOLARDIRECTION=', md)]
  clip3 <- regexpr(', ', sza) 
  sza <- as.numeric((substr(sza, (clip3 + 2), 10000)))
  
  # Need the gain designation for each band
  gain_01 <- gsub(' ', '', strsplit(md[grep('GAIN.*=01', md)], ',')[[1]][[2]])
  gain_02 <- gsub(' ', '', strsplit(md[grep('GAIN.*=02', md)], ',')[[1]][[2]])
  gain_04 <- gsub(' ', '', strsplit(md[grep('GAIN.*=04', md)], ',')[[1]][[2]])
  gain_05 <- gsub(' ', '', strsplit(md[grep('GAIN.*=05', md)], ',')[[1]][[2]])
  gain_06 <- gsub(' ', '', strsplit(md[grep('GAIN.*=06', md)], ',')[[1]][[2]])
  gain_07 <- gsub(' ', '', strsplit(md[grep('GAIN.*=07', md)], ',')[[1]][[2]])
  gain_08 <- gsub(' ', '', strsplit(md[grep('GAIN.*=08', md)], ',')[[1]][[2]])
  gain_09 <- gsub(' ', '', strsplit(md[grep('GAIN.*=09', md)], ',')[[1]][[2]])
  gain_03b <- gsub(' ', '', strsplit(md[grep('GAIN.*=3B', md)], ',')[[1]][[2]])
  gain_03n <- gsub(' ', '', strsplit(md[grep('GAIN.*=3N', md)], ',')[[1]][[2]])
  
  # Calculate Earth Sun Distance (Achard and D'Souza 1994; Eva and Lambin, 1998)
  earth_sun_dist <- (1 - 0.01672 * cos(calc_radians(0.9856 * (doy - 4))))
  #-----------------------------------------------------------------------------
  # Define CRS
  # Define Upper left and lower right--need for x, y min/max
  # For offset (pixel size / 2), needs to be defined for ASTER pixel 
  # resolutions (15, 30)
  
  # Grab LR and UL values
  lr <- substr(md[grep('LOWERRIGHTM', md)], 15, 50)
  ul <- substr(md[grep('UPPERLEFTM', md)], 14, 50)
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
  
  # Define UTM zone
  utm_row <- grep('UTMZONECODE', md)
  utm_zone <- substr(md[utm_row[1]], 1, 50)
  clip6 <- regexpr('=', utm_zone) 
  utm_zone <- substr(utm_zone, clip6 + 1, 50)
  
  # Configure extent properties (15m VNIR)
  y_min <- min(ul_y, lr_y)
  y_max <- max(ul_y, lr_y)
  x_max <- max(ul_x, lr_x)
  x_min <- min(ul_x, lr_x)
  
  # Configure extent properties (30m SWIR)
  y_min_30m <- min(ul_y_30m, lr_y_30m)
  y_max_30m <- max(ul_y_30m, lr_y_30m)
  x_max_30m <- max(ul_x_30m, lr_x_30m)
  x_min_30m <- min(ul_x_30m, lr_x_30m)
  
  raster_dims_15m <- extent(x_min, x_max, y_min, y_max)
  raster_dims_30m <- extent(x_min_30m, x_max_30m, y_min_30m, y_max_30m)
  
  # Compile Cordinate Reference System string to attach projection information
  crs_string <- paste('+proj=utm +zone=', utm_zone, ' +datum=WGS84 +units=m 
                      +no_defs +ellps=WGS84 +towgs84=0,0,0', sep = '')
  
  # Remove unneccessary variables
  rm(clip4, clip5, clip6, lr, lr_x, lr_y, md, ul, ul_x, ul_y, utm_zone,
     x_min, x_max, y_min, y_max, utm_row)
  
  # Get a list of sds names
  sds <- get_subdatasets(file_name)
  
  # Limit loop to SDS that contain VNIR/SWIR data (9 max)
  match_vnir <- grep('VNIR_Swath', sds)
  match_swir <- grep('SWIR_Swath', sds)
  #-----------------------------------------------------------------------------
  if (length(match_vnir)+length(match_swir) > 1){
    for (k in 1:max(match_vnir, match_swir)){
      # Isolate the name of the first sds
      sub_dataset <- sds[k]
      
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
      gdal_translate(file_name, tif_name, sd_index=k)
      
      aster_file <- raster(tif_name, crs = crs_string)
      
      if (ast_band_name == '1'){
        # Need to know which gain value you use
        if (gain_01 == 'HGH'){
          ucc1 <- ucc[1, 2] 
        }else if(gain_01 == 'NOR'){
          ucc1 <- ucc[1, 3] 
        }else{
          ucc1 <- ucc[1, 4] 
        }
        irradiance1 <- irradiance[1]
        
        # Define Extent
        extent(aster_file) <- raster_dims_15m
    
      }else if (ast_band_name == '2'){
        # Need to know which gain value you use
        if (gain_02 == 'HGH'){
          ucc1 <- ucc[2, 2] 
        }else if(gain_02 == 'NOR'){
          ucc1 <- ucc[2, 3] 
        }else{
          ucc1 <- ucc[2, 4] 
        }
        irradiance1 <- irradiance[2]
        
        # Define Extent
        extent(aster_file) <- raster_dims_15m
    
      }else if (ast_band_name == '3N'){
        # Need to know which gain value you use
        if (gain_03n == 'HGH'){
          ucc1 <- ucc[3, 2] 
        }else if(gain_03n == 'NOR'){
          ucc1 <- ucc[3, 3] 
        }else{
          ucc1 <- ucc[3, 4] 
        }
        irradiance1 <- irradiance[3]
        
        # Define Extent
        extent(aster_file) <- raster_dims_15m

      }else if (ast_band_name == '4'){
        # Need to know which gain value you use
        if (gain_04 == 'HGH'){
          ucc1 <- ucc[5, 2] 
        }else if(gain_04 == 'NOR'){
          ucc1 <- ucc[5, 3] 
        }else if(gain_04 == 'LO1'){
          ucc1 <- ucc[5, 4] 
        }else{
          ucc1 <- ucc[5, 5] 
        }
        irradiance1 <- irradiance[4]
        
        # Define Extent
        extent(aster_file) <- raster_dims_30m

      }else if (ast_band_name == '5'){
        # Need to know which gain value you use
        if (gain_05 == 'HGH'){
          ucc1 <- ucc[6, 2] 
        }else if(gain_05 == 'NOR'){
          ucc1 <- ucc[6, 3] 
        }else if(gain_05 == 'LO1'){
          ucc1 <- ucc[6, 4] 
        }else{
          ucc1 <- ucc[6, 5] 
        }
        irradiance1 <- irradiance[5]
        
        # Define Extent
        extent(aster_file) <- raster_dims_30m
        
      }else if (ast_band_name == '6'){
        # Need to know which gain value you use
        if (gain_06 == 'HGH'){
          ucc1 <- ucc[7, 2] 
        }else if(gain_06 == 'NOR'){
          ucc1 <- ucc[7, 3] 
        }else if(gain_06 == 'LO1'){
          ucc1 <- ucc[7, 4] 
        }else{
          ucc1 <- ucc[7, 5] 
        }
        irradiance1 <- irradiance[6]
        
        # Define Extent
        extent(aster_file) <- raster_dims_30m

      }else if (ast_band_name == '7'){
        # Need to know which gain value you use
        if (gain_07 == 'HGH'){
          ucc1 <- ucc[8, 2] 
        }else if(gain_07 == 'NOR'){
          ucc1 <- ucc[8, 3] 
        }else if(gain_07 == 'LO1'){
          ucc1 <- ucc[8, 4] 
        }else{
          ucc1 <- ucc[8, 5] 
        }
        irradiance1 <- irradiance[7]
        
        # Define Extent
        extent(aster_file) <- raster_dims_30m
        
      }else if (ast_band_name == '8'){
        # Need to know which gain value you use
        if (gain_08 == 'HGH'){
          ucc1 <- ucc[9, 2] 
        }else if(gain_08 == 'NOR'){
          ucc1 <- ucc[9, 3] 
        }else if(gain_08 == 'LO1'){
          ucc1 <- ucc[9, 4] 
        }else{
          ucc1 <- ucc[9, 5] 
        }
        irradiance1 <- irradiance[8]
        
        # Define Extent
        extent(aster_file) <- raster_dims_30m
        
      }else if (ast_band_name == '9'){
        # Need to know which gain value you use
        if (gain_09 == 'HGH'){
          ucc1 <- ucc[10, 2] 
        }else if(gain_09 == 'NOR'){
          ucc1 <- ucc[10, 3] 
        }else if(gain_09 == 'LO1'){
          ucc1 <- ucc[10, 4] 
        }else{
          ucc1 <- ucc[10, 5] 
        }
        irradiance1 <- irradiance[9]
        
        # Define Extent
        extent(aster_file) <- raster_dims_30m
      }
      #-------------------------------------------------------------------------
      # Set up output file names
      ref_out_name <- gsub(paste(ast_band_name, '.tif', sep = ''), 
                           paste(ast_band_name, '_reflectance.tif', sep = ''), 
                           tif_name)
      rad_out_name <- gsub(paste(ast_band_name, '.tif', sep = ''), 
                           paste(ast_band_name, '_radiance.tif', sep = ''),
                           tif_name)
      # Convert DN to large raster layer
      aster_file <- calc(aster_file, fun =function(x){x})
      
      # Export the DN raster layer file (Geotiff format) to the output directory
      writeRaster(aster_file, filename = tif_name,  options = 'INTERLEAVE=BAND',
                  NAflag = 0, format = 'GTiff', datatype = 'INT1U', 
                  overwrite = TRUE)
      
      # Convert from DN to Radiance
      rad <- calc(aster_file, calc_radiance)
      rad[rad == calc_radiance(0)] <- 0
      rm(aster_file)
      # export the raster layer file (Geotiff format) to the output directory
      writeRaster(rad, filename = rad_out_name,  options = 'INTERLEAVE=BAND', 
                  NAflag = 0, format = 'GTiff', datatype = 'FLT8S', 
                  overwrite = TRUE)
      
      # Convert from Radiance to TOA Reflectance
      ref <- calc(rad, calc_reflectance)
      rm(rad)
      # export the raster layer file (Geotiff format) to the output directory
      writeRaster(ref, filename = ref_out_name,  options = 'INTERLEAVE=BAND', 
                  NAflag = 0, format = 'GTiff', datatype = 'FLT8S', 
                  overwrite = TRUE)
      
      
      # Remove unneccessary variables
      rm(ucc1, irradiance1, ref_out_name, rad_out_name, ref, sub_dataset,
         sd_name, sub_name, tif_name, new_file_name)
      #-------------------------------------------------------------------------
    }
  }else{
    print(paste0(file_name,' does not contain any VNIR/SWIR bands to process'))
    print('This is likely an ASTER L1T TIR-only observation')
  }
  # Remove unneccessary variables
rm( crs_string, earth_sun_dist, doy, file_name, gain_01,gain_02, gain_03b, 
    gain_03n, gain_04, gain_05, gain_06, gain_07, gain_08, gain_09, sds, sza, 
    lr_x_30m,lr_y_30m, match_swir, match_vnir, raster_dims_15m, raster_dims_30m,
    ul_x_30m, ul_y_30m, x_max_30m, x_min_30m, y_max_30m, y_min_30m)
}
#-------------------------------------------------------------------------------
# References
# ABRAMS, M., HOOK, S., and RAMACHANDRAN, B., 1999, Aster user handbook,
# Version 2, NASA/Jet Propulsion Laboratory, Pasadena, CA, at 
# https://asterweb.jpl.nasa.gov/content/03_data/04_Documents/
# aster_user_guide_v2.pdf

# ARCHARD, F., AND D'SOUZA, G., 1994, Collection and pre-processing of 
# NOAA-AVHRR 1km resolution data for tropical forest resource assessment. 
# Report EUR 16055, European Commission, Luxembourg, at 
# http://bookshop.europa.eu/en/collection-and-pre-processing-of-noaa-avhrr-1-km
# -resolution-data-for-tropical-forest-resource-assessment-pbCLNA16055/

# EVA, H., AND LAMBIN, E.F., 1998, Burnt area mapping in Central Africa using 
# ATSR data, International Journal of Remote Sensing, v. 19, no. 18, 3473-3497, 
# at http://dx.doi.org/10.1080/014311698213768

# Thome, K.J., Biggar, S.F., and Slater, P.N., 2001, Effects of assumed solar
# spectral irradiance on intercomparisons of earth-observing sensors. In 
# International Symposium on Remote Sensing, International Society for Optics
# and Photonics, pp. 260-269, at http://dx.doi.org/10.1117/12.450668.
#------------------------------------------------------------------------------