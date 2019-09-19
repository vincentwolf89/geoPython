# import gc
# gc.collect()
import arcpy
from Basisfuncties import*
import math
from arcpy.sa import *
import numpy as np
import pandas as pd


arcpy.env.overwriteOutput = True
# werkdatabase
arcpy.env.workspace = "C:/Users/vince/Desktop/GIS/stph_testomgeving.gdb"

# profielen = 'profielen_sm_test_sel'
# waterstanden = "gekb_safe"
# intredelijn = "vl_dvmin_90m"
# intredelijn_buffer = "voorlanden_aangepast"
# uittredelijn = "binnenteenlijn_2m"
# sloten = 'waterlopen_safe_langs'
# sloten_punt = "waterlopen_safe_langs_point"
# dijkvakindeling = "dijkvakindeling_sm_test"
# koppeling_voorlandbuffers = 'voorlanden_aangepast_koppeling'
#
# naam_run = "test_20_juli"
#
# # standaard parameters
# n = 0.25
# gamma_p = 16.5
# gamma_w = 9.81
# theta = 37
# sterktefactor = 1
# v = 0.000001

def velden_voor_profielen(profielen):
    velden_profielen = ['hp', 'dpip', 'DL', 'deltaH', 'L', 'bron_hp', 'z_max','mw']
    bestaande_velden = arcpy.ListFields(profielen)

    for veld in bestaande_velden:
        if veld.name in velden_profielen:
            arcpy.DeleteField_management(profielen, veld.name)


    # nieuwe velden:
    veld1 = "bron_hp"
    veld2 = "hp"
    veld3 = "dpip"
    veld4 = "DL"
    veld5 = "L"
    veld6 = "deltaH"
    veld7 = "z_max"
    veld8 = "mw"

    instelling = 2

    arcpy.AddField_management(profielen, veld1, "TEXT", field_length=50)
    arcpy.AddField_management(profielen, veld2, "DOUBLE", instelling, field_is_nullable="NULLABLE")
    arcpy.AddField_management(profielen, veld3, "DOUBLE", instelling, field_is_nullable="NULLABLE")
    arcpy.AddField_management(profielen, veld4, "DOUBLE", instelling, field_is_nullable="NULLABLE")
    arcpy.AddField_management(profielen, veld5, "DOUBLE", instelling, field_is_nullable="NULLABLE")
    arcpy.AddField_management(profielen, veld6, "DOUBLE", instelling, field_is_nullable="NULLABLE")
    arcpy.AddField_management(profielen, veld7, "DOUBLE", instelling, field_is_nullable="NULLABLE")
    arcpy.AddField_management(profielen, veld8, "DOUBLE", instelling, field_is_nullable="NULLABLE")

    print "profielen voorzien van schone velden"

def koppel_hoogte_zandlaag(profielen):
    zandlagen = r"C:\Users\vince\Desktop\GIS\zandlagen_safe.gdb\zandlaag_totaal_xls_z_totaal_route"
    output = 'spatial_zandlagen_profielen'
    veld_z = 'z_totaal'
    veld_id = 'uniek_id'

    bestaande_velden = arcpy.ListFields(profielen)

    for field in bestaande_velden:
        if field.name == "z_max":
            arcpy.DeleteField_management(profielen, "z_max")
            print "oude veld met z_max verwijderd"
        else:
            continue

    fieldmappings = arcpy.FieldMappings()

    fieldmappings.addTable(profielen)
    fieldmappings.addTable(zandlagen)

    velden = ['uniek_id', 'z_totaal']

    keepers = velden

    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    arcpy.SpatialJoin_analysis(profielen, zandlagen, output, "#", "#", fieldmappings)
    arcpy.JoinField_management(profielen, veld_id, output, veld_id, veld_z)
    arcpy.AlterField_management(profielen, veld_z, 'z_max', 'z_max')

    print "nieuwe z_max toegevoegd aan profielen"

def knoop_gekb_profielen(profielen,waterstanden):

    velden = ["uniek_id","mw_2015"]
    output = "test_profielen_gekb"
    fieldmappings = arcpy.FieldMappings()


    fieldmappings.addTable(waterstanden)
    fieldmappings.addTable(profielen)
    keepers = velden

    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))


    arcpy.SpatialJoin_analysis(profielen, waterstanden, output, "#", "#", fieldmappings, match_option="CLOSEST")
    arcpy.AlterField_management(output, "mw_2015", "mw")

    #check of mw veld al bestaat
    bestaande_velden = arcpy.ListFields(profielen)

    for field in bestaande_velden:
        if field.name == "mw":
            arcpy.DeleteField_management(profielen, "mw")
        else:
            continue

    arcpy.JoinField_management(profielen, "uniek_id", "test_profielen_gekb", "uniek_id",
                               ["mw"])

    print "profielen voorzien van maatgevende waterstand"


