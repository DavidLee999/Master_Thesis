# -*- coding: utf-8 -*-
"""
Created on Wed Jul 05 11:20:07 2017

@author: li_pe
"""

import gdal, ogr, osr, numpy
import sys
import matplotlib.pyplot as plt
import os, shutil
import xlrd, xlwt

def zonal_stats(FID, input_zone_polygon, input_value_raster, band, noDataValue):
    
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
    banddataraster = raster.GetRasterBand(band)
    # banddataraster.SetNoDataValue( -9999 )
    dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount).astype(numpy.float)
    logic = numpy.where( dataraster == noDataValue) # no_data value
    
    percent = 1 - float(len(logic[0])) / dataraster.size
    if percent < 0.4:
        print 'In the scene %s within the shapefile %s, the valid pixels are too few to do a average. (percentage: %f)' %(input_value_raster, input_zone_polygon, percent)
        return 0.0
    
    bandmask = target_ds.GetRasterBand(1)
    datamask = bandmask.ReadAsArray(0, 0, xcount, ycount).astype(numpy.float)
    datamask[logic] = 0.0
            
    # Mask zone of raster
    zoneraster = numpy.ma.masked_array(dataraster, numpy.logical_not(datamask))
    
    # Calculate statistics of zonal raster
    return numpy.mean(zoneraster)

def loop_zonal_stats(input_zone_polygon, input_value_raster, band, noDataValue):

    shp = ogr.Open(input_zone_polygon)
    lyr = shp.GetLayer()
    featList = range(lyr.GetFeatureCount()) # -1 for multiple features
    statDict = {}

    for FID in featList:
        #feat = lyr.GetFeature(FID)
        meanValue = zonal_stats(FID, input_zone_polygon, input_value_raster, band, noDataValue)
        statDict[FID] = meanValue
    return statDict

def main(input_zone_polygon, input_value_raster, band, noDataValue):
    return loop_zonal_stats(input_zone_polygon, input_value_raster, band, noDataValue)

def centerPos( FID, input_zone_polygon, input_value_raster ):
    
    raster = gdal.Open( input_value_raster )
    shp = ogr.Open( input_zone_polygon )
    lyr = shp.GetLayer()
    feat = lyr.GetFeature(FID)
    
    transform = raster.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = int(transform[1])
    pixelHeight = int(transform[5])
    
    target_ds = gdal.GetDriverByName('MEM').Create( '', raster.RasterXSize, raster.RasterYSize, 1, gdal.GDT_Byte )
    target_ds.SetGeoTransform(( xOrigin, pixelWidth, 0, yOrigin, 0, pixelHeight ))
        
    raster_srs = osr.SpatialReference()
    raster_srs.ImportFromWkt( raster.GetProjectionRef() )
    target_ds.SetProjection( raster_srs.ExportToWkt() )
    
    if lyr.GetFeatureCount() > 1:
        
#        driver = ogr.GetDriverByName( 'ESRI Shapefile' )
#        filename = os.path.join( os.path.split(input_zone_polygon)[0], r'temp\temp%d.shp' %FID )
#        datasource = driver.CreateDataSource( filename )
        d = ogr.GetDriverByName('MEMORY').CreateDataSource( 'tmp.shp' )
        layer = d.CreateLayer( 'layerName',geom_type = ogr.wkbPolygon, srs = raster_srs )    
        layer.CreateFeature(feat)
    
        # Rasterize zone polygon to raster
        gdal.RasterizeLayer( target_ds, [1], layer, burn_values=[1] )
        
    else:
        # Rasterize zone polygon to raster
        gdal.RasterizeLayer( target_ds, [1], lyr, burn_values=[1] )
        
    bandmask = target_ds.GetRasterBand(1)
    array = bandmask.ReadAsArray()
    bg = 0.310369
    logic = numpy.where( array == 1 )
    
    rasterBand = raster.GetRasterBand(1)
    rasterArray = rasterBand.ReadAsArray()
    
    sumX = 0
    sumY = 0
    sum_diff = 0
    for i in range( logic[0].shape[0] ):
        
        gray_value = rasterArray[logic[0][i]][logic[1][i]]
        diff = gray_value - bg
        print diff
        print logic[1][i]
        sum_diff = sum_diff + diff
        sumX = sumX + diff * logic[1][i]
        sumY = sumY + diff * logic[0][i]
    
    center_x = sumX / sum_diff
    center_y = sumY / sum_diff
    
    return[center_y, center_x]
    
    
    
    
        
    

