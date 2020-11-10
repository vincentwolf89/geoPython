import arcpy
import os
arcpy.env.overwriteOutput = True

arcpy.env.workspace = r"D:\Projecten\WSRL\safe\ruimtebeslag.gdb"
features = "dvIndelingSept2020"
field = 'koppeling_RB'


def splitByAttributes(features, field):
    shapeList = []

    # list features in layer
    with arcpy.da.SearchCursor(features,[field]) as cursor:
        for row in cursor:
            shapeName = str(row[0])
            if shapeName in shapeList:
                pass
            else:
                shapeList.append(shapeName)

    print shapeList

    # select features in layer 
    for item in shapeList:
        lyr = arcpy.MakeFeatureLayer_management(features, 'templyr') 
        where = '"' + field + '" = ' + "'" + item + "'"
        selected = arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", where)
        outputName = str(item)
        outputName = (outputName.replace('+', '_'))
        outputName = (outputName.replace('.', '_'))

        arcpy.CopyFeatures_management(selected,outputName)

splitByAttributes(features,field)

