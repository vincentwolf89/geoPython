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
arcpy.env.workspace = 'C:/Users/vince/Desktop/GIS/profielscript_final.gdb'

def knip_profielen():
  #intersect with dv indeling --> point
  inFeatures = ["profielen_25m", "dv_indeling"]
  intersectOutput = "nul_punten_profielen_50m"
  clusterTolerance = 0.5
  arcpy.Intersect_analysis(inFeatures, intersectOutput, "", clusterTolerance, "point")

  #split profielen voor koppeling
  inFeatures = "profielen_25m"
  pointFeatures = "nul_punten_profielen_50m"
  outFeatureclass = "profielknips"
  searchRadius = "1"
  arcpy.SplitLineAtPoint_management(inFeatures, pointFeatures, outFeatureclass, searchRadius)

  #koppel aan profielknips
  targetFeatures = "profielknips"
  joinFeatures = "bovenlijn"
  outfc = "profielen_bovenlijn"

  velden = ['profielnummer','rivierzijde']  # defineeer de te behouden velden
  fieldmappings = arcpy.FieldMappings()


  fieldmappings.addTable(targetFeatures)
  fieldmappings.addTable(joinFeatures)
  keepers = velden

  for field in fieldmappings.fields:
    if field.name not in keepers:
      fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))
  # voer de spatial join uit
  arcpy.SpatialJoin_analysis(targetFeatures, joinFeatures, outfc, "#", "#", fieldmappings, match_option="INTERSECT",
                             search_radius=1)



def join_to_dv_indeling():
    targetFeatures = "profielen_25m"
    joinFeatures = "dv_indeling"
    outfc = "profielen"


    velden = ['profielnummer', 'koppel_id', 'dv_nummer']  # defineeer de te behouden velden
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


def generate_points():
    # Set local variables
    in_features = 'profielen'
    out_fc_1 = 'profielen_50m_punten'


    # Execute GeneratePointsAlongLines by distance
    arcpy.GeneratePointsAlongLines_management(in_features, out_fc_1, 'DISTANCE',
                                            Distance= 2)
    print "punten om de 2 meter op ieder profiel gemaakt"


def values_points():
    # Set local variables
    inPointFeatures = "profielen_50m_punten"
    inRaster = "C:/Users/vince/Desktop/GIS/losse rasters/ahn3clip/ahn3clip_safe"
    outPointFeatures = "profielen_punten_z"

    # Check out the ArcGIS Spatial Analyst extension license
    arcpy.CheckOutExtension("Spatial")

    # Execute ExtractValuesToPoints
    ExtractValuesToPoints(inPointFeatures, inRaster, outPointFeatures,
                          "INTERPOLATE", "VALUE_ONLY")
    print "z-waarde aan punten gekoppeld"


def velden():

    arcpy.env.outputCoordinateSystem = arcpy.Describe("profielen_punten_z").spatialReference
    # Set local variables
    in_features = "profielen_punten_z"
    properties = "POINT_X_Y_Z_M"
    length_unit = ""
    area_unit = ""
    coordinate_system = ""

    # Generate the extent coordinates using Add Geometry Properties tool
    arcpy.AddGeometryAttributes_management(in_features, properties, length_unit,
                                           area_unit,
                                           coordinate_system)


def koppel_centerline():
    targetFeatures = "profielen_punten_z"
    joinFeatures = "dv_indeling"
    outfc = "profielen_punten_z_join1"


    # pas de veldnamen aan
    input = 'profielen_punten_z'

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

def koppel_bovenlijn():
    targetFeatures = "profielen_punten_z_join1"
    joinFeatures = "profielen_bovenlijn"
    outfc = "profielen_punten_z_join2"


    # spatial join punten 2
    velden = ['z_ahn', 'type_lijn', 'x', 'y', 'profielnummer', 'koppel_id', 'rivierzijde']  # defineeer de te behouden velden
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
    inFeatures = "profielen_punten_z_join2"
    fieldName1 = "deltaX"
    fieldName2 = "deltaY"
    fieldName3 = "afstand"
    #fieldname4 = "omklap"
    fieldPrecision = 2


    # Execute AddField twice for two new fields
    arcpy.AddField_management(inFeatures, fieldName1, "FlOAT", fieldPrecision, field_is_nullable="NULLABLE")
    arcpy.AddField_management(inFeatures, fieldName2, "FlOAT", fieldPrecision, field_is_nullable="NULLABLE")
    arcpy.AddField_management(inFeatures, fieldName3, "FlOAT", fieldPrecision, field_is_nullable="NULLABLE")
    #arcpy.AddField_management(inFeatures, fieldname4, "FlOAT", fieldPrecision, field_is_nullable="NULLABLE")
    print "velden toegevoegd"


