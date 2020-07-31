import sys
sys.path.append('.')

from basisfuncties import *
import arcpy

copy_trajectory_lr()

def set_measurements_trajectory(profielen,trajectlijn,code,stapgrootte_punten,toetspeil): #rechts = rivier, profielen van binnen naar buiten
    # clean feature
    existing_fields = arcpy.ListFields(profielen)
    needed_fields = ['OBJECTID', 'SHAPE', 'SHAPE_Length','Shape','Shape_Length',code,toetspeil,'profielnummer']
    for field in existing_fields:
        if field.name not in needed_fields:
            arcpy.DeleteField_management(profielen, field.name)

    # add needed fields
    #arcpy.AddField_management(profielen, "profielnummer", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(profielen, "van", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(profielen, "tot", "DOUBLE", 2, field_is_nullable="NULLABLE")

    #arcpy.CalculateField_management(profielen, "profielnummer", '!OBJECTID!', "PYTHON")

    # split profiles
    rivierlijn = "river"
    landlijn = "land"
    clusterTolerance = 0
    invoer = [profielen, trajectlijn]
    uitvoer = 'snijpunten_centerline'
    arcpy.Intersect_analysis(invoer, uitvoer, "", clusterTolerance, "point")
    arcpy.SplitLineAtPoint_management(profielen, uitvoer, 'profielsplits', 1)

    velden = ['profielnummer', 'van', 'tot',code]

    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable('profielsplits')
    fieldmappings.addTable(rivierlijn)
    fieldmappings.addTable(landlijn)
    keepers = velden

    # join splits to river/land parts
    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    arcpy.SpatialJoin_analysis('profielsplits', rivierlijn, 'profieldeel_rivier', "JOIN_ONE_TO_ONE", "KEEP_COMMON", fieldmappings,
                               match_option="INTERSECT")
    arcpy.SpatialJoin_analysis('profielsplits', landlijn, 'profieldeel_land', "JOIN_ONE_TO_ONE", "KEEP_COMMON",
                               fieldmappings,
                               match_option="INTERSECT")

    # create routes
    arcpy.CalculateField_management("profieldeel_rivier", "tot", '!Shape_Length!', "PYTHON")
    arcpy.CalculateField_management("profieldeel_land", "tot", '!Shape_Length!', "PYTHON")
    arcpy.CalculateField_management("profieldeel_rivier", "van", 0, "PYTHON")
    arcpy.CalculateField_management("profieldeel_land", "van", 0, "PYTHON")


    arcpy.CreateRoutes_lr('profieldeel_rivier', "profielnummer", "routes_rivier_", "TWO_FIELDS", "van", "tot", "", "1", "0",
                          "IGNORE", "INDEX")

    arcpy.CreateRoutes_lr('profieldeel_land', "profielnummer", "routes_land_", "TWO_FIELDS", "tot", "van", "", "1",
                          "0", "IGNORE", "INDEX")

    #join code
    velden = ['profielnummer',code]
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable('routes_land_')
    fieldmappings.addTable('routes_rivier_')
    fieldmappings.addTable(trajectlijn)

    keepers = velden
    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    arcpy.SpatialJoin_analysis('routes_rivier_', trajectlijn, 'routes_rivier', "JOIN_ONE_TO_ONE", "KEEP_COMMON",
                               fieldmappings,
                               match_option="INTERSECT")
    arcpy.SpatialJoin_analysis('routes_land_', trajectlijn, 'routes_land', "JOIN_ONE_TO_ONE", "KEEP_COMMON",
                               fieldmappings,
                               match_option="INTERSECT")

    # generate points
    arcpy.GeneratePointsAlongLines_management('routes_land', 'punten_land', 'DISTANCE', Distance= stapgrootte_punten)
    arcpy.GeneratePointsAlongLines_management('routes_rivier', 'punten_rivier', 'DISTANCE', Distance=stapgrootte_punten)


    # id field for joining table
    arcpy.AddField_management('punten_land', 'punt_id', "DOUBLE", field_precision=2, field_is_nullable="NULLABLE")
    arcpy.AddField_management('punten_rivier', 'punt_id', "DOUBLE", field_precision=2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management("punten_land", "punt_id", '!OBJECTID!', "PYTHON")
    arcpy.CalculateField_management("punten_rivier", "punt_id", '!OBJECTID!', "PYTHON")


    # find points along routes
    Output_Event_Table_Properties = "RID POINT MEAS"
    arcpy.LocateFeaturesAlongRoutes_lr('punten_land', 'routes_land', "profielnummer", "1 Meters",
                                       'uitvoer_tabel_land', Output_Event_Table_Properties, "FIRST", "DISTANCE", "ZERO",
                                       "FIELDS", "M_DIRECTON")
    arcpy.LocateFeaturesAlongRoutes_lr('punten_rivier', 'routes_rivier', "profielnummer", "1 Meters",
                                       'uitvoer_tabel_rivier', Output_Event_Table_Properties, "FIRST", "DISTANCE", "ZERO",
                                       "FIELDS", "M_DIRECTON")

    # join fields from table
    arcpy.JoinField_management('punten_land', 'punt_id', 'uitvoer_tabel_land', 'punt_id', 'MEAS')
    arcpy.JoinField_management('punten_rivier', 'punt_id', 'uitvoer_tabel_rivier', 'punt_id', 'MEAS')
    arcpy.AlterField_management('punten_land', 'MEAS', 'afstand')
    arcpy.AlterField_management('punten_rivier', 'MEAS', 'afstand')

    with arcpy.da.UpdateCursor('punten_rivier', ['profielnummer', 'afstand']) as cursor:
        for row in cursor:
            row[1] = row[1]*-1
            cursor.updateRow(row)

    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable('punten_land')
    fieldmappings.addTable('punten_rivier')
    fieldmappings.addTable('snijpunten_centerline')

    velden = ['profielnummer', 'afstand', code]
    keepers = velden

    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    arcpy.FeatureToPoint_management("snijpunten_centerline", "punten_centerline")
    arcpy.Merge_management(['punten_land', 'punten_rivier','punten_centerline'], 'punten_profielen', fieldmappings)

    arcpy.CalculateField_management("punten_profielen", "afstand", 'round(!afstand!, 1)', "PYTHON")

    # set centerline values to 0
    with arcpy.da.UpdateCursor('punten_profielen', ['afstand']) as cursor:
        for row in cursor:
            if row[0] == None:
                row[0] = 0
                cursor.updateRow(row)

    print 'Meetpunten op routes gelokaliseerd'