def knip_profielen_140m(profielen, intredelijn,dijkvakindeling):
    #maximale kwelweg op basis van landwaartse grens

    inFeatures = [profielen, 'split_140m']
    clusterTolerance = 0
    intersectOutput = "max_lengte_punten"
    arcpy.Intersect_analysis(inFeatures, intersectOutput, "", clusterTolerance, "point")

    inFeatures = [profielen, intredelijn]
    clusterTolerance = 0
    intersectOutput = "max_voorland_punten"
    arcpy.Intersect_analysis(inFeatures, intersectOutput, "", clusterTolerance, "point")

    inFeatures = profielen
    pointFeatures = "max_lengte_punten"
    outFeatureclass = "profielen_crop"
    searchRadius = 0.5

    arcpy.SplitLineAtPoint_management(inFeatures, pointFeatures, outFeatureclass, searchRadius)


    inFeatures = "profielen_crop"
    pointFeatures = "max_voorland_punten"
    outFeatureclass = "profielen_140m"
    searchRadius = 0.5

    arcpy.SplitLineAtPoint_management(inFeatures, pointFeatures, outFeatureclass, searchRadius)
    print 'split op basis van voorlanden gemaakt'

    arcpy.MakeFeatureLayer_management('profielen_140m', 'templaag')
    arcpy.SelectLayerByLocation_management('templaag', 'intersect', dijkvakindeling)
    arcpy.CopyFeatures_management('templaag', 'ingekorte_profielen')
    print 'selectie klaar, geknipt op maximale lengte binnenwaarts, zie lijn split_140m'

def split_profielen_waterlopen(sloten_punt,dijkvakindeling):
    # zoek dichtstbijzijnde waterloop in 25 radius vanaf lijn
    inFeatures = "ingekorte_profielen"
    pointFeatures = sloten_punt # bestand met alle sloten
    outFeatureclass = "split_waterlopen"
    searchRadius = "25 Meters"

    arcpy.SplitLineAtPoint_management(inFeatures, pointFeatures, outFeatureclass, searchRadius)

    arcpy.MakeFeatureLayer_management('split_waterlopen', 'templaag2')
    arcpy.SelectLayerByLocation_management('templaag2', 'intersect', dijkvakindeling)
    arcpy.CopyFeatures_management('templaag2', 'split_waterlopen_2')
    print 'selectie klaar, profielen gekoppeld aan waterloop indien aanwezig in radius van '+searchRadius


    # spatial join naar slootpunten
    targetFeatures = "split_waterlopen_2"
    joinFeatures = sloten_punt # bestand met alle sloten
    outfc = "join_waterlopen"

    # geef aan welke velden behouden blijven
    fieldmappings = arcpy.FieldMappings()

    # Add all fields from inputs.
    fieldmappings.addTable(targetFeatures)
    fieldmappings.addTable(joinFeatures)

    velden = ['naam_dwp', 'n', 'D', 'gamma_p', 'gamma_w', 'theta', 'd70', 'd70m', 'k', 'sterktefactor', 'mw', 'v', 'hp',
              'dpip', 'DL', 'deltaH', 'L', 'verval', 'F1', 'F2', 'F3', 'kritiek_vv', 'optredend_vv', 'kv_ov', 'uniek_id', 'z_max', 'bron_hp','koppel_id','dv_nummer', 'gem_slootbodem', 'winterpeil', 'note']

    # definieer te behouden velden
    keepers = velden

    # verwijder overige velden
    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    # voer de spatial join uit
    arcpy.SpatialJoin_analysis(targetFeatures, joinFeatures, outfc, "#", "#", fieldmappings, match_option='WITHIN_A_DISTANCE',search_radius= '25 Meters')

    # verander veldnaam van joincount
    fc = "join_waterlopen"
    field1 = "Join_Count"  # short int, non nullable field
    new_name1 = "soort_uittredepunt"

    arcpy.AlterField_management(fc, field1, new_name1)

