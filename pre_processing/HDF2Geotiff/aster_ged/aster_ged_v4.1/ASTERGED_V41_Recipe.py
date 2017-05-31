# -*- coding: utf-8 -*-
"""
Author: afriesz
Contact: LPDAAC@ugsg.gov
Organization: Land Processes Distributed Active Archive Center (LP DAAC)
Last modified: 03/22/2017

Purpose:
--------
The Advanced Spaceborne Thermal Emission and Reflection Radiometer (ASTER) 
Global Emissivity Dataset (GED) Version 4.1 (V4.1) provides monthly emissivity 
for ASTER bands 10-14 from 2000-2015. ASTER GED V4.1 is a global product with a
0.05° spatial resolution. ASTER GED V4.1 files are stored in HDF5 (.h5) file 
format. The ASTER GED V4.1 product contains a known issue that prevents the 
user from viewing the data in its correct spatial orientation. When brought 
into a GIS or remote sensing program, the global ASTER GED V4.1 image is 
displayed without a coordinate reference system. This script corrects the 
issue. This script takes an ASTER GED V4.1 file (.h5) as an input and outputs 
georeferenced GeoTIFF files for each science dataset contained in the file.

Prerequisites:
--------------
This script has been tested with the specifications listed below.
    - Windows 7 64-bit OS 
    - Python 3.4 or 2.7
    - Packages Installed
        - h5py 2.6.0
        - numpy 1.11.0
        - osgeo with gdal and osr 1.11.1
        
Usage:
------
The 'inFileLoc' variable is used to specify the location of your ASTER GED 
Version 4.1 file (.h5). Replace the text inside the quotes (' ') with the 
path and ASTER GED file name. Be aware that paths contain backslashes (\) must
be preceded by an r outside of the quotes(e.g., r'path\to\file\astergedv4.h5').

Related:
--------
ASTERGED_V3_Recipe.py ----- script for georeferencing ASTER GED V3
ASTERGED_V41_Recipe.R  ----- script for georeferencing ASTER GED V4.1
ASTERGED_V3_Recipe.R  ----- script for georeferencing ASTER GED V3
"""
inFileLoc = 'PATH_TO_INPUT_FILE/INPUT_FILE'

from osgeo import gdal, osr
import h5py
import numpy as np
import os

# Convert '\\' in path to '/'
inFileLoc = inFileLoc.replace('\\', '/')
''' Create directory to store output GeoTIFFs '''
outFileLoc = inFileLoc[:-3]
if not os.path.exists(outFileLoc):
    os.makedirs(outFileLoc)

# For input HDF5 files
if inFileLoc[-2:] == 'h5':    
    with h5py.File(inFileLoc, 'r') as hf:
        # Access the SDS group within the ASTER GED HDF5 file
        sdsGroup = hf.get('SDS') # SDS is the name of the group
        # Get list of dataset key names    
        dsList = [k for k, v in sdsGroup.items()]
        for ds in dsList:
        #for ds in range(len(dsList)-2):
            # Get and transpose the dataset data
            dsArray = np.array(hf.get('/SDS/{}'.format(ds)))
            # Specify an output filename...product name + SDS Name
            out_filename = '{}/{}_{}.tif'.format(outFileLoc, outFileLoc.split('/')[-1] , ds)
            ''' Emissivity and Emissivity Uncertainty both contain 5 bands. 
                This results in a 3 dimensional array that will be output as a
                5 band GeoTiff. '''
            if len(dsArray.shape) == 3:
                ''' Output 3D array as a multi-band GeoTIFF '''
                # Get the number of columns, rows, and bands
                nband, ncol, nrow = dsArray.shape
                # Emissivity and Emissivity Uncertainty is uint8
                dtype = gdal.GDT_Byte
                format = "GTiff"
                driver = gdal.GetDriverByName(format)
                out_ds = driver.Create( out_filename, nrow, ncol, nband, dtype )
                out_ds.SetGeoTransform( (-180.00, 0.05, 0, 90.00, 0, -0.05) )
                ''' Specify Coordinate Reference System for the output GeoTIFF.
                    CRS == WGS84 '''
                srs = osr.SpatialReference()
                srs.SetWellKnownGeogCS('WGS84')
                out_ds.SetProjection(srs.ExportToWkt())
                # Write each band to the GeoTiff
                for n in range(nband):
                    out_ds.GetRasterBand(n+1).WriteArray(dsArray[n,:,:])
                out_ds = None
            else:   # Remaining SDS' are 2D
                ncol, nrow = dsArray.shape
                nband = 1
                ''' The NDVI SDS datatype is uint16. It's the only dataset in
                    the product that is '''
                if ds == 'NDVI':
                    dtype = gdal.GDT_UInt16
                else:
                    dtype = gdal.GDT_Byte
                format = "GTiff"
                driver = gdal.GetDriverByName(format)
                out_ds = driver.Create( out_filename, nrow, ncol, nband, dtype )
                out_ds.GetRasterBand(1).WriteArray(dsArray)
                out_ds.SetGeoTransform( (-180.00, 0.05, 0, 90.00, 0, -0.05) )
                ''' Specify Coordinate Reference System for the output GeoTIFF.
                    CRS == WGS84 '''
                srs = osr.SpatialReference()
                srs.SetWellKnownGeogCS('WGS84')
                out_ds.SetProjection(srs.ExportToWkt())
                out_ds = None