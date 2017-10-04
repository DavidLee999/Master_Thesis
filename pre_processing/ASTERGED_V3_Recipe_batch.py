# -*- coding: utf-8 -*-
"""
Author: afriesz
Contact: LPDAAC@ugsg.gov
Organization: Land Processes Distributed Active Archive Center (LP DAAC)
Last modified: 03/22/2017


Purpose:
--------
The Advanced Spaceborne Thermal Emission and Reflection Radiometer (ASTER) 
Global Emissivity Dataset (GED) Version 3 (V3) provides land surface 
temperature and emissivity for ASTER bands 10-14 acquired from 2000-2008. ASTER
GED V3 is a global product made up of 1° x 1° tiles and is distributed in two 
spatial resolutions (100 m and 1 km). ASTER GED V3 files are stored in HDF5 
(.h5) file format.
The ASTER GED V3 product contains a known issue that prevents the user from 
viewing the data in its correct spatial location. When brought into a GIS or 
remote sensing program, the spatial placement of ASTER GED V3 tiles is 
misplaced by a full 180° longitude and without a coordinate reference system. 
This script corrects those issues. This script takes an ASTER GED V3 file (.h5) 
as an input and outputs georeferenced GeoTIFF files for each science dataset 
contained in the file.

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
Version 3 file (.h5). Replace the text inside the quotes (' ') with the 
path and ASTER GED file name. Be aware that paths containing backslashes (\) 
must be preseded by an r outside of the quotes 
(e.g., r'path\to\file\astergedv3.h5').

Related:
--------
ASTERGED_V41_Recipe.py ----- script for georeferencing ASTER GED V4.1
ASTERGED_V41_Recipe.R  ----- script for georeferencing ASTER GED V4.1
ASTERGED_V3_Recipe.R  ----- script for georeferencing ASTER GED V3
"""

#inFileLoc = r'E:\Penghua\data\emissivity_map\AG100.v003.65.-015.0001.h5'

from osgeo import gdal, osr
import h5py
import numpy as np
import glob, os

# Function for writing output GeoTIFFs
def Array2Raster(sdsArray, out_filename, ullat, ullon, cellSize, dtype):
    if len(sdsArray.shape) == 3:
        nband, ncol, nrow = sdsArray.shape
        dtype = dtype
        format = "GTiff"
        driver = gdal.GetDriverByName(format)
        out_ds = driver.Create( out_filename, nrow, ncol, nband, dtype )
        out_ds.SetGeoTransform( (ullon, cellSize, 0, ullat, 0, -cellSize) )
        ''' Specify Coordinate Reference System for the output GeoTiff.
            CRS == WGS84 '''
        srs = osr.SpatialReference()
        srs.SetWellKnownGeogCS('WGS84')
        out_ds.SetProjection(srs.ExportToWkt())
        # Write each band to the GeoTiff
        for n in range(nband):
            out_ds.GetRasterBand(n+1).WriteArray(sdsArray[n,:,:])
        out_ds = None
    else:
        ncol, nrow = sdsArray.shape
        nband = 1
        dtype = dtype
        format = "GTiff"
        driver = gdal.GetDriverByName(format)
        out_ds = driver.Create( out_filename, nrow, ncol, nband, dtype )
        out_ds.SetGeoTransform( (ullon, cellSize, 0, ullat, 0, -cellSize) )
        ''' Specify Coordinate Reference System for the output GeoTiff.
            CRS == WGS84 '''
        srs = osr.SpatialReference()
        srs.SetWellKnownGeogCS('WGS84')
        out_ds.SetProjection(srs.ExportToWkt())
        out_ds.GetRasterBand(1).WriteArray(sdsArray[:,:])
        out_ds = None
        
sourFile = r'E:\Penghua\data\emissivity_map\emissivity_map_Chile\030418575278187'
os.chdir(sourFile)

