import arcpy
import numpy
from arcpy.sa import *
from itertools import groupby
import math
import matplotlib.pyplot as plt
from os import path
import sys
import pandas as pd

sys.setrecursionlimit(1000000000)


arcpy.env.overwriteOutput = True

# Set environment settings
arcpy.env.workspace = 'C:/Users/vince/Desktop/GIS/profielen_vergelijking.gdb'


import arcpy
from arcpy.sa import *
from itertools import groupby
import math


arcpy.env.overwriteOutput = True

# Set environment settings
arcpy.env.workspace = 'C:/Users/vince/Desktop/GIS/profielen_vergelijking.gdb'

def generate_points():
    # Set local variables
    in_features = 'maatgevende_profielen_temp'
    out_fc_1 = 'maatgevende_profielen_temp_punten'


    # Execute GeneratePointsAlongLines by distance
    arcpy.GeneratePointsAlongLines_management(in_features, out_fc_1, 'DISTANCE',
                                            Distance= 2)
    print "punten om de 2 meter op ieder profiel gemaakt"

def values_points():
    # Set local variables
    inPointFeatures = "maatgevende_profielen_temp_punten"
    inRaster = "C:/Users/vince/Desktop/GIS/losse rasters/ahn3clip/ahn3clip_safe"
    outPointFeatures = "maatgevende_profielen_temp_punten_z"

    # Check out the ArcGIS Spatial Analyst extension license
    arcpy.CheckOutExtension("Spatial")

    # Execute ExtractValuesToPoints
    ExtractValuesToPoints(inPointFeatures, inRaster, outPointFeatures,
                          "INTERPOLATE", "VALUE_ONLY")
    print "z-waarde aan punten gekoppeld"

def velden():

    arcpy.env.outputCoordinateSystem = arcpy.Describe("maatgevende_profielen_temp_punten_z").spatialReference
    # Set local variables
    in_features = "maatgevende_profielen_temp_punten_z"
    properties = "POINT_X_Y_Z_M"
    length_unit = ""
    area_unit = ""
    coordinate_system = ""

    # Generate the extent coordinates using Add Geometry Properties tool
    arcpy.AddGeometryAttributes_management(in_features, properties, length_unit,
                                           area_unit,
                                           coordinate_system)

def koppel_centerline():
    targetFeatures = "maatgevende_profielen_temp_punten_z"
    joinFeatures = "dv_indeling"
    outfc = "maatgevende_profielen_temp_punten_z_join"


    # pas de veldnamen aan
    input = 'maatgevende_profielen_temp_punten_z'

    hoogte = 'RASTERVALU'
    hoogte_nieuw = 'z_ahn'

    x_oud = 'POINT_X'
    x_nieuw = 'x'

    y_oud = 'POINT_Y'
    y_nieuw = 'y'

    arcpy.AlterField_management(input, hoogte, hoogte_nieuw)
    arcpy.AlterField_management(input, x_oud, x_nieuw)
    arcpy.AlterField_management(input, y_oud, y_nieuw)




    # spatial join punten 2
    velden = ['z_ahn', 'type_lijn', 'x', 'y', 'profielnummer', 'koppel_id']  # defineeer de te behouden velden
    fieldmappings = arcpy.FieldMappings()

    # stel de fieldmapping in
    fieldmappings.addTable(targetFeatures)
    fieldmappings.addTable(joinFeatures)
    keepers = velden

    # verwijder de niet-benodigde velden
    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))
    # voer de spatial join uit
    arcpy.SpatialJoin_analysis(targetFeatures, joinFeatures, outfc, "#", "#", fieldmappings, match_option="INTERSECT",
                               search_radius=1)
    print "join compleet"

def voeg_velden_toe():
    # Set local variables
    inFeatures = "maatgevende_profielen_temp_punten_z_join"
    fieldName1 = "deltaX"
    fieldName2 = "deltaY"
    fieldName3 = "afstand"
    fieldname4 = "omklap"
    fieldPrecision = 2


    # Execute AddField twice for two new fields
    arcpy.AddField_management(inFeatures, fieldName1, "FlOAT", fieldPrecision, field_is_nullable="NULLABLE")
    arcpy.AddField_management(inFeatures, fieldName2, "FlOAT", fieldPrecision, field_is_nullable="NULLABLE")
    arcpy.AddField_management(inFeatures, fieldName3, "FlOAT", fieldPrecision, field_is_nullable="NULLABLE")
    arcpy.AddField_management(inFeatures, fieldname4, "FlOAT", fieldPrecision, field_is_nullable="NULLABLE")
    print "velden toegevoegd"