#if __name__ == "__main__":
#
#    #
#    # Returns for each feature a dictionary item (FID) with the statistical values in the following order: Average, Mean, Medain, Standard Deviation, Variance
#    #
#    # example run : $ python grid.py <full-path><output-shapefile-name>.shp xmin xmax ymin ymax gridHeight gridWidth
#    #
#
#    if len( sys.argv ) != 3:
#        print "[ ERROR ] you must supply two arguments: input-zone-shapefile-name.shp input-value-raster-name.tif "
#        sys.exit( 1 )
#    print 'Returns for each feature a dictionary item (FID) with the statistical values in the following order: Average, Mean, Medain, Standard Deviation, Variance'
#    print main( sys.argv[1], sys.argv[2] )

#shpfile = r'E:\Penghua\data\Etna\2014.06.22\TET\ac_results_1.05_new\Mask\sub_tem.shp'
#
#rasterfile = r'E:\Penghua\data\Etna\2014.06.22\TET\ac_results_1.05_new\FBI_TET1_20140622T232052_20140622T232155_L2_002589_WHM_cobined_MIR_TIR_tem.tif'
#
#tet_radiance = r'E:\Penghua\data\Etna\2014.06.22\TET\FBI_TET1_20140622T232052_20140622T232155_L2_002589_WHM_MWIR_near_repro_cut.tif'

#if os.path.exists(os.path.join(os.path.split(shpfile)[0], 'temp')) == False:
#    
#    os.mkdir(os.path.join(os.path.split(shpfile)[0], 'temp'))
   
#sta = main(shpfile, rasterfile, 4, 0)
#l = centerPos(0, shpfile, tet_radiance)

#shutil.rmtree(os.path.join(os.path.split(shpfile)[0], 'temp'))


shpFile = r'E:\Penghua\data\Lybien-1\shapefiles'

shp = []

os.chdir(shpFile)

for files in os.listdir(shpFile):
    
    if files.endswith('.shp') and 'rect' in files:
        
        shp.append(os.path.abspath(files)) 

sourFile = r'E:\Penghua\data\Lybien-1' #\self_test

os.chdir(sourFile)


#filename = xlwt.Workbook()
#
#sheet1 = filename.add_sheet(u'MIR')
#
#sheet2 = filename.add_sheet(u'TIR')
#
#sheet1.write(1, 0, u'rect2')
#
#sheet1.write(2, 0, u'rect4')
#
#sheet1.write(3, 0, u'rect6')
#            
#sheet2.write(1, 0, u'rect2')
#
#sheet2.write(2, 0, u'rect4')
#
#sheet2.write(3, 0, u'rect6')
#
#count = 1

