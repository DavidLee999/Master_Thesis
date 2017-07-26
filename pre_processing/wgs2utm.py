# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 12:20:08 2017

@author: li_pe
"""

from osgeo import gdal
from osgeo import osr
import subprocess
import os


#targetTiff = gdal.Open(r'E:\Penghua\test\AG100.v003.64.-015.0001_Emissivity_Mean_reprojected.tif')
def wgs2utm(inFileLoc, zone, resample=False, pixel_size = None, nodata_dst = -9999):
        
    resultImgPath = os.path.dirname( inFileLoc ) + '\\' + 'repro'
    
    if os.path.exists(resultImgPath) == False:
        
        os.makedirs(resultImgPath)
    
    dir_name, img = os.path.split(inFileLoc)
    
    img_name, postfix = os.path.splitext(img)
    
    outFileLoc = resultImgPath + '\\' + img_name + '_repro' + postfix

    
    L = ['gdalwarp']
    
    L.extend(['-t_srs', zone])
    
    L.extend(['-dstnodata', str(nodata_dst)])
    
    L.extend(['-of', 'GTiff', '-overwrite'])
    
    if resample == True:
        
        L.extend(['-tr', str(pixel_size[0]), str(pixel_size[1]), '-r', 'near'])
    
    L.append(inFileLoc)
    
    L.append(outFileLoc)

    subprocess.call(L)
    
    print 'end'



location = ['Etna', 'Demmin', 'Lascar', 'Lybien-1', 'Lybien-2', 'Portugal']

UTM_zone = {'Etna':'EPSG:32633', 'Demmin':'EPSG:32633', 'Lascar':'EPSG:32719', 'Lybien-1':'EPSG:32634', 'Lybien-2':'EPSG:32633', 'Portugal':'EPSG:32629'}

sourFile = r'E:\Penghua\data\LST' + '\\' + location[3]

os.chdir(sourFile)

for files in os.listdir(sourFile):
    
    if os.path.isdir(files) == True:
        
        for fil in os.listdir(files):
            
            if fil.endswith('.tif') and 'MOD' in fil:
                
                inFileLoc = os.path.abspath(files) + '\\' + fil
                                           
                wgs2utm(inFileLoc, UTM_zone[location[3]], True, [150,150])
                
#reproject TET images to UTM coord. system

#sourFile = r'E:\Penghua\data\georeferenced_TET' + '\\' + location[0] + '\\new_selected_data'
#
#os.chdir(sourFile)
#
#for files in os.listdir(sourFile):
#    
#    if os.path.isdir(files) == True:
#        
#        for fil in os.listdir(files):
#            
#            if fil.endswith('.tif') and 'near' in fil :
#                
#                inFileLoc = os.path.abspath(files) + '\\' + fil
#                
#                wgs2utm(inFileLoc, UTM_zone[location[0]], True, [150,150])


#reproject water vapor data to UTM coord. system

#sourFile = r'E:\Penghua\data\corresponding_water_vapor' + '\\' + location[0] + '\\new_selected_data'
#
#os.chdir(sourFile)
#
#for files in os.listdir(sourFile):
#    
#    if os.path.isdir(files) == True:
#        
#        for fil in os.listdir(files):
#            
#            if fil.endswith('.tif') and 'water' in fil:
#                
#                inFileLoc = os.path.abspath(files) + '\\' + fil
#                #print inFileLoc
#                wgs2utm(inFileLoc, UTM_zone[location[0]], True, [150,150])


#reproject DEM to UTM coord. system


#sourFile = r'E:\Penghua\data\DEM' + '\\' + location[5] + '\\merged'
#
#os.chdir(sourFile)
#
#for files in os.listdir(sourFile):
#
#    if files.endswith('.tif') and 'DEM' in files:
#
#        inFileLoc = os.path.abspath(files)
#        #print inFileLoc
#        wgs2utm(inFileLoc, UTM_zone[location[5]], True, [150,150], 0)



#for loc in location[1:]:
    
#sourFile = r'E:\Penghua\data\emissivity_map\emissivity_map_' + location[5] + '\\merged'
#
#os.chdir(sourFile)
#
#for files in os.listdir(sourFile):
#    
#        if files.endswith('.tif') and 'band' in files:
#        
#            inFileLoc = os.path.abspath(files)
#            
#            wgs2utm(inFileLoc, UTM_zone[location[5]], True, [150,150])


#sourFile = r'E:\Penghua\data\SST' + '\\' + location[1]
#
#os.chdir(sourFile)
#
#for files in os.listdir(sourFile):
#    
#    if os.path.isdir(files) == True:
#        
#        for fil in os.listdir(files):
#            
#            if fil.endswith('.tif') and 'UTM' in fil:
#                
#                inFileLoc = os.path.abspath(files) + '\\' + fil
#                                           
#                wgs2utm(inFileLoc, UTM_zone[location[1]], True, [150,150])