for file in glob.glob('*.h5'):
    inFileLoc = sourFile + '\\' + file
    
    filename, suffix = os.path.splitext(inFileLoc)
    
    if os.path.exists(filename):
        continue
    
    # Convert '\\' in path to '/'
    inFileLoc = inFileLoc.replace('\\', '/')                            
    ''' execute the appropriate code to convert the h5 files to GeoTIFFs '''
    ''' Create directory to store output GeoTiffs '''
    outFileLoc = inFileLoc[:-3]
    if not os.path.exists(outFileLoc):
        os.makedirs(outFileLoc)
            
    with h5py.File(inFileLoc, 'r') as hf:
        # Access the SDS group within the ASTER GED HDF5 file
        groupList = [k for k, v in hf.items()]
        
        # Get geoLocation data
        def getGeolocation(groupList, hf):
            # Get geolocation group        
            geoLocationGroup = [glgr for glgr in groupList if 'Geolocation' in glgr]
            lat =  [k for k, v in hf[geoLocationGroup[0]].items() if 'lat' in k.lower()]
            lon =  [k for k, v in hf[geoLocationGroup[0]].items() if 'lon' in k.lower()]
            # Get upperleft corner cordinate
            ullat = np.array(hf.get('/{}/{}'.format(geoLocationGroup[0], lat[0])))[0,0]
            ullon = np.array(hf.get('/{}/{}'.format(geoLocationGroup[0], lon[0])))[0,0]
            # Determine cell size
            if hf.filename.split('/')[-1].split('.')[0] == 'AG100':
                cellSize = .001 # 100 meter
            else:
                cellSize = .01  # 1 km
            return(ullat, ullon, cellSize)
            
        # Geotransformation information for outputs    
        ullat, ullon, cellSize = getGeolocation(groupList, hf)
                
        # Loop through the sdsGrouplist
        for g in groupList:
            ''' Determine how many members g contains...get and transpose dataset 
                (ds) for each member '''
            if len(hf[g].items()) > 1:
                if g.lower() == 'geolocation':    # Geolocation datatype is float32
                    memberList = [k for k, v in hf[g].items()]
                    for m in memberList:
                        sdsArray = np.array(hf.get('/{}/{}'.format(g, m)))
                        out_filename = '{}/{}_{}_{}.tif'.format(outFileLoc, outFileLoc.split('/')[-1] , g.replace (' ', '_'), m)
                    
                        Array2Raster(sdsArray, out_filename, ullat, ullon, cellSize, gdal.GDT_Float32)
                
                elif g.lower() == 'temperature':
                    memberList = [k for k, v in hf[g].items()]
                    for m in memberList:
                        if m.lower() == 'mean':
                            sdsArray = np.array(hf.get('/{}/{}'.format(g, m)))
                            out_filename = '{}/{}_{}_{}.tif'.format(outFileLoc, outFileLoc.split('/')[-1] , g.replace (' ', '_'), m)
                        
                            Array2Raster(sdsArray, out_filename, ullat, ullon, cellSize, gdal.GDT_Int32)
                        else:
                            sdsArray = np.array(hf.get('/{}/{}'.format(g, m)))
                            out_filename = '{}/{}_{}_{}.tif'.format(outFileLoc, outFileLoc.split('/')[-1] , g.replace (' ', '_'), m)
                        
                            Array2Raster(sdsArray, out_filename, ullat, ullon, cellSize, gdal.GDT_Int16)
            
                else:
                    memberList = [k for k, v in hf[g].items()]
                    for m in memberList:
                        sdsArray = np.array(hf.get('/{}/{}'.format(g, m)))
                        out_filename = '{}/{}_{}_{}.tif'.format(outFileLoc, outFileLoc.split('/')[-1] , g.replace (' ', '_'), m)
                        
                        Array2Raster(sdsArray, out_filename, ullat, ullon, cellSize, gdal.GDT_Int16)
                
            else:
                memberList = [k for k, v in hf[g].items()]
                m = memberList[0]
                sdsArray = np.array(hf.get('/{}/{}'.format(g, m)))
                out_filename = '{}/{}_{}_{}.tif'.format(outFileLoc, outFileLoc.split('/')[-1] , g.replace (' ', '_'), m)
                
                Array2Raster(sdsArray, out_filename, ullat, ullon, cellSize, gdal.GDT_Int16)
  
    
    
