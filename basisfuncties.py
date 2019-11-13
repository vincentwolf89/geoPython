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
    needed_fields = ['OBJECTID', 'SHAPE', 'SHAPE_Length','Shape','Shape_Length',code]
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

    arcpy.CalculateField_management("punten_profielen", "afstand", 'round(!afstand!, 1)', "PYTHON")

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


def kruinhoogte_groepen(uitvoerpunten,stapgrootte_punten,afronding,code):

    # Verwijder punten zonder z_waarde en rond afstand af
    with arcpy.da.UpdateCursor(uitvoerpunten, ['afstand', 'z_ahn'],sql_clause = (None,"ORDER BY afstand ASC")) as cursor:
        for row in cursor:
            if row[1] is None:
                cursor.deleteRow()
            else:
                row[0] = round(row[0],afronding)
                cursor.updateRow(row)
    del cursor

    existing_fields = arcpy.ListFields(uitvoerpunten)
    needed_fields = ['OBJECTID', 'SHAPE', 'SHAPE_Length', 'Shape', 'Shape_Length','afstand','z_ahn','profielnummer', code,'x','y']
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




def max_kruinhoogte(uitvoerpunten,profielen,code,uitvoer_maxpunten):
    # feature class to numpy array
    array = arcpy.da.FeatureClassToNumPyArray(uitvoerpunten, ('OBJECTID', 'profielnummer', code, 'afstand', 'z_ahn','groep'))
    # dataframe, algemeen
    df = pd.DataFrame(array)
    sorted = df.sort_values(['profielnummer', 'afstand'], ascending=[True, True])

    # dataframe voor maximale kruinhoogtes over 1.5m voor alle profielen
    df_maxwaardes = pd.DataFrame(columns=['profielnummer', 'max_kruinhoogte'])

    # sorteer op profielnummer
    groep_profiel = sorted.groupby('profielnummer')

    # itereer over profielen
    for name, groep in groep_profiel:
        # dataframe voor maximale kruinhoogtes over 1.5 m voor alle groepen per profiel
        df_profiel = pd.DataFrame(columns=['profielnummer', 'max_kruinhoogte'])

        # itereer over groepen binnen profielen
        groep_punten = groep.groupby(["groep"])

        for groep, groep_binnen_profiel in groep_punten:
            # bepaal gemiddelde kruinhoogte over 1.5 m(3 meetpunten), extra kolom 'max_kr'
            groep_binnen_profiel['max_kr'] = groep_binnen_profiel.iloc[:, 4].rolling(window=3).mean()
            # shift kolom 'max_kr' om middenpunt voor ieder rolling mean te verkrijgen (punt 2 van 3 meetpunten)
            groep_binnen_profiel['middelpunt_max'] = groep_binnen_profiel['max_kr'].shift(-1)

            # zoeken naar middelpunt rolling mean voor maken centerline max_kruinhoogte
            max_groep = groep_binnen_profiel['middelpunt_max'].max()

            # als rolling mean aanwezig is: opbouwen van dataframe
            if type(max_groep) is not float:
                # koppel_id voor OBJECTID puntenlaag
                ## inbouwen maximale afstand tot referentielijn? (if idxmax-afstand loop)
                id_midden_max = groep_binnen_profiel.loc[groep_binnen_profiel['middelpunt_max'].idxmax(), 'OBJECTID']
                # maximale kruinhoogte (rolling mean)
                max_kruin = max_groep
                # vul dataframe van het profiel aan met max-waardes
                df_profiel.loc[id_midden_max] = name, max_kruin

        # print df_profiel

        # bepaal maximale waardes per profiel en vul dataframe voor maximale kruinhoogtes alle profielen
        # check of profiel een maximale kruinhoogte heeft
        if df_profiel.empty == True:
            pass
        else:
            kr_max = df_profiel['max_kruinhoogte'].max()
            OID_max = df_profiel['max_kruinhoogte'].idxmax()

            df_maxwaardes.loc[OID_max] = name, kr_max

    # print per profiel de gevonden resultaten
    print df_maxwaardes
        # break

    # update profielen met maximale kruinhoogte
    existing_fields = arcpy.ListFields(profielen)
    needed_fields = ['OBJECTID', 'SHAPE', 'SHAPE_Length','Shape_Length','Shape','profielnummer', code]
    for field in existing_fields:
        if field.name not in needed_fields:
            arcpy.DeleteField_management(profielen, field.name)

    # voeg veld voor maximale kruinhoogte toe aan lijn-laag profielen
    arcpy.AddField_management(profielen, "max_kruinhoogte", "DOUBLE", 2, field_is_nullable="NULLABLE")
    with arcpy.da.UpdateCursor(profielen, ['profielnummer','max_kruinhoogte']) as cursor:
        for row in cursor:
            profielnummer = row[0]
            for i, row in df_maxwaardes.iterrows():
                if row['profielnummer'] == profielnummer:
                    row[1] = round(row['max_kruinhoogte'],2)
                    cursor.updateRow(row)


    # genereer puntenlijn met maximale gemiddelde kruinhoogte
    arcpy.CopyFeatures_management(uitvoerpunten, uitvoer_maxpunten)
    list_oid = df_maxwaardes.index.values.tolist()

    # selecteer middelpunten maximale kruinhoogte over 1.5 m
    with arcpy.da.UpdateCursor(uitvoer_maxpunten, ("OBJECTID")) as cursor:
        for row in cursor:
            if row[0] in list_oid:
                pass
            else:
                cursor.deleteRow()






