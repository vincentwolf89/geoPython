## hoogtetoets HDSR 2019
# hierin worden de basisfuncties beschreven die nodig zijn om de batch te kunnen doorrekenen, zier hiervoor 'batch_ht_hdsr.py'

# importeren van benodigde modules
import gc
gc.collect()
import arcpy
import math
from arcpy.sa import *
import pandas as pd
from itertools import groupby
from xlsxwriter.workbook import Workbook
import matplotlib.pyplot as plt

# uitzetten foutmelding pandas
pd.set_option('mode.chained_assignment', None)


# hulpfuncties
def CopyParallelL(plyP,sLength): #functie voor profielen maken haaks op trajectlijn
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
def CopyParallelR(plyP,sLength): #functie voor profielen maken haaks op trajectlijn
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
def average(lijst):
    return sum(lijst) / len(lijst)

# functie voor het bepalen van land- en rivierzijde
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
    # print "Water- en landdelen gemaakt"

# functie voor het bepalen van profielen op de trajectlijn
def generate_profiles(profiel_interval,profiel_lengte_land,profiel_lengte_rivier,trajectlijn,code,toetspeil,profielen):
    # maak punten op profielen
    arcpy.GeneratePointsAlongLines_management(trajectlijn, 'traject_punten', 'DISTANCE', Distance=profiel_interval, Include_End_Points='END_POINTS')
    arcpy.AddField_management('traject_punten', "profielnummer", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management('traject_punten', "lengte_landzijde", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management('traject_punten', "lengte_rivierzijde", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management('traject_punten', "profielnummer", '!OBJECTID!', "PYTHON")
    arcpy.CalculateField_management('traject_punten', "lengte_landzijde", profiel_lengte_land, "PYTHON")
    arcpy.CalculateField_management('traject_punten', "lengte_rivierzijde", profiel_lengte_rivier, "PYTHON")

    # route voor trajectlijn
    existing_fields = arcpy.ListFields(trajectlijn)
    needed_fields = ['OBJECTID', 'SHAPE', 'SHAPE_Length','Shape','Shape_Length',code,toetspeil]
    for field in existing_fields:
        if field.name not in needed_fields:
            arcpy.DeleteField_management(trajectlijn, field.name)
    arcpy.AddField_management(trajectlijn, "van", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(trajectlijn, "tot", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management(trajectlijn, "van", 0, "PYTHON")
    # arcpy.CalculateField_management(trajectlijn, "tot", "!Shape_Length!", "PYTHON")
    arcpy.CalculateField_management(trajectlijn, "tot", "round(!shape.length!)", "PYTHON")
    arcpy.CreateRoutes_lr(trajectlijn, code, 'route_traject', "TWO_FIELDS", "van", "tot", "", "1",
                          "0", "IGNORE", "INDEX")


    # lokaliseer profielpunten
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
    # tijdelijke layer
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
    # arcpy.FlipLine_edit(profielen) # alleen nodig indien profielen verkeerde richting hebben

    # print 'Profielen gemaakt op trajectlijn'

# functie voor het bepalen van afstanden van meetpunten op profielen t.o.v. trajectlijn
def set_measurements_trajectory(profielen, trajectlijn, code, stapgrootte_punten,
                                toetspeil):  # rechts = rivier, profielen van binnen naar buiten
    # schoonmaken laag
    existing_fields = arcpy.ListFields(profielen)
    needed_fields = ['OBJECTID', 'SHAPE', 'SHAPE_Length', 'Shape', 'Shape_Length', code, toetspeil]
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
    velden = ['profielnummer', code]
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

    # punten op lijn genereren
    arcpy.GeneratePointsAlongLines_management('routes_land', 'punten_land', 'DISTANCE', Distance=stapgrootte_punten)
    arcpy.GeneratePointsAlongLines_management('routes_rivier', 'punten_rivier', 'DISTANCE',
                                              Distance=stapgrootte_punten)

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

    velden = ['profielnummer', 'afstand', code]
    keepers = velden

    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    arcpy.FeatureToPoint_management("snijpunten_centerline", "punten_centerline")
    arcpy.Merge_management(['punten_land', 'punten_rivier', 'punten_centerline'], 'punten_profielen', fieldmappings)

    arcpy.CalculateField_management("punten_profielen", "afstand", 'round(!afstand!, 1)', "PYTHON")

    # zet trajectlijn-waardes op 0
    with arcpy.da.UpdateCursor('punten_profielen', ['afstand']) as cursor:
        for row in cursor:
            if row[0] == None:
                row[0] = 0
                cursor.updateRow(row)

    print 'Meetpunten op routes gelokaliseerd'

# functie voor het koppelen van hoogtewaardes aan meetpunten
def extract_z_arcpy(invoerpunten, uitvoerpunten, raster): #

    # Test de ArcGIS Spatial Analyst extension license
    arcpy.CheckOutExtension("Spatial")

    # Koppel z-waardes
    ExtractValuesToPoints(invoerpunten, raster, uitvoerpunten,
                          "INTERPOLATE", "VALUE_ONLY")

    # Pas het veld 'RASTERVALU' aan naar 'z_ahn'
    arcpy.AlterField_management(uitvoerpunten, 'RASTERVALU', 'z_ahn')
    print "Hoogtewaarde aan punten gekoppeld"

# functie voor het koppelen van XY-coordinaten aan de meetpunten voor o.a. Excel uitvoer
def add_xy(uitvoerpunten,code):

    # schoonmaken laag
    existing_fields = arcpy.ListFields(uitvoerpunten)
    needed_fields = ['OBJECTID', 'Shape', 'profielnummer', 'afstand', 'z_ahn', code]
    for field in existing_fields:
        if field.name not in needed_fields:
            arcpy.DeleteField_management(trajectlijn, field.name)

    arcpy.env.outputCoordinateSystem = arcpy.Describe(uitvoerpunten).spatialReference
    # bepaal benodigde variabelen
    in_features = uitvoerpunten
    properties = "POINT_X_Y_Z_M"
    length_unit = ""
    area_unit = ""
    coordinate_system = ""

    # voeg gewenste geometrie-attributen toe
    arcpy.AddGeometryAttributes_management(in_features, properties, length_unit,
                                           area_unit,
                                           coordinate_system)

    # pas veldnamen aan
    arcpy.AlterField_management(uitvoerpunten, 'POINT_X', 'x')
    arcpy.AlterField_management(uitvoerpunten, 'POINT_Y', 'y')

    print "XY-coordinaten aan punten gekoppeld"

# functie voor het schrijven van de gewenste uitvoer naar .xlsx-formaat
def excel_writer(uitvoerpunten,code,excel,id,trajecten,toetspeil):
    # toetshoogte aan uitvoerpunten koppelen
    arcpy.JoinField_management(uitvoerpunten, 'Naam', trajecten, 'Naam', toetspeil)

    # binnenhalen van dataframe
    array = arcpy.da.FeatureClassToNumPyArray(uitvoerpunten,('OBJECTID', 'profielnummer', code, 'afstand', 'z_ahn', 'x', 'y',toetspeil))

    df = pd.DataFrame(array)
    df = df.dropna()
    sorted = df.sort_values(['profielnummer', 'afstand'], ascending=[True, True])

    # opbouw xlsx
    workbook = Workbook(excel)
    worksheet = workbook.add_worksheet()

    # stijl toevoegen voor headers
    bold = workbook.add_format({'bold': True})


    # schrijf kolomnamen
    worksheet.write(0, 0, "Profielnummer", bold)
    worksheet.write(0, 1, "Afstand [m]", bold)
    worksheet.write(0, 2, "Hoogte AHN3 [m NAP]", bold)
    worksheet.write(0, 3, "x [RD]", bold)
    worksheet.write(0, 4, "y [RD]", bold)

    # schrijf kolommen vanuit df
    worksheet.write_column('A2', sorted['profielnummer'])
    worksheet.write_column('B2', sorted['afstand'])
    worksheet.write_column('C2', sorted['z_ahn'])
    worksheet.write_column('D2', sorted['x'])
    worksheet.write_column('E2', sorted['y'])

    # groepeer per profielnummer
    grouped = sorted.groupby('profielnummer')

    # definieer startrij
    startpunt = 2


    # lege lijngrafiek invoegen met zowel afstand als hoogte als invoer
    line_chart1 = workbook.add_chart({'type': 'scatter',
                                 'subtype': 'straight'})

    # toetshoogte toevoegen als horizontale lijn, deel 1 voor legenda
    minimum = min(sorted['afstand'])
    maximum = max(sorted['afstand'])
    th = sorted[toetspeil].iloc[0]

    worksheet.write('K8', minimum)
    worksheet.write('K9', maximum)
    worksheet.write('K10', th)
    worksheet.write('K11', th)

    line_chart1.add_series({
        'name': 'toetshoogte: ' + str(th) + ' m NAP',

        'categories': '=Sheet1!$K$8:$K$9',
        'values': '=Sheet1!$K$10:$K$11',
        'line': {
            'color': 'red',
            'width': 1.5,
            'dash_type': 'long_dash'
        }
    })

    # lijnen toevoegen aan lijngrafiek
    count = 0
    for name, group in grouped:
        profielnaam = str(int(name))
        meetpunten = len(group['profielnummer'])

        # eerste profiel
        if count == 0:
            line_chart1.add_series({
                'name': 'profiel ' + profielnaam,

                'categories': '=Sheet1!B' + str(startpunt) + ':B' + str(meetpunten + 1),
                'values': '=Sheet1!C' + str(startpunt) + ':C' + str(meetpunten + 1),
                'line': {'width': 1}
            })
            count +=1
        # opvolgende profielen
        else:
            if count is not 0:
                line_chart1.add_series({
                    'name': 'profiel '+profielnaam,

                    'categories': '=Sheet1!B'+str(startpunt)+':B' + str(startpunt+meetpunten-1),
                    'values':     '=Sheet1!C'+str(startpunt)+':C' + str(startpunt+meetpunten-1),
                    'line': {'width': 1}
                })
        # startpunt verzetten
        startpunt += (meetpunten)



    # toetshoogte toevoegen als horizontale lijn, deel 2 voor voorgrond-lijn
    minimum = min(sorted['afstand'])
    maximum = max(sorted['afstand'])
    th = sorted[toetspeil].iloc[0]

    worksheet.write('K8', minimum)
    worksheet.write('K9', maximum)
    worksheet.write('K10', th)
    worksheet.write('K11', th)

    line_chart1.add_series({
        'name': 'toetshoogte: ' + str(th) + ' m NAP',

        'categories': '=Sheet1!$K$8:$K$9',
        'values': '=Sheet1!$K$10:$K$11',
        'line': {
            'color': 'red',
            'width': 1.5,
            'dash_type': 'long_dash'
        }
    })

    # kolommen aanpassen
    line_chart1.set_title({'name': 'Overzicht profielen '+id})
    line_chart1.set_x_axis({'name': 'Afstand [m]'})
    line_chart1.set_y_axis({'name': 'Hoogte [m NAP]'})
    line_chart1.set_x_axis({'interval_tick': 0.5})
    line_chart1.set_x_axis({'min': -10, 'max': 20})
    line_chart1.set_size({'width': 1000, 'height': 400})
    # line_chart1.set_style(1)
    worksheet.insert_chart('G3', line_chart1)
    workbook.close()

    print '.xlsx-bestand gemaakt voor profielset'

# functie voor het bepalen van aaneengesloten groepen van meetpunten voor het bepalen van de gemiddelde maximale kruinhoogte
def kruinhoogte_groepen(uitvoerpunten,stapgrootte_punten,afronding,code):

    # verwijder punten zonder z_waarde en rond afstand af
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

    # voeg benodigde velden toe
    arcpy.AddField_management(uitvoerpunten, "groep", "DOUBLE", 2, field_is_nullable="NULLABLE")

    # sorteer punten op profielnummer, afstand
    sort_fields = [["profielnummer", "ASCENDING"], ["afstand", "ASCENDING"]]
    arcpy.Sort_management(uitvoerpunten, "sorted", sort_fields)

    # bepaal groepsnummer
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

    # aanpassen eerste groepwaardes (van None naar 1)
    with arcpy.da.UpdateCursor('sorted', ['groep']) as cursor:
        for row in cursor:
            if row[0] == None:
                row[0] = 1
                cursor.updateRow(row)
    del cursor
    # vervang niet-gesorteerde puntenset
    arcpy.CopyFeatures_management("sorted", uitvoerpunten)
    print 'Kruinhoogte voor alle aaneengesloten groepen binnen profielen bepaald'

# functie voor het bepalen van de gemiddelde maximale kruinhoogte
def max_kruinhoogte(uitvoerpunten, profielen, code, uitvoer_maxpunten,min_afstand,max_afstand,toetspeil):
    # maak dataframe van featureclass
    array = arcpy.da.FeatureClassToNumPyArray(uitvoerpunten,
                                              ('OBJECTID', 'profielnummer', code, 'afstand', 'z_ahn', 'groep'))
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
        df_profiel_tester = pd.DataFrame(columns=['profielnummer', 'max_kruinhoogte'])
        # itereer over groepen binnen profielen
        groep_punten = groep.groupby(["groep"])

        for groep, groep_binnen_profiel in groep_punten:
            # bepaal gemiddelde kruinhoogte over 1.5 m(3 meetpunten), extra kolom 'max_kr'
            groep_binnen_profiel['max_kr'] = groep_binnen_profiel.iloc[:, 4].rolling(window=3).mean()
            # shift kolom 'max_kr' om middenpunt voor ieder rolling mean te verkrijgen (punt 2 van 3 meetpunten)
            groep_binnen_profiel['middelpunt_max'] = groep_binnen_profiel['max_kr'].shift(-1)

            # zoeken naar middelpunt rolling mean voor maken centerline max_kruinhoogte
            for i, row in groep_binnen_profiel.iterrows():
                afstand = row['afstand']
                if afstand > min_afstand and afstand < max_afstand:
                    df_profiel_tester.loc[row['OBJECTID']] = name, row['middelpunt_max']
        if df_profiel_tester.empty == True:
            pass
        else:
            df_profielmax = df_profiel_tester['max_kruinhoogte'].max()
            id_df_profielmax = df_profiel_tester['max_kruinhoogte'].idxmax()

            df_profiel.loc[id_df_profielmax] = name, df_profielmax

        # check of profiel een maximale kruinhoogte heeft
        if df_profiel.empty == True:
            pass
        else:
            kr_max = df_profiel['max_kruinhoogte'].max()
            OID_max = df_profiel['max_kruinhoogte'].idxmax()

            df_maxwaardes.loc[OID_max] = name, kr_max
            # print df_profiel

    # print per profiel de gevonden resultaten
    print df_maxwaardes

    # update profielen met maximale kruinhoogte
    existing_fields = arcpy.ListFields(profielen)
    needed_fields = ['OBJECTID', 'SHAPE', 'SHAPE_Length', 'Shape_Length', 'Shape', 'profielnummer', code,toetspeil]
    for field in existing_fields:
        if field.name not in needed_fields:
            arcpy.DeleteField_management(profielen, field.name)

    # voeg veld voor maximale kruinhoogte toe aan lijn-laag profielen
    arcpy.AddField_management(profielen, "maxKruinhoogte2014", "DOUBLE", 2, field_is_nullable="NULLABLE")
    with arcpy.da.UpdateCursor(profielen, ['profielnummer', 'maxKruinhoogte2014']) as cursor:
        for row in cursor:
            profielnummer = row[0]
            for i, row in df_maxwaardes.iterrows():
                if row['profielnummer'] == profielnummer:
                    row[1] = round(row['max_kruinhoogte'], 2)
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

    print 'Maximale kruinhoogte voor ieder profiel bepaald indien mogelijk'

# functie voor het bepalen van de binnen-en buitenkruin locaties per profiel
def kruinbepalen(invoer, code, uitvoer_binnenkruin, uitvoer_buitenkruin,verschil_maxkruin,min_afstand,max_afstand):
    # maak dataframe van featureclass
    array = arcpy.da.FeatureClassToNumPyArray(invoer, ('OBJECTID', 'profielnummer', code, 'afstand', 'z_ahn'))
    df = pd.DataFrame(array)
    df2 = df.dropna()
    sorted = df2.sort_values(['profielnummer', 'afstand'], ascending=[True, True])
    grouped = sorted.groupby('profielnummer')

    list_id_bik = []
    list_id_buk = []

    afstand_bik = max_afstand
    afstand_buk = min_afstand

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

    # wegschrijven naar gis

    # binnenkruin
    if list_id_bik:
        arcpy.MakeFeatureLayer_management(invoer, 'punten_binnenkruin_temp')
        punten_bik = arcpy.SelectLayerByAttribute_management('punten_binnenkruin_temp', "ADD_TO_SELECTION",
                                                             "OBJECTID in (" + str(list_id_bik)[1:-1] + ")")
        arcpy.CopyFeatures_management('punten_binnenkruin_temp', uitvoer_binnenkruin)

    # buitenkruin
    if list_id_buk:
        arcpy.MakeFeatureLayer_management(invoer, 'punten_buitenkruin_temp')
        punten_buk = arcpy.SelectLayerByAttribute_management('punten_buitenkruin_temp', "ADD_TO_SELECTION",
                                                             "OBJECTID in (" + str(list_id_buk)[1:-1] + ")")
        arcpy.CopyFeatures_management('punten_buitenkruin_temp', uitvoer_buitenkruin)


    print 'Kruinpunten bepaald'

# functie voor het bepalen van de binnenteen per profiel
def binnenteenbepalen(invoer, code, min_achterland, max_achterland, uitvoer_binnenteen, min_afstand,
                      max_afstand,uitvoer_binnenkruin):
    # test op binnenkruin bepaald is
    if arcpy.Exists(uitvoer_binnenkruin):
        # maak dataframe van featureclass
        array = arcpy.da.FeatureClassToNumPyArray(invoer, ('OBJECTID', 'profielnummer', code, 'afstand', 'z_ahn'))
        df = pd.DataFrame(array)
        df2 = df.dropna()
        sorted = df2.sort_values(['profielnummer', 'afstand'], ascending=[True, True])
        grouped = sorted.groupby('profielnummer')

        # lijst OBJECTIDs
        list_id_bit = []

        # binnenhalen binnenkruindata
        array_bik = arcpy.da.FeatureClassToNumPyArray(uitvoer_binnenkruin, ('OBJECTID', 'profielnummer', code, 'afstand', 'z_ahn'))
        df_bik = pd.DataFrame(array_bik)

        for name, group in grouped:

            bik_afstand = df_bik.loc[df_bik['profielnummer'] == name, 'afstand']
            for item in bik_afstand.values:
                bik = item

            # maximale kruinhoogte
            max_kruin = max(group['z_ahn'])
            landzijde = group.sort_values(['afstand'], ascending=False)  # afnemend, landzijde
            rivierzijde = group.sort_values(['afstand'], ascending=True)  # toenemend, rivierzijde

            # maaiveldhoogte dijk
            mv_dijk_lijst = []
            for index, row in landzijde.iterrows():
                if row['afstand'] > min_afstand and row['afstand'] < max_afstand:
                    mv_dijk_lijst.append(row['z_ahn'])

            if mv_dijk_lijst:
                mv_dijk = average(mv_dijk_lijst)
                # print mv_dijk

            # maaiveldhoogte achterland
            mv_achterland_lijst = []
            for index, row in landzijde.iterrows():
                if row['afstand'] > min_achterland and row['afstand'] < max_achterland:
                    mv_achterland_lijst.append(row['z_ahn'])

            if mv_achterland_lijst:
                mv_achterland = average(mv_achterland_lijst)
                # print mv_achterland

            x1 = group['afstand']
            y1 = group['z_ahn']

            # extra, toevoegen indien nodig
            # f = interp1d(x1, y1, kind='linear')
            # x_new = np.linspace(min(x1), max(x1), 200)

            # plot, standaard uit
            # fig = plt.figure(figsize=(25, 2))
            # ax = fig.add_subplot(111)
            # ax.plot(x1, y1, linewidth=2, color="red")
            # ax.plot(x_new, f(x_new), linewidth=2, color="blue")
            # ax.plot(x_new, f(x_new), 'o', color="blue")
            # ax.plot(x1, y1, 'o', color="red")

            # aanpassen van dataframe voor bepaling binnenteen
            df = rivierzijde
            df['next_afstand'] = df['afstand'].shift(-1)
            df['next_z'] = df['z_ahn'].shift(-1)
            df['talud'] = abs((df['z_ahn'] - df['next_z']) / (df['afstand'] - df['next_afstand']))
            df['max_talud'] = df.iloc[:, 7].rolling(window=3).mean()
            df['next_max_talud'] = df['max_talud'].shift(-1)


            try:
                mv_dijk, mv_achterland
                for index, row in df.iterrows():
                    if mv_dijk > mv_achterland and row['afstand'] - row['next_afstand'] <= 2 and row['afstand'] > 3 and \
                            row['next_max_talud'] < row['max_talud'] and row['afstand'] > bik:
                        list_id_bit.append(row['OBJECTID'])
                        # ax.plot(row['next_afstand'], row['next_z'], 'o', markersize=12)
                        break
            except NameError:
                list_id_bit = []

        # wegschrijven naar gis
        if list_id_bit:
            arcpy.MakeFeatureLayer_management(invoer, 'punten_binnenteen_temp')
            punten_bit = arcpy.SelectLayerByAttribute_management('punten_binnenteen_temp', "ADD_TO_SELECTION",
                                                                 "OBJECTID in (" + str(list_id_bit)[1:-1] + ")")
            arcpy.CopyFeatures_management('punten_binnenteen_temp', uitvoer_binnenteen)
        print 'Binnenteen bepaald'
    else:
        pass

# functie voor het koppelen van het hbn(toetshoogte) aan de profielen
def koppeling_hbn_hdsr(profielen,toetspeil):

    # schoonmaken laag
    bestaande_velden = arcpy.ListFields(profielen)
    te_verwijderen = ['kruin2014_th']
    for field in bestaande_velden:
        if field.name in te_verwijderen:
            arcpy.DeleteField_management(profielen, field.name)

    arcpy.AddField_management(profielen, "kruin2014_th", "DOUBLE", 2, field_is_nullable="NULLABLE")



    with arcpy.da.UpdateCursor(profielen, ['maxKruinhoogte2014', toetspeil, 'kruin2014_th']) as cursor:

        for row in cursor:
            if row[0] is not None and row[0] >= row[1]:
                verschil = abs(row[0] - row[1])
                row[2] = round(verschil,2)
                cursor.updateRow(row)
            else:
                if row[0] is not None and row[0]<row[1]:
                    verschil = abs(row[0] - row[1])
                    row[2] = -round(verschil,2)
                    cursor.updateRow(row)

    print "Kruinhoogte-hbn berekend"

# functie voor het bepalen van de restlevensduur
def bereken_restlevensduur(profielen,bodemdalingskaart,afstand_zichtjaar,toetspeil):
    # profiellijnen middenpunt
    arcpy.FeatureToPoint_management(profielen, 'profielen_temp','CENTROID')

    # middenpunt z-waarde bodemdaling
    arcpy.CheckOutExtension("Spatial")
    ExtractValuesToPoints('profielen_temp', bodemdalingskaart, 'profielen_temp_z',
                          "NONE", "VALUE_ONLY")

    # schoonmaken laag
    bestaande_velden = arcpy.ListFields('profielen_temp_z')
    te_verwijderen = ['bdMmj', 'rldJaar']
    for field in bestaande_velden:
        if field.name in te_verwijderen:
            arcpy.DeleteField_management('profielen_temp_z', field.name)

    # Pas het veld 'RASTERVALU' aan naar 'z_ahn'
    arcpy.AlterField_management('profielen_temp_z', 'RASTERVALU', 'bdMmj')
    del bestaande_velden

    # bodemdaling toevoegen aan profielen
    bestaande_velden = arcpy.ListFields(profielen)
    te_verwijderen = ['bdMmj', 'rldJaar']
    for field in bestaande_velden:
        if field.name in te_verwijderen:
            arcpy.DeleteField_management(profielen, field.name)
    arcpy.JoinField_management(profielen, 'profielnummer', 'profielen_temp_z', 'profielnummer', 'bdMmj')


    # maximale kruinhoogte aanpassen aan bodemdaling, 'bd_' voor velden
    bestaande_velden = arcpy.ListFields(profielen)
    te_verwijderen = ['maxKruinhoogte2024','kruin2024_th']
    for field in bestaande_velden:
        if field.name in te_verwijderen:
            arcpy.DeleteField_management(profielen, field.name)
    arcpy.AddField_management(profielen, "maxKruinhoogte2024", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(profielen, "kruin2024_th", "DOUBLE", 2, field_is_nullable="NULLABLE")

    # bereken maximale kruinhoogte-bodemdaling per x jaren
    with arcpy.da.UpdateCursor(profielen, ['profielnummer','bdMmj','maxKruinhoogte2014', 'maxKruinhoogte2024']) as cursor:
        for row in cursor:
            if row[2] is not None and row[1] < 0:
                bd_meters = row[1]/1000
                row[3] = round(row[2]-abs(afstand_zichtjaar*bd_meters),2)
                cursor.updateRow(row)
            elif row[2] is not None and row[1] >= 0:
                row[3] = row[2]
                row[1] = 0
                cursor.updateRow(row)
            elif row[2] is None and row[1] >= 0:
                row[1] = 0
                cursor.updateRow(row)
            else:
                pass
    # bereken verschil maximale kruinhoogte-bodemdaling per x jaren met hbn
    with arcpy.da.UpdateCursor(profielen, [toetspeil,'bdMmj','maxKruinhoogte2024','kruin2024_th']) as cursor:
        for row in cursor:
            if row[2] is not None and row[2] >= row[0]:
                verschil = abs(row[2] - row[0])
                row[3] = round(verschil,2)
                cursor.updateRow(row)
            else:
                if row[2] is not None and row[2]<row[0]:
                    verschil = abs(row[2] - row[0])
                    row[3] = -round(verschil,2)
                    cursor.updateRow(row)


    # restlevensduur berekenen
    arcpy.AddField_management(profielen, "rldJaar", "DOUBLE")
    with arcpy.da.UpdateCursor(profielen, ('bdMmj','rldJaar','kruin2024_th')) as cursor:
        for row in cursor:
            if row[2] is not None and row[0] is not None:
                resthoogte = row[2]
                if resthoogte <= 0:
                    row[1] = 0

                elif row[0] < 0:
                    resthoogte_mm = row[2]*1000
                    bodemdaling_mm = abs(row[0])
                    row[1] = round(resthoogte_mm/bodemdaling_mm,1)
                else:
                    if row[0]==0:
                        row[1] =999
                cursor.updateRow(row)

    print 'Restlevensduur berekend'



def splitByAttributes(features, field):
    shapeList = []

    # list features in layer
    with arcpy.da.SearchCursor(features,[field]) as cursor:
        for row in cursor:
            shapeName = str(row[0])
            if shapeName in shapeList:
                pass
            else:
                shapeList.append(shapeName)

    print shapeList

    # select features in layer 
    for item in shapeList:
        lyr = arcpy.MakeFeatureLayer_management(features, 'templyr') 
        where = '"' + field + '" = ' + "'" + item + "'"
        selected = arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", where)
        outputName = str(item)
        outputName = (outputName.replace('+', '_'))
        outputName = (outputName.replace('.', '_'))

        arcpy.CopyFeatures_management(selected,outputName)

def split_profielen(profielen,trajectlijn,code):
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
                            match_option="INTERSECT",search_radius=3)
    arcpy.SpatialJoin_analysis('profielsplits', landlijn, 'profieldeel_land', "JOIN_ONE_TO_ONE", "KEEP_COMMON",
                            fieldmappings,
                            match_option="INTERSECT",search_radius=3)