def uittredepunten_land(uittredelijn,dijkvakindeling):
    out_feature_class = 'bufferpunten_ahn3'
    where_clause = '"soort_uittredepunt" < 1'
    arcpy.MakeFeatureLayer_management('join_waterlopen', 'templaag3')
    arcpy.Select_analysis('templaag3', out_feature_class, where_clause)

    inFeatures = ['bufferpunten_ahn3', uittredelijn]
    clusterTolerance = 0
    intersectOutput = "ahn3_punten_uittredelijn"
    arcpy.Intersect_analysis(inFeatures, intersectOutput, "", clusterTolerance, "point")

    inFeatures = "bufferpunten_ahn3"
    pointFeatures = "ahn3_punten_uittredelijn"
    outFeatureclass = "bufferpunten_ahn3_split1"
    searchRadius = 1
    arcpy.SplitLineAtPoint_management(inFeatures, pointFeatures, outFeatureclass, searchRadius)


    arcpy.MakeFeatureLayer_management('bufferpunten_ahn3_split1', 'templaag4')
    arcpy.SelectLayerByLocation_management('templaag4', 'intersect', dijkvakindeling)
    arcpy.CopyFeatures_management('templaag4', 'bufferpunten_ahn3_split2')


    inFeatures = ['bufferpunten_ahn3', uittredelijn]
    clusterTolerance = 0
    intersectOutput = "bufferpunten_ahn3_punt_"
    arcpy.Intersect_analysis(inFeatures, intersectOutput, "", clusterTolerance, "point")

    punten_ahn3 = "bufferpunten_ahn3_punt_"
    bufferzones_ahn3 = "bufferpunten_ahn3_punt_zone"
    distanceField = "10 Meters"

    arcpy.Buffer_analysis(punten_ahn3, bufferzones_ahn3, distanceField)
    ##############################
    # koppel lagen los en aan elkaar

    out_feature_class = 'laag_waterlopen'
    where_clause = '"soort_uittredepunt" > 0'
    arcpy.MakeFeatureLayer_management('join_waterlopen', 'water')
    arcpy.Select_analysis('water', out_feature_class, where_clause)

    arcpy.Merge_management(['laag_waterlopen', 'bufferpunten_ahn3_split2'], 'test_merge')
    #################################
    bufferpunten = 'bufferpunten_ahn3_punt_zone'
    raster = r'C:\Users\vince\Desktop\GIS\losse rasters\ahn3clip\ahn3clip_2m'
    clip_bufferpunten = "C:\Users\\vince\Desktop\GIS\stph_testomgeving.gdb\clip_bufferpunten"
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
    with arcpy.da.UpdateCursor(punten_temp, ['uniek_id']) as cursor1:
        for row in cursor1:
            if row[0] is None:
                cursor1.deleteRow()
            else:
                continue

    # bereken statistieken voor iedere bufferzone
    array = arcpy.da.FeatureClassToNumPyArray(punten_temp, ('uniek_id', 'grid_code'))
    df = pd.DataFrame(array)
    df_1 = df.dropna()
    means = df_1.groupby(['uniek_id']).mean()

    # vul het woordenboek met setjes
    dct = {}
    for index, row in means.iterrows():
        naam = index
        hoogte = row['grid_code']
        dct[naam] = (hoogte)


    # spatial join naar slootpunten
    targetFeatures = "test_merge"
    joinFeatures = dijkvakindeling # dijkvakindeling
    outfc = "profielen_final"

    # geef aan welke velden behouden blijven
    fieldmappings = arcpy.FieldMappings()

    # Add all fields from inputs.
    fieldmappings.addTable(targetFeatures)
    fieldmappings.addTable(joinFeatures)

    velden = ['naam_dwp', 'n', 'D', 'gamma_p', 'gamma_w', 'theta', 'd70', 'd70m', 'k', 'sterktefactor', 'mw', 'hp',
              'dpip', 'DL', 'deltaH', 'L', 'verval', 'F1', 'F2', 'F3', 'kritiek_vv', 'optredend_vv', 'kv_ov',
              'type_lijn', 'uniek_id', 'z_max', 'bron_hp','koppel_id','dv_nummer', 'winterpeil', 'gem_slootbodem', 'gemiddelde_z', 'note']

    # definieer te behouden velden
    keepers = velden

    # verwijder overige velden
    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    # voer de spatial join uit
    arcpy.SpatialJoin_analysis(targetFeatures, joinFeatures, outfc, "#", "#", fieldmappings)

    # update profielen met nieuwe ahn
    velden = ['uniek_id', 'hp']
    with arcpy.da.UpdateCursor('profielen_final', velden) as cursor:
        for row in cursor:
            id = row[0]
            if id in dct:
                row[1] = float(dct[id])

            cursor.updateRow(row)
    print "uittredepunten die niet in een sloot liggen voorzien van gemiddelde maaiveldhoogte binnen de buffer"