def generate_profiles(profiel_interval,profiel_lengte_land,profiel_lengte_rivier,trajectlijn,code,profielen):
    # traject to points
    arcpy.GeneratePointsAlongLines_management(trajectlijn, 'traject_punten', 'DISTANCE', Distance=profiel_interval, Include_End_Points='END_POINTS')
    arcpy.AddField_management('traject_punten', "profielnummer", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management('traject_punten', "lengte_landzijde", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management('traject_punten', "lengte_rivierzijde", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management('traject_punten', "profielnummer", '!OBJECTID!', "PYTHON")
    arcpy.CalculateField_management('traject_punten', "lengte_landzijde", profiel_lengte_land, "PYTHON")
    arcpy.CalculateField_management('traject_punten', "lengte_rivierzijde", profiel_lengte_rivier, "PYTHON")

    # route voor trajectlijn
    # arcpy.CreateRoutes_lr(trajectlijn, code, "route_traject", "LENGTH", "", "", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")

    existing_fields = arcpy.ListFields(trajectlijn)
    needed_fields = ['OBJECTID', 'SHAPE', 'SHAPE_Length','Shape','Shape_Length',code]
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
    # arcpy.FlipLine_edit(profielen)

    print 'profielen gemaakt op trajectlijn'


def kruinbepalen(invoer, code, uitvoer_binnenkruin, uitvoer_buitenkruin,verschil_maxkruin):
    array = arcpy.da.FeatureClassToNumPyArray(invoer, ('OBJECTID', 'profielnummer', code, 'afstand', 'z_ahn'))
    df = pd.DataFrame(array)
    df2 = df.dropna()
    sorted = df2.sort_values(['profielnummer', 'afstand'], ascending=[True, True])
    grouped = sorted.groupby('profielnummer')

    list_id_bik = []
    list_id_buk = []

    afstand_bik = 5
    afstand_buk = -5

    for name, group in grouped:
        # maximale kruinhoogte
        max_kruin = max(group['z_ahn'])

        landzijde = group.sort_values(['afstand'], ascending=False)  # afnemend, landzijde
        rivierzijde = group.sort_values(['afstand'], ascending=True)  # toenemend, rivierzijde

        # bik
        for index, row in landzijde.iterrows():
            if row['z_ahn'] > max_kruin - verschil_maxkruin and row['afstand'] < afstand_bik and row['afstand'] > 0:
                x_bik = row['afstand']
                y_bik = row['z_ahn']
                list_id_bik.append(row['OBJECTID'])
                break

        # buk
        for index, row in rivierzijde.iterrows():
            if row['z_ahn'] > max_kruin - verschil_maxkruin and row['afstand'] > afstand_buk and row['afstand'] < 0:
                x_buk = row['afstand']
                y_buk = row['z_ahn']
                list_id_buk.append(row['OBJECTID'])
                break

        # # bit
        # # maaiveldhoogte achterland
        # mv_achterland_lijst = []
        # for index, row in landzijde.iterrows():
        #     if row['afstand'] > min_achterland and row['afstand'] < max_achterland :
        #         mv_achterland_lijst.append(row['z_ahn'])
        # mv_achterland = average(mv_achterland_lijst)
        # # print mv_achterland
        # row_iterator = rivierzijde.iterrows()
        # _, last = row_iterator.next()  # take first item from row_iterator
        # for i, row in row_iterator:
        #
        #     hoogte1 = last['z_ahn']
        #     hoogte2 = row['z_ahn']
        #     afstand1 = last['afstand']
        #     afstand2 = row['afstand']
        #     delta_h = abs(hoogte1 - hoogte2)
        #     delta_a = abs(afstand1 - afstand2)
        #     talud = delta_h / delta_a
        #     if afstand2 > 0 and afstand2 < max_achterland and hoogte2 < mv_achterland + 0.5 and talud < max_talud:
        #         x_bit = row['afstand']
        #         y_bit = row['z_ahn']
        #         list_id_bit.append(row['OBJECTID'])
        #         print row['afstand']
        #         break
        #     last = row

        # x1 = group['afstand']
        # y1 = group['z_ahn']
        #
        #
        #
        #
        #
        #
        #
        # fig = plt.figure(figsize=(25, 2))
        # ax = fig.add_subplot(111)
        # ax.plot(x1, y1, linewidth=2, color="red")
        #
        # try:
        #     x_bik
        #     ax.plot(x_bik, y_bik, 'ro', markersize=6)
        # except NameError:
        #     pass
        #
        # try:
        #     x_buk
        #     ax.plot(x_buk, y_buk, 'ro', markersize=6)
        # except NameError:
        #     pass
        # try:
        #     x_bit
        #     ax.plot(x_bit, y_bit, 'ro', markersize=6)
        # except NameError:
        #     pass
        # try:
        #     x_but
        #     ax.plot(x_but, y_but, 'ro', markersize=6)
        # except NameError:
        #     pass
        # plt.show()
        #
        #
        #
        #
        #
        #
        #
        # try:
        #     x_buk
        #     del x_buk, y_buk
        # except NameError:
        #     pass
        #
        # try:
        #     x_bik
        #     del x_bik, y_bik
        # except NameError:
        #     pass
        # try:
        #     x_but
        #     del x_but, y_but
        # except NameError:
        #     pass
        # try:
        #     x_bit
        #     del x_bit, y_bit
        # except NameError:
        #     pass

    # wegschrijven naar gis

    # binnenkruin
    arcpy.MakeFeatureLayer_management(invoer, 'punten_binnenkruin_temp')
    punten_bik = arcpy.SelectLayerByAttribute_management('punten_binnenkruin_temp', "ADD_TO_SELECTION",
                                                         "OBJECTID in (" + str(list_id_bik)[1:-1] + ")")
    arcpy.CopyFeatures_management('punten_binnenkruin_temp', uitvoer_binnenkruin)

    # buitenkruin
    arcpy.MakeFeatureLayer_management(invoer, 'punten_buitenkruin_temp')
    punten_buk = arcpy.SelectLayerByAttribute_management('punten_buitenkruin_temp', "ADD_TO_SELECTION",
                                                         "OBJECTID in (" + str(list_id_buk)[1:-1] + ")")
    arcpy.CopyFeatures_management('punten_buitenkruin_temp', uitvoer_buitenkruin)

    # arcpy.MakeFeatureLayer_management(invoer, 'punten_binnenteen_temp')
    # punten_bit = arcpy.SelectLayerByAttribute_management('punten_binnenteen_temp', "ADD_TO_SELECTION",
    #                                                      "OBJECTID in (" + str(list_id_bit)[1:-1] + ")")
    # arcpy.CopyFeatures_management('punten_binnenteen_temp', 'punten_binnenteen')