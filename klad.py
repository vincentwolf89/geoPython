from osgeo import ogr
from shapely.geometry import MultiLineString, Point
from shapely import wkt
import sys

## set the driver for the data
driver = ogr.GetDriverByName("FileGDB")
################################################################################
## CHANGE gdb, input_lyr_name, distance, output_pts (optional)

## path to the FileGDB
gdb = r'D:\Projecten\WSRL\temp_sh.gdb'
## open the GDB in write mode (1)
ds = driver.Open(gdb, 1)

## single linear feature
input_lyr_name = "trajectlijnSH"

## distance between each points
distance = 10

## output point fc name
output_pts = "{0}_{1}m_points".format(input_lyr_name, distance)
################################################################################

## reference the layer using the layers name
if input_lyr_name in [ds.GetLayerByIndex(lyr_name).GetName() for lyr_name in range(ds.GetLayerCount())]:
    lyr = ds.GetLayerByName(input_lyr_name)
    print ("{0} found in {1}".format(input_lyr_name, gdb))
## if the feature class cannot be found exit gracefully
else:
    print ("{0} NOT found in {1}".format(input_lyr_name, gdb))
    sys.exit()

