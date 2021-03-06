## import

import arcpy
import numpy as np
import pandas as pd
from itertools import groupby
from arcpy.sa import *

# overschrijf de oude data
arcpy.env.overwriteOutput = True

# definieer de werkomgeving
arcpy.env.workspace = r'D:\Projecten\HHNK\ds_5_1.gdb'


## invoer
profielen = 'profielen_5_1'  # profielen, zoals gegenereerd via scriptdeel
profielen_hr = 'profielen_hr'  # werklaag, deze kan onaangepast blijven
invoer = 'profielen_punten_z'  # werklaag, deze kan onaangepast blijven.
stapgrootte_punten = 2  # stapgrootte tussen de punten vanuit de hoogtedata (niet kleiner dan gridgrootte)
stapgrootte_punten_marge = 3.5 # marge tussen de punten, om enige ruimte te laten voor kleine laagtes die er niet direct toe doen

maximale_beginwaarde = 60  # de maximale afstand waarop, t.o.v. de gedefinieerde landwaartse lijn, mag worden begonnen met de volume berekening
hoogte_controle = 1  # een punt binnen de volumegroep moet dit niveau hebben (TRDA 2006: min 1 m boven Rp)
maximaal_talud_zz = 1  # het maximale talud aan de zeezijde (TRDA 2006: 1:1)
maximaal_talud_lz = 0.5  # het maximale talud aan de zeezijde (TRDA 2006: 1:2)
minimale_hoogte_boven_rp = 0.01  # minimale hoogte van alle punten die nodig is om een aaneengesloten volume te verkrijgen
max_gp_hoogte = 'max_h_gp' # veld voor het meenemen van profielen waarbij maximale grensprofielhoogte handmatig is aangepast
raster = r'D:\Projecten\HHNK\raster\AHN3_5_11.tif'  # hoogtedata voor het ophalen van hoogte-waardes
hr = 'hr_ref_5_1_iiv'  # JARKUS-raaien op 0 m RSP met bijbehorende hr (Rp, Hs en Tp)

profiel_interval = 10 # interval tussen de te maken profielen
profiel_lengte_zee = 120 # profiel lengte aan de zeezijde
profiel_lengte_land = 0 # profiel lengte aan de landzijde
### LET OP ### TRAJECTLIJN MOET NOORD-ZUID GEORIENTEERD ZIJN
trajectlijn = 'lijn_jrk_5_1' # trajectlijn waarlangs de profielen moeten worden gemaakt
sectie_id = 'code' # dit veld moet aanwezig zijn binnen de trajectlijn, ter referentie
aantekeningen_bebouwing = 'grensprofiel_nabij_bebouwing' # indien aanwezig wordt deze laag bekeken door het script
minimale_profiellengte = 20 # de minimale lengte van een profiel. Indien sprake van erge kromming in de trajectlijn kunnen profielen zo automatisch worden verwijderd.

velden = ['afstand', 'z_ahn', 'groep', 'volume_groep', 'profielnummer', 'kenmerk'] # werkvelden voor script


