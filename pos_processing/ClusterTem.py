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

#below 400K
k1_mir1 = 114191600
k2_mir1 = 3677.661

k1_tir1 = 2105041
k2_tir1 = 1613.220
#above 400k
k1_mir2 = 155890700
k2_mir2 = 3821.000

k1_tir2 = 2125447
k2_tir2 = 1617.380
    
def clusterTem(FID, input_zone_polygon, input_value_raster, NoDataValue = -9999):
    
    # Open data
    raster = gdal.Open(input_value_raster)
#    bg_ras1ter = gdal.Open(bg_value_raster)
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
        datasource = ogr.GetDriverByName( 'MEMORY' ).CreateDataSource('tmp.shp')
        layer = datasource.CreateLayer('layerName', geom_type = ogr.wkbPolygon, srs = raster_srs)    
        layer.CreateFeature(feat)
    
        # Rasterize zone polygon to raster
        gdal.RasterizeLayer(target_ds, [1], layer, burn_values=[1])
        
    else:
        # Rasterize zone polygon to raster
        gdal.RasterizeLayer(target_ds, [1], lyr, burn_values=[1])
        

    # Read raster as arrays
    #banddataraster = raster.GetRasterBand(4)
    # banddataraster.SetNoDataValue( -9999 )
    #dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount).astype(numpy.float)
    #logic = numpy.where( dataraster == NoDataValue ) # no_data value
    
#    MIR_tem_band = raster.GetRasterBand(1)
#    TIR_tem_band = raster.GetRasterBand(2)
    sub_pix_tem_band = raster.GetRasterBand(4)
    sub_pix_area_band = raster.GetRasterBand(5)
#    bg_tem_band = bg_raster.GetRasterBand(1)
    
#    MIR_tem_array = MIR_tem_band.ReadAsArray(xoff, yoff, xcount, ycount).astype(numpy.float)
    sub_pix_tem_array = sub_pix_tem_band.ReadAsArray(xoff, yoff, xcount, ycount).astype(numpy.float)
    sub_pix_area_array = sub_pix_area_band.ReadAsArray(xoff, yoff, xcount, ycount).astype(numpy.float)
#    bg_tem_array = bg_tem_band.ReadAsArray(xoff, yoff, xcount, ycount).astype(numpy.float)
    logic = numpy.where( sub_pix_tem_array == NoDataValue ) # no_data value
    
    #bg_area_array = numpy.ones(MIR_tem_array.shape, numpy.float) - sub_pix_area_array
    
    #logic = numpy.where( dataraster == -9999 ) # no_data value
                              
    bandmask = target_ds.GetRasterBand(1)
    datamask = bandmask.ReadAsArray(0, 0, xcount, ycount).astype(numpy.float)
    datamask[logic] = 0.0
    print datamask
    valid_tem = numpy.ma.masked_array(sub_pix_tem_array, numpy.logical_not(datamask))
    valid_area = numpy.ma.masked_array(sub_pix_area_array, numpy.logical_not(datamask))
    
    rad = valid_tem.copy()
    
    logic1 = numpy.where(rad <= 400)
    logic2 = numpy.where(rad > 400)
    
    rad[logic1] = (k1_tir1 / (numpy.exp(k2_tir1 / valid_tem[logic1]) - 1)) / 1000
    rad[logic2] = (k1_tir2 / (numpy.exp(k2_tir2 / valid_tem[logic2]) - 1)) / 1000
    #rad = (k1_tir / (numpy.exp(k2_tir / valid_tem) - 1)) / 1000   
    rad_weightedAverage = numpy.average(rad, weights = valid_area)
    
    rad400 = (k1_tir1 / (numpy.exp(k2_tir1 / 400) - 1)) / 1000
             
    if rad_weightedAverage <= rad400:
        
        tem = k2_tir1 / math.log(k1_tir1 / (rad_weightedAverage*1000) + 1, math.e)
    
    elif rad_weightedAverage > rad400:
        
        tem = k2_tir2 / math.log(k1_tir2 / (rad_weightedAverage*1000) + 1, math.e)
    #print zone
    #print numpy.mean(zone)
    #tem = k2_tir / math.log(k1_tir / (rad_weightedAverage*1000) + 1, math.e)
    print "feature %d" %FID    
    print tem
    print numpy.average(valid_tem, weights = valid_area)
    print numpy.mean(valid_tem)
    #print tem
    
    return tem
