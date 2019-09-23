import gc
gc.collect()
import arcpy
import math
from arcpy.sa import *
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import xlwt
import operator
import itertools
from itertools import groupby
from operator import itemgetter


arcpy.env.overwriteOutput = True

# definieer de werkomgeving
arcpy.env.workspace = r'C:\Users\vince\Desktop\GIS\maatgevende_profielen.gdb'

profielen = 'profielen_safe_10m'
dijkvakindeling = r'C:\Users\vince\Desktop\GIS\stph_testomgeving.gdb\dijkvakindeling_sm_juli_2019'
raster = r'C:\Users\vince\Desktop\GIS\losse rasters\ahn3clip\ahn3clip_safe'
landlijn = 'landzijde'
rivierlijn = 'rivierzijde'
stapgrootte_punten = 2
resultfile = "C:/Users/vince/Desktop/mg_aug_2019.xls"

binnenteenlijn = r'C:\Users\vince\Desktop\GIS\profielscript_final.gdb\binnenteenlijn_safe'
binnenkruinlijn = r'C:\Users\vince\Desktop\GIS\profielscript_final.gdb\binnenkruinlijn_safe'
buitenkruinlijn = dijkvakindeling
buitenteenlijn = r'C:\Users\vince\Desktop\GIS\profielscript_final.gdb\buitenteenlijn_safe'



