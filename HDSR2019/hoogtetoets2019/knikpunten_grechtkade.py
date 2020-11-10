from basisfuncties import *
import arcpy
from arcpy.sa import *
# from itertools import groupby
# from basisfuncties import average
arcpy.env.workspace = r'D:\Projecten\HDSR\data\januari_2020.gdb'
# # sta arcpy toe oude data te overschrijven
arcpy.env.overwriteOutput = True
import pandas as pd


trajectlijn = 'grechtkade_selectie'
code = 'Naam'
mergepunten = "merge_"
uitvoerpunten = 'punten_profielen'
knikpunten = 'knikpunten_grechtkade'

profielen = 'profielen_RWK_areaal_2024'
bit_lijn = 'binnenteen_lijn'
but_lijn = 'buitenteen_lijn'
bik_lijn = 'binnenkruin_lijn'
buk_lijn = 'buitenkruin_lijn'
sl_bodem_lijn = 'slootbodem_segmenten_z'
sl_insteek_lijn = 'insteek_segmenten_z'


def intersect_kniklijnen():
    # snijpunten profielen-kniklijnen
    isect_bit = arcpy.Intersect_analysis([profielen,bit_lijn], 'isect_bit', "ALL", "0,01 Meters", "POINT")
    isect_but = arcpy.Intersect_analysis([profielen,but_lijn], 'isect_but', "ALL", "0,01 Meters", "POINT")
    isect_bik = arcpy.Intersect_analysis([profielen,bik_lijn], 'isect_bik', "ALL", "0,01 Meters", "POINT")
    isect_buk = arcpy.Intersect_analysis([profielen,buk_lijn], 'isect_buk', "ALL", "0,01 Meters", "POINT")
    isect_sl_bodem = arcpy.Intersect_analysis([profielen,sl_bodem_lijn], 'isect_sl_bodem', "ALL", "0,01 Meters", "POINT")
    isect_sl_insteek = arcpy.Intersect_analysis([profielen,sl_insteek_lijn], 'isect_sl_insteek', "ALL", "0,01 Meters", "POINT")

    # alle snijpunten als lijst
    totaal = [isect_bit,isect_but, isect_bik,isect_buk,isect_sl_bodem,isect_sl_insteek]


    # merge snijpunten
    arcpy.Merge_management(totaal, "merge", "")
    arcpy.FeatureToPoint_management("merge", "merge_")

    print ('snijpunten gemaakt op kniklijnen')

