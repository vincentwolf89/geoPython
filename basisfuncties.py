import gc
gc.collect()
import arcpy
import math
from arcpy.sa import *
import xlwt
import pandas as pd
from itertools import groupby
# uitzetten melding pandas
pd.set_option('mode.chained_assignment', None)

# arcpy.env.overwriteOutput = True


# arcpy.env.workspace = r'C:\Users\vince\Desktop\GIS\test.gdb'

# profielen = 'test_profielen'
# invoerpunten = 'punten_profielen'
# uitvoerpunten = 'punten_profielen_z'
# stapgrootte_punten = 2
# raster = r'C:\Users\vince\Desktop\GIS\losse rasters\ahn3clip\ahn3clip_2m'
# trajectlijn = 'test_trajectlijn'
# code = 'dv_nummer'
# resultfile = "C:/Users/vince/Desktop/testprofielen.xls"



def average(lijst):
    return sum(lijst) / len(lijst)



def set_trajectory_right_left():
    test = test
    #afmaken
    # fc = r'C:\Users\OWNER\Documents\ArcGIS\Default.gdb\samplePolyline'
    #
    # fields = ['x1', 'x2', 'y1', 'y2']
    #
    # # Add fields to your FC
    # for field in fields:
    #     arcpy.AddField_management(fc, str(field), "DOUBLE")
    #
    # with arcpy.da.UpdateCursor(fc, ('x1', 'x2', 'y1', 'y2', "SHAPE@")) as cursor:
    #     for row in cursor:
    #         row[0] = row[4].firstPoint.X
    #         row[1] = row[4].lastPoint.X
    #         row[2] = row[4].firstPoint.Y
    #         row[3] = row[4].lastPoint.Y



def CopyParallelL(plyP,sLength):
    part=plyP.getPart(0)
    lArray=arcpy.Array()
    for ptX in part:
        dL=plyP.measureOnLine(ptX)
        ptX0=plyP.positionAlongLine (dL-0.01).firstPoint
        ptX1=plyP.positionAlongLine (dL+0.01).firstPoint
        dX=float(ptX1.X)-float(ptX0.X)
        dY=float(ptX1.Y)-float(ptX0.Y)
        lenV=math.hypot(dX,dY)
        sX=-dY*sLength/lenV;sY=dX*sLength/lenV
        leftP=arcpy.Point(ptX.X+sX,ptX.Y+sY)
        lArray.add(leftP)
    array = arcpy.Array([lArray])
    section=arcpy.Polyline(array)
    return section

def CopyParallelR(plyP,sLength):
    part=plyP.getPart(0)
    rArray=arcpy.Array()
    for ptX in part:
        dL=plyP.measureOnLine(ptX)
        ptX0=plyP.positionAlongLine (dL-0.01).firstPoint
        ptX1=plyP.positionAlongLine (dL+0.01).firstPoint
        dX=float(ptX1.X)-float(ptX0.X)
        dY=float(ptX1.Y)-float(ptX0.Y)
        lenV=math.hypot(dX,dY)
        sX=-dY*sLength/lenV;sY=dX*sLength/lenV
        rightP=arcpy.Point(ptX.X-sX, ptX.Y-sY)
        rArray.add(rightP)
    array = arcpy.Array([rArray])
    section=arcpy.Polyline(array)
    return section

