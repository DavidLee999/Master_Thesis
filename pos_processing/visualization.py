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

data_dir = r'E:\Penghua\data\Portugal\2016.08.11\TET\ac_results'
raster_file = r'FBI_TET1_20160811T133543_20160811T133705_L2_C_EL-04047_cobined_MIR_TIR_tem.tif'
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

#Read the data into a 2D Numeric array with ReadAsArray(<xoff>, <yoff>, <xsize>, <ysize>)
# Etna: 820, 2100, 50, 50 Stromboli: 950, 1335, 30, 30 Bardarbunga1: 1385, 1675, 200, 200 Bardarbunga2: 1525, 1680, 200, 200 Chile: 200, 2350, 500, 600
effective_fire_subarea = FRP_band.ReadAsArray(700, 900, 400, 500)

mask_nodatavalue = effective_fire_subarea == 0
masked_effective_fire_subarea = np.ma.array(effective_fire_subarea, mask = mask_nodatavalue, fill_value = 0)

plt.imshow(masked_effective_fire_subarea, cmap = 'gist_heat_r') #'hot_r' 'gist_heat_r'
plt.title('Portugal: fire radiactive power [MW]')
plt.colorbar()