def sellmeijer_aangepast(naam_run, v,gamma_p, gamma_w, theta, sterktefactor, n):
    # # STUK TESTCODE OM RIJEN MET OVERLAPPENDE BUFFERPOLYGONS TE VERWIJDEREN #
    #
    # deleter_velden = ['uniek_id','hp', 'gem_slootbodem']
    # with arcpy.da.UpdateCursor("profielen_final", deleter_velden) as deleter:
    #     for row in deleter:
    #         if row[1] is None and row[2] is None:
    #             print row[0], "is verwijderd!"
    #             deleter.deleteRow()
    #         else:
    #             pass
    # # -------------------------------------------------------------



    # geef aan welk bestand gebruikt gaat worden voor de formule

    fc = "profielen_final"
    outfc = naam_run

    # add some fields

    veld_1 = "F1"
    veld_2 = "F2"
    veld_3 = "F3"
    veld_4 = "verval"
    veld_5 = "kritiek_vv"
    veld_6 = "optredend_vv"
    veld_7 = "kv_ov"

    fieldPrecision = 2

    arcpy.AddField_management(fc, veld_1, "DOUBLE", fieldPrecision, field_is_nullable="NULLABLE")
    arcpy.AddField_management(fc, veld_2, "DOUBLE", fieldPrecision, field_is_nullable="NULLABLE")
    arcpy.AddField_management(fc, veld_3, "DOUBLE", fieldPrecision, field_is_nullable="NULLABLE")
    arcpy.AddField_management(fc, veld_4, "DOUBLE", fieldPrecision, field_is_nullable="NULLABLE")
    arcpy.AddField_management(fc, veld_5, "DOUBLE", fieldPrecision, field_is_nullable="NULLABLE")
    arcpy.AddField_management(fc, veld_6, "DOUBLE", fieldPrecision, field_is_nullable="NULLABLE")
    arcpy.AddField_management(fc, veld_7, "DOUBLE", fieldPrecision, field_is_nullable="NULLABLE")


    velden = ['d70', 'd70m', 'k', 'mw', 'hp', 'dpip', 'DL', 'deltaH', 'L', 'verval', 'F1', 'F2', 'F3', 'kritiek_vv', 'optredend_vv', 'kv_ov',
              'type_lijn', 'uniek_id', 'z_max', 'bron_hp', 'koppel_id', 'dv_nummer', 'winterpeil', 'gem_slootbodem', 'Shape_Length','D', 'note']

    # verwijder ongeldige profielen
    velden_bestaand = arcpy.ListFields(fc)
    lijst_fc_velden = []
    for item in velden_bestaand:
        lijst_fc_velden.append(item.name)


    for item in velden:
        if item not in lijst_fc_velden:
            arcpy.AddField_management(fc, item, "DOUBLE", 2, field_is_nullable="NULLABLE")
        else:
            continue


    with arcpy.da.UpdateCursor(fc, velden) as deleter:
        for row in deleter:
            if row[26] == 'niet_berekenen' or (row[4] is None and row[23] is None):
                print "geen berekening uitgevoerd voor profiel "+str(row[17])
                deleter.deleteRow()
            else:
                continue

    with arcpy.da.UpdateCursor(fc, velden) as cursor:


        # als er geen geldige parameters zijn voor het dijkvak, skip dan dpip berekening
        for row in cursor:

            # bereken dikte deklaag indien zandlaag niet hoger is dan slootbodem of ahn3

            if row[23] is None and row[18] < row[4]:
                row[5] = abs(row[4]-row[18])
            elif row[23] is not None and row[18] < row[23]:
                row[5] = abs(row[23]-row[18])
            elif row[18] >= row[4] or row[18] >= row[23]:
                row[5] = 0
            cursor.updateRow(row)
            dpip = row[5]


            # definieer L (dit is de lengte van de lijn)
            row[8] = row[24]
            L = row[24]
            cursor.updateRow(row)

            #definieer de overige parameters

            naam_dwp = row[17]
            D = row[25]
            d70 = row[0]
            d70m = row[1]
            k = row[2]
            mw = row[3]

            # bepaal hp
            if row[22] is not None:
                row[19] = 'winterpeil WSRL'
                hp = row[22]
            else:
                row[19] = 'gemiddelde hoogte AHN3'
                hp = row[4]
            row[4] = hp
            cursor.updateRow(row)



            #alleen rekenen als er geldige parameters aanwezig zijn
            if naam_dwp is not None:

                #calculate kappa
                kappa = v / 9.81 * k
                #calculate verval
                row[9] = mw-hp
                cursor.updateRow(row)
                #recalculate DL
                DL = D / L
                row[6] = DL
                #calculate deltaH
                deltaH = mw-hp
                row[7] = deltaH
                #calculate F1
                row[10] = gamma_p/gamma_w*n*math.tan(theta*math.pi/180)
                cursor.updateRow(row)
                #calculate F2
                row[11] = ((d70/d70m)**0.4)*(d70m/((kappa*L)**(1/3.0)))
                cursor.updateRow(row)
                #calculate F3
                row[12] = 0.91*DL**((0.28/(DL**(2.8)-1))+0.04)
                cursor.updateRow(row)
                #calculate kritiek verval
                row[13] = (L*row[10]*row[11]*row[12])/sterktefactor
                cursor.updateRow(row)
                #calculate optredend verval
                row[14] = row[9]-(0.3*dpip)
                cursor.updateRow(row)

                #bereken kritiekverval-optredendverval
                row[15] = row[13]-row[14]
                cursor.updateRow(row)
                print "profiel met uniek_id "+str(naam_dwp)+" is berekend"
            else:
                pass

        # velden toevoegen voor beta berekening
        inFeatures = "profielen_final"
        fieldName1 = "y_pip"
        fieldName2 = "y_up"
        fieldName3 = "beta_dsn_piping"
        fieldName4 = "beta_dsn_opbarsten"
        fieldName5 = "beta_max"
        fieldName6 = "toelichting_beta"
        fieldName7 = "beta_min"

        fieldPrecision = 2


        arcpy.AddField_management(inFeatures, fieldName1, "DOUBLE", fieldPrecision, field_is_nullable="NULLABLE")
        arcpy.AddField_management(inFeatures, fieldName2, "DOUBLE", fieldPrecision, field_is_nullable="NULLABLE")
        arcpy.AddField_management(inFeatures, fieldName3, "DOUBLE", fieldPrecision, field_is_nullable="NULLABLE")
        arcpy.AddField_management(inFeatures, fieldName4, "DOUBLE", fieldPrecision, field_is_nullable="NULLABLE")
        arcpy.AddField_management(inFeatures, fieldName5, "DOUBLE", fieldPrecision, field_is_nullable="NULLABLE")
        arcpy.AddField_management(inFeatures, fieldName7, "DOUBLE", fieldPrecision, field_is_nullable="NULLABLE")
        arcpy.AddField_management(inFeatures, fieldName6, "TEXT")
        #print "velden toegevoegd"

        arcpy.CopyFeatures_management("profielen_final", outfc)

        print "sellmeijer script doorlopen voor alle profielen"



