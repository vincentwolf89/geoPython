import arcpy

arcpy.env.overwriteOutput = True

arcpy.env.workspace = 'C:/Users/vince/Desktop/GIS/buffer_huizen.gdb'

bufferzone = 'split_100m'
huizen_veld = 'huizen_100m'
huizen = r'C:\Users\vince\Desktop\bag_panden\bag_panden\panden_vlakken.shp'
dijkvakindeling = r'C:\Users\vince\Desktop\GIS\data.gdb\dijkvakindeling_juli_2019_clean'


dct = {}
arcpy.MakeFeatureLayer_management(bufferzone, 'bufferzone_lyr')

with arcpy.da.UpdateCursor(bufferzone,['dv_nummer']) as cursor:
    for row in cursor:
        query = "\"dv_nummer\"=" + str(int(row[0]))
        arcpy.management.SelectLayerByAttribute("bufferzone_lyr", "NEW_SELECTION", query)

        arcpy.MakeFeatureLayer_management('bufferzone_lyr', 'bufferzone_lyr_row')
        arcpy.MakeFeatureLayer_management(huizen, 'huizen_lyr')
        arcpy.SelectLayerByLocation_management('huizen_lyr', 'intersect', 'bufferzone_lyr_row')
        arcpy.CopyFeatures_management('huizen_lyr', 'test_huizen_selectie')
        arcpy.GetCount_management('test_huizen_selectie')
        result = arcpy.GetCount_management('test_huizen_selectie').getOutput(0)

        key = int(row[0])
        count = int(result)
        dct[key] = count

with arcpy.da.UpdateCursor(dijkvakindeling,['dv_nummer', huizen_veld]) as cursor:
    for row in cursor:
        key = int(row[0])
        if key in dct:
            row[1] = dct[key]
            print key
            cursor.updateRow(row)
        else:
            continue