def copy_trajectory_lr(trajectlijn,code):
    existing_fields = arcpy.ListFields(trajectlijn)
    needed_fields = ['OBJECTID','Shape','Shape_Length','SHAPE', 'SHAPE_Length',code]
    for field in existing_fields:
        if field.name not in needed_fields:
            arcpy.DeleteField_management(trajectlijn, field.name)

    arcpy.AddField_management(trajectlijn, "Width", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management(trajectlijn, "Width", 5, "PYTHON")

    arcpy.CopyFeatures_management(trajectlijn, "river")
    arcpy.CopyFeatures_management(trajectlijn, "land")
    land = "land"
    river = "river"


    with arcpy.da.UpdateCursor(land, ("Shape@", "Width")) as cursor:
        for shp, w in cursor:
            LeftLine = CopyParallelL(shp, w)
            cursor.updateRow((LeftLine, w))

    with arcpy.da.UpdateCursor(river, ("Shape@", "Width")) as cursor:
        for shp, w in cursor:
            RightLine = CopyParallelR(shp, w)
            cursor.updateRow((RightLine, w))
    print "river and land parts created"

def set_measurements_trajectory(profielen,trajectlijn,code,stapgrootte_punten): #rechts = rivier, profielen van binnen naar buiten
    # clean feature
    existing_fields = arcpy.ListFields(profielen)
    needed_fields = ['OBJECTID', 'SHAPE', 'SHAPE_Length','Shape','Shape_Length']
    for field in existing_fields:
        if field.name not in needed_fields:
            arcpy.DeleteField_management(profielen, field.name)

    # add needed fields
    arcpy.AddField_management(profielen, "profielnummer", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(profielen, "van", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(profielen, "tot", "DOUBLE", 2, field_is_nullable="NULLABLE")

    arcpy.CalculateField_management(profielen, "profielnummer", '!OBJECTID!', "PYTHON")

    # split profiles
    rivierlijn = "river"
    landlijn = "land"
    clusterTolerance = 0
    invoer = [profielen, trajectlijn]
    uitvoer = 'snijpunten_centerline'
    arcpy.Intersect_analysis(invoer, uitvoer, "", clusterTolerance, "point")
    arcpy.SplitLineAtPoint_management(profielen, uitvoer, 'profielsplits', 1)

    velden = ['profielnummer', 'van', 'tot',code]

    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable('profielsplits')
    fieldmappings.addTable(rivierlijn)
    fieldmappings.addTable(landlijn)
    keepers = velden

    # join splits to river/land parts
    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    arcpy.SpatialJoin_analysis('profielsplits', rivierlijn, 'profieldeel_rivier', "JOIN_ONE_TO_ONE", "KEEP_COMMON", fieldmappings,
                               match_option="INTERSECT")
    arcpy.SpatialJoin_analysis('profielsplits', landlijn, 'profieldeel_land', "JOIN_ONE_TO_ONE", "KEEP_COMMON",
                               fieldmappings,
                               match_option="INTERSECT")

    # create routes
    arcpy.CalculateField_management("profieldeel_rivier", "tot", '!Shape_Length!', "PYTHON")
    arcpy.CalculateField_management("profieldeel_land", "tot", '!Shape_Length!', "PYTHON")
    arcpy.CalculateField_management("profieldeel_rivier", "van", 0, "PYTHON")
    arcpy.CalculateField_management("profieldeel_land", "van", 0, "PYTHON")


    arcpy.CreateRoutes_lr('profieldeel_rivier', "profielnummer", "routes_rivier_", "TWO_FIELDS", "van", "tot", "", "1", "0",
                          "IGNORE", "INDEX")

    arcpy.CreateRoutes_lr('profieldeel_land', "profielnummer", "routes_land_", "TWO_FIELDS", "tot", "van", "", "1",
                          "0", "IGNORE", "INDEX")

    #join code
    velden = ['profielnummer',code]
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable('routes_land_')
    fieldmappings.addTable('routes_rivier_')
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

    # generate points
    arcpy.GeneratePointsAlongLines_management('routes_land', 'punten_land', 'DISTANCE', Distance= stapgrootte_punten)
    arcpy.GeneratePointsAlongLines_management('routes_rivier', 'punten_rivier', 'DISTANCE', Distance=stapgrootte_punten)


    # id field for joining table
    arcpy.AddField_management('punten_land', 'punt_id', "DOUBLE", field_precision=2, field_is_nullable="NULLABLE")
    arcpy.AddField_management('punten_rivier', 'punt_id', "DOUBLE", field_precision=2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management("punten_land", "punt_id", '!OBJECTID!', "PYTHON")
    arcpy.CalculateField_management("punten_rivier", "punt_id", '!OBJECTID!', "PYTHON")


    # find points along routes
    Output_Event_Table_Properties = "RID POINT MEAS"
    arcpy.LocateFeaturesAlongRoutes_lr('punten_land', 'routes_land', "profielnummer", "1 Meters",
                                       'uitvoer_tabel_land', Output_Event_Table_Properties, "FIRST", "DISTANCE", "ZERO",
                                       "FIELDS", "M_DIRECTON")
    arcpy.LocateFeaturesAlongRoutes_lr('punten_rivier', 'routes_rivier', "profielnummer", "1 Meters",
                                       'uitvoer_tabel_rivier', Output_Event_Table_Properties, "FIRST", "DISTANCE", "ZERO",
                                       "FIELDS", "M_DIRECTON")

    # join fields from table
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

    velden = ['profielnummer', 'afstand', code]
    keepers = velden

    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    arcpy.FeatureToPoint_management("snijpunten_centerline", "punten_centerline")
    arcpy.Merge_management(['punten_land', 'punten_rivier','punten_centerline'], 'punten_profielen', fieldmappings)

    arcpy.CalculateField_management("punten_profielen", "afstand", 'round(!afstand!, 0)', "PYTHON")

    # set centerline values to 0
    with arcpy.da.UpdateCursor('punten_profielen', ['afstand']) as cursor:
        for row in cursor:
            if row[0] == None:
                row[0] = 0
                cursor.updateRow(row)

    print 'points located on routes'

def extract_z_arcpy(invoerpunten, uitvoerpunten, raster): #

    # Test de ArcGIS Spatial Analyst extension license
    arcpy.CheckOutExtension("Spatial")

    # Koppel z-waardes
    ExtractValuesToPoints(invoerpunten, raster, uitvoerpunten,
                          "INTERPOLATE", "VALUE_ONLY")

    # Pas het veld 'RASTERVALU' aan naar 'z_ahn'
    arcpy.AlterField_management(uitvoerpunten, 'RASTERVALU', 'z_ahn')
    print "elevation added to points"

def add_xy(uitvoerpunten,code):

    existing_fields = arcpy.ListFields(uitvoerpunten)
    needed_fields = ['OBJECTID', 'Shape', 'profielnummer', 'afstand', 'z_ahn', code]
    for field in existing_fields:
        if field.name not in needed_fields:
            arcpy.DeleteField_management(trajectlijn, field.name)

    arcpy.env.outputCoordinateSystem = arcpy.Describe(uitvoerpunten).spatialReference
    # Set local variables
    in_features = uitvoerpunten
    properties = "POINT_X_Y_Z_M"
    length_unit = ""
    area_unit = ""
    coordinate_system = ""

    # Generate the extent coordinates using Add Geometry Properties tool
    arcpy.AddGeometryAttributes_management(in_features, properties, length_unit,
                                           area_unit,
                                           coordinate_system)

    arcpy.AlterField_management(uitvoerpunten, 'POINT_X', 'x')
    arcpy.AlterField_management(uitvoerpunten, 'POINT_Y', 'y')

    print "x and y added"

def to_excel(uitvoerpunten,resultfile):


    fields = ['profielnummer', 'afstand', 'z_ahn', 'x', 'y']
    list_profielnummer = []
    list_afstand = []
    list_z_ahn = []
    list_x = []
    list_y =[]

    with arcpy.da.SearchCursor(uitvoerpunten, fields) as cur:
        for row in cur:
            if row[2] is None:
                pass
            elif row[1] == None:
                profielnummer = row[0]
                afstand = 0
                z_ahn = row[2]
                x = row[3]
                y = row[4]


                list_profielnummer.append(profielnummer)
                list_afstand.append(round(afstand,1))
                list_z_ahn.append(round(z_ahn,2))
                list_x.append(round(x,2))
                list_y.append(round(y,2))
            else:
                profielnummer = row[0]
                afstand = row[1]
                z_ahn = row[2]
                x = row[3]
                y = row[4]

                list_profielnummer.append(profielnummer)
                list_afstand.append(round(afstand,1))
                list_z_ahn.append(round(z_ahn,2))
                list_x.append(round(x,2))
                list_y.append(round(y,2))
        # define styles

    style = xlwt.easyxf('font: bold 1')  # define style
    wb = xlwt.Workbook()  # open new workbook
    ws = wb.add_sheet("overzicht")  # add new sheet

    # write headers
    row = 0
    ws.write(row, 0, "profielnummer", style=style)
    ws.write(row, 1, "afstand buk [m, buitenkant -]", style=style)
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
    print "Excel file generated"

def create_contour_lines(trajectlijn,raster,contourlines,distance):
    # buffer trajectlijn
    buffer_traject = 'buffer_traject'

    print "buffer gemaakt"
    arcpy.Buffer_analysis(trajectlijn,buffer_traject, "50 Meters", "FULL", "ROUND", "NONE", "", "PLANAR")

    # clip raster with buffer
    arcpy.Clip_management(raster, "110891,550900001 435080,382600008 140346,480208685 445543,559100002",
                          "clip_dijktraject", buffer_traject, "-3,402823e+038", "ClippingGeometry",
                          "MAINTAIN_EXTENT")

    print "raster geclipt"
    arcpy.Contour_3d("clip_dijktraject", contourlines, distance, "0", "1")
    print "contour gemaakt"

def snap_to_contour(puntenset,contour,output_tabel):
    # neartable
    arcpy.GenerateNearTable_analysis(puntenset, contour, output_tabel, "5 Meters", "NO_LOCATION", "ANGLE", "CLOSEST", "0", "PLANAR")

    arcpy.CopyFeatures_management(contour, "contour_copy")

    # delete onnodig
    id_punten =[]
    id_contour = []
    with arcpy.da.UpdateCursor(output_tabel, ("IN_FID", "NEAR_FID")) as cursor:
        for row in cursor:
            id_punten.append(row[0])
            id_contour.append(row[1])
    contour_copy = 'contour_copy'
    with arcpy.da.UpdateCursor(contour_copy, ("OBJECTID")) as cursor:
        for row in cursor:
            if row[0] not in id_contour:
                cursor.deleteRow()
            else:
                pass

    # snap
    arcpy.Snap_edit(puntenset, "contour_copy EDGE '3 Meters'")
    arcpy.CopyFeatures_management(puntenset, puntenset+"_snap")


def kruinhoogte_groepen(uitvoerpunten,stapgrootte_punten):

    # Verwijder punten zonder z_waarde en rond afstand af
    with arcpy.da.UpdateCursor(uitvoerpunten, ['afstand', 'z_ahn'],sql_clause = (None,"ORDER BY afstand ASC")) as cursor:
        for row in cursor:
            if row[1] is None:
                cursor.deleteRow()
            else:
                row[0] = round(row[0])
                cursor.updateRow(row)
    del cursor

    existing_fields = arcpy.ListFields(uitvoerpunten)
    needed_fields = ['OBJECTID', 'SHAPE', 'SHAPE_Length', 'Shape', 'Shape_Length','afstand','z_ahn','profielnummer', 'dv_nummer','x','y']
    for field in existing_fields:
        if field.name not in needed_fields:
            arcpy.DeleteField_management(uitvoerpunten, field.name)

    # add needed fields
    arcpy.AddField_management(uitvoerpunten, "groep", "DOUBLE", 2, field_is_nullable="NULLABLE")

    # Sorteer punten op profielnummer, afstand
    sort_fields = [["profielnummer", "ASCENDING"], ["afstand", "ASCENDING"]]
    arcpy.Sort_management(uitvoerpunten, "sorted", sort_fields)

    # Bepaal groepsnummer
    with arcpy.da.UpdateCursor('sorted', ['afstand', 'z_ahn', 'groep', 'profielnummer']) as cursor:
            for k, g in groupby(cursor, lambda x: x[3]):
                p = g.next()[0] # eerste waarde

                value = 1

                for row in g:
                    c = row[0] # volgende waarde
                    if abs(c-p) <= stapgrootte_punten:
                        row[2] = value
                        cursor.updateRow(row)
                    else:
                        value+=1
                        # print "Nieuwe volumegroep gemaakt op profiel, g"
                        # pass

                    p = row[0]

                    row[2] = value
                    cursor.updateRow(row)

    del cursor

    # Aanpassen eerste groepwaardes (van None naar 1)
    with arcpy.da.UpdateCursor('sorted', ['groep']) as cursor:
        for row in cursor:
            if row[0] == None:
                row[0] = 1
                cursor.updateRow(row)
    del cursor
    # Vervang niet-gesorteerede puntenset
    arcpy.CopyFeatures_management("sorted", uitvoerpunten)

def max_kruinhoogte(uitvoerpunten,profielen):
    # feature class to numpy array
    array = arcpy.da.FeatureClassToNumPyArray(uitvoerpunten, ('OBJECTID', 'profielnummer', 'dv_nummer', 'afstand', 'z_ahn','groep'))
    df = pd.DataFrame(array)
    sorted = df.sort_values(['profielnummer', 'afstand'], ascending=[True, True])

    groep_profiel = sorted.groupby('profielnummer')

    max_kr = {}
    df_maxwaardes = pd.DataFrame(columns=['profielnummer', 'max_kruinhoogte'])

    for name, groep in groep_profiel:
        df_profiel = pd.DataFrame(columns=['profielnummer', 'max_kruinhoogte'])

        max_kr_profiel = []
        id_max = []
        groep_punten = groep.groupby(["groep"])

        max_kruinhoogtes = []
        profielnummers = []
        OBJECTIDs = []
        for groep, groep_binnen_profiel in groep_punten:
            groep_binnen_profiel['max_kr'] = groep_binnen_profiel.iloc[:, 4].rolling(window=3).mean()
            groep_binnen_profiel['middelpunt_max'] = groep_binnen_profiel['max_kr'].shift(-1)

            # zoeken naar middelste waarde rolling mean voor maken centerline max_kruinhoogte
            max_groep = groep_binnen_profiel['middelpunt_max'].max()

            if type(max_groep) is not float:
                id_midden_max = groep_binnen_profiel.loc[groep_binnen_profiel['middelpunt_max'].idxmax(), 'OBJECTID']
                max_kruin = max_groep

                max_kruinhoogtes.append(max_kruin)
                profielnummers.append(name)
                OBJECTIDs.append(id_midden_max)
                df_profiel.loc[id_midden_max] = name, max_kruin

                # print max_kruin, id_midden_max

                # df_profiel.loc[id_midden_max] = name, max_kruin



            # print groep_binnen_profiel

            midden = groep_binnen_profiel['middelpunt_max'].argmax()




            max_kr_profiel.append(max_groep)

        if max_kr_profiel:
            max_kr[name] = max(max_kr_profiel)
        else:
            pass


        # print max_kruinhoogtes,profielnummers,OBJECTIDs


        # print df_profiel
        kr_max = df_profiel['max_kruinhoogte'].max()
        OID_max = df_profiel['max_kruinhoogte'].idxmax()

        df_maxwaardes.loc[OID_max] = name, kr_max

    print df_maxwaardes
        # break


    # print max_kr
    # update profielen met maximale kruinhoogte

    existing_fields = arcpy.ListFields(profielen)
    needed_fields = ['OBJECTID', 'SHAPE', 'SHAPE_Length', 'Shape','profielnummer', 'dv_nummer']
    for field in existing_fields:
        if field.name not in needed_fields:
            arcpy.DeleteField_management(profielen, field.name)

    arcpy.AddField_management(profielen, "max_kruinhoogte", "DOUBLE", 2, field_is_nullable="NULLABLE")

    with arcpy.da.UpdateCursor(profielen, ['profielnummer','max_kruinhoogte']) as cursor:
        for row in cursor:
            if row[0] in max_kr:
                # print max_kr[row[0]]
                row[1] = round(max_kr[row[0]],2)
                cursor.updateRow(row)







# df maken globaal, df maken per groep, max df groep koppelen met df globaal
# df.set_index('month')

def max_kruinhoogte_test(uitvoerpunten,profielen):
    # feature class to numpy array
    array = arcpy.da.FeatureClassToNumPyArray(uitvoerpunten, ('OBJECTID', 'profielnummer', 'dv_nummer', 'afstand', 'z_ahn','groep'))
    df = pd.DataFrame(array)
    sorted = df.sort_values(['profielnummer', 'afstand'], ascending=[True, True])

    groep_profiel = sorted.groupby('profielnummer')

    max_kr = {}
    df_maxwaardes = pd.DataFrame(columns=['profielnummer', 'max_kruinhoogte'])

    for name, groep in groep_profiel:
        df_profiel = pd.DataFrame(columns=['profielnummer', 'max_kruinhoogte'])

        max_kr_profiel = []
        id_max = []
        groep_punten = groep.groupby(["groep"])

        max_kruinhoogtes = []
        profielnummers = []
        OBJECTIDs = []
        for groep, groep_binnen_profiel in groep_punten:
            groep_binnen_profiel['max_kr'] = groep_binnen_profiel.iloc[:, 4].rolling(window=3).mean()
            groep_binnen_profiel['middelpunt_max'] = groep_binnen_profiel['max_kr'].shift(-1)

            # zoeken naar middelste waarde rolling mean voor maken centerline max_kruinhoogte
            max_groep = groep_binnen_profiel['middelpunt_max'].max()

            if type(max_groep) is not float:
                id_midden_max = groep_binnen_profiel.loc[groep_binnen_profiel['middelpunt_max'].idxmax(), 'OBJECTID']
                max_kruin = max_groep

                max_kruinhoogtes.append(max_kruin)
                profielnummers.append(name)
                OBJECTIDs.append(id_midden_max)
                df_profiel.loc[id_midden_max] = name, max_kruin

                # print max_kruin, id_midden_max

                # df_profiel.loc[id_midden_max] = name, max_kruin



            # print groep_binnen_profiel

            midden = groep_binnen_profiel['middelpunt_max'].argmax()




            max_kr_profiel.append(max_groep)

        if max_kr_profiel:
            max_kr[name] = max(max_kr_profiel)
        else:
            pass


        # print max_kruinhoogtes,profielnummers,OBJECTIDs


        # print df_profiel
        kr_max = df_profiel['max_kruinhoogte'].max()
        OID_max = df_profiel['max_kruinhoogte'].idxmax()

        df_maxwaardes.loc[OID_max] = name, kr_max

    print df_maxwaardes
        # break


    # print max_kr
    # update profielen met maximale kruinhoogte

    existing_fields = arcpy.ListFields(profielen)
    needed_fields = ['OBJECTID', 'SHAPE', 'SHAPE_Length', 'Shape','profielnummer', 'dv_nummer']
    for field in existing_fields:
        if field.name not in needed_fields:
            arcpy.DeleteField_management(profielen, field.name)

    arcpy.AddField_management(profielen, "max_kruinhoogte", "DOUBLE", 2, field_is_nullable="NULLABLE")

    with arcpy.da.UpdateCursor(profielen, ['profielnummer','max_kruinhoogte']) as cursor:
        for row in cursor:
            profielnummer = row[0]
            for i, row in df_maxwaardes.iterrows():
                if row['profielnummer'] == profielnummer:
                    print profielnummer
                    row[1] = round(row['max_kruinhoogte'],2)
                    cursor.updateRow(row)


    # genereer puntenlijn met maximale gemiddelde kruinhoogte
    arcpy.CopyFeatures_management(uitvoerpunten, "kruinhoogte_max_punten")
    list_oid = df_maxwaardes.index.values.tolist()

    with arcpy.da.UpdateCursor("kruinhoogte_max_punten", ("OBJECTID")) as cursor:
        for row in cursor:
            if row[0] in list_oid:
                print row[0]
            else:
                cursor.deleteRow()







