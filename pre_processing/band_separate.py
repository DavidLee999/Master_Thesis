# -*- coding: utf-8 -*-
"""
Created on Mon May 15 10:03:37 2017

@author: li_pe
"""

from osgeo import gdal
from osgeo import osr
import subprocess
import os


def band_separate(inFileLoc, outFileLoc, band, nodata=-9999):
   
 
#    name, postfix = os.path.splitext(inFileLoc)

    #outFileLoc = name + '_band' + band_num2

    command =[]

    command.extend(['gdal_translate', '-of', 'GTiff', '-b', str(band), '-a_nodata', str(nodata)])

    command.append(inFileLoc)

    command.append(outFileLoc)

    subprocess.call(command)
    

location = ['Etna', 'Demmin', 'Lascar', 'Lybien-1', 'Lybien-2', 'Portugal']

UTM_zone = {'Etna':'EPSG:32633', 'Demmin':'EPSG:32633', 'Lascar':'EPSG:32719', 'Lybien-1':'EPSG:32634', 'Lybien-2':'EPSG:32633', 'Portugal':'EPSG:32629'}

#sourFile = r'E:\Penghua\data\corresponding_water_vapor' + '\\' + location[5]
#
#name = '_UTM29N.tif'
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
#                
#                abspath, postfix = os.path.splitext(inFileLoc)
#                
#                outFileLoc = abspath + name
#
#                band_separate(inFileLoc, outFileLoc, 1)

#name = ['_band2_8.6.tif', '_band3_9.1.tif']
#
##for loc in location[1:]:
#    
#sourFile = r'E:\Penghua\data\emissivity_map\emissivity_map_' + location[5] + '\\merged'
#
#os.chdir(sourFile)
#
#for files in os.listdir(sourFile):
#
#    if files.endswith('.tif') and location[5] in files:
#        
#        inFileLoc = os.path.abspath(files)
#
#        abspath, postfix = os.path.splitext(inFileLoc)
#        
#        outFileLoc1 = abspath + name[0]
#            
#        band_separate(inFileLoc, outFileLoc1, 2)
#            
#        outFileLoc2 = abspath + name[1]
#            
#        band_separate(inFileLoc, outFileLoc2, 3)

name = '_UTM33N.tif'

sourFile = r'E:\Penghua\data\SST' + '\\' + location[0]

os.chdir(sourFile)

for files in os.listdir(sourFile):
    
    if os.path.isdir(files) == True:
        
        for fil in os.listdir(files):
            
            if fil.endswith('.tif') and 'SST' in fil:
                
                inFileLoc = os.path.abspath(files) + '\\' + fil
                                    
                outFileLoc = os.path.splitext(inFileLoc)[0] + name
                                             
                band_separate(inFileLoc, outFileLoc, 1)               