def split_berekende_profielen(naam_run):

    # intersect voor puntenlagen
    # maak punten op L1/L2
    inFeatures = [naam_run, 'buitenteenlijn_safe']
    clusterTolerance = 0
    intersectOutput = "punten_buiten"
    arcpy.Intersect_analysis(inFeatures, intersectOutput, "", clusterTolerance, "point")

    # maak punten op L2/L3
    inFeatures = [naam_run, 'binnenteenlijn_safe']
    clusterTolerance = 0
    intersectOutput = "punten_binnen"
    arcpy.Intersect_analysis(inFeatures, intersectOutput, "", clusterTolerance, "point")

    # split
    inFeatures = naam_run
    pointFeatures = "punten_buiten"
    outFeatureclass = "splitsing_buiten"
    searchRadius = "0.3 Meters"

    arcpy.SplitLineAtPoint_management(inFeatures, pointFeatures, outFeatureclass, searchRadius)

    # split lines
    inFeatures = "splitsing_buiten"
    pointFeatures = "punten_binnen"
    outFeatureclass = "splitsing_final"
    searchRadius = "0.3 Meters"

    arcpy.SplitLineAtPoint_management(inFeatures, pointFeatures, outFeatureclass, searchRadius)

def koppel_losse_delen(dijkvakindeling):
    if arcpy.Exists("join_L1"):
        arcpy.DeleteFeatures_management("join_L1")
    if arcpy.Exists("join_L2"):
        arcpy.DeleteFeatures_management("join_L2")
    if arcpy.Exists("join_L3"):
        arcpy.DeleteFeatures_management("join_L3")

    # koppel L1
    targetFeatures = "splitsing_final"
    joinFeatures = "buitenteen_plus_1m_" #dit is het basisbestand met de 64 dijkvakken en snijdt ALLE dwp
    outfc = "join_L1"

    # geef aan welke velden behouden blijven
    fieldmappings = arcpy.FieldMappings()

    # Add all fields from inputs.
    fieldmappings.addTable(targetFeatures)
    fieldmappings.addTable(joinFeatures)

    velden = ['uniek_id', 'L1']

    # definieer te behouden velden
    keepers = velden

    # verwijder overige velden
    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    # voer de spatial join uit
    arcpy.SpatialJoin_analysis(targetFeatures, joinFeatures, outfc, "#", "#", fieldmappings)

    del targetFeatures,joinFeatures,fieldmappings,velden,keepers
    #koppel L2
    targetFeatures = "splitsing_final"
    joinFeatures = dijkvakindeling #dit is het basisbestand met de 64 dijkvakken en snijdt ALLE dwp
    outfc = "join_L2"

    # geef aan welke velden behouden blijven
    fieldmappings = arcpy.FieldMappings()

    # Add all fields from inputs.
    fieldmappings.addTable(targetFeatures)
    fieldmappings.addTable(joinFeatures)

    velden = ['uniek_id', 'L2']

    # definieer te behouden velden
    keepers = velden

    # verwijder overige velden
    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    # voer de spatial join uit
    arcpy.SpatialJoin_analysis(targetFeatures, joinFeatures, outfc, "#", "#", fieldmappings)
    del targetFeatures, joinFeatures, fieldmappings, velden, keepers

    #koppel L3
    targetFeatures = "splitsing_final"
    joinFeatures = "binnenteenlijn_2m" #dit is het basisbestand met de 64 dijkvakken en snijdt ALLE dwp
    outfc = "join_L3"

    # geef aan welke velden behouden blijven
    fieldmappings = arcpy.FieldMappings()

    # Add all fields from inputs.
    fieldmappings.addTable(targetFeatures)
    fieldmappings.addTable(joinFeatures)

    velden = ['uniek_id', 'L3']

    # definieer te behouden velden
    keepers = velden

    # verwijder overige velden
    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    # voer de spatial join uit
    arcpy.SpatialJoin_analysis(targetFeatures, joinFeatures, outfc, "#", "#", fieldmappings)
    del targetFeatures, joinFeatures, fieldmappings, velden, keepers

