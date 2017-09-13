# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 11:37:53 2017

@author: li_pe
"""

from osgeo import gdal, ogr, osr
import numpy as np
import os

def raster2array( rasterfn, bandNum ):
    raster = gdal.Open( rasterfn )
    band = raster.GetRasterBand( bandNum )
    array = band.ReadAsArray()
    
    return array

def array2raster( newRasterfn, rasterfn, array ):
    raster = gdal.Open( rasterfn )
    geotransform = raster.GetGeoTransform()
    
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    cols = array.shape[1]
    rows = array.shape[0]
    
    driver = gdal.GetDriverByName( 'GTiff' )
    outRaster = driver.Create( newRasterfn, cols, rows, 1, gdal.GDT_Byte )
    outRaster.SetGeoTransform(( originX, pixelWidth, 0, originY, 0, pixelHeight ))
    outband = outRaster.GetRasterBand( 1 )
    outband.WriteArray( array )
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromWkt( raster.GetProjectionRef() )
    outRaster.SetProjection( outRasterSRS.ExportToWkt() )
    
    outband.FlushCache()
    
def createMaskArray( array, MaskValue ):
    logicL = np.where( array > MaskValue )
    logicS = np.where( array <= MaskValue )
    
    array[logicL] = 1
    array[logicS] = 0
    
    return array
    
def raster2shp( rasterfn, bandNum ):
    
#    folder = os.path.split(rasterfn)[0]
#    output = os.path.join( folder, 'POLY' )
#    
#    if os.path.exists(output) == False:
#        os.mkdir( output )
#    else:
#        return
    
    raster = gdal.Open( rasterfn )
    band = raster.GetRasterBand( bandNum )
    
    drv = ogr.GetDriverByName('ESRI Shapefile')
    dst_layername = 'sub_tem'
    dst_ds = drv.CreateDataSource( dst_layername + '.shp')
    
    srs = osr.SpatialReference()
    srs.ImportFromWkt( raster.GetProjectionRef() )
    
    dst_layer = dst_ds.CreateLayer(dst_layername, geom_type=ogr.wkbPolygon, srs = srs )
    
    dst_fieldname = 'DN'
    fd = ogr.FieldDefn( dst_fieldname, ogr.OFTInteger )
    dst_layer.CreateField( fd )
    dst_field = 0
    
    gdal.Polygonize(band, None, dst_layer, dst_field, ["8CONNECTED=8"], callback = None)
   
    featNum = dst_layer.GetFeatureCount()
    
    for i in range(featNum):
        
        feat = dst_layer.GetFeature(i)
        
        Fid = feat.GetFID()
        
        feat.SetField('DN', Fid)
        
        dst_layer.SetFeature(feat)
    
    
    

    
#    lyr = dst_ds.GetLayer()
#    
#    lyr.DeleteFeature(lyr.GetFeatureCount() - 1)


src_ds = r'E:\Penghua\data\Bardarbunga\2014.09.22\TET\ac_results\FBI_TET1_20140922T015526_20140922T015628_L2_C_EL-00453_cobined_MIR_TIR_tem.tif'

outputfolder = os.path.join( os.path.split(src_ds)[0], 'Mask' )

if os.path.exists( outputfolder ) == False:
    os.mkdir( outputfolder )
    
os.chdir( outputfolder )

newRaster = os.path.join( outputfolder, 'sub_tem.tif' )

array = raster2array( src_ds, 4 )
array = createMaskArray( array, 0 )
array2raster( newRaster, src_ds, array)

raster2shp( newRaster, 1)

#src_band = src_ds.GetRasterBand(3)
#
#dst_layername = 'POLY'
#
#drv = ogr.GetDriverByName('ESRI Shapefile')
#
#dst_ds = drv.CreateDataSource( dst_layername + '.shp')
#
#srs = osr.SpatialReference()
#
#srs.ImportFromEPSG(32633)
#
#dst_layer = dst_ds.CreateLayer( dst_layername, srs )
#
#gdal.Polygonize( src_band, None, dst_layer, -1, [], callback = None )