## functies
def profielen_op_lijn(profiel_interval,profiel_lengte_zee,profiel_lengte_land,trajectlijn,code, profielen):
    # traject to points
    arcpy.GeneratePointsAlongLines_management(trajectlijn, 'traject_punten', 'DISTANCE', Distance=profiel_interval, Include_End_Points='END_POINTS')
    arcpy.AddField_management('traject_punten', "profielnummer", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management('traject_punten', "lengte_landzijde", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management('traject_punten', "lengte_zeezijde", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management('traject_punten', "profielnummer", '!OBJECTID!', "PYTHON")
    arcpy.CalculateField_management('traject_punten', "lengte_landzijde", profiel_lengte_land, "PYTHON")
    arcpy.CalculateField_management('traject_punten', "lengte_zeezijde", profiel_lengte_zee, "PYTHON")

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

    # offset zeedeel profiel
    arcpy.MakeRouteEventLayer_lr('route_traject', code, 'tabel_traject_punten', "rid POINT meas", 'deel_zee',
                                 "lengte_zeezijde", "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "RIGHT",
                                 "POINT")

    arcpy.MakeRouteEventLayer_lr('route_traject', code, 'tabel_traject_punten', "rid POINT meas", 'deel_land',
                                 "lengte_landzijde", "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT",
                                 "POINT")
    # temp inzicht layer
    arcpy.CopyFeatures_management('deel_zee', "temp_zeedeel")
    arcpy.CopyFeatures_management('deel_land', "temp_landdeel")
    arcpy.AddField_management('temp_zeedeel', "id", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management('temp_landdeel', "id", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management('temp_zeedeel', "id", 2, "PYTHON")
    arcpy.CalculateField_management('temp_landdeel', "id", 1, "PYTHON")





    arcpy.Merge_management("'temp_zeedeel';'temp_landdeel'", 'merge_profielpunten')
    arcpy.PointsToLine_management('merge_profielpunten', profielen, "profielnummer", "id", "NO_CLOSE")

    arcpy.SpatialJoin_analysis(profielen, trajectlijn, 'profielen_temp', "JOIN_ONE_TO_ONE", "KEEP_ALL", match_option="INTERSECT")
    arcpy.CopyFeatures_management('profielen_temp', profielen)

    # arcpy.AddField_management(profielen, "van", "DOUBLE", 2, field_is_nullable="NULLABLE")
    # arcpy.AddField_management(trajectlijn, "tot", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management(profielen, "van", 0, "PYTHON")
    arcpy.CalculateField_management(profielen, "tot", "round(!shape.length!)", "PYTHON")

    arcpy.FlipLine_edit(profielen)

    # selecteer profielen die intersecten met laag 'grensprofiel_nabij_bebouwing'
    arcpy.AddField_management(profielen, max_gp_hoogte, "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(profielen, 'resultaat', "TEXT")
    arcpy.SpatialJoin_analysis(profielen, aantekeningen_bebouwing, 'test_profielen', "#", "#", match_option="INTERSECT",search_radius=1)

    arcpy.CopyFeatures_management('test_profielen', profielen)
    with arcpy.da.UpdateCursor(profielen,['maxwaarde', max_gp_hoogte]) as cursor:
        for row in cursor:
            if row[0] is None:
                pass
            else:
                row[1] = row[0]
                cursor.updateRow(row)

    print 'profielen gemaakt op grensprofiellijn'

def aanpassing_ongeldige_profielen():
    # intersect op trajectlijn
    arcpy.Intersect_analysis([profielen, trajectlijn], 'splitpunten_profielen', output_type="point")
    # split profielen
    searchRadius = "2 Meters"
    arcpy.SplitLineAtPoint_management(profielen, 'splitpunten_profielen', 'split_profielen', searchRadius)

    # laat alleen het geldende profiel over
    with arcpy.da.UpdateCursor('split_profielen', ['OBJECTID', 'profielnummer']) as cursor:
        for k, g in groupby(cursor, lambda x: x[1]):
            counter = 0
            for row in g:
                counter += 1
                if counter > 1:
                    cursor.deleteRow()
                else:
                    pass
    del cursor
    # verwijder profielen korter dan gewenste afstand
    with arcpy.da.UpdateCursor('split_profielen', ['OBJECTID', 'profielnummer', 'SHAPE@LENGTH']) as cursor:
        for row in cursor:
            if row[2] < minimale_profiellengte:
                cursor.deleteRow()
            else:
                pass

    del cursor
    arcpy.CopyFeatures_management('split_profielen', profielen)
    arcpy.CalculateField_management(profielen, "van", 0, "PYTHON")
    arcpy.CalculateField_management(profielen, "tot", "round(!shape.length!)", "PYTHON")

def koppel_hr(): # hier worden de hr aan de profielen gekoppeld

    # verwijder bestaande velden met Rp, Hs, Tp en volume grensprofiel indien aanwezig
    bestaande_velden_profielen = arcpy.ListFields(profielen)
    velden_profielen = ['Rp', 'Hs', 'Tp', 'volume_grensprofiel']

    for veld in bestaande_velden_profielen:
        if veld.name in velden_profielen:
            arcpy.DeleteField_management(profielen, veld.name)

    invoer_hr = profielen
    uitvoer_hr = profielen_hr
    velden = ['profielnummer', 'Rp', 'Hs', 'Tp','van','tot',max_gp_hoogte]  # defineeer de te behouden velden

    # stel de fieldmapping in
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(invoer_hr)
    fieldmappings.addTable(hr)
    keepers = velden

    # verwijder de niet-benodigde velden
    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    # voer de spatial join uit
    arcpy.SpatialJoin_analysis(invoer_hr, hr, uitvoer_hr, "#", "#", fieldmappings, match_option="CLOSEST")

    print "Hydraulische randvoorwaarden van JARKUS-raaien gekoppeld aan profielen"

def bereken_grensprofiel(): # hier wordt per profiel het minimale volume uitgerekend op basis van het TRDA2006 en de gekoppelde hr

    arcpy.AddField_management(profielen_hr, 'min_grensprofiel', "FlOAT", 2, field_is_nullable="NULLABLE")

    with arcpy.da.UpdateCursor(profielen_hr,['profielnummer', 'Rp', 'Hs', 'Tp','min_grensprofiel']) as cursor:
        for row in cursor:
            Tp = row[3] # Golfperiode
            Hs = row[2] # Golfhoogte
            kruin = 3 # Minimale kruinbreedte
            h = 0.12*Tp*np.sqrt(Hs) # Volumeberekening

            # Check of hoogte grensprofiel minimaal 2,5 m is, meldt indien niet het geval
            if h < 2.5:
                print 'minimale hoogte grensprofiel te laag bij profiel '+str(row[0])
            else:
                pass

            # Bereken losse delen grensprofiel
            d1 = (h*h)*0.5          # Driehoek zeezijde
            d2 = kruin*h            # Rechthoek midden
            d3 = (h*(h*2))*0.5      # Driehoek landzijde

            volume_gp = d1+d2+d3    # Bereken volume
            # Update rij met waarde volume
            row[4] = volume_gp
            cursor.updateRow(row)
    print "Minimaal benodigde grensprofielvolumes berekend voor profielen"

def afstanden_punten(): # hier worden routes gemaakt op de profielen, zodat de afstanden kunnen worden berekend

    arcpy.CreateRoutes_lr(profielen_hr, "profielnummer", "routes_profielen", "TWO_FIELDS", "van", "tot", "", "1", "0", "IGNORE", "INDEX")
    print 'Routes gemaakt op profielen'

    arcpy.GeneratePointsAlongLines_management('routes_profielen', 'punten_route', 'DISTANCE', Distance= stapgrootte_punten, Include_End_Points='END_POINTS')
    print 'Punten op routes gemaakt met stapgrootte '+str(stapgrootte_punten)+" m"

    # Een extra veld met punt_id is nodig om straks te kunnen koppelen
    arcpy.AddField_management('punten_route', 'punt_id', "DOUBLE", field_precision=2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management("punten_route", "punt_id", '!OBJECTID!', "PYTHON")
    print 'Id-veld aan punten toegevoegd'

    # Lokaliseren van de punten op de gemaakte routes
    Output_Event_Table_Properties = "RID POINT MEAS"
    arcpy.LocateFeaturesAlongRoutes_lr('punten_route', 'routes_profielen', "profielnummer", "1 Meters",
                                       'uitvoer_tabel', Output_Event_Table_Properties, "FIRST", "DISTANCE", "ZERO",
                                       "FIELDS", "M_DIRECTON")
    print 'Punten op route gelokaliseerd'

    # Koppelen van tabel met locaties met de punten, hier is het punt_id veld weer nodig
    arcpy.JoinField_management('punten_route', 'punt_id', 'uitvoer_tabel', 'punt_id', 'MEAS')
    arcpy.AlterField_management('punten_route', 'MEAS', 'afstand')
    print 'MEAS toegevoegd aan puntenlaag vanuit tabel en veldnaam aangepast naar afstand'

    # Koppelen van grensprofiel en rekenpeil velden aan puntenlaag
    velden = ['Rp', 'Hs', 'Tp', 'min_grensprofiel',max_gp_hoogte]
    arcpy.JoinField_management('punten_route', 'profielnummer', profielen_hr, 'profielnummer', velden)
    print "Velden voor grensprofiel en rekenpeil toegevoegd"

def hoogtewaarde_punten(): # hier wordt een hoogtewaarde aan ieder punt, op iedere route, gekoppeld
    # bepaal invoer
    invoer_punten = "punten_route"
    uitvoer_punten = "profielen_punten_z"

    # Test de ArcGIS Spatial Analyst extension license
    arcpy.CheckOutExtension("Spatial")

    # Koppel z-waardes
    ExtractValuesToPoints(invoer_punten, raster, uitvoer_punten,
                          "INTERPOLATE", "VALUE_ONLY")

    # Pas het veld 'RASTERVALU' aan naar 'z_ahn'
    arcpy.AlterField_management(uitvoer_punten, 'RASTERVALU', 'z_ahn')
    print "Hoogte-waarde aan punten gekoppeld en veld aangepast naar z_ahn"

    # punten met nodata (bebouwing) krijgen maxwaarde volgens 'aantekeningen_bebouwing'
    with arcpy.da.UpdateCursor(uitvoer_punten,[max_gp_hoogte,'z_ahn']) as cursor:
        for row in cursor:
            if row[1] is None and row[0] is not None:
                row[1] = row[0]
                cursor.updateRow(row)
            else:
                pass
    print "Maximale grensprofielhoogtes doorgevoerd voor betreffende profielen"

def aanpassen_groepen(): # hier worden de groepen aangepast en groepen die aangesloten zijn voorzien van hetzelfde nummer
    # Voeg nodige velden toe aan definitieve puntenlaag
    arcpy.AddField_management(invoer, 'kenmerk', "TEXT", field_length=50)
    arcpy.AddField_management(invoer, 'z_rest', "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(invoer, 'groep', "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(invoer, 'volume_groep', "DOUBLE", 2, field_is_nullable="NULLABLE")


    # Verwijder punten zonder z_waarde en rond afstand af
    with arcpy.da.UpdateCursor(invoer, ['afstand', 'z_ahn', 'z_rest']) as tester:
        for row in tester:
            if row[1] is None:
                tester.deleteRow()
            else:
                row[0] = round(row[0])
                tester.updateRow(row)

    # Test of alle punten boven de minimaal vereiste hoogte boven Rekenpeil liggen, verwijder indien niet het geval
    with arcpy.da.UpdateCursor(invoer, ['afstand', 'z_ahn', 'groep', 'volume_groep', 'profielnummer', 'kenmerk', 'z_rest', 'Rp', 'Hs', 'Tp']) as cur0:
        for row in cur0:
            row[2] = 1
            cur0.updateRow(row)
            if row[1] < (row[7]+minimale_hoogte_boven_rp):
                cur0.deleteRow()
            else:
                pass

    # Bepaal resthoogte dat aanwezig is voor volume berekening grensprofiel
    with arcpy.da.UpdateCursor(invoer, ['afstand', 'z_ahn', 'z_rest', 'Rp']) as cur4:
        for row in cur4:
            row[2] = row[1]-(row[3]+minimale_hoogte_boven_rp)
            cur4.updateRow(row)


    # Bepaal volume per aaneengesloten set punten
    with arcpy.da.UpdateCursor(invoer, ['afstand', 'z_ahn', 'groep', 'volume_groep', 'profielnummer', 'kenmerk']) as cur1:
        for k, g in groupby(cur1, lambda x: x[4]):
            p = g.next()[0] # eerste waarde
            value = 1

            for row in g:
                c = row[0] # volgende waarde
                if c-p <= stapgrootte_punten_marge: # van 2 naar 5
                    row[2] = value
                    cur1.updateRow(row)
                else:
                    value+=1
                    # print "Nieuwe volumegroep gemaakt op profiel, g"
                    # pass

                p = row[0]

                row[2] = value
                cur1.updateRow(row)


    with arcpy.da.UpdateCursor(invoer, ['afstand', 'z_ahn', 'groep', 'volume_groep', 'profielnummer', 'kenmerk']) as cur3:
        for row in cur3:
            row[5] = str(row[2]) + "en" + str(row[4])
            cur3.updateRow(row)
    print "Profielen voorzien van aangesloten groepen"

def bereken_opzet(): # hier worden per groep, ongeacht of deze aaneengesloten is met een bovenliggend profiel, de volumes berekend.
    dct = {} # lege dictionary voor koppeling
    array = arcpy.da.FeatureClassToNumPyArray(invoer, ('afstand', 'z_ahn','groep','profielnummer', 'kenmerk','z_rest'))
    df = pd.DataFrame(array)

    grouped = df.groupby(["profielnummer"])

    # Met behulp van trapz(integratie) het volume per groep berekenen
    for name, group in grouped:
        for key, grp in group.groupby(['groep']):
            x = grp['afstand']
            y = grp['z_rest']

            waarde = np.trapz(y,x)
            if waarde < 0:
                waarde = waarde*-1
            else:
                waarde = waarde

            id = str(key)+"en"+str(name)

            #
            # print id_final, waarde
            dct[id] = waarde
    print "Ruwe volumes per groep berekend"

    # Update vanuit pandas naar feature-class
    with arcpy.da.UpdateCursor(invoer, ['afstand', 'z_ahn', 'groep', 'volume_groep', 'profielnummer', 'kenmerk']) as cur2:
        for row in cur2:
            kenmerk = row[5]
            if kenmerk in dct:
                row[3] = dct[kenmerk]
                cur2.updateRow(row)
            else:
                pass
    print "Volumes toegevoegd aan puntenlaag"

def ruimtebeslag():  # hier wordt het minimale ruimtebeslag berekend, op basis van het minimale grensprofielvolume en de taludhellingen (zeewaarts max 1:1, landwaarts max 1:2)

    # te vullen lijsten en dictionaries
    totaal_profielen = []
    voldoende_profielen = []
    onvoldoende_profielen = []

    voldoende_volume = []
    voldoende_talud_landzijde = []
    onvoldoende_talud_zeezijde =[]
    onvoldoende_talud_landzijde = []


    start_totaal = {}
    dct = {}  # lege dictionary om te iteratie over groepen per profiel mogelijk te maken
    dct_koppel = {}  # lege dictionary om later volumes aan de zeewaartse begrenzing toe te voegen
    OID_zeewaarts = []  # OID voor punt begrenzing zeewaarts
    OID_start = []  # OID voor punt begrenzing zeewaarts

    # maak een pandas dataframe van de punten featureclass
    array = arcpy.da.FeatureClassToNumPyArray(invoer, (
        'profielnummer', 'afstand', 'groep', 'z_rest', 'z_ahn', 'min_grensprofiel', 'volume_groep', 'Rp', 'OBJECTID'))
    df = pd.DataFrame(array)

    # sorteer dataframe op profielnummer, afstand
    sorted = df.sort_values(['profielnummer', 'afstand'], ascending=[True, True])
    grouped = sorted.groupby(["profielnummer"])

    # groepeer de punten per profiel
    for name, group in grouped:
        totaal_profielen.append(name)
        afstanden = group['afstand']
        hoogtes = group['z_rest']
        groepen = group['groep']
        hoogtes_ahn = group['z_ahn']
        v_grensprofielen = group['min_grensprofiel']
        v_groep = group['volume_groep']
        lijst_OID = group['OBJECTID']

        # maak een nieuw dataframe per profiel
        gr_df = pd.DataFrame(list(zip(afstanden, hoogtes, groepen, hoogtes_ahn, v_grensprofielen, v_groep, lijst_OID)),
                             columns=['afstand', 'hoogte_rest', 'groep', 'hoogte_ahn', 'min_volume', 'volume_groep',
                                      'OBJECTID'])
        gr_df['afstand_2'] = gr_df['afstand'].shift(-1)
        gr_df['hoogte_2'] = gr_df['hoogte_ahn'].shift(-1)

        grouped_2 = gr_df.groupby(["groep"])

        # controle talud landzijde, deel 1
        if name not in dct:

            #  groepering per profiel
            for groep, group in grouped_2:


                # reset index van groep om goede startpunt te vinden
                group = group.reset_index()

                volume_nodig = group['min_volume'].iloc[0]
                volume_aanwezig = group['volume_groep'].iloc[0]

                # test of voldoende volume aanwezig is in de groep, ongeacht andere condities
                if volume_aanwezig >= volume_nodig:
                    voldoende_volume.append(name)
                    for i, row in group.iterrows():

                        # controle talud landzijde
                        a0 = row['afstand']
                        h0 = row['hoogte_ahn']
                        a1 = row['afstand_2']
                        h1 = row['hoogte_2']

                        talud_lz = abs(h0 - h1) / abs(a0 - a1)
                        # print talud_lz
                        if talud_lz <= maximaal_talud_lz:
                            if a0< maximale_beginwaarde:
                                start_totaal[name] = groep, a0, h0, i
                                voldoende_talud_landzijde.append(name)

                                dct[name] = name
                                break
                            # stop als maximale beginwaarde wordt overschreden
                            else:
                                break
                        # ga door als vereiste talud nog niet gevonden is
                        else:
                            continue

                # ga door als eerste groep geen voldoende resultaten geeft
                else:
                    continue
        # stop als profiel al is doorgerekend
        else:
            break

        # als voldoende talud aan landzijde aanwezig is, ga door met berekening deel 2
        if name in start_totaal:

            groep_select = start_totaal[name][0]

            # groepering per profiel
            for groep, group in grouped_2:

                # lege lijsten voor stapsgewijze berekening volume (np.trapz)
                afstand = []
                hoogte = []

                hoogte_check = [] # lijst voor controle of een punt binnen de groep voldoet aan rp+1m
                if groep == groep_select:

                    # startpunt, bepaald in rekendeel 1
                    starti = start_totaal[name][3]


                    for i, row in group.iloc[starti:].iterrows():
                        # print row['afstand'], name
                        a0 = row['afstand']
                        h0 = row['hoogte_ahn']
                        hrest0 = row['hoogte_rest']

                        a1 = row['afstand_2']
                        h1 = row['hoogte_2']

                        afstand.append(a0)
                        hoogte.append(hrest0)
                        hoogte_check.append(row['hoogte_ahn'])

                        waarde = np.trapz(hoogte, afstand)

                        #controle talud zeezijde
                        controle_zz = abs(h0-h1)/abs(a0-a1)

                        if waarde > row['min_volume'] and controle_zz <= maximaal_talud_zz and max(hoogte_check)>= hoogte_controle:
                        # if waarde > 50:

                            voldoende_profielen.append(name)
                            startOID = group['OBJECTID'].iloc[starti]
                            OID_start.append(startOID)
                            OID_zeewaarts.append(row['OBJECTID'])
                            dct_koppel[name] = waarde
                            break
                        else:
                            # ####testcode voor het toevoegen van profielen met onvoldoende score taludhelling aan voldoende profielen#####
                            # if waarde > row['min_volume'] and controle_zz > maximaal_talud_zz and max(
                            #         hoogte_check) >= hoogte_controle:
                            #     startOID = group['OBJECTID'].iloc[starti]
                            #     OID_start.append(startOID)
                            #     OID_zeewaarts.append(row['OBJECTID'])
                            #     dct_koppel[name] = waarde
                            #     voldoende_profielen.append(name)
                            # #########################################################################################################
                            continue

                else:
                    continue


    # geneneer lijnenlaag met profielen zonder grensprofiel
    for item in totaal_profielen:
        if item in voldoende_profielen:
            pass
        else:
            onvoldoende_profielen.append(item)

    # maak deelsecties voor profielen die voldoende volume hebben maar een of meerdere taluds met een te steile helling
    for item in totaal_profielen:
        if item in voldoende_volume and item in voldoende_talud_landzijde and item not in voldoende_profielen:
            onvoldoende_talud_zeezijde.append(item)
        else:
            if item in voldoende_volume and item not in voldoende_talud_landzijde and item not in voldoende_profielen:
                onvoldoende_talud_landzijde.append(item)

    arcpy.MakeFeatureLayer_management(profielen, "TEMP_LYR_1")
    onvoldoende = set(onvoldoende_profielen)




    # verwijder oude profielen met onvoldoende resultaten
    if arcpy.Exists("onvoldoende_profielen"):
        arcpy.DeleteFeatures_management("onvoldoende_profielen")

    if not onvoldoende:
        print "geen onvoldoende resultaten"




    # voeg onvoldoende profiel toe aan gislaag onvoldoende profielen
    if onvoldoende_profielen:
        for values in onvoldoende:
            query = "\"profielnummer\"=" + str(values)
            arcpy.management.SelectLayerByAttribute("TEMP_LYR_1", "ADD_TO_SELECTION", query)

        arcpy.CopyFeatures_management("TEMP_LYR_1", 'onvoldoende_profielen')




    # maak zeewaartse begrenzing
    if OID_zeewaarts:
        arcpy.MakeFeatureLayer_management(invoer, "TEMP_LYR")
        for values in OID_zeewaarts:
            query = "\"OBJECTID\"=" + str(values)
            arcpy.management.SelectLayerByAttribute("TEMP_LYR", "ADD_TO_SELECTION", query)

        arcpy.CopyFeatures_management("TEMP_LYR", 'begrenzing_zeewaarts')




    # voeg berekend volume toe aan gislaag begrenzing profielen
    arcpy.AddField_management('begrenzing_zeewaarts', 'volume_grensprofiel', "FlOAT", 2,
                              field_is_nullable="NULLABLE")
    with arcpy.da.UpdateCursor('begrenzing_zeewaarts', ['profielnummer', 'volume_grensprofiel']) as cursor:
        for row in cursor:
            if int(row[0]) in dct_koppel:
                row[1] = dct_koppel[int(row[0])]
                cursor.updateRow(row)
            else:
                pass




    # maak landwaartse begrenzing
    if OID_start:
        arcpy.MakeFeatureLayer_management(invoer, "TEMP_LYR_2")
        for values in OID_start:
            query = "\"OBJECTID\"=" + str(values)
            arcpy.management.SelectLayerByAttribute("TEMP_LYR_2", "ADD_TO_SELECTION", query)

        arcpy.CopyFeatures_management("TEMP_LYR_2", 'begrenzing_landwaarts')




    # voeg velden Rp, Hs en Tp toe aan invoerprofielen
    bestaande_velden_profielen = arcpy.ListFields(profielen)
    velden_profielen = ['Rp', 'Hs', 'Tp','volume_grensprofiel']

    for veld in bestaande_velden_profielen:
        if veld.name in velden_profielen:
            arcpy.DeleteField_management(profielen, veld.name)

    arcpy.JoinField_management(profielen, 'profielnummer', profielen_hr, 'profielnummer',
                               ['Rp', 'Hs', 'Tp', 'min_volume'])
    # voeg het berekende volume grensprofiel toe aan invoerprofielen
    arcpy.JoinField_management(profielen, 'profielnummer', 'begrenzing_zeewaarts', 'profielnummer',
                               'volume_grensprofiel')

    # update resultaten in profielen
    with arcpy.da.UpdateCursor(profielen, ['profielnummer', 'resultaat']) as cursor:
        for row in cursor:
            if row[0] in set(voldoende_profielen):
                row[1] = "voldoende resultaat"
                cursor.updateRow(row)
            else:
                if row[0] not in set(voldoende_profielen):
                    if row[0] in set(onvoldoende_talud_zeezijde):
                        row[1] = "voldoende volume, talud zeezijde te steil"
                        cursor.updateRow(row)
                    elif row[0] in set(onvoldoende_talud_landzijde):
                        row[1] = "voldoende volume, talud landzijde te steil"
                        cursor.updateRow(row)
                    else:
                        row[1] = "onvoldoende volume voor inpassing grensprofiel"
                        cursor.updateRow(row)





    print "Ruimtebeslag berekend indien mogelijk"


## runnen functies
profielen_op_lijn(profiel_interval,profiel_lengte_zee,profiel_lengte_land,trajectlijn,sectie_id,profielen)
# aanpassing_ongeldige_profielen()
# koppel_hr()
# bereken_grensprofiel()
# afstanden_punten()
# hoogtewaarde_punten()
# aanpassen_groepen()
# bereken_opzet()
# ruimtebeslag()