#time = ['2014.06.22', '2014.09.16', '2015.12.25', '2016.04.12', '2016.11.01']
#
#sc_mir2 = []
#sc_tir2 = []
#
#sc_mir1 = []
#sc_tir1 = []
#
#for files in os.listdir(sourFile):
#    
#    if '0' in files:
#        
#        folder = os.path.join(os.path.abspath(files), r'TET')
#        
#        for fil in os.listdir(folder):
#            
#            if '9.1' in fil:
#                
#                ac_results = os.path.join(folder, fil)
#                
#                if len( os.listdir(ac_results) ) != 0 :
#                    
#                    for fi in os.listdir(ac_results):
#                        
#                        if fi.endswith('.tif') and 'MIR_only' in fi:
#                            
#                            TET_tem_MIR = os.path.join(ac_results, fi)
#                            
#                        if fi.endswith('.tif') and 'TIR_only' in fi:
#
#                            TET_tem_TIR = os.path.join(ac_results, fi)
#                    
#                    sc_mir2.append((main(shp[1], TET_tem_MIR)[0]+main(shp[3], TET_tem_MIR)[0]+main(shp[4], TET_tem_MIR)[0]) / 3.0)
#                    
#                    sc_tir2.append((main(shp[1], TET_tem_TIR)[0]+main(shp[3], TET_tem_TIR)[0]+main(shp[4], TET_tem_TIR)[0]) / 3.0)
#                    
#            if files in time and '1.00' in fil:
#                
#                #time.append(files)
#                
#                ac_results = os.path.join(folder, fil)
#                
#                if len( os.listdir(ac_results) ) != 0 :
#                    
#                    for fi in os.listdir(ac_results):
#                        
#                        if fi.endswith('.tif') and 'MIR_only' in fi:
#                    
#                            TET_tem_MIR = os.path.join(ac_results, fi)
#                            
#                        if fi.endswith('.tif') and 'TIR_only' in fi:
#                    
#                            TET_tem_TIR = os.path.join(ac_results, fi)
#                    
#                    sc_mir1.append((main(shp[1], TET_tem_MIR)[0]+main(shp[3], TET_tem_MIR)[0]+main(shp[4], TET_tem_MIR)[0]) / 3.0)
#                    
#                    sc_tir1.append((main(shp[1], TET_tem_TIR)[0]+main(shp[3], TET_tem_TIR)[0]+main(shp[4], TET_tem_TIR)[0]) / 3.0)


scale_factor = ['1.00', '1.05', '1.10', '1.15', '1.20']

#scale_factor = ['0.50', '0.55', '0.60', '0.65', '0.70', '0.75', '0.80', '0.85', '0.90']

sc_mir = [[], [], [], [], []]#, [], [], [], []]
sc_tir = [[], [], [], [], []]#, [], [], [], []]
time = []

for i in range(len(scale_factor)):
    
    #print scale_factor[i]
    
    
    for files in os.listdir(sourFile):
        
        if ('0' in files) and ('2017' in files): #files in time: ('2017' not in files)
            
            
#            print files
            
#            sheet1.write(0, count, files)
#            
#            sheet2.write(0, count, files)
            
            ac_folder = os.path.join(os.path.abspath(files), r'TET\ac_results_%s\compared' %scale_factor[i]) #\compared _9.1
            
            
            if os.path.exists(os.path.join(os.path.abspath(files), r'TET\ac_results_%s\compared' %scale_factor[i])) == True:
            
                ac_results = os.path.join(os.path.abspath(files), r'TET\ac_results_%s\compared' %scale_factor[i])
                
                if i == 0:
                
                    time.append(files)
                    
                
                if os.path.exists(os.path.join(ac_results, 'temp')) == False:
    
                    os.mkdir(os.path.join(ac_results, 'temp'))
            
                for fil in os.listdir(ac_results):
                
                    if  fil.endswith('.tif') and 'MIR' in fil: #fil.endswith('.tif') and
                    
                        TET_tem_MIR = os.path.join(ac_results, fil)
#                        print TET_tem_MIR
                    if  fil.endswith('.tif') and 'TIR' in fil:
                    
                        TET_tem_TIR = os.path.join(ac_results, fil)
#                        print TET_tem_TIR


#            MIR_rect2 = main(shp[1], TET_tem_MIR)
#            
#            MIR_rect4 = main(shp[3], TET_tem_MIR)
#            
#            MIR_rect6 = main(shp[4], TET_tem_MIR)
#            
#            TIR_rect2 = main(shp[1], TET_tem_MIR)
#            
#            TIR_rect4 = main(shp[3], TET_tem_MIR)
#            
#            TIR_rect6 = main(shp[4], TET_tem_MIR)
#            
#            
#            sheet1.write(1, count, float(MIR_rect2[0]))
#            sheet1.write(2, count, float(MIR_rect4[0]))
#            sheet1.write(3, count, float(MIR_rect6[0]))
#            
#            sheet2.write(1, count, float(TIR_rect2[0]))
#            sheet2.write(2, count, float(TIR_rect4[0]))
#            sheet2.write(3, count, float(TIR_rect6[0]))
#            
#            if os.path.exists(os.path.join(ac_results, 'temp')) == True:
#            
#                shutil.rmtree(os.path.join(ac_results, 'temp'))
##            
#            count = count + 1                         
                