def verwijder_lege_velden():
    velden1 = ['uniek_id','L1']
    velden2 = ['uniek_id', 'L2']
    velden3 = ['uniek_id', 'L3']

    with arcpy.da.UpdateCursor("join_L1", velden1) as cursor:
        for row in cursor:
            if row[1] < 1:
                cursor.deleteRow()
            else:
                pass
    with arcpy.da.UpdateCursor("join_L2", velden2) as cursor:
        for row in cursor:
            if row[1] < 1:
                cursor.deleteRow()
            else:
                pass
    with arcpy.da.UpdateCursor("join_L3", velden3) as cursor:
        for row in cursor:
            if row[1] < 1:
                cursor.deleteRow()
            else:
                pass

def voeg_nieuwe_velden_toe():
    fieldName1 = "L_voor"
    fieldName2 = "L_dijk"
    fieldName3 = "L_achter"

    fieldPrecision = 2

    arcpy.AddField_management('join_L1', fieldName1, "DOUBLE", fieldPrecision, field_is_nullable="NULLABLE")
    arcpy.AddField_management('join_L2', fieldName2, "DOUBLE", fieldPrecision, field_is_nullable="NULLABLE")
    arcpy.AddField_management('join_L3', fieldName3, "DOUBLE", fieldPrecision, field_is_nullable="NULLABLE")

    arcpy.CalculateField_management("join_L1", "L_voor", '!Shape_Length!', "PYTHON")
    arcpy.CalculateField_management("join_L2", "L_dijk", '!Shape_Length!', "PYTHON")
    arcpy.CalculateField_management("join_L3", "L_achter", '!Shape_Length!', "PYTHON")