def bereken_waardes():
    tbl =  'maatgevende_profielen_temp_punten_z_join'
    fields = ['x', 'y', 'type_lijn', 'deltaX', 'deltaY', 'koppel_id', 'omklap','afstand']
    listp = []
    listx = []
    listy = []
    with arcpy.da.UpdateCursor(tbl, fields) as cur:
        for k, g in groupby(cur, lambda x: x[5]):

            for row in g:
                if row[2] == 0:
                    p = str(row[5])
                    x_vast = (row[0])
                    y_vast = (row[1])
                    listx.append(x_vast)
                    listy.append(y_vast)
                    listp.append(p)
                    #print row[5]
                else:
                    continue
    #print listp
    dictionary_X = dict(zip(listp, listx))
    dictionary_Y = dict(zip(listp, listy))




    with arcpy.da.UpdateCursor(tbl, fields) as cur3:
        for k, g in groupby(cur3, lambda x: x[5]):

            for row in g:
                nummer = str(row[5])
                x_0 = (dictionary_X[(nummer)])
                y_0 = (dictionary_Y[(nummer)])

                row[3] = row[0] - x_0
                if row[3] < 0:
                    row[3] = row[3] * -1
                    row[6] = -1
                elif row[3] > 0:
                    row[6] = 1

                row[4] = row[1] - y_0
                if row[4] < 0:
                    row[4] = row[4] * -1
                    # row[7] = -1
                else:
                    pass

                # if row[6] == 1:
                # row[4] = row[4]*-1

                row[7] = math.sqrt((row[3]) ** 2 + (row[4]) ** 2)

                if row[6] == -1:
                    row[7] = row[7] * -1

                # if row[7] < 0:
                # row[5] = row[5]*-1
                # else:
                # pass
                cur3.updateRow(row)



def plotter():
    input = "profielen_vergelijking_punten_z_join_test"
    arr = arcpy.da.FeatureClassToNumPyArray(input, ('profielnummer', 'z_ahn', 'afstand', 'koppel_id'))
    df = pd.DataFrame(arr)

    input2 = "maatgevende_profielen_temp_punten_z_join"
    arr2 = arcpy.da.FeatureClassToNumPyArray(input, ('z_ahn', 'afstand', 'koppel_id'))
    df2 = pd.DataFrame(arr2)

    outpath = "C:/Users/vince/Desktop/plots_safe"



    grouped = df.groupby('koppel_id')


    for name, group in grouped:
        fig = plt.figure(figsize=(50, 10))
        group.set_index('afstand', inplace=True)
        group.groupby('profielnummer')['z_ahn'].plot(legend=False)


        #if name in naam:
            #x = dictionary_x_as[(name)]
            #y = dictionary_y_as[(name)]
            #plt.plot(x, y, linewidth=4.0, color= "red")
        #else:
            #pass

        #x = dictionary_x_as[(name)]
        #y = dictionary_y_as[(name)]
        #plt.plot(x, y, linewidth=2.0)

        #plt.show()
        #plt.savefig(str(name)+".png")
        #plt.savefig(path.join(outpath, "profiel_{0}.png".format(name)), pad_inches=0.02, dpi=300, bbox_inches='tight')
        #plt.figure(figsize=(20, 2))
        plt.axis([-100, 100, None, None])
        plt.savefig(path.join(outpath, "profiel_{0}.png".format(name)), figsize=(20, 2))
        plt.close()


#generate_points()
#values_points()
#velden()
#koppel_centerline()
#voeg_velden_toe()
#bereken_waardes()


input = "maatgevende_profielen_temp_punten_z_join"
arr2 = arcpy.da.FeatureClassToNumPyArray(input, ('z_ahn', 'afstand', 'koppel_id'))
df2 = pd.DataFrame(arr2)

grouped2 = df2.groupby('koppel_id')

naam = []
x_as = []
z_ahn = []

for name, group in grouped2:
    naam.append(name)
    x = group['afstand']
    y = group['z_ahn']
    x_as.append(x)
    z_ahn.append(y)



dictionary_x_as = dict(zip(naam, x_as))
dictionary_y_as = dict(zip(naam, z_ahn))


#x_0 = (dictionary_X[(nummer)])
#y_0 = (dictionary_Y[(nummer)])

#x_0 = (dictionary_X[(nummer)])
x = dictionary_x_as[(3)]
y = dictionary_y_as[(3)]

plotter()






