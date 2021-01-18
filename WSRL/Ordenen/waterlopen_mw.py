import arcpy
import pandas as pd
from arcpy.sa import *

arcpy.env.workspace = r'D:\Projecten\WSRL\test_25_11.gdb'
arcpy.env.overwriteOutput = True

code_waterloop = 'CODE'
watergangen = 'unsplit_code_test'
profiel_lengte_land = 10
profiel_lengte_rivier = 10
profiel_interval = 5
profiel_interval_3 = 10
min_breedte = 0.6
tussenafstand_lang = 50
marge = 20

objecten = 'objecten_selectie'
contour_ahn = r'D:\Projecten\WSRL\A5H watergangen\watervlakkent.shp'
watergangen_totaal = r'D:\Projecten\WSRL\shp\waterlijnen_mw.shp'
watergangen_geselecteerd = r'D:\Projecten\WSRL\shp\watergangen_inmeten.shp'
kunstwerken = r'D:\Projecten\WSRL\A5H watergangen\watervlakkent.shp'
totaal_meetprofielen = []

def maak_objecten():
    # totale waterlopen-geselecteerde waterlopen
    arcpy.MakeFeatureLayer_management(watergangen_totaal, 'watergangen_totaal_lyr')
    arcpy.SelectLayerByLocation_management('watergangen_totaal_lyr', 'contains', watergangen_geselecteerd,invert_spatial_relationship='INVERT')
    arcpy.CopyFeatures_management('watergangen_totaal_lyr', 'watergangen_minselectie')
    # intersect van totale waterlopen met geselecteerde waterlopen
    arcpy.Intersect_analysis([watergangen_geselecteerd, 'watergangen_minselectie'], 'watergangen_t_', "", 0.1, "point")
    arcpy.FeatureToPoint_management("watergangen_t_", "watergangen_t")


    arcpy.CopyFeatures_management(kunstwerken, 'kunstwerken_selectie')
    with arcpy.da.UpdateCursor('kunstwerken_selectie', ['CATEGORIE']) as cursor:
        for row in cursor:
            left_text = 'Kunstwerk'
            left_row = str(row[0].partition(" ")[0])
            if left_text == left_row:
                pass
            else:
                cursor.deleteRow()

    arcpy.FeatureToPoint_management("kunstwerken_selectie", "kunstwerken_selectie_punt",
                                    "CENTROID")


    arcpy.Merge_management(['watergangen_t','kunstwerken_selectie_punt'], 'objecten_selectie')

def knip_sloten(profielen,slootlijn,code,meetprofielen,waterloop):


    # # verwijder profiel indien middelpunt op niet-nan data ligt
    # existing_fields = arcpy.ListFields(profielen)
    # needed_fields = ['RASTERVALU']
    # for field in existing_fields:
    #     if field.name in needed_fields:
    #         arcpy.DeleteField_management(profielen, field.name)
    # arcpy.Intersect_analysis([profielen, slootlijn], 'middelpunten_profielen', "", 0.5, "point")
    #
    # arcpy.FeatureToPoint_management('middelpunten_profielen', 'middelpunten_profielen_', "CENTROID")
    # ExtractValuesToPoints('middelpunten_profielen_', raster, 'middelpunten_profielen_z', "INTERPOLATE", "VALUE_ONLY")
    # arcpy.JoinField_management(profielen, "profielnummer", "middelpunten_profielen_z", "profielnummer", ["RASTERVALU"])
    #
    # with arcpy.da.UpdateCursor(profielen, ['RASTERVALU']) as cursor:
    #     for row in cursor:
    #         if row[0] is not None:
    #             cursor.deleteRow()
    #         else:
    #             continue




    # intersect op snijpunten met gridlijnen
    intersects = [profielen,contour_ahn]
    arcpy.Intersect_analysis(intersects, 'knip_sloten_punt', "", 0, "point")
    # knip profiellijnen met intersects

    searchRadius = "0.2 Meters"
    arcpy.SplitLineAtPoint_management(profielen, 'knip_sloten_punt', 'knip_profielen', searchRadius)

    arcpy.MakeFeatureLayer_management('knip_profielen', 'knip_profielen_temp')
    arcpy.SelectLayerByLocation_management('knip_profielen_temp', 'intersect', slootlijn,"0,1 Meters", "NEW_SELECTION", "NOT_INVERT")
    # arcpy.CopyFeatures_management('knip_profielen_temp', 'slootbreedtes')
    arcpy.CopyFeatures_management('knip_profielen_temp', meetprofielen)

    print "waterspiegel-profielen gemaakt voor "+str(waterloop)




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
    needed_fields = ['OBJECTID_12','OBJECTID','OBJECTID_1', 'SHAPE', 'SHAPE_Length','Shape','Shape_Length',code]
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
    arcpy.JoinField_management(profielen, 'profielnummer', 'merge_profielpunten', 'profielnummer', 'MEAS')
    arcpy.SpatialJoin_analysis(profielen, trajectlijn, 'profielen_temp', "JOIN_ONE_TO_ONE", "KEEP_ALL", match_option="INTERSECT")
    arcpy.CopyFeatures_management('profielen_temp', profielen)
    # arcpy.FlipLine_edit(profielen)

    print "profielen gemaakt op waterloop korter dan 100 m"