def join_velden_aan_resultaten(naam_run):

    arcpy.JoinField_management(naam_run, "uniek_id", "join_L1", "uniek_id",
                               ["L_voor"])
    arcpy.JoinField_management(naam_run, "uniek_id", "join_L2", "uniek_id",
                               ["L_dijk"])
    arcpy.JoinField_management(naam_run, "uniek_id", "join_L3", "uniek_id",
                               ["L_achter"])

def calc_r_exit(naam_run):


    fieldName4 = "dempingsfactor"
    fieldPrecision = 2
    arcpy.AddField_management(naam_run, fieldName4, "DOUBLE", fieldPrecision, field_is_nullable="NULLABLE")

    velden = ["dpip","D","k","hp","mw","L_voor","L_dijk","L_achter","dempingsfactor"]

    with arcpy.da.UpdateCursor(naam_run, velden) as cursor:


        for row in cursor:

            # workaround dpip
            if row[0] <= 0:
                dpip = 0.01
            else:
                dpip = row[0]


            D = row[1]
            k = row[2]
            hp = row[3]
            mw = row[4]
            # L_voor = row[5]
            L_dijk = row[6]
            # L_achter = row[7]

            if row[5]== None:
                L_voor = 1
            else:
                L_voor = row[5]
            if row[7] == None:
                L_achter = 1
            else:
                L_achter = row[7]

            lambda2 = np.sqrt(((k* 86400) * D) * (dpip / 0.01))
            #slight modification: foreshore is counted as dijkzate

            phi2 = hp + (mw - hp)*((lambda2*np.tanh(2000/lambda2))/(lambda2*np.tanh(L_voor/0.01)+L_dijk+L_achter+lambda2*np.tanh(2000/lambda2)))
            phi_test = hp +(mw-hp)*((lambda2*np.tanh(2000/lambda2))/(lambda2*np.tanh(L_voor/lambda2)+L_dijk+L_achter+lambda2*np.tanh(2000/lambda2)))
            dempingsfactor = (phi_test-hp)/(mw-hp)
            row[8] = dempingsfactor

            if dpip < 0:
                row[8] = 1
            cursor.updateRow(row)

def bereken_beta(naam_run):

    inFeatures = naam_run


    # bereken waardes

    bmax = 3.72 # vaste parameter
    sf = 1.0 # vaste parameter
    fields = ['y_pip', 'beta_dsn_piping', 'kritiek_vv', 'optredend_vv', 'hp', 'mw', 'dpip', 'y_up', 'beta_dsn_opbarsten',
              'beta_max', 'toelichting_beta', 'beta_min', 'dempingsfactor', 'note']

    with arcpy.da.UpdateCursor(inFeatures, fields) as cur:
        for row in cur:
            # bereken beta stph
            row[0] = (row[2]/(row[3]*sf))
            cur.updateRow(row)
            ypip = row[0]

            ##
            if row[0] > 0:
                row[1] = (0.43*bmax+math.log(ypip/1.04))/0.37
            else:
                row[1] = 8
            cur.updateRow(row)

            betadsn = row[1]


            # bereken beta opbarsten
            # 1: bereken optredend stijghoogteverschil
            h = row[5]

            if row[4] == 0:
                hexit = 0.1
            else:
                hexit = row[4]

            if row[12] == 0:
                rexit = 1
            else:
                rexit = row[12]

            delta0 = (h-hexit)*rexit



            # 2: bereken kritiek stijghoogteverschil
            if row[6] == 0:
                Ddek = 0.1
            else:
                Ddek = row[6]

            ysat = 16.5
            ywat = 9.81
            delta0u = (Ddek*(ysat-ywat))/ywat

            # 3:bereken benodigde veiligheidsfactor
            yup = delta0u/(delta0*sf)
            row[7] = yup
            cur.updateRow(row)

            ##
            if yup > 0:
                beta_opbarsten = (0.27 * bmax + math.log(yup / 0.48)) / 0.46
                row[8] = beta_opbarsten
            else:
                beta_opbarsten = 8
                row[8] = beta_opbarsten
            cur.updateRow(row)



            # vul toelichting aan
            if row[1] > row[8]:
                row[9] = row[1]
                row[10] = "beta piping heeft hoogste waarde"
            else:
                row[9] = row[8]
                row[10] = "beta opbarsten heeft hoogste waarde"
            cur.updateRow(row)

            if row[0] < 0 or row[7] < 0:
                row[10] = "y_pip of y_up is negatief, beta = 8"
            else:
                pass
            cur.updateRow(row)

            #bereken minimale beta
            if row[1] < row[8]:
                row[11] = row[1]
            else:
                row[11] = row[8]
            cur.updateRow(row)


            # rijen verwijderen/aanpassen beta op basis van 'note' field
            if row[13] == 'beta_7':
                row[9] = 7
                cur.updateRow(row)
            else:
                continue




