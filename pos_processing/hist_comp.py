# -*- coding: utf-8 -*-
"""
Created on Thu Oct 05 13:58:49 2017

@author: li_pe
"""

from osgeo import gdal, ogr, osr
import numpy as np
import matplotlib.pyplot as plt
import os, sys

def zonal_analysis(rasterFile, shpFile, SST = False):
    
    # Open Data
    raster = gdal.Open(rasterFile)
    shp = ogr.Open(shpFile)
    lyr = shp.GetLayer()
    
    # Get raster georeference info.
    transform = raster.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = transform[1]
    pixelHeight = transform[5]
    
    # Reproject vector geometry to same projection as raster
    sourceSR = lyr.GetSpatialRef()
    targetSR = osr.SpatialReference()
    targetSR.ImportFromWkt(raster.GetProjectionRef())
    coordTrans = osr.CoordinateTransformation(sourceSR, targetSR)
    feat = lyr.GetFeature(0)
    geom = feat.GetGeometryRef()
    geom.Transform(coordTrans)

    # Get extent of feat
    geom = feat.GetGeometryRef()
    if (geom.GetGeometryName() == 'MULTIPOLYGON'):
        count = 0
        pointsX = []; pointsY = []
        for polygon in geom:
            geomInner = geom.GetGeometryRef(count)
            ring = geomInner.GetGeometryRef(0)
            numpoints = ring.GetPointCount()
            for p in range(numpoints):
                    lon, lat, z = ring.GetPoint(p)
                    pointsX.append(lon)
                    pointsY.append(lat)
            count += 1
    elif (geom.GetGeometryName() == 'POLYGON'):
        ring = geom.GetGeometryRef(0)
        numpoints = ring.GetPointCount()
        pointsX = []; pointsY = []
        for p in range(numpoints):
                lon, lat, z = ring.GetPoint(p)
                pointsX.append(lon)
                pointsY.append(lat)

    else:
        sys.exit("ERROR: Geometry needs to be either Polygon or Multipolygon")
    
    xmin = min(pointsX)
    xmax = max(pointsX)
    ymin = min(pointsY)
    ymax = max(pointsY)

    # Specify offset and rows and columns to read
    xoff = int((xmin - xOrigin)/pixelWidth)
    yoff = int((yOrigin - ymax)/pixelWidth)
    xcount = int((xmax - xmin)/pixelWidth) + 1
    ycount = int((ymax - ymin)/pixelWidth) + 1
    
    # Create memory target raster
    target_ds = gdal.GetDriverByName('MEM').Create('', xcount, ycount, 1, gdal.GDT_Byte)
    target_ds.SetGeoTransform((
        xmin, pixelWidth, 0,
        ymax, 0, pixelHeight,
    ))

    # Create for target raster the same projection as for the value raster
    raster_srs = osr.SpatialReference()
    raster_srs.ImportFromWkt(raster.GetProjectionRef())
    target_ds.SetProjection(raster_srs.ExportToWkt())
    
    gdal.RasterizeLayer(target_ds, [1], lyr, burn_values=[1])
    
    # Read raster as arrays
    banddataraster = raster.GetRasterBand(1)
    dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount).astype(np.float)
    
    if (SST == True):
        default_tem = 274.15 * np.ones(dataraster.shape)
        dataraster += default_tem
    
    bandmask = target_ds.GetRasterBand(1)
    datamask = bandmask.ReadAsArray(0, 0, xcount, ycount).astype(np.float)
    
    # Mask zone of raster
    zoneraster = np.ma.masked_array(dataraster, np.logical_not(datamask))
    
    #print np.min(zoneraster), np.max(zoneraster),np.mean(zoneraster), np.std(zoneraster), np.sum(zoneraster)
    #plt.hist(zoneraster.compressed(), bins = 100)
    
    return zoneraster

# Definition des Inputdateinamens
dataDir = r"E:\Penghua\data\Etna\2014.09.16\TET\ac_results_1.10"
rasterFileName = "FBI_TET1_20140916T233303_20140916T233426_L2_C_EL-00408_cobined_MIR_TIR_tem.tif"
rasterFile = os.path.join(dataDir, rasterFileName)

MODISDir = r"E:\Penghua\data\Etna\2014.09.16\SST"
MODISFileName = "A2014259013500.L2_LAC_SST_repro_UTM33N_repro_cut.tif"
MODISFile = os.path.join(MODISDir, MODISFileName)

shpDir = r"E:\Penghua\data\Etna\shapefiles"
shpFileName = ["rect2.shp", "rect4.shp", "rect6.shp", "rect7.shp"]

diffDir = r"E:\Penghua\data\Etna\2014.09.16\TET\ac_results_1.10\compared"
diffFileName = "diff_MIR.tif"
diffFile = os.path.join(diffDir, diffFileName)

# get subarea raster array
TETZoneArray = []
MODISZoneArray = []
differences = []
for i in range(len(shpFileName)):
    shpFile = os.path.join(shpDir, shpFileName[i])
    
    TETzoneraster = zonal_analysis(rasterFile, shpFile)
    MODISzoneraster = zonal_analysis(MODISFile, shpFile, True)
    diffzoneraster = zonal_analysis(diffFile, shpFile)
    
    TETZoneArray.append(TETzoneraster)
    MODISZoneArray.append(MODISzoneraster)
    differences.append(diffzoneraster)
    
# plot
# subplot, 2 rows, 4 columns
for i in range(len(shpFileName)):
    fig, axes = plt.subplots(3, 1)
    axes.flatten()
    
    axes[0].hist(MODISZoneArray[i].compressed(), bins = 100)
    axes[0].set_title("Rect%d. MODIS" %(i + 1))
    
    axes[1].hist(TETZoneArray[i].compressed(), bins = 100)
    axes[1].set_title("Rect%d. TET" %(i + 1))
    
    axes[2].hist(differences[i].compressed(), bins = 100)
    axes[2].set_title("Rect%d. Differeces" %(i + 1))
    
    fig.tight_layout()