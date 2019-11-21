import arcpy


arcpy.env.workspace = r'D:\Projecten\WSRL\batchtest.gdb'
arcpy.env.overwriteOutput = True

code_waterloop = 'CODE'
watergangen = 'watergangen_inmeten_dissolve_test'
profiel_lengte_land = 20
profiel_lengte_rivier = 20

def generate_waterprofielen_1(profiel_lengte_land,profiel_lengte_rivier,trajectlijn,code,profielen):
    # traject to points
    # arcpy.FeatureToPoint_management(trajectlijn, 'traject_punten',"CENTROID")
    arcpy.GeneratePointsAlongLines_management(trajectlijn, 'traject_punten', 'PERCENTAGE', Percentage=50)
    arcpy.AddField_management('traject_punten', "profielnummer", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management('traject_punten', "lengte_landzijde", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management('traject_punten', "lengte_rivierzijde", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management('traject_punten', "profielnummer", '!OBJECTID!', "PYTHON")
    arcpy.CalculateField_management('traject_punten', "lengte_landzijde", profiel_lengte_land, "PYTHON")
    arcpy.CalculateField_management('traject_punten', "lengte_rivierzijde", profiel_lengte_rivier, "PYTHON")

    # route voor trajectlijn
    # arcpy.CreateRoutes_lr(trajectlijn, code, "route_traject", "LENGTH", "", "", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")

    existing_fields = arcpy.ListFields(trajectlijn)
    needed_fields = ['OBJECTID', 'SHAPE', 'SHAPE_Length','Shape','Shape_Length',code]
    for field in existing_fields:
        if field.name not in needed_fields:
            arcpy.DeleteField_management(trajectlijn, field.name)
    arcpy.AddField_management(trajectlijn, "van", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(trajectlijn, "tot", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management(trajectlijn, "van", 0, "PYTHON")
    arcpy.CalculateField_management(trajectlijn, "tot", "!Shape_Length!", "PYTHON")
    arcpy.CreateRoutes_lr(trajectlijn, code, 'route_traject', "TWO_FIELDS", "van", "tot", "", "1",
                          "0", "IGNORE", "INDEX")


    # locate profielpunten
    arcpy.LocateFeaturesAlongRoutes_lr('traject_punten', 'route_traject', code, "1.5 Meters", 'tabel_traject_punten',
                                       "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS",
                                       "M_DIRECTON")

    # offset rivierdeel profiel
    arcpy.MakeRouteEventLayer_lr('route_traject', code, 'tabel_traject_punten', "rid POINT meas", 'deel_rivier',
                                 "lengte_rivierzijde", "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "RIGHT",
                                 "POINT")

    arcpy.MakeRouteEventLayer_lr('route_traject', code, 'tabel_traject_punten', "rid POINT meas", 'deel_land',
                                 "lengte_landzijde", "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT",
                                 "POINT")
    # temp inzicht layer
    arcpy.CopyFeatures_management('deel_rivier', "temp_rivierdeel")
    arcpy.CopyFeatures_management('deel_land', "temp_landdeel")
    arcpy.AddField_management('temp_rivierdeel', "id", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management('temp_landdeel', "id", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management('temp_rivierdeel', "id", 2, "PYTHON")
    arcpy.CalculateField_management('temp_landdeel', "id", 1, "PYTHON")





    arcpy.Merge_management("'temp_rivierdeel';'temp_landdeel'", 'merge_profielpunten')
    arcpy.PointsToLine_management('merge_profielpunten', profielen, "profielnummer", "id", "NO_CLOSE")

    arcpy.SpatialJoin_analysis(profielen, trajectlijn, 'profielen_temp', "JOIN_ONE_TO_ONE", "KEEP_ALL", match_option="INTERSECT")
    arcpy.CopyFeatures_management('profielen_temp', profielen)
    # arcpy.FlipLine_edit(profielen)

    print 'profielen gemaakt op trajectlijn'

# with arcpy.da.UpdateCursor(watergangen, ['SHAPE@LENGTH','CODE']) as cursor:
#     for row in cursor:
#         lengte= row[0]
#         if lengte < 25:
#             cursor.deleteRow()
#         if lengte > 25 and lengte < 100:
#             # point mid
#             # profiel genereren
#         if lengte > 100 and lengte <350:
#             # points along line 25 m
#             # endpoints
#             # select points along line distance 26m to endpoint (2x)
#             # profiel genereren

with arcpy.da.UpdateCursor(watergangen, ['SHAPE@', code_waterloop,'SHAPE@LENGTH']) as cursor:
    for row in cursor:
        lengte = row[2]
        id = row[1]
        waterloop = 'waterloop_' + str(row[1])
        profielen = 'profielen_' + str(row[1])
        # profielen = 'profielen_' + str(row[1])
        # uitvoerpunten = 'punten_profielen_z_' + str(row[1])
        # uitvoer_maxpunten = 'max_kruinhoogte_' + str(row[1])
        # uitvoer_binnenkruin = 'binnenkruin_' + str(row[1])
        # uitvoer_buitenkruin = 'buitenkruin_' + str(row[1])
        # uitvoer_binnenteen = 'binnenteen_' + str(row[1])
        # resultfile = excelmap + str(row[1]) + '.xls'
        # excel = excelmap + str(row[1]) + '.xlsx'
        where = '"' + code_waterloop + '" = ' + "'" + str(id) + "'"
        #
        # # selecteer betreffend traject
        arcpy.Select_analysis(watergangen, waterloop, where)

        # verwijder indien lengte < 25m
        #         if lengte < 25:
        #             cursor.deleteRow()

        # geneneer punten op voor secties >25m en <100m
        generate_waterprofielen_1(profiel_lengte_land,profiel_lengte_rivier,waterloop,code_waterloop,profielen)


