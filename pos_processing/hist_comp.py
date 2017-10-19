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


scale_factor = '1.00'
dataDir = r'E:\Penghua\data\Etna'

shpDir = r"E:\Penghua\data\Etna\shapefiles"
shpFileName = ["rect2.shp", "rect4.shp", "rect6.shp", "rect7.shp"]

shpfile = os.path.join(shpDir, shpFileName[2])

TET_tem = []

os.chdir(dataDir)
for folder in os.listdir(dataDir):
    if '2017' not in folder and '0' in folder:
        absfolder = os.path.abspath(folder)
        datafolder = os.path.join(absfolder, r'TET\ac_results_%s' %scale_factor)
        
        for files in os.listdir(datafolder):
            if 'tem' in files and files.endswith('.tif'):
                TET_tem.append(os.path.join(datafolder, files))

TETrect = []
for i in range(len(TET_tem)):
    rasterfile = TET_tem[i]
    
    TETzoneraster = zonal_analysis(rasterfile, shpfile)
    
    TETrect.append(TETzoneraster)

for i in range(len(TET_tem)):
    fig, axes = plt.subplots()
    axes.hist(TETrect[i].compressed(), bins = 100)
    axes.axvline(np.mean(TETrect[i]), color = 'red', linewidth = 2)
    axes.axvline(np.mean(TETrect[i]) - np.std(TETrect[i]), color = 'red', linestyle = 'dashed', linewidth = 1)
    axes.axvline(np.mean(TETrect[i]) + np.std(TETrect[i]), color = 'red', linestyle = 'dashed', linewidth = 1)
    fig.tight_layout()
    plt.show()
    
    
    


# Definition des Inputdateinamens
# scene1
#dataDir = r"E:\Penghua\data\Etna\2014.09.16\TET\ac_results_1.00"
#rasterFileName = "FBI_TET1_20140916T233303_20140916T233426_L2_C_EL-00408_cobined_MIR_TIR_tem.tif"
#rasterFile = os.path.join(dataDir, rasterFileName)
#
#MODISDir = r"E:\Penghua\data\Etna\2014.09.16\SST"
#MODISFileName = "A2014259013500.L2_LAC_SST_repro_UTM33N_repro_cut.tif"
#MODISFile = os.path.join(MODISDir, MODISFileName)
#
#shpDir = r"E:\Penghua\data\Etna\shapefiles"
#shpFileName = ["rect2.shp", "rect4.shp", "rect6.shp", "rect7.shp"]
#
#diffDir = r"E:\Penghua\data\Etna\2014.09.16\TET\ac_results_1.00\compared"
#diffFileName = "diff_MIR.tif"
#diffFile = os.path.join(diffDir, diffFileName)

#scene2
#dataDir = r"E:\Penghua\data\Etna\2014.06.22\TET\ac_results_1.10"
#rasterFileName = "FBI_TET1_20140622T232052_20140622T232155_L2_002589_WHM_cobined_MIR_TIR_tem.tif"
#rasterFile = os.path.join(dataDir, rasterFileName)
#
#MODISDir = r"E:\Penghua\data\Etna\2014.06.22\SST"
#MODISFileName = "A2014173003000.L2_LAC_SST_repro_UTM33N_repro_cut.tif"
#MODISFile = os.path.join(MODISDir, MODISFileName)
#
#shpDir = r"E:\Penghua\data\Etna\shapefiles"
#shpFileName = ["rect2.shp", "rect4.shp", "rect6.shp", "rect7.shp"]
#
#diffDir = r"E:\Penghua\data\Etna\2014.06.22\TET\ac_results_1.10\compared"
#diffFileName = "diff_MIR.tif"
#diffFile = os.path.join(diffDir, diffFileName)
#
#
## get subarea raster array
#TETZoneArray = []
#MODISZoneArray = []
#differences = []
#for i in range(len(shpFileName)):
#    shpFile = os.path.join(shpDir, shpFileName[i])
#    
#    TETzoneraster = zonal_analysis(rasterFile, shpFile)
#    MODISzoneraster = zonal_analysis(MODISFile, shpFile, True)
#    diffzoneraster = zonal_analysis(diffFile, shpFile)
#    
#    TETZoneArray.append(TETzoneraster)
#    MODISZoneArray.append(MODISzoneraster)
#    differences.append(diffzoneraster)
    



# plot
# subplot, 3 rows, 1 columns
#for i in range(len(shpFileName)):
#    fig, axes = plt.subplots(3, 1)
#    axes.flatten()
#    
#    axes[0].hist(MODISZoneArray[i].compressed(), bins = 100)
#    axes[0].set_title("Rect%d. MODIS" %(i + 1))
#    axes[0].set_xlabel('temperatures', fontsize = 9)
#    axes[0].grid()
#    
#    axes[1].hist(TETZoneArray[i].compressed(), bins = 100)
#    axes[1].set_title("Rect%d. TET" %(i + 1))
#    axes[1].set_xlabel('temperatures', fontsize = 9)
#    axes[1].grid()
#    
#    axes[2].hist(differences[i].compressed(), bins = 100)
#    axes[2].set_title("Rect%d. Differeces" %(i + 1))
#    axes[2].set_xlabel('temperature difference', fontsize = 9)
#    axes[2].grid()
#    
#    fig.tight_layout()
#    #fig.savefig(os.path.join(r'E:\Penghua\results\hist_analysis\sc1.10', r'rect%d.png' %(i + 1)), dpi=500)
#    plt.show()
    
#TET = []
#MODIS = []
#Diff = []
#for i in range(len(TETZoneArray)):
#    TET.extend(TETZoneArray[i].compressed())
#    MODIS.extend(MODISZoneArray[i].compressed())
#    Diff.extend(differences[i].compressed())
#
#fig2, axes2 = plt.subplots(3, 1)
#axes2.flatten()
#
#axes2[0].hist(MODIS, bins = 100, stacked = True)
#axes2[0].set_title('MODIS')
#axes2[0].set_xlabel('temperatures', fontsize = 9)
#axes2[0].set_yticks(range(0, 1000, 300))
#axes2[0].set_yticklabels(range(0, 1000, 300), fontsize = 6)
#axes2[0].grid()
#
#axes2[1].hist(TET, bins = 100, stacked = True)
#axes2[1].set_title('TET')
#axes2[1].set_xlabel('temperatures', fontsize = 9)
#axes2[1].set_yticks(range(0, 550, 200))
#axes2[1].set_yticklabels(range(0, 550, 200), fontsize = 6)
#axes2[1].grid()
#
#axes2[2].hist(Diff, bins = 100, stacked = True)
#axes2[2].set_title('Differences')
#axes2[2].set_xlabel('temperature differences', fontsize = 9)
#axes2[2].set_yticks(range(0, 1000, 300))
#axes2[2].set_yticklabels(range(0, 1000, 300), fontsize = 6)
#axes2[2].grid()
#
#fig2.tight_layout()
##fig2.savefig(os.path.join(r'E:\Penghua\results\hist_analysis\2014.06.22\sc1.10', r'rect_all.png'), dpi=500)
#plt.show()