#                if files == '2016.08.14':
    
                calcRes = []
                
                calcRes.append((main(shp[0], TET_tem_MIR, 1, 0.0)[0]))
                    
                calcRes.append((main(shp[1], TET_tem_MIR, 1, 0.0)[0]))
                    
                calcRes.append((main(shp[2], TET_tem_MIR, 1, 0.0)[0]))
                
                calcRes.append((main(shp[3], TET_tem_MIR, 1, 0.0)[0]))
            
                calcRes.append((main(shp[4], TET_tem_MIR, 1, 0.0)[0]))
                
#                    calcRes.append((main(shp[5], TET_tem_MIR, 1, 0.0)[0]))
                
                calcRes = numpy.array(calcRes)
                
                non = numpy.where(calcRes == 0)
                
                aver = numpy.sum(calcRes) / (len(calcRes) - len(non[0]))
                
                
                sc_mir[i].append(aver)
                
#                sc_mir[i].append((main(shp[1], TET_tem_MIR, 1, 0.0)[0] + main(shp[3], TET_tem_MIR, 1, 0.0)[0] + main(shp[4], TET_tem_MIR, 1, 0.0)[0] + main(shp[5], TET_tem_MIR, 1, 0.0)[0]) / 4.0)

                calcRes = []
                
                calcRes.append((main(shp[0], TET_tem_TIR, 1, 0.0)[0]))
                    
                calcRes.append((main(shp[1], TET_tem_TIR, 1, 0.0)[0]))
                    
                calcRes.append((main(shp[2], TET_tem_TIR, 1, 0.0)[0]))
                
                calcRes.append((main(shp[3], TET_tem_TIR, 1, 0.0)[0]))
#                
                calcRes.append((main(shp[4], TET_tem_TIR, 1, 0.0)[0]))
                
#                    calcRes.append((main(shp[5], TET_tem_TIR, 1, 0.0)[0]))
                
                calcRes = numpy.array(calcRes)
                
                non = numpy.where(calcRes == 0)
                
                aver = numpy.sum(calcRes) / (len(calcRes) - len(non[0]))
                
                sc_tir[i].append(aver)
                
#                sc_tir[i].append((main(shp[1], TET_tem_TIR, 1, 0.0)[0] + main(shp[3], TET_tem_TIR, 1, 0.0)[0] + main(shp[4], TET_tem_TIR, 1, 0.0)[0] + main(shp[5], TET_tem_TIR, 1, 0.0)[0]) / 4.0)
                

#                else:
#                    
#                    calcRes = []
#                
#                    calcRes.append((main(shp[0], TET_tem_MIR, 1, 0.0)[0]))
#                
#                    calcRes.append((main(shp[1], TET_tem_MIR, 1, 0.0)[0]))
#                
#                    calcRes.append((main(shp[2], TET_tem_MIR, 1, 0.0)[0]))
#                
#                    calcRes.append((main(shp[3], TET_tem_MIR, 1, 0.0)[0]))
#                    
#                    calcRes.append((main(shp[4], TET_tem_MIR, 1, 0.0)[0]))
#                
#                    calcRes = numpy.array(calcRes)
#                
#                    non = numpy.where(calcRes == 0)
#                
#                    aver = numpy.sum(calcRes) / (len(calcRes) - len(non[0]))
#                
#                    sc_mir[i].append(aver)
#                
##                sc_mir[i].append((main(shp[1], TET_tem_MIR, 1, 0.0)[0] + main(shp[3], TET_tem_MIR, 1, 0.0)[0] + main(shp[4], TET_tem_MIR, 1, 0.0)[0] + main(shp[5], TET_tem_MIR, 1, 0.0)[0]) / 4.0)
#                
#                    calcRes = []
#                
#                    calcRes.append((main(shp[0], TET_tem_TIR, 1, 0.0)[0]))
#                
#                    calcRes.append((main(shp[1], TET_tem_TIR, 1, 0.0)[0]))
#                
#                    calcRes.append((main(shp[2], TET_tem_TIR, 1, 0.0)[0]))
#                
#                    calcRes.append((main(shp[3], TET_tem_TIR, 1, 0.0)[0]))
#                    
#                    calcRes.append((main(shp[4], TET_tem_TIR, 1, 0.0)[0]))
#                
#                    calcRes = numpy.array(calcRes)
#                
#                    non = numpy.where(calcRes == 0)
#                
#                    aver = numpy.sum(calcRes) / (len(calcRes) - len(non[0]))
#                
#                    sc_tir[i].append(aver)


