# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 10:32:08 2017

@author: li_pe
"""
import os, shutil
import numpy as np
from osgeo import gdal, gdalnumeric, gdalconst
import xlrd, xlwt

def compare ( TET_tem_path, SST_tem_path, outputFile ):
    if os.path.exists(outputFile) == False:
        os.mkdir(outputFile)
    elif os.path.exists(outputFile) == True:
        return
    
    os.chdir(outputFile)
    
    TET_tem = gdal.Open(TET_tem_path)
    SST_tem = gdal.Open(SST_tem_path)
    
    MIR_band = TET_tem.GetRasterBand(1)
    TIR_band = TET_tem.GetRasterBand(2)
    SST_band = SST_tem.GetRasterBand(1)
    
    MIR_data = MIR_band.ReadAsArray()
    TIR_data = TIR_band.ReadAsArray()
    SST_data = SST_band.ReadAsArray()
    
    default_tem = 274.15 * np.ones(SST_data.shape)
    
#    MIR_deg = MIR_data + default_tem
#    TIR_deg = TIR_data + default_tem

    SST_K = SST_data # + default_tem
    diff_MIR = MIR_data - SST_K
    diff_TIR = TIR_data - SST_K
    
    logic1 = np.where(np.absolute(diff_MIR)>50)
    diff_MIR[logic1] = 0
            
    logic2 = np.where(np.absolute(diff_TIR)>50)
    diff_TIR[logic2] = 0
    
    diff_MIR_max = diff_MIR.max()
    diff_TIR_max = diff_TIR.max()
    
    diff_MIR_min = diff_MIR.min()
    diff_TIR_min = diff_TIR.min()
    
    diff_MIR_mean = diff_MIR.mean()
    diff_TIR_mean = diff_TIR.mean()
    
    diff_MIR_std = diff_MIR.std()
    diff_TIR_std = diff_TIR.std()
    
    diff_MIR_median = np.median(diff_MIR[diff_MIR.nonzero()])
    diff_TIR_median = np.median(diff_TIR[diff_TIR.nonzero()])
    
    abs_diff_MIR = np.absolute(diff_MIR)
    abs_diff_TIR = np.absolute(diff_TIR)
    
    abs_diff_MIR_mean = abs_diff_MIR.mean()
    abs_diff_TIR_mean = abs_diff_TIR.mean()
    
    abs_diff_MIR_std = abs_diff_MIR.std()
    abs_diff_TIR_std = abs_diff_TIR.std()
    
    f = open( os.path.join(outputFile, 'statistics_info.txt'), 'w' )
    
    f.write('Difference between SST and TET temperature.\n')
    f.write('MIR band.\tUnit: degrees Celsius.\n')
    f.write('Maximum: %s.\nMinimum: %s.\n' %(str(diff_MIR_max), str(diff_MIR_min)))
    f.write('Mean: %s.\nStandard Deviation: %s.\nMedian Value: %s.\n' %(str(diff_MIR_mean), str(diff_MIR_std), str(diff_MIR_median)))
    f.write('Absolute Mean: %s.\nAbsolute Standard Deviation: %s.\n\n' %(str(abs_diff_MIR_mean), str(abs_diff_MIR_std)))
    
    f.write('Difference between SST and TET temperature.\n')
    f.write('TIR band.\tUnit: degrees Celsius.\n')
    f.write('Maximum: %s.\nMinimum: %s.\n' %(str(diff_TIR_max), str(diff_TIR_min)))
    f.write('Mean: %s.\nStandard Deviation: %s.\nMedian Value: %s.\n' %(str(diff_TIR_mean), str(diff_TIR_std), str(diff_TIR_median)))
    f.write('Absolute Mean: %s.\nAbsolute Standard Deviation: %s.\n' %(str(abs_diff_TIR_mean), str(abs_diff_TIR_std)))
    
    f.close()
            
    driver = gdal.GetDriverByName('GTiff')
    
    MIR_out = driver.Create('diff_MIR.tif', TET_tem.RasterXSize, TET_tem.RasterYSize, 1, MIR_band.DataType)
    gdalnumeric.CopyDatasetInfo(TET_tem, MIR_out)
    MIR_bandOut = MIR_out.GetRasterBand(1)
    MIR_bandOut.SetNoDataValue(0.0)
    gdalnumeric.BandWriteArray(MIR_bandOut, diff_MIR)
    
    TIR_out = driver.Create('diff_TIR.tif', TET_tem.RasterXSize, TET_tem.RasterYSize, 1, TIR_band.DataType)
    gdalnumeric.CopyDatasetInfo(TET_tem, TIR_out)
    TIR_bandOut = TIR_out.GetRasterBand(1)
    TIR_bandOut.SetNoDataValue(0.0)
    gdalnumeric.BandWriteArray(TIR_bandOut, diff_TIR)
    
    print 'end'

def cal (inputimg):
    
    diff = gdal.Open(inputimg)
    
    diff_band = diff.GetRasterBand(1)
    
    diff_data = diff_band.ReadAsArray()
    
    diff_data_mean = diff_data.mean()
    
    diff_data_std = diff_data.std()
    
    print diff_data_mean
    
    return diff_data_mean, diff_data_std

Location = ['Etna', 'Demmin', 'Lascar', 'Lybien-1', 'Lybien-2', 'Portugal']

sourFile = r'E:\Penghua\data' + '\\' + Location[4] #+ r'\self_test'

os.chdir(sourFile)

for files in os.listdir(sourFile):
    
    if '0' in files: # and files == '2016.08.14':
        
        folder = os.path.join(os.path.abspath(files), r'TET')
        
        LST = os.path.join(os.path.abspath(files), r'LST')
        
        for fil in os.listdir(folder):
            
            if 'ac_results' in fil:
                
                f = os.path.join(folder, fil)
                
                if len( os.listdir(f) ) != 0 :
                    
                    for img in os.listdir(f):
                        
                        if img.endswith('.tif') and 'tem' in img:
                            
                            tet_tem = os.path.join(f, img)
#                            print tet_tem
                    outputFile = os.path.join(f, 'compared')
#                    if os.path.exists(outputFile) == True:
#                        shutil.rmtree(outputFile)
                    for lst_img in os.listdir(LST):
                        
                        if lst_img.endswith('.tif') and 'LST' in lst_img:
                            
                            lst_tem = os.path.join(LST, lst_img)
#                            print lst_tem
                    compare(tet_tem, lst_tem, outputFile)
                    
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
#
#for files in os.listdir(sourFile):
#    
#    if '0' in files:
#        print files
#        sheet1.write(0, count, files)
#        
#        sheet2.write(0, count, files)
#        
#        if os.path.exists(os.path.join(os.path.abspath(files), r'TET\ac_results_1.20\compared\cut')) == True:
#        
#            ac_results = os.path.join(os.path.abspath(files), r'TET\ac_results_1.20\compared\cut')
#        
#            for fil in os.listdir(ac_results):
#            
#                if fil.endswith('.tif') and 'MIR_cut_rect2' in fil:
#                
#                    TET_tem_MIR2 = os.path.join(ac_results, fil)
#                    
#                if fil.endswith('.tif') and 'MIR_cut_rect4' in fil:
#                
#                    TET_tem_MIR4 = os.path.join(ac_results, fil)
#                    
#                if fil.endswith('.tif') and 'MIR_cut_rect6' in fil:
#                
#                    TET_tem_MIR6 = os.path.join(ac_results, fil)
#                    
#                if fil.endswith('.tif') and 'TIR_cut_rect2' in fil:
#                
#                    TET_tem_TIR2 = os.path.join(ac_results, fil)
#                    
#                if fil.endswith('.tif') and 'TIR_cut_rect4' in fil:
#                
#                    TET_tem_TIR4 = os.path.join(ac_results, fil)
#                    
#                if fil.endswith('.tif') and 'TIR_cut_rect6' in fil:
#                
#                    TET_tem_TIR6 = os.path.join(ac_results, fil)
#            
#            mean_MIR2, std_MIR2 = cal(TET_tem_MIR2)
#            
#            mean_MIR4, std_MIR6 = cal(TET_tem_MIR4)
#            
#            mean_MIR6, std_MIR6 = cal(TET_tem_MIR6)
#            
#            mean_TIR2, std_TIR2 = cal(TET_tem_TIR2)
#            
#            mean_TIR4, std_TIR6 = cal(TET_tem_TIR4)
#            
#            mean_TIR6, std_TIR6 = cal(TET_tem_TIR6)
#            
#            sheet1.write(1, count, float(mean_MIR2))
#            sheet1.write(2, count, float(mean_MIR4))
#            sheet1.write(3, count, float(mean_MIR6))
#            
#            sheet2.write(1, count, float(mean_TIR2))
#            sheet2.write(2, count, float(mean_TIR4))
#            sheet2.write(3, count, float(mean_TIR6))
#            
#        count = count + 1
#
#filename.save(os.path.join(sourFile, 'scale_factor_1.20.xls'))

#        SST = os.path.join(os.path.abspath(files), r'SST')
#        
#        for fi in os.listdir(SST):
#            
#            if fi.endswith('.tif') and 'SST' in fi:
#                
#                SST_tem_path = os.path.join(SST, fi)               
                
#    outputFile = os.path.join(os.path.split(TET_tem_path)[0], 'compared')
#    
#    compare(TET_tem_path, SST_tem_path, outputFile)
#    
#    os.chdir(sourFile)