def calc_extensie(naam_run, intredelijn_buffer, koppeling_voorlandbuffers):
    # voorlanden aangepast koppeling
    # intersect
    clusterTolerance = 0
    invoer = [naam_run, intredelijn_buffer]
    uitvoer = 'snijpunten_intredelijn'
    arcpy.Intersect_analysis(invoer, uitvoer, "", clusterTolerance, "point")
    del invoer, uitvoer

    invoer = naam_run
    punten = "snijpunten_intredelijn"
    uitvoer = "lengtes_tot_buffer"
    searchRadius = 1

    arcpy.SplitLineAtPoint_management(invoer, punten, uitvoer, searchRadius)
    arcpy.MakeFeatureLayer_management('lengtes_tot_buffer', 'lengtes_tot_buffer_temp')
    arcpy.SelectLayerByLocation_management('lengtes_tot_buffer_temp', 'intersect', koppeling_voorlandbuffers)
    arcpy.CopyFeatures_management('lengtes_tot_buffer_temp', 'voorlanden_tot_buffer')

    arcpy.AddField_management('voorlanden_tot_buffer', 'lengte_buffer', "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management("voorlanden_tot_buffer", "lengte_buffer", '!Shape_Length!', "PYTHON")
    arcpy.JoinField_management(naam_run, "uniek_id", "voorlanden_tot_buffer", "uniek_id",["lengte_buffer"])


def controle_stph(naam_run):
    arcpy.AddField_management(naam_run, 'controle_stph', "TEXT", field_length=50)
    # arcpy.AddField_management(naam_run, 'waarde_controle', "DOUBLE", 2.0, field_is_nullable="NULLABLE")

    fields = ['kritiek_vv','optredend_vv', 'uniek_id','controle_stph']
    ypip = 1.31
    ybpip = 1
    with arcpy.da.UpdateCursor(naam_run, fields) as cursor:
        for row in cursor:
            kv = row[0]
            ov = row[1]

            deler = (kv/(ypip*ybpip))

            if ov <= deler:
                print "controle piping: voldoende", row[2]
                row[3] = 'voldoende'
                cursor.updateRow(row)
            else:
                row[3] = 'onvoldoende'
                print "controle piping: onvoldoende", row[2]
                cursor.updateRow(row)


def verlenger(coastline, directions):
    # coastline = r"C:\Users\vince\Desktop\GIS\analyse_stph.gdb\voorlanden_30m"
    # directions = "profielen_final"
    g = arcpy.Geometry()
    bank = arcpy.CopyFeatures_management(coastline, g)[0]

    with arcpy.da.UpdateCursor(directions, "Shape@") as cursor:
        for row in cursor:
            line = row[0]
            pStart = line.firstPoint
            pEnd = line.lastPoint
            L = line.length
            dX = (pEnd.X - pStart.X) / L;
            dY = (pEnd.Y - pStart.Y) / L
            p = pEnd
            m = 0
            while True:
                l = bank.distanceTo(p)
                L += l
                p.X = pStart.X + dX * L
                p.Y = pStart.Y + dY * L
                m += 1
                if m > 100: break
                if l < 0.001: break
            if m > 100: continue
            row[0] = arcpy.Polyline(arcpy.Array([pStart, p]))
            cursor.updateRow(row)

# velden_voor_profielen()
# koppel_hoogte_zandlaag()
# knoop_gekb_profielen()
# knip_profielen_140m()
# split_profielen_waterlopen()
# uittredepunten_land()
#
# sellmeijer_aangepast()
#
# split_berekende_profielen()
# koppel_losse_delen()
# verwijder_lege_velden()
# voeg_nieuwe_velden_toe()
# join_velden_aan_resultaten()
# calc_r_exit()
# bereken_beta()
#
# calc_extensie()



