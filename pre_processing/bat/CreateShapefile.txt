SET MYPATH=E:\Penghua\data\georeferenced_TET\Portugal\alpha_channel

FOR %i IN (%MYPATH%\*.tif) DO (
    python gdal_polygonize.py -b 2 %i -f "ESRI Shapefile" %MYPATH%\%~ni.shp
)