def afstanden_punten(): # hier worden routes gemaakt op de profielen, zodat de afstanden kunnen worden berekend


    # split profielen
    clusterTolerance = 0
    invoer = [profielen, dijkvakindeling]
    uitvoer = 'snijpunten_centerline'
    arcpy.Intersect_analysis(invoer, uitvoer, "", clusterTolerance, "point")
    arcpy.SplitLineAtPoint_management(profielen, uitvoer, 'profielsplits', 1)

    velden = ['profielnummer', 'van', 'tot','dv_nummer']
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable('profielsplits')
    fieldmappings.addTable(landlijn)
    fieldmappings.addTable(rivierlijn)
    keepers = velden

    # koppel splits aan rivier/land delen
    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    arcpy.SpatialJoin_analysis('profielsplits', rivierlijn, 'profieldeel_rivier', "JOIN_ONE_TO_ONE", "KEEP_COMMON", fieldmappings,
                               match_option="INTERSECT")
    arcpy.SpatialJoin_analysis('profielsplits', landlijn, 'profieldeel_land', "JOIN_ONE_TO_ONE", "KEEP_COMMON",
                               fieldmappings,
                               match_option="INTERSECT")

    # maak routes
    arcpy.CalculateField_management("profieldeel_rivier", "tot", '!Shape_Length!', "PYTHON")
    arcpy.CalculateField_management("profieldeel_land", "tot", '!Shape_Length!', "PYTHON")

    arcpy.CreateRoutes_lr('profieldeel_rivier', "profielnummer", "routes_rivier_", "TWO_FIELDS", "van", "tot", "", "1", "0",
                          "IGNORE", "INDEX")

    arcpy.CreateRoutes_lr('profieldeel_land', "profielnummer", "routes_land_", "TWO_FIELDS", "tot", "van", "", "1",
                          "0", "IGNORE", "INDEX")

    #koppel dijkvaknummer
    velden = ['profielnummer','dv_nummer']
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable('routes_land_')
    fieldmappings.addTable('routes_rivier_')
    fieldmappings.addTable(dijkvakindeling)

    keepers = velden
    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    arcpy.SpatialJoin_analysis('routes_rivier_', dijkvakindeling, 'routes_rivier', "JOIN_ONE_TO_ONE", "KEEP_COMMON",
                               fieldmappings,
                               match_option="INTERSECT")
    arcpy.SpatialJoin_analysis('routes_land_', dijkvakindeling, 'routes_land', "JOIN_ONE_TO_ONE", "KEEP_COMMON",
                               fieldmappings,
                               match_option="INTERSECT")


    arcpy.GeneratePointsAlongLines_management('routes_land', 'punten_land', 'DISTANCE', Distance= stapgrootte_punten)
    arcpy.GeneratePointsAlongLines_management('routes_rivier', 'punten_rivier', 'DISTANCE', Distance=stapgrootte_punten)


    # Een extra veld met punt_id is nodig om straks te kunnen koppelen
    arcpy.AddField_management('punten_land', 'punt_id', "DOUBLE", field_precision=2, field_is_nullable="NULLABLE")
    arcpy.AddField_management('punten_rivier', 'punt_id', "DOUBLE", field_precision=2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management("punten_land", "punt_id", '!OBJECTID!', "PYTHON")
    arcpy.CalculateField_management("punten_rivier", "punt_id", '!OBJECTID!', "PYTHON")


    # Lokaliseren van de punten op de gemaakte routes
    Output_Event_Table_Properties = "RID POINT MEAS"
    arcpy.LocateFeaturesAlongRoutes_lr('punten_land', 'routes_land', "profielnummer", "1 Meters",
                                       'uitvoer_tabel_land', Output_Event_Table_Properties, "FIRST", "DISTANCE", "ZERO",
                                       "FIELDS", "M_DIRECTON")
    arcpy.LocateFeaturesAlongRoutes_lr('punten_rivier', 'routes_rivier', "profielnummer", "1 Meters",
                                       'uitvoer_tabel_rivier', Output_Event_Table_Properties, "FIRST", "DISTANCE", "ZERO",
                                       "FIELDS", "M_DIRECTON")

    # velden aanpassen
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

    velden = ['profielnummer', 'afstand', 'dv_nummer']
    keepers = velden

    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    arcpy.FeatureToPoint_management("snijpunten_centerline", "punten_centerline")
    arcpy.Merge_management(['punten_land', 'punten_rivier','punten_centerline'], 'punten_profielen', fieldmappings)

    print 'punten op route gelocaliseerd'

def values_points(): # hier wordt een hoogtewaarde aan ieder punt, op iedere route, gekoppeld
    # bepaal invoer
    invoer_punten = "punten_profielen"
    uitvoer_punten = "punten_profielen_z"

    # Test de ArcGIS Spatial Analyst extension license
    arcpy.CheckOutExtension("Spatial")

    # Koppel z-waardes
    ExtractValuesToPoints(invoer_punten, raster, uitvoer_punten,
                          "INTERPOLATE", "VALUE_ONLY")

    # Pas het veld 'RASTERVALU' aan naar 'z_ahn'
    arcpy.AlterField_management(uitvoer_punten, 'RASTERVALU', 'z_ahn')
    print "Hoogte-waarde aan punten gekoppeld en veld aangepast naar z_ahn"


def koppeling_kniklijnen():

    # split profielen op kniklijnen
    invoer1 = [profielen, binnenteenlijn]
    invoer2 = [profielen, binnenkruinlijn]
    invoer3 = [profielen, buitenkruinlijn]
    invoer4 = [profielen, buitenteenlijn]

    arcpy.Intersect_analysis(invoer1, 'punten_bit', "", 0, "point")
    arcpy.Intersect_analysis(invoer2, 'punten_bik', "", 0, "point")
    arcpy.Intersect_analysis(invoer3, 'punten_buk', "", 0, "point")
    arcpy.Intersect_analysis(invoer4, 'punten_but', "", 0, "point")

    arcpy.SplitLineAtPoint_management(profielen, 'punten_bit', 'split_geometrie1', 1)
    arcpy.SplitLineAtPoint_management('split_geometrie1', 'punten_but', 'split_geometrie2', 1)
    arcpy.SplitLineAtPoint_management('split_geometrie2', 'punten_buk', 'split_geometrie3', 1)
    arcpy.SplitLineAtPoint_management('split_geometrie3', 'punten_bik', 'split_geometrie4', 1)




    velden = ['profielnummer', 'soort', 'dv_nummer','afstand']
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable('split_geometrie4')
    fieldmappings.addTable('koppeldeel_1')
    fieldmappings.addTable('koppeldeel_3')
    fieldmappings.addTable('koppeldeel_binnenkant')
    fieldmappings.addTable('koppeldeel_buitenkant')
    fieldmappings.addTable(dijkvakindeling)

    keepers = velden


    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))



    arcpy.SpatialJoin_analysis('split_geometrie4', 'koppeldeel_1', 'buitentalud', "JOIN_ONE_TO_ONE", "KEEP_COMMON", fieldmappings,
                               match_option="INTERSECT")
    arcpy.SpatialJoin_analysis('split_geometrie4', 'koppeldeel_3', 'binnentalud', "JOIN_ONE_TO_ONE", "KEEP_COMMON", fieldmappings,
                               match_option="INTERSECT")
    arcpy.SpatialJoin_analysis('split_geometrie4', 'buitenkruin_koppel', 'kruin', "JOIN_ONE_TO_ONE", "KEEP_COMMON",fieldmappings,
                               match_option="INTERSECT")

    arcpy.AddField_management('kruin', 'kruin_check', "TEXT", field_length=50)
    with arcpy.da.UpdateCursor('kruin', ['kruin_check']) as cursor:
        for row in cursor:
            row[0] = "kruin_totaal"
            cursor.updateRow(row)



    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable('binnentalud')
    fieldmappings.addTable('buitentalud')
    fieldmappings.addTable('kruin')
    fieldmappings.addTable('punten_profielen_z')


    velden = ['profielnummer', 'soort', 'z_ahn','kruin_check','dv_nummer','afstand']
    keepers = velden

    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))
    arcpy.Merge_management(['binnentalud', 'buitentalud', 'kruin'], 'profieldelen', fieldmappings)

    arcpy.SpatialJoin_analysis('punten_profielen_z', 'profieldelen', 'profielen_punten_final_', "JOIN_ONE_TO_ONE", "KEEP_COMMON",
                               fieldmappings,
                               match_option="INTERSECT")

    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable('kruin')
    fieldmappings.addTable('profielen_punten_final_')

    velden = ['profielnummer', 'soort', 'z_ahn','kruin_check', 'dv_nummer','afstand']
    keepers = velden

    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    arcpy.SpatialJoin_analysis('profielen_punten_final_', 'kruin', 'profielen_punten_final', "JOIN_ONE_TO_ONE",
                               "KEEP_ALL",
                               fieldmappings,
                               match_option="INTERSECT")