def generate_waterprofielen_2(profiel_lengte_land,profiel_lengte_rivier,trajectlijn,code,profielen, profiel_interval):
    # traject to points
    # arcpy.FeatureToPoint_management(trajectlijn, 'traject_punten',"CENTROID")
    arcpy.GeneratePointsAlongLines_management(trajectlijn, 'traject_punten', 'DISTANCE', Distance=profiel_interval)
    # arcpy.GeneratePointsAlongLines_management(trajectlijn, 'traject_punten', 'DISTANCE', Distance=25)
    arcpy.AddField_management('traject_punten', "profielnummer", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management('traject_punten', "lengte_landzijde", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management('traject_punten', "lengte_rivierzijde", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management('traject_punten', "profielnummer", '!OBJECTID!', "PYTHON")
    arcpy.CalculateField_management('traject_punten', "lengte_landzijde", profiel_lengte_land, "PYTHON")
    arcpy.CalculateField_management('traject_punten', "lengte_rivierzijde", profiel_lengte_rivier, "PYTHON")

    # route voor trajectlijn
    # arcpy.CreateRoutes_lr(trajectlijn, code, "route_traject", "LENGTH", "", "", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")

    existing_fields = arcpy.ListFields(trajectlijn)
    needed_fields = ['OBJECTID_12','OBJECTID','OBJECTID_1', 'SHAPE', 'SHAPE_Length','Shape','Shape_Length',code]
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

    arcpy.JoinField_management(profielen, 'profielnummer', 'merge_profielpunten', 'profielnummer', 'MEAS')
    arcpy.MakeFeatureLayer_management(profielen, 'profielen_lyr')
    arcpy.SelectLayerByLocation_management('profielen_lyr', 'WITHIN_A_DISTANCE', objecten, search_distance=10,  invert_spatial_relationship="INVERT")

    arcpy.CopyFeatures_management('profielen_lyr', 'test')

    arcpy.CopyFeatures_management('test', profielen)


    arcpy.FeatureVerticesToPoints_management(trajectlijn, 'temp_eindpunten', 'BOTH_ENDS')
    arcpy.MakeFeatureLayer_management(profielen, 'profielen_lyr')
    arcpy.SelectLayerByLocation_management('profielen_lyr', 'WITHIN_A_DISTANCE', 'temp_eindpunten', search_distance=10,
                                           invert_spatial_relationship="INVERT")
    arcpy.CopyFeatures_management('profielen_lyr', 'test')

    arcpy.CopyFeatures_management('test', profielen)






    list_profielnummers = []
    with arcpy.da.SearchCursor(profielen,['profielnummer']) as cursor:
        for row in cursor:
            list_profielnummers.append(row[0])

    profiel_1 = int(min(list_profielnummers))
    profiel_2 = int(max(list_profielnummers))

    with arcpy.da.UpdateCursor(profielen,['profielnummer']) as cursor:
        for row in cursor:
            if int(row[0]) == profiel_1 or int(row[0]) == profiel_2:
                pass
            else:
                cursor.deleteRow()
    print "profielen gemaakt op waterloop 100-350 m"
def generate_waterprofielen_3(profiel_lengte_land,profiel_lengte_rivier,trajectlijn,code,profielen, profiel_interval):
    lijst3 = []
    # traject to points
    # arcpy.FeatureToPoint_management(trajectlijn, 'traject_punten',"CENTROID")
    arcpy.GeneratePointsAlongLines_management(trajectlijn, 'traject_punten', 'DISTANCE', Distance=profiel_interval)
    # arcpy.GeneratePointsAlongLines_management(trajectlijn, 'traject_punten', 'DISTANCE', Distance=25)
    arcpy.AddField_management('traject_punten', "profielnummer", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management('traject_punten', "lengte_landzijde", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management('traject_punten', "lengte_rivierzijde", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management('traject_punten', "profielnummer", '!OBJECTID!', "PYTHON")
    arcpy.CalculateField_management('traject_punten', "lengte_landzijde", profiel_lengte_land, "PYTHON")
    arcpy.CalculateField_management('traject_punten', "lengte_rivierzijde", profiel_lengte_rivier, "PYTHON")

    # route voor trajectlijn
    # arcpy.CreateRoutes_lr(trajectlijn, code, "route_traject", "LENGTH", "", "", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")

    existing_fields = arcpy.ListFields(trajectlijn)
    needed_fields = ['OBJECTID_12','OBJECTID','OBJECTID_1', 'SHAPE', 'SHAPE_Length','Shape','Shape_Length',code]
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
    arcpy.JoinField_management(profielen, 'profielnummer', 'merge_profielpunten', 'profielnummer', 'MEAS')


    arcpy.MakeFeatureLayer_management(profielen, 'profielen_lyr')
    arcpy.SelectLayerByLocation_management('profielen_lyr', 'WITHIN_A_DISTANCE', objecten, search_distance=10,  invert_spatial_relationship="INVERT")

    arcpy.CopyFeatures_management('profielen_lyr', 'test')

    arcpy.CopyFeatures_management('test', profielen)

    array = arcpy.da.FeatureClassToNumPyArray(profielen, ('OBJECTID', 'profielnummer', code_waterloop, 'MEAS','tot'))
    df = pd.DataFrame(array)
    df= df.sort_values(['MEAS'], ascending=True)
    df['next_meas'] = df['MEAS'].shift(-1)
    df['difference'] = abs(df['MEAS']-df['next_meas'])
    # print df

    counter = 0
    row_iterator = df.iterrows()
    _, last = row_iterator.next()  # take first item from row_iterator
    for i, row in row_iterator:
        huidig = last['MEAS']
        volgende = row['MEAS']
        verschil = abs(volgende-huidig)
        counter += verschil
        if counter > tussenafstand_lang and row['MEAS'] < (row['tot']-marge):
            lijst3.append(row['profielnummer'])
            # print row['MEAS']
            counter = 0
        else:
            pass
        # print(row['MEAS'])
        # print(last['MEAS'])
        last = row





    # som = 0
    # for index, row in df.iterrows():
    #     som += row['difference']
    #     if som < 80:
    #         pass
    #     else:
    #         if som > 80:
    #             lijst3.append(row['profielnummer'])
    #             # print som, row['MEAS']
    #         som = 0


    with arcpy.da.UpdateCursor(profielen,['profielnummer']) as cursor:
        for row in cursor:
            if row[0] in lijst3:
                pass
            else:
                cursor.deleteRow()

    arcpy.FeatureVerticesToPoints_management(trajectlijn, 'temp_eindpunten', 'BOTH_ENDS')
    arcpy.MakeFeatureLayer_management(profielen, 'profielen_lyr')
    arcpy.SelectLayerByLocation_management('profielen_lyr', 'WITHIN_A_DISTANCE', 'temp_eindpunten', search_distance=10,
                                           invert_spatial_relationship="INVERT")
    arcpy.CopyFeatures_management('profielen_lyr', 'test')

    arcpy.CopyFeatures_management('test', profielen)

    print "profielen gemaakt op waterloop langer dan 350 m"
def runner():
    with arcpy.da.UpdateCursor(watergangen, ['SHAPE@', code_waterloop,'SHAPE@LENGTH']) as cursor:
        for row in cursor:
            lengte = row[2]
            id = row[1]

            waterloop = 'waterloop_' + str(row[1])
            meetprofielen = 'meetprofielen_' + str(row[1])
            profielen = 'profielen_' + str(row[1])

            where = '"' + code_waterloop + '" = ' + "'" + str(id) + "'"

            # selecteer betreffend traject
            arcpy.Select_analysis(watergangen, waterloop, where)

            # verwijder indien lengte < 25m
            if lengte < 25:
                print str(waterloop)+' is korter dan 25 m en doet niet mee'
                cursor.deleteRow()

            # geneneer profielen waterlopen voor secties >25m en <100m
            if lengte < 100:
                generate_waterprofielen_1(profiel_lengte_land,profiel_lengte_rivier,waterloop,code_waterloop,profielen)
            # genereer profielen waterlopen voor secties >100m en < 350m
            elif lengte > 100 and lengte < 350:
                generate_waterprofielen_2(profiel_lengte_land, profiel_lengte_rivier, waterloop, code_waterloop, profielen,
                                          profiel_interval)

            else:
                generate_waterprofielen_3(profiel_lengte_land, profiel_lengte_rivier, waterloop, code_waterloop, profielen,
                                          profiel_interval)

            knip_sloten(profielen,waterloop,code_waterloop,meetprofielen,waterloop)
            totaal_meetprofielen.append(meetprofielen)

# maak_objecten()
runner()
arcpy.Merge_management(totaal_meetprofielen, 'totaal_meetprofielen')
existing_fields = arcpy.ListFields('totaal_meetprofielen')
needed_fields = ['OBJECTID','Shape','Shape_Length','CODE']
for field in existing_fields:
    if field.name not in needed_fields:
        arcpy.DeleteField_management('totaal_meetprofielen', field.name)


arcpy.AddField_management('totaal_meetprofielen', "lengte_wl", "DOUBLE", 2, field_is_nullable="NULLABLE")
arcpy.CalculateField_management('totaal_meetprofielen', "lengte_wl", '!Shape_Length!', "PYTHON")