import arcpy
from arcpy.sa import *
import numpy as np
import pandas as pd

# overschrijf de oude data
arcpy.env.overwriteOutput = True

# definieer de werkomgeving
arcpy.env.workspace = 'C:/Users/vince/Desktop/GIS/temp.gdb'

raster = r"C:\Users\vince\Desktop\wolfwater\HHNK\data\ahn3_kust_nh_tx_1m.tif"

zone = "zone"
nwo = "vlakken"
hr = r"C:\Users\vince\Desktop\GIS\duinscript.gdb\hr_ref_13_1_iiv"

# selecteer nwo in zone
arcpy.MakeFeatureLayer_management(nwo, 'nwo_temp')
arcpy.SelectLayerByLocation_management('nwo_temp', 'intersect', zone)
arcpy.CopyFeatures_management('nwo_temp', 'nwo_grensprofielzone')

arcpy.AddField_management('nwo_grensprofielzone', "maaiveldhoogte", "DOUBLE", 2, field_is_nullable="NULLABLE")


# maaiveldhoogte nwo (punt)
arcpy.FeatureToPoint_management("nwo_grensprofielzone", "nwo_grensprofielzone_punten", "CENTROID")

existing_fields = arcpy.ListFields(nwo)
needed_fields = ['OBJECTID', 'SHAPE', 'SHAPE_Length', 'Shape','SHAPE_Area','nummer_nwo','soort_nwo']

for field in existing_fields:
    if field.name not in needed_fields:
        arcpy.DeleteField_management("nwo_grensprofielzone_punten", field.name)





# koppel hoogtepunten


punten_ahn3 = "nwo_grensprofielzone_punten"
bufferzones_ahn3 = "nwo_grensprofielzone_punten_zone"
distanceField = "20 Meters"

arcpy.Buffer_analysis(punten_ahn3, bufferzones_ahn3, distanceField)
bufferpunten = 'nwo_grensprofielzone_punten_zone'
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
with arcpy.da.UpdateCursor(punten_temp, ['nummer_nwo']) as cursor1:
    for row in cursor1:
        if row[0] is None:
            cursor1.deleteRow()
        else:
            continue
#
# # bereken statistieken voor iedere bufferzone
array = arcpy.da.FeatureClassToNumPyArray(punten_temp, ('nummer_nwo', 'grid_code'))
df = pd.DataFrame(array)
df_1 = df.dropna()
means = df_1.groupby(['nummer_nwo']).mean()
#
# # vul het woordenboek met setjes
dct = {}
for index, row in means.iterrows():
    naam = index
    hoogte = row['grid_code']
    dct[naam] = (hoogte)


# update profielen met nieuwe ahn
velden = ['nummer_nwo', 'maaiveldhoogte','soort_nwo']
with arcpy.da.UpdateCursor("nwo_grensprofielzone", velden) as cursor:
    for row in cursor:
        id = row[0]
        if id in dct:
            row[1] = float(dct[id])

        cursor.updateRow(row)

# koppel hr
arcpy.SpatialJoin_analysis("nwo_grensprofielzone", hr, "nwo_grensprofielzone_hr", "#", "#", match_option="CLOSEST")
arcpy.CopyFeatures_management('nwo_grensprofielzone_hr', 'nwo_grensprofielzone')




# test of nwo wel of niet voldoende boven rekenpeil ligt
arcpy.AddField_management('nwo_grensprofielzone', "resthoogte", "DOUBLE", 2, field_is_nullable="NULLABLE")
arcpy.AddField_management('nwo_grensprofielzone', "resthoogte_nwo", "DOUBLE", 2, field_is_nullable="NULLABLE")
arcpy.AddField_management('nwo_grensprofielzone', "oppervlakte_tekort", "DOUBLE", 2, field_is_nullable="NULLABLE")
arcpy.AddField_management('nwo_grensprofielzone', "situatie", "TEXT")

velden = ['nummer_nwo', 'Rp', 'maaiveldhoogte','soort_nwo','resthoogte','situatie','resthoogte_nwo','oppervlakte_tekort','SHAPE_Area']
with arcpy.da.UpdateCursor("nwo_grensprofielzone", velden) as cursor:
    for row in cursor:
        if row[2] is not None:
            row[4] = row[2]-row[1]
            cursor.updateRow(row)
        else:
            row[5] = "geen maaiveldhoogte gevonden"


with arcpy.da.UpdateCursor("nwo_grensprofielzone", velden) as cursor:
    for row in cursor:
        if row[2] is not None:
            type = row[3]
            if type == "bunker":
                row[6] = row[4]-8

            else:
                if type == "overig":
                    row[6] = row[4]-3
            cursor.updateRow(row)
        else:
            pass

with arcpy.da.UpdateCursor("nwo_grensprofielzone", velden) as cursor:
    for row in cursor:
        if row[2] is not None:
            resterend = row[6]
            if resterend < 0:
                row[7] = (row[6]*row[8])*-1
                row[5] = "tekort aan hoogte"
            else:
                row[5] = "voldoende hoogte boven rekenpeil"
            cursor.updateRow(row)
        else:
            pass



