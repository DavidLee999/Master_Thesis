# -*- coding: utf-8 -*-
"""
Created on Mon May 15 16:56:18 2017

@author: li_pe
"""
from osgeo import gdal
from osgeo import osr, ogr
import subprocess
import os

def alpha_channel(inFileLoc, outFileLoc, nodata=-9999):
    
    command = ['gdalwarp', '-of', 'GTiff', '-dstalpha']
    
    command.extend(['-srcnodata', str(nodata)])
    
    command.extend(['-co', '"ALPHA=YES"', '-dstnodata', '0', '-overwrite'])
    
    command.append(inFileLoc)
    
    command.append(outFileLoc)

    subprocess.call(command)
    

   
sourfile = r'E:\Penghua\data\georeferenced_TET\Etna\new_selected_data'

outputfile = r'E:\Penghua\data\georeferenced_TET\Etna\new_selected_data\alpha_channel'

if os.path.exists(outputfile) == False:
    
    os.makedirs(outputfile)

os.chdir(sourfile)

fold_name = 'repro'

id = 'MWIR'

for folds in os.listdir(sourfile):
    
    if 'TET' in folds:
    
        reprojected_fold = os.path.abspath(folds) + '\\' + fold_name
                                      
        for files in os.listdir(reprojected_fold):
        
            if files.endswith('.tif') and id in files:
            
                inFileLoc = os.path.join(reprojected_fold, files)
            
                file_name, postfix = os.path.splitext(files)
            
                outFileLoc = outputfile + '\\' + file_name + '_alpha.tif'
            
                alpha_channel(inFileLoc, outFileLoc)
