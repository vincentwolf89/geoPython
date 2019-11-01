import arcpy
from arcpy.sa import *
import numpy as np
import pandas as pd

# overschrijf de oude data
arcpy.env.overwriteOutput = True

# definieer de werkomgeving
arcpy.env.workspace = 'C:/Users/vince/Desktop/GIS/temp.gdb'

raster = r"C:\Users\vince\Desktop\wolfwater\HHNK\data\ahn3_kust_nh_tx_1m.tif"

zone = r'C:\Users\vince\Desktop\GIS\13_1_ds_temp.gdb\grensprofielzone_13_1_iiv'
kl = 'kl_13_1'
hr = r"C:\Users\vince\Desktop\GIS\duinscript.gdb\hr_ref_13_1_iiv"

# selecteer nwo in zone
arcpy.MakeFeatureLayer_management(kl, 'kl_temp')
arcpy.SelectLayerByLocation_management('kl_temp', 'intersect', zone)
arcpy.CopyFeatures_management('kl_temp', 'kl_grensprofielzone')

arcpy.AddField_management('kl_grensprofielzone', "maaiveldhoogte", "DOUBLE", 2, field_is_nullable="NULLABLE")


# maaiveldhoogte kl (punt)
arcpy.Intersect_analysis([kl,zone], "intersecting_kl", "", 0, "point")

# koppel hoogtepunten
punten_ahn3 = "intersecting_kl"
bufferzones_ahn3 = "kl_grensprofielzone_punten_zone"
distanceField = "5 Meters"

arcpy.Buffer_analysis(punten_ahn3, bufferzones_ahn3, distanceField)
bufferpunten = "kl_grensprofielzone_punten_zone"
clip_bufferpunten = "clip_bufferpunten"
raster_punten = "clip_bufferpunten_punten"

punten_temp = "koppeling_ahn_punten"

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
with arcpy.da.UpdateCursor(punten_temp, ['nr_kl']) as cursor1:
    for row in cursor1:
        if row[0] is None:
            cursor1.deleteRow()
        else:
            continue

# bereken statistieken voor iedere bufferzone
array = arcpy.da.FeatureClassToNumPyArray(punten_temp, ('nr_kl', 'grid_code'))
df = pd.DataFrame(array)
df_1 = df.dropna()
means = df_1.groupby(['nr_kl']).mean()
#
# # vul het woordenboek met setjes
dct = {}
for index, row in means.iterrows():
    naam = index
    hoogte = row['grid_code']
    dct[naam] = (hoogte)


# update met nieuwe ahn
velden = ['nr_kl', 'maaiveldhoogte']
with arcpy.da.UpdateCursor("kl_grensprofielzone", velden) as cursor:
    for row in cursor:
        id = row[0]
        if id in dct:
            row[1] = float(dct[id])

        cursor.updateRow(row)

# koppel hr
arcpy.SpatialJoin_analysis("kl_grensprofielzone", hr, "kl_grensprofielzone_hr", "#", "#", match_option="CLOSEST")
arcpy.CopyFeatures_management('kl_grensprofielzone_hr', 'kl_grensprofielzone')


# verwijder loze punten in de kl laag
with arcpy.da.UpdateCursor('kl_grensprofielzone', ['maaiveldhoogte']) as cursor1:
    for row in cursor1:
        if row[0] is None:
            cursor1.deleteRow()
        else:
            continue


# test of kl wel of niet voldoende boven rekenpeil ligt
arcpy.AddField_management('kl_grensprofielzone', "resthoogte", "DOUBLE", 2, field_is_nullable="NULLABLE")
arcpy.AddField_management('kl_grensprofielzone', "resthoogte_kl", "DOUBLE", 2, field_is_nullable="NULLABLE")

arcpy.AddField_management('kl_grensprofielzone', "situatie", "TEXT")

velden = ['nr_kl', 'Rp', 'maaiveldhoogte','resthoogte','situatie','resthoogte_kl']
with arcpy.da.UpdateCursor("kl_grensprofielzone", velden) as cursor:
    for row in cursor:
        if row[2] is not None:
            row[3] = row[2]-row[1]
            cursor.updateRow(row)
        else:
            row[4] = "geen maaiveldhoogte gevonden"

with arcpy.da.UpdateCursor("kl_grensprofielzone", velden) as cursor:
    for row in cursor:
        if row[2] is not None:
            row[5] = row[3]-1
            cursor.updateRow(row)
        else:
            pass

with arcpy.da.UpdateCursor("kl_grensprofielzone", velden) as cursor:
    for row in cursor:
        if row[2] is not None:
            resterend = row[5]
            if resterend < 0:
                row[4] = "tekort aan hoogte"
            else:
                row[4] = "voldoende hoogte boven rekenpeil"
            cursor.updateRow(row)
        else:
            pass


