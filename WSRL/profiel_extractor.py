import arcpy
import numpy
from arcpy.sa import *
from itertools import groupby
import math
import matplotlib.pyplot as plt
from os import path
import sys
import pandas as pd
import xlwt

sys.setrecursionlimit(1000000000)


arcpy.env.overwriteOutput = True


# Set environment settings
arcpy.env.workspace = 'C:/Users/vince/Desktop/GIS/profielscript_final.gdb'

resultfile = "C:/Users/vince/Desktop/mg_aug_2019.xls" #excel, mocht je daarnaar willen exporteren
profielen_invoer = r'C:\Users\vince\Desktop\GIS\maatgevende_profielen.gdb\mg_aug_2019' # Lars, hier kun je dus je hele berg profielen in zetten!
dv_indeling = r'C:\Users\vince\Desktop\GIS\stph_testomgeving.gdb\dijkvakindeling_sm_juli_2019' # dit is mijn 0-lijn voor de omrekening van xyz naar xz
bovenlijn = "bovenlijn" # offset van 2 m vanaf de 0-lijn om binnenwaarts/buitenwaarts te bepalen

def knip_profielen():
  #intersect with dv indeling --> point
  inFeatures = [profielen_invoer, dv_indeling]
  intersectOutput = "nul_punten_profielen"
  clusterTolerance = 0.5
  arcpy.Intersect_analysis(inFeatures, intersectOutput, "", clusterTolerance, "point")

  #split profielen voor koppeling
  inFeatures = profielen_invoer
  pointFeatures = "nul_punten_profielen"
  outFeatureclass = "profielknips"
  searchRadius = "1"
  arcpy.SplitLineAtPoint_management(inFeatures, pointFeatures, outFeatureclass, searchRadius)

  #koppel aan profielknips
  targetFeatures = "profielknips"
  joinFeatures = bovenlijn
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
    targetFeatures = profielen_invoer
    joinFeatures = dv_indeling
    outfc = "profielen"


    for f in arcpy.ListFields(profielen_invoer):
        if (f.name== 'profielnummer'):
            arcpy.DeleteField_management(profielen_invoer, f.name)
        else:
            pass

    velden = ['dv_nummer']  # defineeer de te behouden velden
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

    # voeg veld profielnummer toe en vul met OID
    inFeatures = outfc
    fieldName1 = "profielnummer"
    fieldPrecision = 1
    arcpy.AddField_management(inFeatures, fieldName1, "DOUBLE", fieldPrecision, field_is_nullable="NULLABLE")

    arcpy.CalculateField_management(inFeatures, "profielnummer", '!OBJECTID!', "PYTHON")




def generate_points():
    # Set local variables
    in_features = 'profielen'
    out_fc_1 = 'profielen_punten'


    # Execute GeneratePointsAlongLines by distance
    arcpy.GeneratePointsAlongLines_management(in_features, out_fc_1, 'DISTANCE',
                                            Distance= 2)
    print "punten om de 2 meter op ieder profiel gemaakt"


def values_points():
    # Set local variables
    inPointFeatures = "profielen_punten"
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
    joinFeatures = dv_indeling
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
    velden = ['z_ahn', 'type_lijn', 'x', 'y', 'profielnummer']  # defineeer de te behouden velden
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
    velden = ['z_ahn', 'type_lijn', 'x', 'y', 'profielnummer', 'rivierzijde']  # defineeer de te behouden velden
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



def to_excel():


    fields = ['profielnummer', 'afstand', 'z_ahn', 'x', 'y']
    list_profielnummer = []
    list_afstand = []
    list_z_ahn = []
    list_x = []
    list_y =[]

    with arcpy.da.SearchCursor("profielen_punten_z_join2", fields) as cur:
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



#basisvolgorde:

join_to_dv_indeling()
generate_points()
values_points()
velden()
koppel_centerline()
knip_profielen()
koppel_bovenlijn()
voeg_velden_toe()
bereken_waardes()
to_excel()





