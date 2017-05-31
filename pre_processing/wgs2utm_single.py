# -*- coding: utf-8 -*-
"""
Created on Wed May 03 11:55:52 2017

@author: li_pe
"""

from osgeo import gdal
from osgeo import osr
import os

inFileLoc = r'E:\Penghua\data\emissivity_map\emissivity_map_etna\merged\emissivity_map_etna.tif'

zone = 33

sourTiff = gdal.Open(inFileLoc)
    
sourseWKT = sourTiff.GetProjection()

utmCoordSystem = osr.SpatialReference()
    
utmCoordSystem.SetWellKnownGeogCS('WGS84')
    
utmCoordSystem.SetUTM(zone, True)
    
targetWKT = utmCoordSystem.ExportToWkt()

reprojectedFile = gdal.AutoCreateWarpedVRT(sourTiff, sourseWKT, targetWKT)
    
reprojected = gdal.ReprojectImage(sourTiff, reprojectedFile, sourseWKT, targetWKT)
    
reprojAttributes = reprojectedFile.GetGeoTransform()
    
driver = gdal.GetDriverByName("GTiff")
    
resultImgPath = os.path.dirname( inFileLoc )

resultImgName = resultImgPath + '\\' + 'emissivity_map_etna_UTM33N.tif'
       
destFile = driver.CreateCopy(resultImgName, reprojectedFile, 0)