#                sc_mir[i].append((main(shp[0], TET_tem_MIR)[0] + main(shp[1], TET_tem_MIR)[0] + main(shp[2], TET_tem_MIR)[0] + \
#                          main(shp[3], TET_tem_MIR)[0] + main(shp[4], TET_tem_MIR)[0]) / 5.0)
#                
#                sc_tir[i].append((main(shp[0], TET_tem_TIR)[0] + main(shp[1], TET_tem_TIR)[0] + main(shp[2], TET_tem_TIR)[0] + \
#                          main(shp[3], TET_tem_TIR)[0] + main(shp[4], TET_tem_TIR)[0] ) / 5.0)
                
                if os.path.exists(os.path.join(ac_results, 'temp')) == True:
                    
                    shutil.rmtree(os.path.join(ac_results, 'temp'))
#                
#            else:
#                
#                sc_mir[i].append(0.0)
#                sc_tir[i].append(0.0)
           
#fig1, ax1 = plt.subplots()
#p1, = ax1.plot(sc_mir_2[2], 'ro-', markerfacecolor='none')
#p2, = ax1.plot(sc_mir_3[2], 'ro--', markerfacecolor='none')
#p3, = ax1.plot(sc_tir_2[2], 'bo-', markerfacecolor='none')
#p4, = ax1.plot(sc_tir_3[2], 'bo--', markerfacecolor='none')
#ax1.set_title('Temperature(Libya) Differences with different emissivities(scale factor 1.10)')
#ax1.set_xlabel('time')
#ax1.set_ylabel('Temperature [K]')
#ax1.set_xticks(range(3))
#ax1.set_xticklabels(time)
#plt.legend([p1,p2,p3,p4], ['MIR band imagery. Emissivity in spectrum band 8.6 $\mu$m','MIR band imagery. Emissivity in spectrum band 9.1 $\mu$m','TIR band imagery. Emissivity in spectrum band 8.6 $\mu$m','TIR band imagery. Emissivity in spectrum band 9.1 $\mu$m'],prop={'size':7})
#fig1.tight_layout()
#plt.grid()
#fig1.savefig(os.path.join(r'E:\Penghua\results\comLST\Lybia-1', r'diff_emi1.png'), dpi=200)
#plt.show()
#
#zero = numpy.zeros([1,9])
#fig1, ax1 = plt.subplots()
#p1, = ax1.plot(sc_mir[0], 'yo-')
#p2, = ax1.plot(sc_mir[1], 'go-')
#p3, = ax1.plot(sc_mir[2], 'ro-')
#p4, = ax1.plot(sc_mir[3], 'ko-')
#p5, = ax1.plot(sc_mir[4], 'co-')
#p6, = ax1.plot(zero[0], 'b--')
#ax1.set_title('Temperature Differences with MODIS LST for Lybia-1 Scenes (MIR band)')
#ax1.set_xlabel('time')
#ax1.set_ylabel('Temperature Differences [K]')
#ax1.set_xticks(range(9))
#ax1.set_xticklabels(time, rotation=30, fontsize=9)
#plt.legend([p1,p2,p3,p4,p5], ['scale factor 1.00','scale factor 1.05','scale factor 1.10','scale factor 1.15','scale factor 1.20'],prop={'size':7})
#fig1.tight_layout()
#plt.grid()
#fig1.savefig(os.path.join(r'E:\Penghua\results\ComLST\Lybia-1', r'Lybia-1_scf_mir.png'), dpi=500)
#plt.show()
#
#fig1, ax1 = plt.subplots()
#p1, = ax1.plot(sc_tir[0], 'yo-')
#p2, = ax1.plot(sc_tir[1], 'go-')
#p3, = ax1.plot(sc_tir[2], 'ro-')
#p4, = ax1.plot(sc_tir[3], 'ko-')
#p5, = ax1.plot(sc_tir[4], 'co-')
#p6, = ax1.plot(zero[0], 'b--')
#ax1.set_title('Temperature Differences with MODIS LST for Lybia-1 Scenes (TIR band)')
#ax1.set_xlabel('tnaime')
#ax1.set_ylabel('Temperature Differences [K]')
#ax1.set_xticks(range(9))
#ax1.set_xticklabels(time, rotation=30, fontsize=9)
#plt.legend([p1,p2,p3,p4,p5], ['scale factor 1.00','scale factor 1.05','scale factor 1.10','scale factor 1.15','scale factor 1.20'],prop={'size':7})
#fig1.tight_layout()
#plt.grid()
#fig1.savefig(os.path.join(r'E:\Penghua\results\ComLST\Lybia-1', r'Lybia-1_scf_test_tir.png'), dpi=500)
#plt.show()
#
#
#sc = []
#
#index = []
#
#b_sc = []
#
#for i in range(len(sc_mir[0])):
#    
#    temp = []
#    
#    for j in range(len(sc_mir)):
#        
#        if sc_mir[j][i] == 0:
#            
#            temp.append(10)
#            
#        else:
#            
#            temp.append(abs(sc_mir[j][i]))
#    
#    sc.append(min(temp))
#    
#    index.append(temp.index(min(temp)))
#    
#    b_sc.append(scale_factor[temp.index(min(temp))])
#
#diff_tem = []
#
#count = 0
#
#for sc in b_sc:
#    
#    diff_tem.append(sc_mir[scale_factor.index(sc)][count])
#    
#    count = count + 1
#    
#fig, ax1 = plt.subplots()
#p1, = ax1.plot(b_sc, 'ro-')
#ax1.set_title('Best scale factor for each scene (MIR band)')
#ax1.set_ylabel('scale factor')
#ax1.set_xlabel('time')
#ax1.set_yticks(numpy.arange(1.05,1.21,0.01))
#ax1.set_xticks(range(9))
#ax1.set_xticklabels(time, rotation=30, fontsize=9)
#fig.tight_layout()
#plt.grid()
#fig.savefig(os.path.join(r'E:\Penghua\results\ComLST\Lybia-1', r'Lybia-1_bsc_mir.png'), dpi=500)
#plt.show()
#one = 1.15 * numpy.ones([1,9])
#p2, = ax1.plot(one[0], 'b--')
#fig.savefig(os.path.join(r'E:\Penghua\results\ComLST\Lybia-1', r'Lybia-1_bsc&ssc_mir.png'), dpi=500)
#plt.show()
#
#fig, ax1 = plt.subplots()
#p1, = ax1.plot(b_sc, 'ro-')
#ax1.set_title('Best scale factor for each scene and corresponding $\Delta$T (MIR band)')
#ax1.set_ylabel('best scale factor for each scene', color='r')
#ax1.tick_params('y', colors='r')
#
#ax2 = ax1.twinx()
#p2, = ax2.plot(diff_tem, 'bo--', markerfacecolor='none')
#ax2.set_ylabel('corresponding $\Delta$T [K]', color='b')
#ax2.tick_params('y', colors='b')
#ax1.set_xlabel('time')
#ax1.set_xticks(range(9))
#ax1.set_xticklabels(time, rotation=30, fontsize=9)
#fig.tight_layout()
#plt.grid()
#plt.legend([p1,p2], [r'best scale factor', r'corresponding $\Delta$T'],prop={'size':7})
#fig.savefig(os.path.join(r'E:\Penghua\results\ComLST\Lybia-1', r'Lybia-1_bsc&tem_mir.png'), dpi=500)
#plt.show()
#
#fig2, ax1 = plt.subplots()
#p1, = ax1.plot(diff_tem, 'ro-', markerfacecolor='none')
#p3, = ax1.plot(sc_mir[3], 'bo--', markerfacecolor='none')
#ax1.set_title('Temperature Differences with MODIS LST for Lybia-1 Scenes (MIR band)')
#ax1.set_ylabel('Temperature Differences [K]')
#ax1.set_xlabel('time')
#ax1.set_xticks(range(9))
#ax1.set_xticklabels(time, rotation=30, fontsize=9)
#plt.legend([p1,p3], [r'smallest $\Delta$T','$\Delta$T for scale factor 1.15'],prop={'size':7})
#plt.grid()
#fig2.tight_layout()
#fig2.savefig(os.path.join(r'E:\Penghua\results\ComLST\Lybia-1', r'Lybia-1_bsc&temCom_mir.png'), dpi=500)
#plt.show()
#
#sc = []
#
#index = []
#
#b_sc = []
#
#for i in range(len(sc_tir[0])):
#    
#    temp = []
#    
#    for j in range(len(sc_tir)):
#        
#        if sc_tir[j][i] == 0:
#            
#            temp.append(10)
#            
#        else:
#            
#            temp.append(abs(sc_tir[j][i]))
#    
#    sc.append(min(temp))
#    
#    index.append(temp.index(min(temp)))
#    
#    b_sc.append(scale_factor[temp.index(min(temp))])
#
#diff_tem = []
#
#count = 0
#
#for s in b_sc:
#    
#    diff_tem.append(sc_tir[scale_factor.index(s)][count])
#    
#    count = count + 1
#    
#fig, ax1 = plt.subplots()
#p1, = ax1.plot(b_sc, 'ro-')
#ax1.set_title('Best scale factor for each scene (TIR band)')
#ax1.set_ylabel('scale factor')
#ax1.set_xlabel('time')
#ax1.set_xticks(range(9))
#ax1.set_yticks(numpy.arange(1.0,1.16,0.01))
#ax1.set_xticklabels(time, rotation=30, fontsize=7)
#fig.tight_layout()
#plt.grid()
#fig.savefig(os.path.join(r'E:\Penghua\results\ComLST\Lybia-1', r'Lybia-1_bsc_tir.png'), dpi=500)
#plt.show()
#one = 1.05 * numpy.ones([1,9])
#p2, = ax1.plot(one[0], 'b--')
#fig.savefig(os.path.join(r'E:\Penghua\results\ComLST\Lybia-1', r'Lybia-1_bsc&ssc_tir.png'), dpi=500)
#plt.show()
#
#fig, ax1 = plt.subplots()
#p1, = ax1.plot(b_sc, 'ro-')
#ax1.set_title('Best scale factor for each scene and corresponding $\Delta$T(TIR band)')
#ax1.set_ylabel('best scale factor for each scene', color='r')
##ax1.set_yticks(numpy.arange(1.0,1.15,0.01))
#ax1.tick_params('y', colors='r')
#
#ax2 = ax1.twinx()
#p2, = ax2.plot(diff_tem, 'bo--', markerfacecolor='none')
#ax2.set_ylabel('corresponding $\Delta$T [K]', color='b')
#ax2.tick_params('y', colors='b')
#ax1.set_xlabel('time')
#ax1.set_xticks(range(9))
#ax1.set_xticklabels(time, rotation=30, fontsize=9)
#fig.tight_layout()
#plt.grid()
#plt.legend([p1,p2], [r'best scale factor', r'corresponding $\Delta$T'],prop={'size':7})
#fig.savefig(os.path.join(r'E:\Penghua\results\ComLST\Lybia-1', r'Lybia-1_bsc&tem_tir.png'), dpi=500)
#plt.show()
#
#fig2, ax1 = plt.subplots()
#p1, = ax1.plot(diff_tem, 'ro-', markerfacecolor='none')
#p2, = ax1.plot(sc_tir[1], 'bo--', markerfacecolor='none')
#ax1.set_title('Temperature Differences with MODIS LST for Lybia-1 Scenes(TIR band)')
#ax1.set_ylabel('Temperature Differences [K]')
#ax1.set_xlabel('time')
#ax1.set_xticks(range(9))
#ax1.set_xticklabels(time, rotation=30, fontsize=7)
#plt.legend([p1,p2], [r'smallest $\Delta$T',r'$\Delta$T for scale factor 1.05'],prop={'size':7})
#plt.grid()
#fig2.tight_layout()
#fig2.savefig(os.path.join(r'E:\Penghua\results\ComLST\Lybia-1', r'Lybia-1_bsc&temCom_tir.png'), dpi=500)
#plt.show()


