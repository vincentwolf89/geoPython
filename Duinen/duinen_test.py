import arcpy
import numpy as np
import pandas as pd
from itertools import groupby
from arcpy.sa import *


# overschrijf de oude data
arcpy.env.overwriteOutput = True

# definieer de werkomgeving
arcpy.env.workspace = 'C:/Users/vince/Desktop/GIS/duinscript.gdb'

# invoer
profielen ='profielen_13_2' # profielen, zoals gegenereerd via ET-Tools/andere manier
profielen_hr = 'profielen_hr' # werklaag, deze kan onaangepast blijven
invoer = 'profielen_punten_z' # werklaag, deze kan onaangepast blijven.
stapgrootte_punten = 2 # stapgrootte tussen de punten vanuit de hoogtedata (niet kleiner dan gridgrootte)
# marge = 2   # marge tussen de punten, om enige ruimte te laten voor kleine laagtes die er niet direct toe doen ****
maximale_beginwaarde = 48 # de maximale afstand waarop, t.o.v. de gedefinieerde landwaartse lijn, mag worden begonnen met de volume berekening
hoogte_controle = 1 # een punt binnen de volumegroep moet dit niveau hebben (TRDA 2006: min 1 m boven Rp)
maximaal_talud_zz = 1 # het maximale talud aan de zeezijde (TRDA 2006: 1:1)
maximaal_talud_lz = 0.5 # het maximale talud aan de zeezijde (TRDA 2006: 1:2)
minimale_hoogte_boven_rp = 0.1 # minimale hoogte van alle punten die nodig is om een aaneengesloten volume te verkrijgen
raster = r'C:\Users\vince\Desktop\wolfwater\HHNK\data\ahn3_kust_nh_tx_1m.tif' # hoogtedata voor het ophalen van hoogte-waardes
hr = 'hr_ref_13_2_iv' # JARKUS-raaien op 0 m RSP met bijbehorende hr (Rp, Hs en Tp)

velden = ['afstand', 'z_ahn', 'groep', 'volume_groep', 'profielnummer', 'kenmerk']




def koppel_hr(): # hier worden de hr aan de profielen gekoppeld
    invoer_hr = profielen
    uitvoer_hr = profielen_hr
    velden = ['profielnummer', 'Rp', 'Hs', 'Tp','van','tot']  # defineeer de te behouden velden

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
    velden = ['Rp', 'Hs', 'Tp', 'min_grensprofiel']
    arcpy.JoinField_management('punten_route', 'profielnummer', profielen_hr, 'profielnummer', velden)
    print "Velden voor grensprofiel en rekenpeil toegevoegd"


def values_points(): # hier wordt een hoogtewaarde aan ieder punt, op iedere route, gekoppeld
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
                if c-p <= stapgrootte_punten: # van 2 naar 5
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





