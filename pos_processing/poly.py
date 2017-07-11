# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 11:37:53 2017

@author: li_pe
"""

from osgeo import gdal, ogr, osr
import os


def raster2shp( rasterfn, bandNum ):
    raster = gdal.Open( rasterfn )
    band = raster.GetRasterBand( bandNum )
    
    drv = ogr.GetDriverByName('ESRI Shapefile')
    dst_layername = 'POLY'
    dst_ds = drv.CreateDataSource( dst_layername + '.shp')
    
    srs = osr.SpatialReference()
    srs.ImportFromWkt( raster.GetProjectionRef() )
    
    dst_layer = dst_ds.CreateLayer(dst_layername, geom_type=ogr.wkbPolygon, srs = srs )
    
    dst_fieldname = 'DN'
    fd = ogr.FieldDefn( dst_fieldname, ogr.OFTInteger )
    dst_layer.CreateField( fd )
    dst_field = 0
    
    gdal.Polygonize( band, None, dst_layer, dst_field, [], callback = None)

    
#    lyr = dst_ds.GetLayer()
#    
#    lyr.DeleteFeature(lyr.GetFeatureCount() - 1)


src_ds = r'E:\Penghua\data\Etna\2014.06.22\TET\ac_results_1.04_MIR_TIR\FBI_TET1_20140622T232052_20140622T232155_L2_002589_WHM_cobined_MIR_TIR_tem.tif'

os.chdir( os.path.split(src_ds)[0] )

raster2shp(src_ds, 3)

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