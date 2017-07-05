# -*- coding: utf-8 -*-
"""
Created on Wed Jul 05 11:20:07 2017

@author: li_pe
"""

import gdal, ogr, osr, numpy
import sys, os
import matplotlib.pyplot as plt

def zonal_stats(feat, input_zone_polygon, input_value_raster):

    # Open data
    raster = gdal.Open(input_value_raster)
    shp = ogr.Open(input_zone_polygon)
    lyr = shp.GetLayer()

    # Get raster georeference info
    transform = raster.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = transform[1]
    pixelHeight = transform[5]

    # Reproject vector geometry to same projection as raster
    sourceSR = lyr.GetSpatialRef()
    targetSR = osr.SpatialReference()
    targetSR.ImportFromWkt(raster.GetProjectionRef())
    coordTrans = osr.CoordinateTransformation(sourceSR,targetSR)
    feat = lyr.GetNextFeature()
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
    xcount = int((xmax - xmin)/pixelWidth)+1
    ycount = int((ymax - ymin)/pixelWidth)+1

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

    # Rasterize zone polygon to raster
    gdal.RasterizeLayer(target_ds, [1], lyr, burn_values=[1])

    # Read raster as arrays
    banddataraster = raster.GetRasterBand(1)
    dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount).astype(numpy.float)

    bandmask = target_ds.GetRasterBand(1)
    datamask = bandmask.ReadAsArray(0, 0, xcount, ycount).astype(numpy.float)

    # Mask zone of raster
    zoneraster = numpy.ma.masked_array(dataraster,  numpy.logical_not(datamask))

    # Calculate statistics of zonal raster
    #return numpy.average(zoneraster),numpy.mean(zoneraster),numpy.median(zoneraster),numpy.std(zoneraster),numpy.var(zoneraster)
    return numpy.mean(zoneraster)

def loop_zonal_stats(input_zone_polygon, input_value_raster):

    shp = ogr.Open(input_zone_polygon)
    lyr = shp.GetLayer()
    featList = range(lyr.GetFeatureCount())
    statDict = {}

    for FID in featList:
        feat = lyr.GetFeature(FID)
        meanValue = zonal_stats(feat, input_zone_polygon, input_value_raster)
        statDict[FID] = meanValue
    return statDict

def main(input_zone_polygon, input_value_raster):
    return loop_zonal_stats(input_zone_polygon, input_value_raster)


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



shpFile = r'E:\Penghua\data\Etna\shapefiles'

shp = []

os.chdir(shpFile)

for files in os.listdir(shpFile):
    
    if files.endswith('.shp') and 'rect' in files:
        
        shp.append(os.path.abspath(files)) 

sourFile = r'E:\Penghua\data\Etna'

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

scale_factor = ['1.00', '1.05', '1.10', '1.15', '1.20']

sc_mir = [[], [], [], [], []]
sc_tir = [[], [], [], [], []]
time = []

for i in range(len(scale_factor)):
    
    #print scale_factor[i]
    
    
    for files in os.listdir(sourFile):
        
        if '0' in files:
            
            if i == 0:
                
                time.append(files)
            
            #print files
            
    #        sheet1.write(0, count, files)
    #        
    #        sheet2.write(0, count, files)
            
            ac_folder = os.path.join(os.path.abspath(files), r'TET\ac_results_%s\compared' %scale_factor[i])
            
            if os.path.exists(os.path.join(os.path.abspath(files), r'TET\ac_results_%s\compared' %scale_factor[i])) == True:
            
                ac_results = os.path.join(os.path.abspath(files), r'TET\ac_results_%s\compared' %scale_factor[i])
            
                for fil in os.listdir(ac_results):
                
                    if fil.endswith('.tif') and 'MIR' in fil:
                    
                        TET_tem_MIR = os.path.join(ac_results, fil)
                        
                    if fil.endswith('.tif') and 'TIR' in fil:
                    
                        TET_tem_TIR = os.path.join(ac_results, fil)                           
                
                sc_mir[i].append((main(shp[1], TET_tem_MIR)[0]+main(shp[3], TET_tem_MIR)[0]+main(shp[4], TET_tem_MIR)[0]) / 3.0)
                
                sc_tir[i].append((main(shp[1], TET_tem_TIR)[0]+main(shp[3], TET_tem_TIR)[0]+main(shp[4], TET_tem_TIR)[0]) / 3.0)
                
            else:
                
                sc_mir[i].append(0.0)
                sc_tir[i].append(0.0)
                

zero = numpy.zeros([1,16])
plt.xticks(range(16), time, rotation=30, fontsize=4)
p1, = plt.plot(sc_mir[0], 'yo-')
p2, = plt.plot(sc_mir[1], 'go-')
p3, = plt.plot(sc_mir[2], 'ro-')
p4, = plt.plot(sc_mir[3], 'ko-')
p5, = plt.plot(sc_mir[4], 'co-')
p6, = plt.plot(zero[0], 'b--')
plt.title('Temperature Differences for Etna Scenes in MIR band')
plt.xlabel('time')
plt.ylabel('Temperature Differences [deg]')
legend = plt.legend([p1,p2,p3,p4,p5], ['scale factor 1.00','scale factor 1.05','scale factor 1.10','scale factor 1.15','scale factor 1.20'],prop={'size':7})

plt.show()
plt.savefig(os.path.join(sourFile, r'te.png'), dpi=200)
            
#            sheet1.write(1, count, float(MIR_rect2[0]))
#            sheet1.write(2, count, float(MIR_rect4[0]))
#            sheet1.write(3, count, float(MIR_rect6[0]))
#            
#            sheet2.write(1, count, float(TIR_rect2[0]))
#            sheet2.write(2, count, float(TIR_rect4[0]))
#            sheet2.write(3, count, float(TIR_rect6[0]))
#            
#        count = count + 1
#
#filename.save(os.path.join(sourFile, 'scale_factor_1.00.xls'))