#fig1, ax1 = plt.subplots()
#p1, = ax1.plot(range(3),etna_tir[1], 'ro')
#p4, = ax1.plot([3],portugal_tir[1], 'rx')
#p7, = ax1.plot(range(4,6),demmin_tir[1], 'r*')
#p10, = ax1.plot([etna_tir[1][0],etna_tir[1][1],etna_tir[1][2],portugal_tir[1][0],demmin_tir[1][0], demmin_tir[1][1]], 'r--')
#p13, = ax1.plot(numpy.zeros([1,6])[0], 'b--')
#ax1.set_title('Temperature Differences with MODIS SST (TIR band)')
#ax1.set_xlabel('time')
#ax1.set_ylabel('Temperature Differences [K]')
#ax1.set_xticks(range(6))
#ax1.set_xticklabels(time, fontsize=7)
#plt.legend([p1,p4,p7,p10], ['Etna','Portugal','Demmin','scale factor 1.05'],prop={'size':7})
#fig1.tight_layout()
#plt.grid()
#fig1.savefig(os.path.join(r'E:\Penghua\results\ComSST\test2', r'sst_test_tir.png'), dpi=200)
#plt.show()

#fig1, ax1 = plt.subplots()
#p1, = ax1.plot(range(3),etna_mir[1], 'yo')
#p2, = ax1.plot(range(3),etna_mir[2], 'ro')
#p3, = ax1.plot(range(3),etna_mir[3], 'go')
#p4, = ax1.plot([3],portugal_mir[1], 'yx')
#p5, = ax1.plot([3],portugal_mir[2], 'rx')
#p6, = ax1.plot([3],portugal_mir[3], 'gx')
#p7, = ax1.plot(range(4,6),demmin_mir[1], 'y*')
#p8, = ax1.plot(range(4,6),demmin_mir[2], 'r*')
#p9, = ax1.plot(range(4,6),demmin_mir[3], 'g*')
#p10, = ax1.plot([etna_mir[1][0],etna_mir[1][1],etna_mir[1][2],portugal_mir[1][0],demmin_mir[1][0], demmin_mir[1][1]], 'y--')
#p11, = ax1.plot([etna_mir[2][0],etna_mir[2][1],etna_mir[2][2],portugal_mir[2][0],demmin_mir[2][0], demmin_mir[2][1]], 'r--')
#p12, = ax1.plot([etna_mir[3][0],etna_mir[3][1],etna_mir[3][2],portugal_mir[3][0],demmin_mir[3][0], demmin_mir[3][1]], 'g--')
#p13, = ax1.plot(numpy.zeros([1,6])[0], 'b--')
#ax1.set_title('Temperature Differences with MODIS SST (MIR band)')
#ax1.set_xlabel('time')
#ax1.set_ylabel('Temperature Differences [K]')
#ax1.set_xticks(range(6))
#ax1.set_xticklabels(time, fontsize=7)
#plt.legend([p2,p5,p8,p10,p11,p12], ['Etna','Portugal','Demmin','scale factor 1.05', 'scale factor 1.10','scale_factor 1.15'],prop={'size':7})
#fig1.tight_layout()
#plt.grid()
##fig1.savefig(os.path.join(r'E:\Penghua\results\ComSST\test2', r'sst_test&comp_mir.png'), dpi=200)
#plt.show()