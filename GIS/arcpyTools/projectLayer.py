import os
import arcpy
arcpy.env.overwriteOutput = True

# invoer
arcpy.env.workspace = r'C:\Users\Vincent\Desktop\demodataViewer\data.gdb'
# shapefiles uitvoer
outputmap = r'C:\Users\Vincent\Desktop\demodataViewer\shp'

# lijst met alle features
featureclasses = arcpy.ListFeatureClasses()

# Project feature to desired crs and save to .shp
for fc in featureclasses:



    # output data
    output_feat = outputmap+"/"+os.path.splitext(fc)[0]

    # create a spatial reference object for the output coordinate system
    crs = arcpy.SpatialReference(4326)
   

    # run the tool
    arcpy.Project_management(fc, output_feat, crs)
    print os.path.splitext(fc)[0]+" is geconverteerd"



