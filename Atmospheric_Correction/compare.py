# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 10:32:08 2017

@author: li_pe
"""
import os
import numpy as np
from osgeo import gdal, gdalnumeric, gdalconst

def compare ( TET_tem_path, SST_tem_path, outputFile ):
    if os.path.exists(outputFile) == False:
        os.mkdir(outputFile)
    
    os.chdir(outputFile)
    
    TET_tem = gdal.Open(TET_tem_path)
    SST_tem = gdal.Open(SST_tem_path)
    
    MIR_band = TET_tem.GetRasterBand(1)
    TIR_band = TET_tem.GetRasterBand(2)
    SST_band = SST_tem.GetRasterBand(1)
    
    MIR_data = MIR_band.ReadAsArray()
    TIR_data = TIR_band.ReadAsArray()
    SST_data = SST_band.ReadAsArray()
    
    default_tem = -273 * np.ones(MIR_data.shape)
    
    MIR_deg = MIR_data + default_tem
    TIR_deg = TIR_data + default_tem
    
    diff_MIR = SST_data - MIR_deg
    diff_TIR = SST_data - TIR_deg
    
    logic1 = np.where(np.absolute(diff_MIR)>20)
    diff_MIR[logic1] = 0
            
    logic2 = np.where(np.absolute(diff_TIR)>20)
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
    f.write('Absolute Mean: %s.\nAbsolute Standard Deviation: %s.\n' %(str(abs_diff_MIR_mean), str(abs_diff_MIR_std)))
    
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

TET_tem_path = r'E:\Penghua\data\Etna\2014.06.22\TET\ac_results\FBI_TET1_20140622T232052_20140622T232155_L2_002589_WHM_cobined_MIR_TIR_tem.tif'

SST_tem_path = r'E:\Penghua\data\Etna\2014.06.22\SST\A2014173003000.L2_LAC_SST_repro_UTM33N_repro_cut.tif'

outputFile = os.path.join(os.path.split(TET_tem_path)[0], 'compared')

compare(TET_tem_path, SST_tem_path, outputFile)