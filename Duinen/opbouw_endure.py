import matplotlib.pyplot as plt
import numpy as np
from numpy import ma
import rasterio

from osgeo import gdal
from osgeo import osr



ds = gdal.Open(r'C:\Users\vince\Desktop\GIS\losse rasters\clip_test1.tif')
# prj=ds.GetProjection()
# print prj
#
# width = ds.RasterXSize
# height = ds.RasterYSize
#
# print width, height



myarray = np.array(ds.GetRasterBand(1).ReadAsArray())

ndv = ds.GetRasterBand(1).GetNoDataValue()
masked_data = ma.masked_where(myarray == ndv, myarray)

myarray = masked_data


x0, y0 = 60, 10 # These are in _pixel_ coordinates!!
x1, y1 = 70, 80
num = 100
x, y = np.linspace(x0, x1, num), np.linspace(y0, y1, num)

# Extract the values along the line
zi = myarray[x.astype(np.int), y.astype(np.int)]

fig, axes = plt.subplots(nrows=2)
axes[0].imshow(myarray)
axes[0].plot([x0, x1], [y0, y1], 'ro-')
axes[0].axis('image')

axes[1].plot(zi)

plt.show()