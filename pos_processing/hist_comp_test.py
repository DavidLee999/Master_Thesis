# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 15:18:05 2017

@author: li_pe
"""
from osgeo import gdal, ogr, osr
import numpy as np
import matplotlib.pyplot as plt
import os

x = np.arange(294.7, 301.8, 0.5)
#fig, axes = plt.subplots(6, 1, sharex = True)
#axes.flatten()
#n, bins, patches = axes[0].hist(MODISZoneArray[0].compressed(), bins = 100)
#axes[0].axvline(np.mean(MODISZoneArray[0]), color = 'red', linewidth = 0.5)
#axes[0].axvline(np.mean(MODISZoneArray[0])- np.std(MODISZoneArray[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
#axes[0].axvline(np.mean(MODISZoneArray[0])+ np.std(MODISZoneArray[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
#axes[0].set_title('MODIS', fontsize = 5)
#axes[0].set_yticks(range(0, 300, 50))
#axes[0].set_yticklabels(range(0, 300, 50), fontsize = 4)
#axes[0].grid()
#
#n, bins, patches = axes[1].hist(tet100[0].compressed(), bins = 100)
#axes[1].axvline(np.mean(tet100[0]), color = 'red', linewidth = 0.5)
#axes[1].axvline(np.mean(tet100[0])- np.std(tet100[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
#axes[1].axvline(np.mean(tet100[0])+ np.std(tet100[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
#axes[1].set_title('sub-area 1 with scale factor 1.00', fontsize = 5)
#axes[1].set_yticks(range(0, 250, 50))
#axes[1].set_yticklabels(range(0, 250, 50), fontsize = 5)
#axes[1].grid()
#
#n, bins, patches = axes[2].hist(tet105[0].compressed(), bins = 100)
#axes[2].axvline(np.mean(tet105[0]), color = 'red', linewidth = 0.5)
#axes[2].axvline(np.mean(tet105[0])- np.std(tet105[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
#axes[2].axvline(np.mean(tet105[0])+ np.std(tet105[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
#axes[2].set_title('sub-area 1 with scale factor 1.05', fontsize = 5)
#axes[2].set_yticks(range(0, 250, 50))
#axes[2].set_yticklabels(range(0, 250, 50), fontsize = 5)
#axes[2].grid()
#
#n, bins, patches = axes[3].hist(tet110[0].compressed(), bins = 100)
#axes[3].axvline(np.mean(tet110[0]), color = 'red', linewidth = 0.5)
#axes[3].axvline(np.mean(tet110[0])- np.std(tet110[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
#axes[3].axvline(np.mean(tet110[0])+ np.std(tet110[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
#axes[3].set_title('sub-area 1 with scale factor 1.10', fontsize = 5)
#axes[3].set_yticks(range(0, 250, 50))
#axes[3].set_yticklabels(range(0, 250, 50), fontsize = 5)
#axes[3].grid()
#
##n, bins, patches = axes[4].hist(tet115[0].compressed(), bins = 100)
##axes[4].axvline(np.mean(tet115[0]), color = 'red', linewidth = 0.5)
##axes[4].axvline(np.mean(tet115[0])- np.std(tet115[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
##axes[4].axvline(np.mean(tet115[0])+ np.std(tet115[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
##axes[4].set_title('sub-area 1 with scale factor 1.15', fontsize = 5)
##axes[4].set_yticks(range(0, 250, 50))
##axes[4].set_yticklabels(range(0, 250, 50), fontsize = 5)
##axes[4].grid()
#
#n, bins, patches = axes[4].hist(tet115[0].compressed(), bins = 100)
#axes[4].axvline(np.mean(tet115[0]), color = 'red', linewidth = 0.5)
#print np.mean(tet115[0])
#axes[4].axvline(np.mean(tet115[0])- np.std(tet115[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
#axes[4].axvline(np.mean(tet115[0])+ np.std(tet115[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
#axes[4].set_title('sub-area 1 with scale factor 1.15', fontsize = 5)
#axes[4].set_yticks(range(0, 250, 50))
#axes[4].set_yticklabels(range(0, 250, 50), fontsize = 6)
#axes[4].grid()
#
#n, bins, patches = axes[5].hist(tet120[0].compressed(), bins = 100)
#axes[5].axvline(np.mean(tet120[0]), color = 'red', linewidth = 0.5)
#axes[5].axvline(np.mean(tet120[0])- np.std(tet120[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
#axes[5].axvline(np.mean(tet120[0])+ np.std(tet120[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
#axes[5].set_title('sub-area 1 with scale factor 1.20', fontsize = 5)
#axes[5].set_yticks(range(0, 250, 50))
#axes[5].set_yticklabels(range(0, 250, 50), fontsize = 5)
#axes[5].grid()
#
#plt.xticks(x,rotation = 30, fontsize = 5)
#plt.xlabel('temperature', fontsize = 5)
#
#fig.tight_layout()
#fig.savefig(os.path.join(r'E:\Penghua\results', 'test.png'), dpi = 500)

fig, axes = plt.subplots(3, 1)

n, bins, patches = axes[0].hist(MODISZoneArray[0].compressed(), bins = 100)
axes[0].axvline(np.mean(MODISZoneArray[0]), color = 'red', linewidth = 0.5)
axes[0].axvline(np.mean(MODISZoneArray[0])- np.std(MODISZoneArray[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
axes[0].axvline(np.mean(MODISZoneArray[0])+ np.std(MODISZoneArray[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
axes[0].set_title('MODIS', fontsize = 5)
axes[0].set_xticks(x)
axes[0].set_xticklabels(x, rotation = 30, fontsize = 5)
axes[0].set_yticks(range(0, 300, 50))
axes[0].set_yticklabels(range(0, 300, 50), fontsize = 6)
axes[0].grid()

n, bins, patches = axes[1].hist(tet100[0].compressed(), bins = 100)
axes[1].axvline(np.mean(tet100[0]), color = 'red', linewidth = 0.5)
axes[1].axvline(np.mean(tet100[0])- np.std(tet100[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
axes[1].axvline(np.mean(tet100[0])+ np.std(tet100[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
axes[1].set_title('sub-area 1 with scale factor 1.00', fontsize = 5)
axes[1].set_xticks(x)
axes[1].set_xticklabels(x, rotation = 30, fontsize = 5)
axes[1].set_yticks(range(0, 250, 50))
axes[1].set_yticklabels(range(0, 250, 50), fontsize = 6)
axes[1].grid()

n, bins, patches = axes[2].hist(tet105[0].compressed(), bins = 100)
axes[2].axvline(np.mean(tet105[0]), color = 'red', linewidth = 0.5)
axes[2].axvline(np.mean(tet105[0])- np.std(tet105[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
axes[2].axvline(np.mean(tet105[0])+ np.std(tet105[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
axes[2].set_title('sub-area 1 with scale factor 1.05', fontsize = 5)
axes[2].set_xticks(x)
axes[2].set_xticklabels(x, rotation = 30, fontsize = 5)
axes[2].set_yticks(range(0, 250, 50))
axes[2].set_yticklabels(range(0, 250, 50), fontsize = 6)
axes[2].grid()

#plt.xticks(x,rotation = 30, fontsize = 5)
#plt.xlabel('temperature', fontsize = 5)
fig.tight_layout()
fig.savefig(os.path.join(r'E:\Penghua\results', 'test1.png'), dpi = 500)
plt.show()

fig2, axes2 = plt.subplots(3, 1)

n, bins, patches = axes2[0].hist(tet110[0].compressed(), bins = 100)
axes2[0].axvline(np.mean(tet110[0]), color = 'red', linewidth = 0.5)
axes2[0].axvline(np.mean(tet110[0])- np.std(tet110[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
axes2[0].axvline(np.mean(tet110[0])+ np.std(tet110[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
axes2[0].set_title('sub-area 1 with scale factor 1.10', fontsize = 5)
axes2[0].set_xticks(x)
axes2[0].set_xticklabels(x, rotation = 30, fontsize = 5)
axes2[0].set_yticks(range(0, 250, 50))
axes2[0].set_yticklabels(range(0, 250, 50), fontsize = 6)
axes2[0].grid()

n, bins, patches = axes2[1].hist(tet115[0].compressed(), bins = 100)
axes2[1].axvline(np.mean(tet115[0]), color = 'red', linewidth = 0.5)
print np.mean(tet115[0])
axes2[1].axvline(np.mean(tet115[0])- np.std(tet115[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
axes2[1].axvline(np.mean(tet115[0])+ np.std(tet115[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
axes2[1].set_title('sub-area 1 with scale factor 1.15', fontsize = 5)
axes2[1].set_xticks(x)
axes2[1].set_xticklabels(x, rotation = 30, fontsize = 5)
axes2[1].set_yticks(range(0, 250, 50))
axes2[1].set_yticklabels(range(0, 250, 50), fontsize = 6)
axes2[1].grid()

n, bins, patches = axes2[2].hist(tet120[0].compressed(), bins = 100)
axes2[2].axvline(np.mean(tet120[0]), color = 'red', linewidth = 0.5)
axes2[2].axvline(np.mean(tet120[0])- np.std(tet120[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
axes2[2].axvline(np.mean(tet120[0])+ np.std(tet120[0]), color = 'red', linestyle = 'dashed', linewidth = 0.5)
axes2[2].set_title('sub-area 1 with scale factor 1.20', fontsize = 5)
axes2[2].set_xticks(x)
axes2[2].set_xticklabels(x, rotation = 30, fontsize = 5)
axes2[2].set_yticks(range(0, 250, 50))
axes2[2].set_yticklabels(range(0, 250, 50), fontsize = 6)
axes2[2].grid()

#plt.xticks(x,rotation = 90, fontsize = 4)
plt.xlabel('temperature', fontsize = 5)

fig2.tight_layout()
fig2.savefig(os.path.join(r'E:\Penghua\results', 'test2.png'), dpi = 500)
plt.show()




from PIL import Image

images = map(Image.open, ['Test1.jpg', 'Test2.jpg'])
widths, heights = zip(*(i.size for i in images))
total_height = sum(heights)
max_width = max(widths)
new_img = Image.new('RGB', (max_width, total_height))
yoff = 0
for im in images:
    new_img.paste(im, (0, yoff))
    yoff += im.size[1]
new_img.save(os.path.join(r'E:\Penghua\results', 'test_merged.png'))