#    return numpy.mean(zoneraster)

def loop_clusterTem(shpfile, rasterfile, noDataValue):
    shp = ogr.Open(shpfile)
    lyr = shp.GetLayer()
    featNum = lyr.GetFeatureCount()
    
    statDict = {}
    for i in range(featNum - 1):
        mean_tem = clusterTem(i, shpfile, rasterfile, noDataValue)
        statDict[i] = mean_tem
               
    return statDict

def centerPos(FID, input_zone_polygon, input_value_raster, input_bg_raster, noDataValue = 0):
    
    # Open data
    raster = gdal.Open(input_value_raster)
    bg_raster = gdal.Open(input_bg_raster)
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
        
#    bg = 0.310369
#    logic = numpy.where( array == 1 )
    
    rasterBand = raster.GetRasterBand(1)
    rasterArray = rasterBand.ReadAsArray(xoff, yoff, xcount, ycount).astype(numpy.float)
    noDataArray = numpy.where(rasterArray == noDataValue)
    
    bgBand = bg_raster.GetRasterBand(1)
    bgArray = bgBand.ReadAsArray(xoff, yoff, xcount, ycount).astype(numpy.float)

    bandmask = target_ds.GetRasterBand(1)
    datamask= bandmask.ReadAsArray(0, 0, xcount, ycount).astype(numpy.float)
    datamask[noDataArray] = 0.0
    logic = numpy.where(datamask == 1.0)
    
    MIR_rad = numpy.ma.masked_array(rasterArray, numpy.logical_not(datamask))
    bg_tem = numpy.ma.masked_array(bgArray, numpy.logical_not(datamask))

    bg_rad = (k1_mir1 / (numpy.exp(k2_mir1 / bg_tem) - 1)) / 1000

    bg_rad_mean = numpy.mean(bg_rad)
    
    sumX = 0
    sumY = 0
    sum_diff = 0
    for i in range( logic[0].shape[0] ):
        
        gray_value = MIR_rad[logic[0][i]][logic[1][i]]
        diff = gray_value - bg_rad_mean
        sum_diff = sum_diff + diff
        sumX = sumX + diff * logic[1][i]
        sumY = sumY + diff * logic[0][i]

    center_x = sumX / sum_diff + xoff
    center_y = sumY / sum_diff + yoff
    
    return [center_y, center_x]

def loop_centerPos(input_zone_polygon, input_MIR_radiance, input_bg_tem, noDataValue = 0):
    
    shp = ogr.Open(input_zone_polygon)
    lyr = shp.GetLayer()
    featNum = lyr.GetFeatureCount()
    
    statDict = {}
    for i in range(featNum - 1):
        pos = centerPos(i, input_zone_polygon, input_MIR_radiance, input_bg_tem, noDataValue)
        statDict[i] = pos
                
    return statDict

       
shpfile = r'E:\Penghua\data\Etna\2014.06.22\TET\ac_results_1.05_new\Mask\sub_tem.shp'

rasterfile = r'E:\Penghua\data\Etna\2014.06.22\TET\ac_results_1.05_new\FBI_TET1_20140622T232052_20140622T232155_L2_002589_WHM_cobined_MIR_TIR_tem.tif'

tet_radiance = r'E:\Penghua\data\Etna\2014.06.22\TET\FBI_TET1_20140622T232052_20140622T232155_L2_002589_WHM_MWIR_near_repro_cut.tif'

bg_tem = r'E:\Penghua\data\Etna\2014.06.22\TET\ac_results_1.05_new\FBI_TET1_20140622T232052_20140622T232155_L2_002589_WHM_cobined_MIR_TIR_Tback.tif'

alpha = r'E:\Penghua\data\georeferenced_TET\Etna\new_selected_data\alpha_channel\FBI_TET1_20140622T232052_20140622T232155_L2_002589_WHM_MWIR_near_repro_alpha.shp'

#bg = zonalStats.zonal_stats(0, alpha, rasterfile, 2, -9999)

a = loop_clusterTem(shpfile, rasterfile, 0)
b = loop_centerPos(shpfile, tet_radiance, bg_tem)