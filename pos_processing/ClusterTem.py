# -*- coding: utf-8 -*-
"""
Created on Fri Aug 11 10:32:06 2017

@author: li_pe
"""

import gdal, ogr, osr, numpy, math
import sys
import matplotlib.pyplot as plt
import os, shutil
import zonalStats

k1_mir = 155890700
k2_mir = 3821.000

k1_tir = 2105042
k2_tir = 1613.220
    
def clusterTem(FID, input_zone_polygon, input_value_raster, NoDataValue = -9999):
    
    # Open data
    raster = gdal.Open(input_value_raster)
    shp = ogr.Open(input_zone_polygon)
    lyr = shp.GetLayer()

    # Get raster georeference info
    transform = raster.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = int(transform[1])
    pixelHeight = int(transform[5])

    # Reproject vector geometry to same projection as raster
    sourceSR = lyr.GetSpatialRef()
    targetSR = osr.SpatialReference()
    targetSR.ImportFromWkt(raster.GetProjectionRef())
    coordTrans = osr.CoordinateTransformation(sourceSR,targetSR)
    feat = lyr.GetFeature(FID)
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
    xcount = int((xmax - xmin)/pixelWidth)
    ycount = int((ymax - ymin)/pixelWidth)
    
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
    
    # create new layer for each feature
    if lyr.GetFeatureCount() > 1:
#        driver = ogr.GetDriverByName('ESRI Shapefile')
#        filename = os.path.join(os.path.split(input_zone_polygon)[0], r'temp\temp%d.shp' %FID)
#        srs = osr.SpatialReference()
#        srs.ImportFromWkt( raster.GetProjectionRef() )
#        datasource = driver.CreateDataSource(filename)
        datasource = ogr.GetDriverByName( 'MEMORY' ).CreateDataSource( 'tmp.shp' )
        layer = datasource.CreateLayer('layerName', geom_type = ogr.wkbPolygon, srs = raster_srs)    
        layer.CreateFeature(feat)
    
        # Rasterize zone polygon to raster
        gdal.RasterizeLayer(target_ds, [1], layer, burn_values=[1])
        
    else:
        # Rasterize zone polygon to raster
        gdal.RasterizeLayer(target_ds, [1], lyr, burn_values=[1])
        

    # Read raster as arrays
    banddataraster = raster.GetRasterBand(4)
    # banddataraster.SetNoDataValue( -9999 )
    dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount).astype(numpy.float)
    logic = numpy.where( dataraster == NoDataValue ) # no_data value
    
    MIR_tem_band = raster.GetRasterBand(1)
#    TIR_tem_band = raster.GetRasterBand(2)
    sub_pix_tem_band = raster.GetRasterBand(4)
    sub_pix_area_band = raster.GetRasterBand(5)

    MIR_tem_array = MIR_tem_band.ReadAsArray(xoff, yoff, xcount, ycount).astype(numpy.float)
    sub_pix_tem_array = sub_pix_tem_band.ReadAsArray(xoff, yoff, xcount, ycount).astype(numpy.float)
    sub_pix_area_array = sub_pix_area_band.ReadAsArray(xoff, yoff, xcount, ycount).astype(numpy.float)
    logic = numpy.where( sub_pix_tem_array == NoDataValue ) # no_data value
    
    #bg_area_array = numpy.ones(MIR_tem_array.shape, numpy.float) - sub_pix_area_array
    
    #logic = numpy.where( dataraster == -9999 ) # no_data value
                              
    bandmask = target_ds.GetRasterBand(1)
    datamask = bandmask.ReadAsArray(0, 0, xcount, ycount).astype(numpy.float)
    datamask[logic] = 0.0
            
    valid_tem = numpy.ma.masked_array(sub_pix_tem_array, numpy.logical_not(datamask))
    valid_area = numpy.ma.masked_array(sub_pix_area_array, numpy.logical_not(datamask))
    rad = (k1_tir / (numpy.exp(k2_tir / valid_tem) - 1)) / 1000   
    rad_weightedAverage = numpy.average(rad, weights = valid_area)
    #print zone
    #print numpy.mean(zone)
    tem = k2_tir / math.log(k1_tir/(rad_weightedAverage*1000) + 1, math.e)
    print "feature %d" %FID    
    print tem
    print numpy.average(valid_tem, weights = valid_area)
    print numpy.mean(valid_tem)
    #print tem
    
