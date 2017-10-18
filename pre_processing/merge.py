# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#from osgeo import gdal
#from osgeo import osr
import os, sys

#gm = os.path.join(r'C:\Users\li_pe\AppData\Local\Continuum\Anaconda2\pkgs\gdal-2.1.0-py27_0\Scripts\gdal_merge.py')
sys.path.append(r'C:\Users\li_pe\AppData\Local\Continuum\Anaconda2\pkgs\gdal-2.1.0-py27_0\Scripts')

import gdal_merge



def merge(sourFile, outputPath, id, name = None, nodata = -9999):
    
    os.chdir(sourFile)
    
    L = []  
    
    L.insert(0,'')
        
    L.extend(['-o', outputPath, '-of', 'GTiff',  '-a_nodata', '-9999', '-n', str(nodata)])  
        
    if os.path.exists(os.path.dirname(outputPath)) == False:
            
        os.makedirs(os.path.dirname(outputPath))

    for file in os.listdir(sourFile):
        
        if os.path.isdir(file) and id in file:
            
            sourTiff = sourFile + '\\' + file + '\\' + file + name
            
            L.append(sourTiff)
            
        elif file.endswith('.tif') and id in file:
            
            sourTiff = sourFile + '\\' + file 
            
            L.append(sourTiff)
            
        sourTiff = None
          
    sys.argv = L
    print L    
#    gdal_merge.main()
    
    print 'Done.'
    
    
sourFolder = r'\\fram\exchange\simon\MITIP\DEM\030422138591618'
outputFoler = r'\\fram\exchange\simon\MITIP\DEM\030422138591618\merged'
os.chdir(sourFolder)

DEM = []
for files in os.listdir(sourFolder):
    if 'ASTG' in files:
        folder = os.path.abspath(files)
        for tif in os.listdir(folder):
            if 'dem' in tif and tif.endswith('.tif'):
                DEM.append(os.path.join(folder, tif))

outputFile = r'ASTGTM2_DEM_merged.tif'

command = []

command.insert(0, '')

command.extend(['-o', os.path.join(outputFoler, outputFile), '-of', 'GTiff',  '-a_nodata', '-9999', '-n', '-9999'])

command.extend(DEM) 

sys.argv = command

gdal_merge.main()
                
    
    

#sourFile = r'E:\Penghua\data\LST\Lybien-1\new_selected_data'
#
#for files in os.listdir(sourFile):  
#    
#    folder = os.path.join(sourFile, files)
#    
#    outputPath = os.path.join(folder, r'MOD11A1_LST.tif')
#    
#    L = []  
#    
#    L.insert(0,'')
#        
#    L.extend(['-o', outputPath, '-of', 'GTiff',  '-a_nodata', '-9999', '-n', '-9999'])
#    
#    for img in os.listdir(folder):
#        
#        if img.endswith('.tif') and 'MOD' in img:
#            
#            L.append(os.path.join(folder, img))
#            
#    sys.argv = L
#    
#    gdal_merge.main()
    
#sourFile1 = r'E:\Penghua\data\emissivity_map\emissivity_map_Chile\030418575278187'
#
#sourFile2 = r'E:\Penghua\data\emissivity_map\emissivity_map_Portugal\merged'
#
#sourFile3 = r'E:\Penghua\data\DEM\Chile\030418574118118'
#
#name = '_Emissivity_Mean.tif'
#
#id = list(range(37,44))
#
#id2 = 'AG100'
#
#id3 = 'dem'
#outputPath1 = r'E:\Penghua\data\emissivity_map\emissivity_map_Chile\030418575278187\merged\emissivity_map_Chile.tif'
#merge(sourFile1, outputPath1, id2, name)
#for id1 in id:
#    
#    id1_s = str(id1)
#    
#    outputPath1 = r'E:\Penghua\data\DEM\Chile\030418574118118\merged\ASTGTM' + id2 + '.tif'
#
#    merge(sourFile1, outputPath1, id1_s, name)
#
#    
#outputPath2 = sourFile2 + '\\emissivity_map_Portugal.tif'
#    
#merge(sourFile2, outputPath2, id2)


#import os, glob
#
#dir_name=r"E:\Penghua\data\emissivity_map\emissivity_map_Chile\030418575278187"
#directories = filter(os.path.isdir, os.listdir(dir_name))
#print(directories)
#
#for dir in directories:
#  #print(dir)
#  glob.glob(dir+"*_Emissivity_Mean.tif")
#  for file in glob.glob(dir+"\*_Emissivity_Mean.tif"):
#    print(file)
#    
#    outputPath1 = file
#    merge(sourFile1, outputPath1, id1_s, name)

#outputPath3 = sourFile3 + '\\merged\\astgtm2_DEM.tif'
#
#merge(sourFile3, outputPath3, id3)

#sourFile4 = r'E:\Penghua\data\LST\Lybien-1\2017.04.04\0404\repro'
#output = sourFile4 + r'\MOD11_LST_repro.tif'
#id = '11'
#merge(sourFile4, output, id)





#import subprocess
#
#merge_command = ["python", gm, "-o", r"E:\merge.tif", r"E:\AG100.v003.64.-015.0001_Emissivity_Mean_Repro.tif",  r"E:\AG100.v003.64.-016.0001_Emissivity_Mean_Repro.tif"]
#
#subprocess.call(merge_command,shell=True)