def bereken_waardes():
    tbl =  'profielen_punten_z_join2'
    fields = ['x', 'y', 'type_lijn', 'deltaX', 'deltaY', 'profielnummer', 'rivierzijde','afstand']
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
                else:
                  pass

                row[4] = row[1] - y_0
                if row[4] < 0:
                    row[4] = row[4] * -1
                else:
                    pass

                row[7] = math.sqrt((row[3]) ** 2 + (row[4]) ** 2)

                if row[7] < 0 and row[6] == 1:
                    row[7] = row[7]*-1
                elif row[7] > 0 and row[6] == None:
                    row[7] = row[7]*-1
                else:
                    pass


                # if row[7] < 0:
                # row[5] = row[5]*-1
                # else:
                # pass
                cur3.updateRow(row)


def netjes_maken():
    #maak punten op de snijpunten
    inFeatures = ["maatgevende_profielen", "dv_indeling"]
    clusterTolerance = 0
    intersectOutput = "punten_split_mg"
    arcpy.Intersect_analysis(inFeatures, intersectOutput, "", clusterTolerance, "point")

    #split profielen
    inFeatures = "maatgevende_profielen"
    pointFeatures = "punten_split_mg"
    outFeatureclass = "split_mg"
    searchRadius = "1.0 Meters"

    arcpy.SplitLineAtPoint_management(inFeatures, pointFeatures, outFeatureclass, searchRadius)
    print "lijnen zijn gesplitst"

    # join to punten

    targetFeatures = "maatgevende_profielen_temp_punten_z_join"
    joinFeatures = "split_mg"
    outfc = "maatgevende_profielen_final"

    # voer de spatial join uit
    arcpy.SpatialJoin_analysis(targetFeatures, joinFeatures, outfc, "#", "#", match_option="INTERSECT",
                               search_radius=1)
    print "join compleet"

    tbl = 'maatgevende_profielen_final'
    fields = ['x', 'y', 'type_lijn', 'deltaX', 'deltaY', 'profielnummer', 'omklap', 'afstand', 'bovenkant']
    listp = []
    listx = []
    listy = []

    with arcpy.da.UpdateCursor(tbl, fields) as cur3:
        for k, g in groupby(cur3, lambda x: x[5]):

            for row in g:

                if row[8] == "ja" and row[7] > 0:
                    pass
                else:
                    row[7] = row[7] * -1

                cur3.updateRow(row)

                if row[8] == None and row[7] > 0:
                    row[7] = row[7] * -1
                else:
                    pass
                cur3.updateRow(row)

def plotter():
    # maak apart gedeelte voor dictionaries maatgevende profielen
    input2 = "profielen_maatgevend_punten_z_join2"
    arr2 = arcpy.da.FeatureClassToNumPyArray(input2, ('z_ahn', 'afstand', 'koppel_id'))
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


    x = dictionary_x_as[(3)]
    y = dictionary_y_as[(3)]

    # plot maatgevende en serie profielen, per dijkvak (koppel_id)
    input = "profielen_punten_z_join2"
    arr = arcpy.da.FeatureClassToNumPyArray(input, ('profielnummer', 'z_ahn', 'afstand', 'koppel_id'))
    df = pd.DataFrame(arr)
    outpath = "C:/Users/vince/Desktop/plots_safe_test"

    grouped = df.groupby('koppel_id')

    for name, group in grouped:

        group.set_index('afstand', inplace=True)
        group.groupby('profielnummer')['z_ahn'].plot(legend=False)

        if name in naam:
            x = dictionary_x_as[(name)]
            y = dictionary_y_as[(name)]
            plt.plot(x, y, linewidth=3.0, color= "red")
        else:
            pass

        #plt.show()

        plt.xlim(-50, 50)
        plt.ylim(-5, 20)
        #plt.show()
        plt.savefig(path.join(outpath, "profiel_{0}.png".format(name)), pad_inches=0.02, dpi=300, bbox_inches='tight')
        plt.close()

# plotter()
# join_to_dv_indeling()
# netjes_maken()


#basisvolgorde:

# join_to_dv_indeling()
# generate_points()
# values_points()
# velden()
# koppel_centerline()
# knip_profielen()
# koppel_bovenlijn()
# voeg_velden_toe()
# bereken_waardes()