#    for i in range(1): #in range(shift[0].shape[0]):
#
#        loc = [xoff + shift[0][i], yoff + shift[1][i]]
#        
#        offset = [int(loc[0] - 10), int(loc[1] - 10)]
#        
#        bg_mask = banddataraster.ReadAsArray(offset[0], offset[1], 22, 22)
#        bg_mir = MIR_tem_band.ReadAsArray(offset[0], offset[1], 22, 22)
#        bg_tir = TIR_tem_band.ReadAsArray(offset[0], offset[1], 22, 22)
#        
#        logic1 = numpy.where(bg_tir > 265)
#        logic2 = numpy.where(bg_mir - bg_tir < 30)
#        
#        bg_area = bg_tir[logic1 and logic2]
#        
#        bg_mean = numpy.mean(bg_area)
#        bg_stddev = numpy.std(bg_area)
#        
#        bg_tem = bg_mean - bg_stddev
#    
#    
#    sub_tem = sub_pix_tem_array[shift[0][0]][shift[1][0]]
#    
#    sub_area = sub_pix_area_array[shift[0][0]][shift[1][0]]
#    
#    bg_rad = (k1_tir / (numpy.exp(k2_tir / bg_tem) - 1)) / 1000
#    
#    sub_rad = (k1_tir / (numpy.exp(k2_tir / sub_tem) - 1)) / 1000
#              
#    rad = sub_area * sub_rad + (1 - sub_area) * bg_rad
#                   
#    tem = k2_tir / math.log(k1_tir/(rad*1000) + 1, math.e)    
#    print tem
#    print MIR_tem_array[shift[0][0]][shift[1][0]]
    
    # Mask zone of raster
    zoneraster = numpy.ma.masked_array(dataraster, numpy.logical_not(datamask))
 
    MIR_tem = numpy.ma.masked_array(MIR_tem_array, numpy.logical_not(datamask))
    sub_pix_tem = numpy.ma.masked_array(sub_pix_tem_array, numpy.logical_not(datamask))
    sub_pix_area = numpy.ma.masked_array(sub_pix_area_array, numpy.logical_not(datamask))
    #bg_area = numpy.ma.masked_array(bg_area_array, numpy.logical_not(datamask))
    
#    bg_area = numpy.ones(MIR_tem_array.shape, numpy.float) - sub_pix_area
#    
#    tem_avg = numpy.multiply(bg_area, bg) + numpy.multiply(sub_pix_tem, sub_pix_area)
    
    # Calculate statistics of zonal raster
    return numpy.mean(zoneraster)

def loop_clusterTem(shpfile, rasterfile, noDataValue):
    shp = ogr.Open(shpfile)
    lyr = shp.GetLayer()
    featNum = lyr.GetFeatureCount()
    
    for i in range(featNum):
        clusterTem(i, shpfile, rasterfile, noDataValue)
        
shpfile = r'E:\Penghua\data\Etna\2014.06.22\TET\ac_results_1.05_new\Mask\sub_tem.shp'

rasterfile = r'E:\Penghua\data\Etna\2014.06.22\TET\ac_results_1.05_new\FBI_TET1_20140622T232052_20140622T232155_L2_002589_WHM_cobined_MIR_TIR_tem.tif'

tet_radiance = r'E:\Penghua\data\Etna\2014.06.22\TET\FBI_TET1_20140622T232052_20140622T232155_L2_002589_WHM_MWIR_near_repro_cut.tif'

alpha = r'E:\Penghua\data\georeferenced_TET\Etna\new_selected_data\alpha_channel\FBI_TET1_20140622T232052_20140622T232155_L2_002589_WHM_MWIR_near_repro_alpha.shp'

#bg = zonalStats.zonal_stats(0, alpha, rasterfile, 2, -9999)

a = loop_clusterTem(shpfile, rasterfile, 0)