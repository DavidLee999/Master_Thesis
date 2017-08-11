# -*- coding: utf-8 -*-
"""
Created on Tue May 16 13:54:21 2017

@author: li_pe
"""
from osgeo import gdal
from osgeo import osr, ogr
import subprocess
import os


def cut (inputshapefile, inputimg, outputimg, nodata=-9999):
    
    command = ['gdalwarp', '-of', 'GTiff', '-crop_to_cutline']
    
    command.extend(['-cutline', inputshapefile])
    
    command.extend([inputimg, '-overwrite', outputimg])
    
    subprocess.call(command)
    
    print 'end.'



Location = ['Etna', 'Demmin', 'Lascar', 'Lybien-1', 'Lybien-2', 'Portugal']

outputFile = r'E:\Penghua\data' + '\\' + Location[4]

#shapefile = r'E:\Penghua\data\Etna\shapefiles\rect2.shp'

#sourFile = r'E:\Penghua\data' + '\\' + Location[0]
#os.chdir(sourFile)
#
#for files in os.listdir(sourFile):
#    
#    if os.path.exists(os.path.join(os.path.abspath(files), r'TET\ac_results_1.20\compared')) == True:
#        
#        ac_results = os.path.join(os.path.abspath(files), r'TET\ac_results_1.20\compared')
#        
#    else:
#        
#        continue
#    
#    if os.listdir(ac_results) != []:
#        
#        for fil in os.listdir(ac_results):
#            
#            if fil.endswith('.tif') and 'MIR' in fil:
#                
#                TET_tem_path1 = os.path.join(ac_results, fil)
#                
#            if fil.endswith('.tif') and 'TIR' in fil:
#                
#                TET_tem_path2 = os.path.join(ac_results, fil)
#                
#        SST = os.path.join(os.path.abspath(files), r'SST')
#        
#        for fi in os.listdir(SST):
#            
#            if fi.endswith('.tif') and 'SST' in fi:
#                
#                SST_tem_path = os.path.join(SST, fi)
#    
#        outputFolder = os.path.join(os.path.split(TET_tem_path1)[0], 'cut')
#        
#        if os.path.exists(outputFolder) == False:
#            
#            os.mkdir(outputFolder)
#            
#        outputFile1 = os.path.join(outputFolder, 'diff_MIR_cut_rect2.tif')
#        
#        outputFile2 = os.path.join(outputFolder, 'diff_TIR_cut_rect2.tif')
#        
#        outputFile3 = os.path.join(os.path.split(SST_tem_path)[0], 'diff_SST_cut.tif')
#    
#        cut(shapefile, TET_tem_path1, outputFile1)
#        cut(shapefile, TET_tem_path2, outputFile2)
#        cut(shapefile, SST_tem_path, outputFile3)
                    
                
outputfolder = []

   
sourFile = r'E:\Penghua\data\georeferenced_TET' + '\\' + Location[4] + r'\new_selected_data\alpha_channel'

inputShapefile = []

for shp in os.listdir(sourFile):
    
    if shp.endswith('.shp'):
        
        inputShapefile.append(os.path.join(sourFile, shp))


sourWV = r'E:\Penghua\data\corresponding_water_vapor' + '\\' + Location[4] + '\\new_selected_data'

inputWV = []

outputWV = []

counter = 0

for WV in os.listdir(sourWV):
    
    folder = outputFile+'\\'+WV
    
#    if os.path.exists(folder) == False:
#        
#        os.makedirs(folder)
#        
#        os.makedirs(folder+'\\'+'water_vapor')
#        
#        os.makedirs(folder+'\\'+'TET')
#        
#        os.makedirs(folder+'\\'+'emivissivity_map')
#        
#        os.makedirs(folder+'\\'+'DEM')
#        
    os.makedirs(folder+'\\'+'LST')
    
    outputfolder.append(folder)
        
    folder_WV = sourWV + '\\' + WV + '\\' + 'repro'
    
    for file_WV in os.listdir(folder_WV):
        
        if file_WV.endswith('.tif'):
            
            inputWV.append(os.path.join(folder_WV, file_WV))
            
            name, postfix = os.path.splitext(file_WV)
            
            outputWV.append(os.path.join(outputfolder[counter]+'\\'+'water_vapor', name+'_cut.tif'))
    
    counter = counter + 1
