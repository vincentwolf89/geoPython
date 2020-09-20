import arcpy

arcpy.env.workspace = r"D:\Projecten\HDSR\2020\gisData\batchesWaterlopen\batch6.gdb"
arcpy.env.overwriteOutput = True

featureclasses = arcpy.ListRasters()
rasterlijst = []

sr = arcpy.SpatialReference(28992)
for raster in featureclasses:
    if raster.startswith('waterloopRaster'):
        rasterlijst.append(str(raster))
    if raster.startswith('waterloopRaster137'):
        break



print rasterlijst

arcpy.MosaicToNewRaster_management(rasterlijst, arcpy.env.workspace, "tm137",
                                           sr, "32_BIT_FLOAT", "0,5", "1", "LAST", "FIRST")