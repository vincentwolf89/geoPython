import arcpy

# arcpy.env.workspace = 'C:/Users/vince/Desktop/GIS/temp.gdb'

mxd = r'C:\Users\vince\Desktop\test.mxd'
out_gdb = r'C:\Users\vince\Desktop\GIS\temp.gdb'
zone = "grensprofielzone"

mxd = arcpy.mapping.MapDocument(mxd)
# df = arcpy.mapping.ListDataFrames(mxd)
for lyr in arcpy.mapping.ListLayers(mxd):
    if "tussen" in lyr.name:
        print lyr.name
        arcpy.FeatureClassToFeatureClass_conversion(lyr, out_gdb, str(lyr)+"_kopie")

arcpy.SelectLayerByLocation_management('nwo_temp', 'intersect', zone)

