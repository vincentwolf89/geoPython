import arcpy
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")

arcpy.env.workspace = r'D:\GoogleDrive\WSRL\test_vergridden.gdb'
arcpy.env.overwriteOutput = True

lijn = "waterloop_lijn_13"
vlak = "waterloop_13"
smooth = "waterloop_lijn_13_smooth"

waterlopen = "waterlopen_safe"

## middenvlak creeren ##
# waterloop afronden (lijn)
arcpy.SmoothLine_cartography(lijn, smooth, "PAEK", "10 Meters", "FIXED_CLOSED_ENDPOINT", "NO_CHECK")
# euclidean raster
arcpy.gp.EucDistance_sa(smooth, "temp_euclidean", "", "0,25","")
# slope euclidean raster
arcpy.gp.Slope_sa("temp_euclidean", "temp_slope", "DEGREE", "1")
# rastercalc
raster = arcpy.Raster("temp_slope")
outraster = raster <= 38
outraster.save("temp_rastercalc")
# clip raster with polygon
arcpy.Clip_management("temp_rastercalc", "", "temp_clip", vlak, "127", "ClippingGeometry", "MAINTAIN_EXTENT")
# clip to polygon
arcpy.RasterToPolygon_conversion("temp_clip", "temp_poly", "SIMPLIFY", "Value")
# remove items with gridcode 0
with arcpy.da.UpdateCursor("temp_poly", "gridcode") as cursor:
    for row in cursor:
        if row[0] is 0:
            cursor.deleteRow()
        else:
            pass


## middenlijn creeren ##
# selecteer waterloop lijn in polygoon
arcpy.MakeFeatureLayer_management(waterlopen, "temp_waterlopen")
arcpy.SelectLayerByLocation_management("temp_waterlopen", 'intersect', "temp_poly",selection_type="NEW_SELECTION")
arcpy.CopyFeatures_management("temp_waterlopen","waterlopen_binnenpoly")
# profielen op lijn van waterloop
# knip profielen af op rand polygoon
# punten om de x meter op geknipte profielen
# haakse profielen op punten
# profielen knippen op grenzen polyline

# profielen als input voor centerpoints

# centerpoints clippen met euclidean distance middenvlak

# centerline bepalen

