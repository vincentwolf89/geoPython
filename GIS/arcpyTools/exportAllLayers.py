import arcpy
import os
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Users\Vincent\Desktop\dropboxdbSafe.gdb"

featureclasses = arcpy.ListFeatureClasses()
outlocation = r"C:\Users\Vincent\Desktop\shpViewerWGS"
sr = arcpy.Describe(r"C:\Users\Vincent\Desktop\shp_viewer\test.shp").spatialReference

for fc in featureclasses:
    name = str(fc)
    arcpy.AddField_management(fc, 'layername', "TEXT")
    arcpy.AddField_management(fc, 'layerid', "TEXT")
    arcpy.AddField_management(fc, 'layerstyle', "TEXT")
    arcpy.AddField_management(fc, 'layercolor', "TEXT")

    # arcpy.FeatureClassToShapefile_conversion(fc, os.path.join(outlocation,fc))
    # arcpy.CopyFeatures_management(
    #     fc, os.path.join("c:/base/output.gdb",
    #                      os.path.splitext(fc)[0]))

    out = os.path.join(outlocation,fc)
    
    arcpy.Project_management(fc,out,sr,"","","","","")
    