def set_measurements_trajectory(profielen, trajectlijn, code, mergepunten):  # rechts = rivier, profielen van binnen naar buiten
    # schoonmaken laag
    existing_fields = arcpy.ListFields(profielen)
    needed_fields = ['OBJECTID', 'SHAPE', 'SHAPE_Length', 'Shape', 'Shape_Length', code]
    for field in existing_fields:
        if field.name not in needed_fields:
            arcpy.DeleteField_management(profielen, field.name)

    # toevoegen van benodigde velden
    arcpy.AddField_management(profielen, "profielnummer", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(profielen, "van", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(profielen, "tot", "DOUBLE", 2, field_is_nullable="NULLABLE")

    arcpy.CalculateField_management(profielen, "profielnummer", '!OBJECTID!', "PYTHON")

    # split profielen
    rivierlijn = "river"
    landlijn = "land"
    clusterTolerance = 0
    invoer = [profielen, trajectlijn]
    uitvoer = 'snijpunten_centerline'
    arcpy.Intersect_analysis(invoer, uitvoer, "", clusterTolerance, "point")
    arcpy.SplitLineAtPoint_management(profielen, uitvoer, 'profielsplits', 1)

    velden = ['profielnummer', 'van', 'tot', code]

    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable('profielsplits')
    fieldmappings.addTable(rivierlijn)
    fieldmappings.addTable(landlijn)
    keepers = velden

    # koppel splits aan rivier-/landdelen
    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    arcpy.SpatialJoin_analysis('profielsplits', rivierlijn, 'profieldeel_rivier', "JOIN_ONE_TO_ONE", "KEEP_COMMON",
                               fieldmappings,
                               match_option="INTERSECT")
    arcpy.SpatialJoin_analysis('profielsplits', landlijn, 'profieldeel_land', "JOIN_ONE_TO_ONE", "KEEP_COMMON",
                               fieldmappings,
                               match_option="INTERSECT")

    # maak routes
    arcpy.CalculateField_management("profieldeel_rivier", "tot", '!Shape_Length!', "PYTHON")
    arcpy.CalculateField_management("profieldeel_land", "tot", '!Shape_Length!', "PYTHON")
    arcpy.CalculateField_management("profieldeel_rivier", "van", 0, "PYTHON")
    arcpy.CalculateField_management("profieldeel_land", "van", 0, "PYTHON")

    arcpy.CreateRoutes_lr('profieldeel_rivier', "profielnummer", "routes_rivier_", "TWO_FIELDS", "van", "tot", "",
                          "1", "0",
                          "IGNORE", "INDEX")

    arcpy.CreateRoutes_lr('profieldeel_land', "profielnummer", "routes_land_", "TWO_FIELDS", "tot", "van", "", "1",
                          "0", "IGNORE", "INDEX")

    # koppel code
    velden = ['profielnummer', code, 'id','z']
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable('routes_land_')
    fieldmappings.addTable('routes_rivier_')
    fieldmappings.addTable(mergepunten)
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

    # punten uit merge lokaliseren rivier/land
    arcpy.SpatialJoin_analysis(mergepunten, 'routes_rivier', 'punten_rivier', "JOIN_ONE_TO_ONE", "KEEP_COMMON",
                               fieldmappings,
                               match_option="INTERSECT")
    arcpy.SpatialJoin_analysis(mergepunten, 'routes_land', 'punten_land', "JOIN_ONE_TO_ONE", "KEEP_COMMON",
                               fieldmappings,
                               match_option="INTERSECT")


    # arcpy.GeneratePointsAlongLines_management('routes_land', 'punten_land', 'DISTANCE', Distance=stapgrootte_punten)
    # arcpy.GeneratePointsAlongLines_management('routes_rivier', 'punten_rivier', 'DISTANCE',
    #                                           Distance=stapgrootte_punten)

    # id-veld toevoegen voor koppeling met tabel
    arcpy.AddField_management('punten_land', 'punt_id', "DOUBLE", field_precision=2, field_is_nullable="NULLABLE")
    arcpy.AddField_management('punten_rivier', 'punt_id', "DOUBLE", field_precision=2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management("punten_land", "punt_id", '!OBJECTID!', "PYTHON")
    arcpy.CalculateField_management("punten_rivier", "punt_id", '!OBJECTID!', "PYTHON")

    # lokaliseer punten langs routes
    Output_Event_Table_Properties = "RID POINT MEAS"
    arcpy.LocateFeaturesAlongRoutes_lr('punten_land', 'routes_land', "profielnummer", "1 Meters",
                                       'uitvoer_tabel_land', Output_Event_Table_Properties, "FIRST", "DISTANCE",
                                       "ZERO",
                                       "FIELDS", "M_DIRECTON")
    arcpy.LocateFeaturesAlongRoutes_lr('punten_rivier', 'routes_rivier', "profielnummer", "1 Meters",
                                       'uitvoer_tabel_rivier', Output_Event_Table_Properties, "FIRST", "DISTANCE",
                                       "ZERO",
                                       "FIELDS", "M_DIRECTON")

    # koppel velden van de tabel
    arcpy.JoinField_management('punten_land', 'punt_id', 'uitvoer_tabel_land', 'punt_id', 'MEAS')
    arcpy.JoinField_management('punten_rivier', 'punt_id', 'uitvoer_tabel_rivier', 'punt_id', 'MEAS')
    arcpy.AlterField_management('punten_land', 'MEAS', 'afstand')
    arcpy.AlterField_management('punten_rivier', 'MEAS', 'afstand')

    with arcpy.da.UpdateCursor('punten_rivier', ['profielnummer', 'afstand']) as cursor:
        for row in cursor:
            row[1] = row[1] * -1
            cursor.updateRow(row)

    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable('punten_land')
    fieldmappings.addTable('punten_rivier')
    fieldmappings.addTable('snijpunten_centerline')

    velden = ['profielnummer', 'afstand', code, 'id','z']
    keepers = velden

    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    arcpy.FeatureToPoint_management("snijpunten_centerline", "punten_centerline")
    arcpy.Merge_management(['punten_land', 'punten_rivier', 'punten_centerline'], 'punten_profielen', fieldmappings)

    arcpy.CalculateField_management("punten_profielen", "afstand", 'round(!afstand!, 1)', "PYTHON")

    # zet trajectlijn-waardes op 0
    with arcpy.da.UpdateCursor('punten_profielen', ['afstand','id']) as cursor:
        for row in cursor:
            if row[0] == None:
                row[0] = 0
                cursor.updateRow(row)
            elif row[1] == None:
                cursor.deleteRow()


    with arcpy.da.UpdateCursor('punten_profielen', ['id']) as cursor:
        for row in cursor:
            if row[0] is None:
                cursor.deleteRow()

    print ('afstand t.o.v. trajectlijn bepaald')

def z_waardes(uitvoerpunten,knikpunten):

    # Koppel z-waardes
    arcpy.CheckOutExtension("Spatial")
    raster = r'D:\Projecten\HDSR\data\ahn_hdsr.gdb\shore_2019_050m_focal3m'
    ExtractValuesToPoints(uitvoerpunten, raster, knikpunten,"INTERPOLATE", "VALUE_ONLY")

    # Pas het veld 'RASTERVALU' aan naar 'z_ahn'
    arcpy.AlterField_management(knikpunten, 'RASTERVALU', 'z_ahn')

    # schoonmaken laag
    # arcpy.AlterField_management("merge_z", 'FID_testprofielen', 'profielnummer')
    existing_fields = arcpy.ListFields(knikpunten)
    needed_fields = ['OBJECTID','profielnummer', 'Shape', 'z', 'z_ahn','id','afstand']
    for field in existing_fields:
        if field.name not in needed_fields:
            arcpy.DeleteField_management(knikpunten, field.name)

    arcpy.env.outputCoordinateSystem = arcpy.Describe("merge_z").spatialReference
    # bepaal benodigde variabelen
    in_features = knikpunten
    properties = "POINT_X_Y_Z_M"
    length_unit = ""
    area_unit = ""
    coordinate_system = ""

    # voeg gewenste geometrie-attributen toe
    arcpy.AddGeometryAttributes_management(in_features, properties, length_unit,
                                           area_unit,
                                           coordinate_system)
    # pas veldnamen aan
    arcpy.AlterField_management(knikpunten, 'POINT_X', 'x')
    arcpy.AlterField_management(knikpunten, 'POINT_Y', 'y')




    # hoogtewaardes aan niet-waterlooplijnen --> indien rastervalu niet kan worden verkregen
    arcpy.AddField_management(knikpunten, "z_value", "DOUBLE", 2, field_is_nullable="NULLABLE")
    with arcpy.da.UpdateCursor(knikpunten, ['z', 'z_ahn', 'z_value']) as cursor:
        for row in cursor:
            if row[1] is not None:
                row[2] = row[1]
            elif row[1] is None and row[0] is not None:
                row[2] = row[0]
            else:
                pass

            cursor.updateRow(row)
    arcpy.DeleteField_management(knikpunten, ['POINT_M', 'z_ahn', 'z'])

    print ('hoogtewaarde bepaald indien mogelijk')

intersect_kniklijnen()
copy_trajectory_lr(trajectlijn,code)
set_measurements_trajectory(profielen, trajectlijn, code, mergepunten)
z_waardes(uitvoerpunten,knikpunten)