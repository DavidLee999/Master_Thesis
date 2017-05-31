# -*- coding: utf-8 -*-
"""
Created on Wed May 17 10:41:05 2017

@author: li_pe
"""
import os, sys
from osgeo import gdal
from osgeo import osr

sys.path.append(r'C:\Users\li_pe\AppData\Local\Continuum\Anaconda2\pkgs\gdal-2.1.0-py27_0\Scripts')

import gdal_merge


def band_merge(inputimg, outputimg):
    
    L = []
    
    L.append('')
        
    L.extend(['-o', outputimg, '-of', 'GTiff', '-n', '-9999', '-a_nodata', '-9999'])  
    
    L.append('-separate')
    
    for bands in inputimg:
        
        L.append(bands)
       
    sys.argv = L
    
    gdal_merge.main()
    

sourFolder = r'E:\Penghua\data\Portugal'

inputimg = []

for files in os.listdir(sourFolder):
    
    TET_folder = sourFolder + '\\' + files + '\\' + 'TET'
    
    for img in os.listdir(TET_folder):
        
        if 'MWIR' in img:
            
            resultImgName = img.split('MWIR')[0] + 'cobined_MIR_TIR.tif'
            
            outputimg = os.path.join(TET_folder, resultImgName)
            
            inputimg.insert(0, os.path.join(TET_folder, img))
            
        else:
            
            inputimg.append(os.path.join(TET_folder, img))
            
    band_merge(inputimg, outputimg)
       
    inputimg = []  

