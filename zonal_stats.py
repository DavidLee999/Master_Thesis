"""
Zonal Statistics
Vector-Raster Analysis

Copyright 2013 Matthew Perry

Usage:
  zonal_stats.py VECTOR RASTER
  zonal_stats.py -h | --help
  zonal_stats.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""
from osgeo import gdal, ogr
from osgeo.gdalconst import *
import numpy as np
import sys, os
import xlrd, xlwt
gdal.PushErrorHandler('CPLQuietErrorHandler')


def bbox_to_pixel_offsets(gt, bbox):
    originX = gt[0]
    originY = gt[3]
    pixel_width = gt[1]
    pixel_height = gt[5]
    x1 = int((bbox[0] - originX) / pixel_width)
    x2 = int((bbox[1] - originX) / pixel_width) + 1

    y1 = int((bbox[3] - originY) / pixel_height)
    y2 = int((bbox[2] - originY) / pixel_height) + 1

    xsize = x2 - x1
    ysize = y2 - y1
    return (x1, y1, xsize, ysize)


def zonal_stats(vector_path, raster_path, nodata_value=None, global_src_extent=False):
    rds = gdal.Open(raster_path, GA_ReadOnly)
    assert(rds)
    rb = rds.GetRasterBand(1)
    rgt = rds.GetGeoTransform()

    if nodata_value:
        nodata_value = float(nodata_value)
        rb.SetNoDataValue(nodata_value)

    vds = ogr.Open(vector_path, GA_ReadOnly)  # TODO maybe open update if we want to write stats
    assert(vds)
    vlyr = vds.GetLayer(0)

    # create an in-memory numpy array of the source raster data
    # covering the whole extent of the vector layer
    if global_src_extent:
        # use global source extent
        # useful only when disk IO or raster scanning inefficiencies are your limiting factor
        # advantage: reads raster data in one pass
        # disadvantage: large vector extents may have big memory requirements
        src_offset = bbox_to_pixel_offsets(rgt, vlyr.GetExtent())
        src_array = rb.ReadAsArray(*src_offset)

        # calculate new geotransform of the layer subset
        new_gt = (
            (rgt[0] + (src_offset[0] * rgt[1])),
            rgt[1],
            0.0,
            (rgt[3] + (src_offset[1] * rgt[5])),
            0.0,
            rgt[5]
        )

    mem_drv = ogr.GetDriverByName('Memory')
    driver = gdal.GetDriverByName('MEM')

    # Loop through vectors
    stats = []
    feat = vlyr.GetNextFeature()
    while feat is not None:

        if not global_src_extent:
            # use local source extent
            # fastest option when you have fast disks and well indexed raster (ie tiled Geotiff)
            # advantage: each feature uses the smallest raster chunk
            # disadvantage: lots of reads on the source raster
            src_offset = bbox_to_pixel_offsets(rgt, feat.geometry().GetEnvelope())
            src_array = rb.ReadAsArray(*src_offset)

            # calculate new geotransform of the feature subset
            new_gt = (
                (rgt[0] + (src_offset[0] * rgt[1])),
                rgt[1],
                0.0,
                (rgt[3] + (src_offset[1] * rgt[5])),
                0.0,
                rgt[5]
            )

        # Create a temporary vector layer in memory
        mem_ds = mem_drv.CreateDataSource('out')
        mem_layer = mem_ds.CreateLayer('poly', None, ogr.wkbPolygon)
        mem_layer.CreateFeature(feat.Clone())

        # Rasterize it
        rvds = driver.Create('', src_offset[2], src_offset[3], 1, gdal.GDT_Byte)
        rvds.SetGeoTransform(new_gt)
        gdal.RasterizeLayer(rvds, [1], mem_layer, burn_values=[1])
        rv_array = rvds.ReadAsArray()

        # Mask the source data array with our current feature
        # we take the logical_not to flip 0<->1 to get the correct mask effect
        # we also mask out nodata values explictly
        masked = np.ma.MaskedArray(
            src_array,
            mask=np.logical_or(
                src_array == nodata_value,
                np.logical_not(rv_array)
            )
        )

        feature_stats = {
            'min': float(masked.min()),
            'mean': float(masked.mean()),
            'max': float(masked.max()),
            'std': float(masked.std()),
            'sum': float(masked.sum()),
            'count': int(masked.count()),
            'fid': int(feat.GetFID())}

        stats.append(feature_stats)

        rvds = None
        mem_ds = None
        feat = vlyr.GetNextFeature()

    vds = None
    rds = None
    return stats
    
#Raster = r'E:\Penghua\data\Etna\2014.06.22\TET\ac_results_1.00\compared\diff_MIR.tif'
#
#Vector = r'E:\Penghua\data\Etna\shapefiles\rect6.shp'
#
#states = zonal_stats(Vector, Raster)

shpFile = r'E:\Penghua\data\Etna\shapefiles'

shp = []

os.chdir(shpFile)

for files in os.listdir(shpFile):
    
    if files.endswith('.shp') and 'rect' in files:
        
        shp.append(os.path.abspath(files)) 

sourFile = r'E:\Penghua\data\Etna'

os.chdir(sourFile)

filename = xlwt.Workbook()

sheet1 = filename.add_sheet(u'MIR')

sheet2 = filename.add_sheet(u'TIR')

sheet1.write(1, 0, u'rect2')

sheet1.write(2, 0, u'rect6')

sheet1.write(3, 0, u'rect7')
            
sheet2.write(1, 0, u'rect2')

sheet2.write(2, 0, u'rect6')

sheet2.write(3, 0, u'rect7')

count = 1

for files in os.listdir(sourFile):
    
    if '0' in files:
        print files
        sheet1.write(0, count, files)
        
        sheet2.write(0, count, files)
        
        if os.path.exists(os.path.join(os.path.abspath(files), r'TET\ac_results_1.00\compared')) == True:
        
            ac_results = os.path.join(os.path.abspath(files), r'TET\ac_results_1.00\compared')
        
            for fil in os.listdir(ac_results):
            
                if fil.endswith('.tif') and 'MIR' in fil:
                
                    TET_tem_MIR = os.path.join(ac_results, fil)
                    
                if fil.endswith('.tif') and 'TIR' in fil:
                
                    TET_tem_TIR = os.path.join(ac_results, fil)
            
            MIR_rect2 = zonal_stats(shp[1], TET_tem_MIR)
            
            MIR_rect7 = zonal_stats(shp[5], TET_tem_MIR)
            
            MIR_rect6 = zonal_stats(shp[4], TET_tem_MIR)
            
            TIR_rect2 = zonal_stats(shp[1], TET_tem_MIR)
            
            TIR_rect7 = zonal_stats(shp[5], TET_tem_MIR)
            
            TIR_rect6 = zonal_stats(shp[4], TET_tem_MIR)
            
            
            sheet1.write(1, count, float(MIR_rect2[0]['mean']))
            sheet1.write(2, count, float(MIR_rect6[0]['mean']))
            sheet1.write(3, count, float(MIR_rect7[0]['mean']))
            
            sheet2.write(1, count, float(TIR_rect2[0]['mean']))
            sheet2.write(2, count, float(TIR_rect6[0]['mean']))
            sheet2.write(3, count, float(TIR_rect7[0]['mean']))
            
        count = count + 1

filename.save(os.path.join(sourFile, 'scale_factor_1.00.xls'))
    