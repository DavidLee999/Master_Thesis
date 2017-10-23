# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 09:42:33 2017

@author: li_pe
"""

import numpy as np
import matplotlib.pyplot as plt
import os, sys
from osgeo import gdal

plt.ion()
plt.show()

gdal.AllRegister()

data_dir = r'E:\Penghua\data\Etna\2014.06.22\TET\ac_results'
raster_file = r'FBI_TET1_20140622T232052_20140622T232155_L2_002589_WHM_cobined_MIR_TIR_tem.tif'
input_raster = os.path.join(data_dir, raster_file)

raster = gdal.Open(input_raster)

rows = raster.RasterYSize
cols = raster.RasterXSize
bands = raster.RasterCount

if bands > 2:
    temperature_MIR_band = raster.GetRasterBand(1)
    temperature_TIR_band = raster.GetRasterBand(2)
    fire_probability_band = raster.GetRasterBand(3)
    effective_fire_temp_band = raster.GetRasterBand(4)
    effective_pixel_port_band = raster.GetRasterBand(5)
    FRP_band = raster.GetRasterBand(6)
    
temperature_MIR = temperature_MIR_band.ReadAsArray(0, 0, cols, rows)
temperature_TIR = temperature_TIR_band.ReadAsArray(0, 0, cols, rows)
fire_probability = fire_probability_band.ReadAsArray(0, 0, cols, rows)
effective_fire_temp = effective_fire_temp_band.ReadAsArray(0, 0, cols, rows)
effective_pixel_port = effective_pixel_port_band.ReadAsArray(0, 0, cols, rows)
FRP = FRP_band.ReadAsArray(0, 0, cols, rows)

#effective_fire_temp_subarea = effective_fire_temp_band.ReadAsArray(0, 0, cols, rows) # 750, 2020, 200, 200
temperature_MIR_subarea = temperature_MIR_band.ReadAsArray(0, 0, cols, rows)

mask_nodatavalue = temperature_MIR_subarea == 0
masked_temperature_MIR_subarea = np.ma.array(temperature_MIR_subarea, mask = mask_nodatavalue, fill_value = 0)

plt.imshow(masked_temperature_MIR_subarea, cmap = 'hot_r')
plt.title('Etna: fire radiative power (FRP)')
plt.colorbar()