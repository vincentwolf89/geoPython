import arcpy
from Sellmeijer_basisfuncties import *
import math
from arcpy.sa import *
import numpy as np
import pandas as pd


arcpy.env.overwriteOutput = True
# werkdatabase
arcpy.env.workspace = r'C:\Users\vince\Desktop\GIS\nieuwe_lagen_as.gdb'

profielen = r'C:\Users\vince\Dropbox\Wolfwater\WSRL\gis\wsrl_cloud.gdb\profielen_test'
binnenteen = r'C:\Users\vince\Dropbox\Wolfwater\WSRL\gis\wsrl_cloud.gdb\binnenteenlijn_safe'
buffer = "5 Meters"
raster = r'C:\Users\vince\Desktop\GIS\losse rasters\ahn3clip\ahn3clip_2m'



def zandlaag_koppelen():
    zandlagen = r"C:\Users\vince\Dropbox\Wolfwater\WSRL\gis\wsrl_cloud.gdb\zandlaag_totaal_xls_z_totaal_route"
    output = 'spatial_zandlagen_profielen'
    veld_z = 'z_totaal'
    veld_id = 'uniek_id'

    bestaande_velden = arcpy.ListFields(profielen)

    for field in bestaande_velden:
        if field.name == "z_max":
            arcpy.DeleteField_management(profielen, "z_max")

        elif field.name == "maaiveldhoogte":
            arcpy.DeleteField_management(profielen, "maaiveldhoogte")
        elif field.name == "dikte_deklaag":
            arcpy.DeleteField_management(profielen, "dikte_deklaag")
        elif field.name =="uniek_id":
            arcpy.DeleteField_management(profielen, "uniek_id")
        else:
            continue

    arcpy.AddField_management(profielen, "uniek_id", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(profielen, "maaiveldhoogte", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(profielen, "dikte_deklaag", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management(profielen, "uniek_id", '!OBJECTID!', "PYTHON")


    fieldmappings = arcpy.FieldMappings()

    fieldmappings.addTable(profielen)
    fieldmappings.addTable(zandlagen)

    velden = ['uniek_id', 'z_totaal','maaiveldhoogte','dikte_deklaag']

    keepers = velden

    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    arcpy.SpatialJoin_analysis(profielen, zandlagen, output, "#", "#", fieldmappings)
    arcpy.JoinField_management(profielen, veld_id, output, veld_id, veld_z)
    arcpy.AlterField_management(profielen, veld_z, 'z_max', 'z_max')

    print "profielen voorzien van zandlaaghoogte en extra velden"


def buffers():
    inFeatures = ['spatial_zandlagen_profielen', binnenteen]
    clusterTolerance = 0
    intersectOutput = "snijpunten_binnenteen_20m"

    arcpy.Intersect_analysis(inFeatures, intersectOutput, "", clusterTolerance, "point")

    arcpy.Buffer_analysis(intersectOutput, 'buffer_snijpunten_binnenteen_20m', buffer)
    print "bufferzones gemaakt voor gemiddelde maaiveldhoogte"

def koppeling_ahn3():
    bufferpunten = 'buffer_snijpunten_binnenteen_20m'

    clip_bufferpunten = 'clip_bufferpunten'
    raster_punten = "clip_bufferpunten_punten"

    punten_temp = 'koppeling_ahn_punten'

    desc = arcpy.Describe(bufferpunten)
    afmetingen = str(desc.extent.XMin) + " " + str(desc.extent.YMin) + " " + str(desc.extent.XMax) + " " + str(
        desc.extent.YMax)

    # clip de bufferzones
    arcpy.Clip_management(raster, afmetingen, clip_bufferpunten, bufferpunten,
                          "-3,402823e+038", "ClippingGeometry", "MAINTAIN_EXTENT")

    # raster naar punten
    arcpy.RasterToPoint_conversion(clip_bufferpunten, raster_punten, "VALUE")

    # koppel rasterpunten aan bufferzones
    arcpy.SpatialJoin_analysis(raster_punten, bufferpunten, punten_temp, join_operation="JOIN_ONE_TO_MANY",
                               join_type="KEEP_ALL", match_option="WITHIN")

    # verwijder loze punten in de rasterpunten
    with arcpy.da.UpdateCursor(punten_temp, ['uniek_id']) as cursor1:
        for row in cursor1:
            if row[0] is None:
                cursor1.deleteRow()
            else:
                continue
    print 'ahn-waardes berekend'



def koppeling():
    # bereken statistieken voor iedere bufferzone
    array = arcpy.da.FeatureClassToNumPyArray('koppeling_ahn_punten', ('uniek_id', 'grid_code'))
    df = pd.DataFrame(array)
    df_1 = df.dropna()
    means = df_1.groupby(['uniek_id']).mean()

    # vul het woordenboek met setjes
    dct = {}
    for index, row in means.iterrows():
        naam = index
        hoogte = row['grid_code']
        dct[naam] = (hoogte)


    # update profielen met nieuwe ahn
    velden = ['uniek_id', 'maaiveldhoogte','z_totaal', 'dikte_deklaag']
    with arcpy.da.UpdateCursor('snijpunten_binnenteen_20m', velden) as cursor:
        for row in cursor:
            id = row[0]
            if id in dct:
                row[1] = float(dct[id])

            cursor.updateRow(row)
            if row[1] is not None and row[2] is not None and row[1]>row[2]:
                row[3] = row[1]-row[2]
            else:
                row[3] = 0
            cursor.updateRow(row)

    print "koppeling gemaakt met puntenlaag"


zandlaag_koppelen()
buffers()
koppeling_ahn3()
koppeling()