def volume_berekening():
    array = arcpy.da.FeatureClassToNumPyArray('profielen_punten_final', ('profielnummer','dv_nummer', 'afstand','z_ahn'))

    df = pd.DataFrame(array)
    df_1 = df.dropna()
    sorted = df_1.sort_values(['profielnummer', 'afstand'], ascending=[True, True])
    grouped = sorted.groupby(["dv_nummer"])

    overzicht_volumes = {}

    for name, group in grouped:

        afstanden = group['afstand']
        hoogtes = group['z_ahn']
        profielen = group['profielnummer']
        dijkvak = group['dv_nummer']


        df_volumes = pd.DataFrame(columns=['volume'])


        gr_df = pd.DataFrame(list(zip(profielen, afstanden, hoogtes, dijkvak)),
                             columns=['profielnummer', 'afstand', 'hoogte_ahn','dijkvak'])


        sorted_gr_df = gr_df.sort_values(['profielnummer', 'afstand'], ascending=[True, True])
        grouped_2 = sorted_gr_df.groupby(["profielnummer"])



        for groep, group in grouped_2:

            afstand = group['afstand']
            hoogte = group['hoogte_ahn']
            waarde = np.trapz(hoogte,afstand)

            if waarde == 0:
                continue

            else:

                df_volumes.loc[groep] = waarde


        profiel = df_volumes[['volume']].idxmin().values[0]
        min_volume = df_volumes[['volume']].min().values[0]
        overzicht_volumes[name] = profiel, min_volume



    if overzicht_volumes:
        arcpy.MakeFeatureLayer_management('profielen_safe_10m', "TEMP_LYR")
        for key, value in overzicht_volumes.items():
            query = "\"profielnummer\"=" + str(value[0])
            arcpy.management.SelectLayerByAttribute("TEMP_LYR", "ADD_TO_SELECTION", query)

        arcpy.CopyFeatures_management("TEMP_LYR", 'maatgevende_locaties')

# afmaken
def velden():

    arcpy.env.outputCoordinateSystem = arcpy.Describe("profielen_punten_final").spatialReference
    # Set local variables
    in_features = "profielen_punten_final"
    properties = "POINT_X_Y_Z_M"
    length_unit = ""
    area_unit = ""
    coordinate_system = ""

    # Generate the extent coordinates using Add Geometry Properties tool
    arcpy.AddGeometryAttributes_management(in_features, properties, length_unit,
                                           area_unit,
                                           coordinate_system)

    arcpy.AlterField_management('profielen_punten_final', 'POINT_X', 'x')
    arcpy.AlterField_management('profielen_punten_final', 'POINT_Y', 'y')
def to_excel():


    fields = ['profielnummer', 'afstand', 'z_ahn', 'x', 'y']
    list_profielnummer = []
    list_afstand = []
    list_z_ahn = []
    list_x = []
    list_y =[]

    with arcpy.da.SearchCursor("profielen_punten_final", fields) as cur:
        for row in cur:
            if row[2] is None:
                pass
            else:
                profielnummer = row[0]
                afstand = row[1]
                z_ahn = row[2]
                x = row[3]
                y = row[4]

                list_profielnummer.append(profielnummer)
                list_afstand.append(afstand)
                list_z_ahn.append(z_ahn)
                list_x.append(x)
                list_y.append(y)
        # define styles

    style = xlwt.easyxf('font: bold 1')  # define style
    wb = xlwt.Workbook()  # open new workbook
    ws = wb.add_sheet("overzicht")  # add new sheet

    # write headers
    row = 0
    ws.write(row, 0, "profielnummer", style=style)
    ws.write(row, 1, "afstand buk [m, buitenkant +]", style=style)
    ws.write(row, 2, "z_ahn [m NAP]", style=style)
    ws.write(row, 3, "x", style=style)
    ws.write(row, 4, "y", style=style)


    # write colums
    row = 1
    for i in list_profielnummer:
        ws.write(row, 0, i)
        row += 1

    row = 1
    for i in list_afstand:
        ws.write(row, 1, i)
        row += 1

    row = 1
    for i in list_z_ahn:
        ws.write(row, 2, i)
        row += 1

    row = 1
    for i in list_x:
        ws.write(row, 3, i)
        row += 1

    row = 1
    for i in list_y:
        ws.write(row, 4, i)
        row += 1


    wb.save(resultfile)

afstanden_punten()
values_points()
koppeling_kniklijnen()
volume_berekening()
# velden()
# to_excel()
