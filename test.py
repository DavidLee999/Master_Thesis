# -*- coding: utf-8 -*-
"""
Created on Mon Jul 03 15:58:24 2017

@author: li_pe
"""

from scipy.ndimage import *
import numpy as np
from PIL import Image
import gdal, osr, math

im = gdal.Open(r'E:\Penghua\data\Bardarbunga\2014.09.14_new\TET\FBI_TET1_20140914T022014_20140914T022136_L2_combined_gb_surface.tif')

geotransform = im.GetGeoTransform()
originX = geotransform[0]
originY = geotransform[3]
pixelWidth = geotransform[1]
pixelHeight = geotransform[5]

MIR_bbr_band = im.GetRasterBand(1)
TIR_bbr_band = im.GetRasterBand(2)

MIR_bbr_data = MIR_bbr_band.ReadAsArray()
TIR_bbr_data = TIR_bbr_band.ReadAsArray()

MIR_data = MIR_bbr_data.copy()
TIR_data = TIR_bbr_data.copy()

logic1 = np.where(MIR_bbr_data >= 1)
logic2 = np.where(MIR_bbr_data < 1)

MIR_bbr_data[logic1] = 255
MIR_bbr_data[logic2] = 0
            
logic3 = np.where(TIR_bbr_data >= 7)
logic4 = np.where(TIR_bbr_data < 7)
            
TIR_bbr_data[logic3] = 255
TIR_bbr_data[logic4] = 0
                   
struct = generate_binary_structure(2,2)

dia_img1 = binary_dilation(MIR_bbr_data, struct, 4)
dia_img2 = binary_dilation(MIR_bbr_data, struct, 1)

dia_img1[np.where(dia_img2 == True)] = False
         
#MIR_bbr_data[np.where(dia_img1 == True)] = 255
#MIR_bbr_data[np.where(dia_img1 == False)] = 0

dia_img3 = binary_dilation(TIR_bbr_data, struct, 4)
dia_img4 = binary_dilation(TIR_bbr_data, struct, 1)

dia_img3[np.where(dia_img4 == True)] = False

              
hot_mean1 = MIR_data[logic1].mean()
bg_mean1 = MIR_data[np.where(dia_img1 == True)].mean()
bg_std1 = MIR_data[np.where(dia_img1 == True)].std()

hot_mean2 = TIR_data[logic3].mean()
bg_mean2 = TIR_data[np.where(dia_img3 == True)].mean()
bg_std2 = TIR_data[np.where(dia_img3 == True)].std()

sumRow1 = 0
sumCol1 = 0
diff_sum1 = 0
gray_value_sum1 = 0
for i in range(logic1[0].shape[0]):
    
    gray_value1 = MIR_data[logic1[0][i]][logic1[1][i]]
    gray_value_sum1 = gray_value_sum1 + gray_value1
    
    diff1 = gray_value1 - bg_mean1
    diff_sum1 = diff_sum1 + diff1
    
    sumRow1 = sumRow1 + logic1[0][i] * diff1
    sumCol1 = sumCol1 + logic1[1][i] * diff1

x_c1 = sumRow1 / diff_sum1
y_c1 = sumCol1 / diff_sum1

sumRow2 = 0
sumCol2 = 0
diff_sum2 = 0
gray_value_sum2 = 0
for i in range(logic3[0].shape[0]):
    
    gray_value2 = TIR_data[logic3[0][i]][logic3[1][i]]
    gray_value_sum2 = gray_value_sum2 + gray_value2
    
    diff2 = gray_value2 - bg_mean2
    diff_sum2 = diff_sum2 + diff2
    
    sumRow2 = sumRow2 + logic3[0][i] * diff2
    sumCol2 = sumCol2 + logic3[1][i] * diff2

x_c2 = sumRow2 / diff_sum2
y_c2 = sumCol2 / diff_sum2

z = (hot_mean1 - bg_mean1) / (hot_mean2 - bg_mean2)

rad = (bg_mean1 - z*bg_mean2) / (1 - z)
p = (hot_mean1 - bg_mean1) / (rad - bg_mean1)

Af_mir = p * logic1[0].shape[0] / 4
Af_tir = p * logic3[0].shape[0] / 4


                   
k1_mir = 155890700
k2_mir = 3821.000

k1_tir = 2105042
k2_tir = 1613.220

T_mir = k2_mir / math.log(k1_mir/(rad*1000) + 1, math.e)
T_tir = k2_tir / math.log(k1_tir/(rad*1000) + 1, math.e)

em = gdal.Open(r'E:\Penghua\data\Bardarbunga\data_for_Bardarbunga_20140914\emissivity_map\emissivity_cut\emissivity_map_UTM28N_Band2_8.6_cut.tif')

em_band = em.GetRasterBand(1)
em_data = em.ReadAsArray()

em_mir = em_data[logic1].mean() / 1000
em_tir = em_data[logic3].mean() / 1000
                
#Tk_mir = T_mir * (1 / pow(em_mir, 0.25))
#Tk_tir = T_tir * (1 / pow(em_tir, 0.25))

sigma = 0.00000005670367

FRP = sigma * pow(T_mir, 4)
#cols = MIR_bbr_data.shape[1]
#rows = MIR_bbr_data.shape[0]

#driver = gdal.GetDriverByName('GTiff')
#outRaster = driver.Create('test2.tif', cols, rows, 1, gdal.GDT_Byte) 
#
#outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
#
#outband = outRaster.GetRasterBand(1)
#
#outband.WriteArray(MIR_bbr_data)
#
#outRasterSRS = osr.SpatialReference()
#outRasterSRS.ImportFromWkt(im.GetProjectionRef())
#outRaster.SetProjection(outRasterSRS.ExportToWkt())
#
#outband.FlushCache()

#fire_potential_img = Image.fromarray(fire_potential_data,'L')
#fire_potential_img.save('test.jpg')