#    
#    
#sourTET = r'E:\Penghua\data\georeferenced_TET' + '\\' + Location[4] + '\\new_selected_data'
#
#inputTET = []
#
#outputTET = []
#
#counter = 0
#
#for tet in os.listdir(sourTET):
#    
#    if 'TET' in tet:
#        
#        #print tet
#    
#        folder_TET = sourTET + '\\' + tet + '\\' + 'repro'
#    
#        for file_TET in os.listdir(folder_TET):
#        
#            if file_TET.endswith('.tif') and ('LWIR' in file_TET or 'MWIR' in file_TET):
#            
#                inputTET.append(os.path.join(folder_TET, file_TET))
#            
#                name, postfix  = os.path.splitext(file_TET)
#                        
#                outputTET.append(os.path.join(outputfolder[counter]+'\\'+'TET', name+'_cut.tif'))
#            
#        counter = counter + 1
#    
#    
#    
#emissivity = r'E:\Penghua\data\emissivity_map' + '\\emissivity_map_' + Location[4] + r'\merged\repro'
#
#inputEmi = []
#
#outputEmi = []
#
#for emi in os.listdir(emissivity):
#    
#    if emi.endswith('.tif') and 'band' in emi:
#        
#        inputEmi.append(os.path.join(emissivity, emi))
#        
#for folder in outputfolder:
#
#    abspath, name = os.path.split(inputEmi[0])
#    
#    emi_name, postfix = os.path.splitext(name)
#        
#    outputEmi.append(os.path.join(folder+'\\'+'emivissivity_map', emi_name + '_cut.tif'))
#
#    abspath, name = os.path.split(inputEmi[1])
#    
#    emi_name, postfix = os.path.splitext(name)
#        
#    outputEmi.append(os.path.join(folder+'\\'+'emivissivity_map', emi_name + '_cut.tif'))
#
#
#DEM = r'E:\Penghua\data\DEM' + '\\' + Location[4] + '\\merged\\repro'
#
#inputDEM =  DEM + '\\astgtm2_DEM_repro.tif'
#
#outputDEM = []
#
#for folders in outputfolder:
#    
#    folder, name = os.path.split(inputDEM)
#    
#    dem_name, postfix = os.path.splitext(name)
#    
#    outputDEM.append(os.path.join(folders+'\\'+'DEM', dem_name + '_cut.tif'))

sst = r'E:\Penghua\data\LST' + '\\' + Location[3] + r'\new_selected_data'

inputSST = []

outputSST = []

os.chdir(sst)

counter = 0

for files in os.listdir(sst):
    
    if os.path.isdir(files) == True:
        
        folders = os.path.abspath(files) + '\\repro'
        
        for fil in os.listdir(folders):
                    
            if fil.endswith('.tif') and 'LST' in fil:
                
                inputSST.append(folders + '\\' + fil)
                
                outputSST.append(outputfolder[counter] + '\\LST\\' + os.path.splitext(fil)[0] + '_cut.tif')
                
                counter = counter + 1



counter = 0

for shapefile in inputShapefile:
    
#    cut(shapefile, inputWV[counter], outputWV[counter])
#    
#    cut(shapefile, inputTET[2*counter], outputTET[2*counter])
#    
#    cut(shapefile, inputTET[2*counter+1], outputTET[2*counter+1])
#    
#    cut(shapefile, inputEmi[0], outputEmi[2*counter])
#    
#    cut(shapefile, inputEmi[1], outputEmi[2*counter+1])
#
#    cut(shapefile, inputDEM, outputDEM[counter], 0)
    
#    cut(shapefile, inputSST[counter], outputSST[counter])
    
    counter = counter + 1
