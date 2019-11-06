import arcpy



arcpy.env.workspace = r'D:\GIS\temp.gdb'
bufferzone = r'C:\Users\Vincent\Desktop\HDSR\data\fwshapevoorbasishoogtetoets\RWK_hdsr.shp'
arcpy.CopyFeatures_management(bufferzone, 'temp_keringen')