def ruimtebeslag(): # hier wordt het minimale ruimtebeslag berekend, op basis van het minimale grensprofielvolume en de taludhellingen (zeewaarts max 1:1, landwaarts max 1:2)

    # te vullen lijsten en dictionaries
    totaal_profielen = []
    voldoende_profielen = []
    onvoldoende_profielen = []
    talud_onvoldoende_zz = []
    talud_onvoldoende_lz = []
    talud_onvoldoende_lz_zz = []

    dct = {} # lege dictionary om te iteratie over groepen per profiel mogelijk te maken
    dct_koppel = {} # lege dictionary om later volumes aan de zeewaartse begrenzing toe te voegen
    OID = [] # OID voor punt begrenzing zeewaarts
    OID_start = [] # OID voor punt begrenzing zeewaarts

    # maak een pandas dataframe van de punten featureclass
    array = arcpy.da.FeatureClassToNumPyArray(invoer, (
    'profielnummer', 'afstand', 'groep', 'z_rest', 'z_ahn', 'min_grensprofiel', 'Rp', 'OBJECTID'))
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
        lijst_OID = group['OBJECTID']


        gr_df = pd.DataFrame(list(zip(afstanden, hoogtes, groepen, hoogtes_ahn, v_grensprofielen, lijst_OID)),
                             columns=['afstand', 'hoogte', 'groep', 'hoogte_ahn', 'min_volume', 'OBJECTID'])

        grouped_2 = gr_df.groupby(["groep"])

        if name not in dct:

            # groepeer de punten per volumegroep, voor ieder profiel
            for groep, group in grouped_2:

                # lege lijsten voor hoogte, afstand
                afstand = []
                hoogte = []
                hoogte_check = []
                talud_lz = []


                # vul de lijsten per iteratie over de rij
                afstand.append(group['afstand'].iloc[0])
                hoogte.append(group['hoogte'].iloc[0])

                # iterator om over de profielen te wandelen en onderlinge afstand te bepalen
                row_iterator = group.iterrows()
                _, last = row_iterator.next()

                # startwaardes per groep, deze worden los toegevoegd omdat ze anders niet meegenomen worden via de iterator
                start_ID = group['OBJECTID'].iloc[0]
                startwaarde = group['afstand'].iloc[0]
                starthoogte = group['hoogte_ahn'].iloc[0]
                if startwaarde < maximale_beginwaarde:
                    for i, row in row_iterator:
                        afstand.append(row['afstand'])
                        hoogte.append(row['hoogte'])

                        # controle hoogte (TRDA 2006: 1m)
                        hoogte_check.append(row[
                                                'hoogte_ahn'])  # vul de lijst met ahn-waardes voor controle dat er 1 punt is boven Rp+1m

                        # controle talud zeezijde
                        a0 = last['afstand']
                        h0 = last['hoogte_ahn']
                        a1 = row['afstand']
                        h1 = row['hoogte_ahn']

                        # controle talud landzijde
                        if 1 <= abs(startwaarde-a0) <= 3:
                            if abs((starthoogte-h0)/(abs(startwaarde-a0))) <= maximaal_talud_lz:
                                # print "goedgekeurd talud lz"
                                talud_lz.append(row['OBJECTID'])
                            # elif abs((starthoogte-h0)/(abs(startwaarde-a0))) > maximaal_talud_lz:
                            #     try:
                            #         group['afstand'].iloc[1]
                            #         print "toch een optie...", name
                            #     except NameError:
                            #         pass

                            else:
                                pass

                        else:
                            pass

                        controle_zz = (abs(h0 - h1) / abs(a0 - a1))

                        # bereken het volume voor iedere sectie met integratie (numpy trapz)
                        waarde = np.trapz(hoogte, afstand)
                        if waarde > row['min_volume'] and controle_zz <= maximaal_talud_zz and name not in dct and max(
                                hoogte_check) >= hoogte_controle and talud_lz:

                            # vul de lijsten
                            dct[name] = row['afstand']
                            dct_koppel[name] = waarde
                            OID.append(row['OBJECTID'])
                            OID_start.append(start_ID)
                            # print row['OBJECTID'], controle_zz
                            voldoende_profielen.append(name)
                            break
                        # indien niet wordt voldaan aan de voorwaarde voor talud landzijde, maak melding.
                        elif waarde > row['min_volume'] and controle_zz <= maximaal_talud_zz and name not in dct and max(
                                    hoogte_check) >= hoogte_controle and not talud_lz:
                                # print "talud landzijde onvoldoende, voldoende volume"
                                talud_onvoldoende_lz.append(name)
                                break
                        # indien niet wordt voldaan aan de voorwaarde voor talud zeezijde, maak melding.
                        elif waarde > row['min_volume'] and controle_zz > maximaal_talud_zz and name not in dct and max(
                                    hoogte_check) >= hoogte_controle and talud_lz:
                                # print "talud zeezijde onvoldoende, voldoende volume"
                                talud_onvoldoende_zz.append(name)
                                break
                        else:
                            if waarde > row['min_volume'] and controle_zz > maximaal_talud_zz and name not in dct and max(
                                    hoogte_check) >= hoogte_controle and not talud_lz:
                                talud_onvoldoende_lz_zz.append(name)
                                # print "beide taluds onvoldoende, voldoende volume", name
                                break
                        # row iterator terugzetten
                        last = row
                # break indien startwaarde te groot is
                else:
                    break
            # als volume per profiel gevonden is, ga door naar de volgende
            else:
                pass



    # maak zeewaartse begrenzing
    if OID:
        arcpy.MakeFeatureLayer_management(invoer, "TEMP_LYR")
        for values in OID:
            query = "\"OBJECTID\"=" + str(values)
            arcpy.management.SelectLayerByAttribute("TEMP_LYR", "ADD_TO_SELECTION", query)

        arcpy.CopyFeatures_management("TEMP_LYR", 'begrenzing_zeewaarts')

    # geneneer lijnenlaag met profielen zonder grensprofiel
    for item in totaal_profielen:
        if item in voldoende_profielen:
            pass
        else:
            onvoldoende_profielen.append(item)

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

    # voeg berekend volume toe aan gislaag begrenzing profielen
    arcpy.AddField_management('begrenzing_zeewaarts', 'volume_grensprofiel', "FlOAT", 2, field_is_nullable="NULLABLE")
    with arcpy.da.UpdateCursor('begrenzing_zeewaarts', ['profielnummer', 'volume_grensprofiel']) as cursor:
        for row in cursor:
            if int(row[0]) in dct_koppel:
                row[1] = dct_koppel[int(row[0])]
                cursor.updateRow(row)
            else:
                pass

    # update resultatenveld (onvoldoende volume, te steile helling zeewaarts)
    with arcpy.da.UpdateCursor(profielen, ['profielnummer', 'resultaat']) as cursor:
        for row in cursor:
            if row[0] in set(talud_onvoldoende_lz):
                row[1] = "onvoldoende talud landzijde, voldoende volume"
                cursor.updateRow(row)
            elif row[0] in set(talud_onvoldoende_zz):
                row[1] = "onvoldoende talud zeezijde, voldoende volume"
                cursor.updateRow(row)
            elif row[0] in set(talud_onvoldoende_lz_zz):
                row[1] = "onvoldoende talud, voldoende volume"
                cursor.updateRow(row)
            elif row[0] in voldoende_profielen:
                row[1] = "voldoende volume"
                cursor.updateRow(row)
            else:
                if row[0] not in voldoende_profielen and row[0] not in set(talud_onvoldoende_zz) and row[0] not in set(talud_onvoldoende_lz) and row[0] not in set(talud_onvoldoende_lz_zz):
                    row[1] = "onvoldoende volume"
                    cursor.updateRow(row)



    # maak landwaartse begrenzing
    if OID_start:
        arcpy.MakeFeatureLayer_management(invoer, "TEMP_LYR_2")
        for values in OID_start:
            query = "\"OBJECTID\"=" + str(values)
            arcpy.management.SelectLayerByAttribute("TEMP_LYR_2", "ADD_TO_SELECTION", query)

        arcpy.CopyFeatures_management("TEMP_LYR_2", 'begrenzing_landwaarts')


    # voeg velden Rp, Hs en Tp toe aan invoerprofielen
    arcpy.JoinField_management(profielen, 'profielnummer', profielen_hr, 'profielnummer',
                               ['Rp', 'Hs', 'Tp', 'min_volume'])
    # voeg het berekende volume grensprofiel toe aan invoerprofielen
    arcpy.JoinField_management(profielen, 'profielnummer', 'begrenzing_zeewaarts', 'profielnummer',
                               'volume_grensprofiel')



    print "Ruimtebeslag berekend indien mogelijk"


koppel_hr()
bereken_grensprofiel()
afstanden_punten()
values_points()
aanpassen_groepen()
bereken_opzet()
ruimtebeslag()













