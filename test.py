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
# library


# import matplotlib.pyplot as plt
# import numpy as np
# ind = np.arange(7)
# x1 = [0, 7, 13, 18, 28, 37, 48] #left edge
# x2 = [4, 8, 20, 49, 60, 80, 100] #right edge
#
#
# y = [0.9375, 0.94907407407777766, 0.82857142858571442, 0.88095238094999995, 0.92164902996666676, 0.93453570191250002, 0.94003687729000018]
# w = np.array(x2) - np.array(x1) #variable width, can set this as a scalar also
# # plt.xticks(x1+w, x1)
#
# plt.bar(x1, y, width=w, align='edge', edgecolor='black', linewidth=1.2)
# # plt.show()
#
# # library
