# importeer benodigde modules
import gc
gc.collect()
import arcpy
import math
from arcpy.sa import *
import numpy as np

# DENK AAN HET KOPPELEN VAN DE ZANDLAGEN INDIEN NIEUWE PROFIELEN GEMAAKT ZIJN!!!

# overschrijf oude data, indien aanwezig
arcpy.env.overwriteOutput = True

# definieer .gdb waarin gewerkt wordt
arcpy.env.workspace = "C:/Users/vince/Desktop/GIS/stph_testomgeving.gdb"


profielen = "mg_16_4"
intredelijn = "vl_dvmin_90m"
uittredelijn = "binnenteenlijn_2m"
dijkvakindeling = "dijkvakindeling_stph_juni_2019"
# hoogtegrid = "C:/Users/vince/Desktop/GIS/stph_testomgeving.gdb/raster_safe"
waterstanden = "gekb_safe"

# eerste deel functies. Dit deel is nodig om de juiste waarde van de maaiveldhoogte/slootpeil te genereren.

def koppel_hoogte_zandlaag():
    zandlagen = r"C:\Users\vince\Desktop\GIS\zandlagen_safe.gdb\zandlaag_totaal_xls_z_totaal_route"
    output = 'spatial_zandlagen_profielen'
    veld_z = 'z_totaal'
    veld_id = 'uniek_id'

    bestaande_velden = arcpy.ListFields(profielen)

    for field in bestaande_velden:
        if field.name == "z_max":
            arcpy.DeleteField_management(profielen, "z_max")
            print "oude z_max verwijderd"
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


def knoop_gekb_profielen():

    velden = ["uniek_id","mw_2015"]
    output = "test_profielen_gekb"
    fieldmappings = arcpy.FieldMappings()


    fieldmappings.addTable(waterstanden)
    fieldmappings.addTable(profielen)
    keepers = velden

    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))


    arcpy.SpatialJoin_analysis(profielen, waterstanden, output, "#", "#", fieldmappings, match_option="CLOSEST") #CLOSEST?
    arcpy.AlterField_management(output, "mw_2015", "mw")

    #check of mw veld al bestaat
    bestaande_velden = arcpy.ListFields(profielen)

    for field in bestaande_velden:
        if field.name == "mw":
            arcpy.DeleteField_management(profielen, "mw")
            print "oude mw verwijderd"
        else:
            continue

    arcpy.JoinField_management(profielen, "uniek_id", "test_profielen_gekb", "uniek_id",
                               ["mw"])

    print "profielen voorzien van maatgevende waterstand"




def samenvoegen_sloten():
    # verwijder oude data
    if arcpy.Exists("test_sloten_join"):
        arcpy.DeleteFeatures_management("test_sloten_join")
    else:
        pass
    print "oude waterlopen-data verwijderd"


    # test of het uittredepunt in een sloot ligt
    targetFeatures = "punten2"
    joinFeatures = "waterlopen_safe_dummy"
    outfc = "test_sloten_join"

    # spatial join punten 2
    velden = ['uniek_id','bron_hp','winterpeil'] #defineeer de te behouden velden
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
    arcpy.SpatialJoin_analysis(targetFeatures, joinFeatures, outfc, "#", "#", fieldmappings, match_option="INTERSECT",search_radius= 2) #CLOSEST?
    print "join compleet"

    # update de tabel met welke waarde nodig is in de Sellmeijer berekening
    sloten = 'test_sloten_join'
    fields1 = ['uniek_id', 'winterpeil', 'bron_hp']
    with arcpy.da.UpdateCursor(sloten, fields1) as cursor:
        for row in cursor:
            if row[1] is None:
                row[2] = "ahn3-waarde nodig"
            else:
                row[2] = "slootpeil gebruiken in berekening"
            cursor.updateRow(row)


    # koppel waterpeil sloten
    inFeatures = "eindresultaat"
    joinField = "uniek_id"

    joinTable = "test_sloten_join"
    fieldList = ["bron_hp", "winterpeil"]

    # verwijder dubbelgangers velden
    dropfield = "bron_hp"
    arcpy.DeleteField_management(inFeatures, dropfield)

    arcpy.JoinField_management(inFeatures, joinField, joinTable, joinField, fieldList)


    # koppel aan eindresultaat
    eindres = 'eindresultaat'
    fields2 = ['uniek_id', 'winterpeil', 'hp', 'bron_hp']
    with arcpy.da.UpdateCursor(eindres, fields2) as cursor:
        for row in cursor:
            if row[1] is None:
                row[2] = None
            else:
                row[2] = row[1]
            cursor.updateRow(row)
    print "koppeling gemaakt met eindresultaatlaag"

def buffer_uittredepunten():
    # verwijder oude data
    if arcpy.Exists("punten_buffer"):
        arcpy.DeleteFeatures_management("punten_buffer")
    else:
        pass
    print "oude bufferzones verwijderd"

    # voor alle uittredepunten wordt cirkelvormige buffer van 10m gemaakt.
    punten = "punten2"
    punten_buffer = "punten_buffer"
    distanceField = "buffer_uit"

    arcpy.Buffer_analysis(punten, punten_buffer, distanceField)
    print "nieuwe bufferzones op uittredepunten gemaakt"


def zonal_statistics_sloten():

    # voor alle bufferzones wordt de gemiddelde maaiveldhoogte berekend m.b.v. AHN3
    arcpy.env.overwriteOutput = True
    # invoer
    inZoneData = "punten_buffer"

    # set TARGET FID to uniek_id
    arcpy.CalculateField_management(inZoneData, "FID_mg_16_4", '!uniek_id!', "PYTHON_9.3")
    arcpy.AlterField_management(inZoneData, "FID_mg_16_4", 'id')

    zoneField = "id"  # "naam_dwp"
    inValueRaster = "C:/Users/vince/Desktop/GIS/losse rasters/ahn3clip/ahn3clip_safe"
    outTable = "statistieken_uittrede.dbf"

    # voer bewerking uit
    tabel = ZonalStatisticsAsTable(inZoneData, zoneField, inValueRaster,
                                     outTable,"DATA", "MEAN")

    # verwijder oude tabel
    arcpy.Delete_management("output_tabel_statistieken")
    print "oude tabel met gemiddelde maaiveldhoogtes verwijderd"

    # maak een nieuwe tabel aan in de .gdb
    inTable = tabel
    outLocation = "C:/Users/vince/Desktop/GIS/stph_testomgeving.gdb"
    outTable = "output_tabel_statistieken"
    arcpy.TableToTable_conversion(inTable, outLocation, outTable)

    # verander veldnaam van tabel, 1
    fc = "output_tabel_statistieken"
    field1 = "MEAN"  # short int, non nullable field
    new_name1 = "gemiddelde_z"

    arcpy.AlterField_management(fc, field1, new_name1)

    # verander veldnaam van tabel, 2
    fc = "output_tabel_statistieken"
    field2 = "id"  # short int, non nullable field
    new_name2 = "uniek_id"

    arcpy.AlterField_management(fc, field2, new_name2)
    print "tabel met gemiddelde maaiveldhoogtes gemaakt"


def koppelen_statistics():
    #koppel z waardes

    # invoer
    inFeatures = "eindresultaat"
    joinField = "uniek_id"

    joinTable = "output_tabel_statistieken"
    fieldList = ["gemiddelde_z"]
    #dropFields = ["RASTERVALU"]

    # verwijder bestaande velden met z-waarden uit het AHN3
    #arcpy.DeleteField_management(inFeatures, dropFields)



    arcpy.JoinField_management(inFeatures, joinField, joinTable, joinField, fieldList)
    print 'veld met "gemiddelde_z" toegevoegd aan eindresultaat'

    eindres = 'eindresultaat'
    velden_eindresultaat = ['hp','gemiddelde_z','winterpeil']


    # update hp waarde met winterpeil of gemiddelde ahn3 hoogte
    with arcpy.da.UpdateCursor(eindres, velden_eindresultaat) as cursor:

        for row in cursor:
            if row[2] is None:
                row[0] = row[1]
            else:
                row[0] = row[2]
            cursor.updateRow(row)
    print "eindresultaatlaag is aangepast met nieuwe hp-waarden"



def points_at_lines():
    #verwijder oude data
    if arcpy.Exists("punten1"):
        arcpy.DeleteFeatures_management("punten1")
    else:
        pass
    if arcpy.Exists("punten2"):
        arcpy.DeleteFeatures_management("punten2")
    else:
        pass
    print "oude puntenlagen verwijderd"

    # maak punten op de snijpunten, deel 1
    inFeatures = [profielen, intredelijn]
    clusterTolerance = 0
    intersectOutput = "punten1"
    arcpy.Intersect_analysis(inFeatures, intersectOutput, "", clusterTolerance, "point")
    # maak punten op de snijpunten, deel 2 (uittredepunten)
    inFeatures = [profielen, uittredelijn]
    clusterTolerance = 0
    intersectOutput = "punten2"
    arcpy.Intersect_analysis(inFeatures, intersectOutput, "", clusterTolerance, "point")
    print "nieuwe punten op de snijpunten gemaakt"

def splitlines():
    # verwijder oude data
    if arcpy.Exists("split1"):
        arcpy.DeleteFeatures_management("split1")
    else:
        pass
    if arcpy.Exists("split_final"):
        arcpy.DeleteFeatures_management("split_final")
    else:
        pass
    print "oude lijnen-lagen verwijderd"

    # split lines
    inFeatures = profielen
    pointFeatures = "punten1"
    outFeatureclass = "split1"
    searchRadius = "0.3 Meters"

    arcpy.SplitLineAtPoint_management(inFeatures, pointFeatures, outFeatureclass, searchRadius)

    # split lines
    inFeatures = "split1"
    pointFeatures = "punten2"
    outFeatureclass = "split_final"
    searchRadius = "0.3 Meters"

    arcpy.SplitLineAtPoint_management(inFeatures, pointFeatures, outFeatureclass, searchRadius)
    print "lijnen zijn gesplitst"

def koppeling():
    # verwijder oude data
    if arcpy.Exists("join_test"):
        arcpy.DeleteFeatures_management("join_test")
    else:
        pass
    print "oude koppelingen verwijderd"

    targetFeatures = "split_final"
    joinFeatures = dijkvakindeling #dit is het basisbestand met de 64 dijkvakken en snijdt ALLE dwp
    outfc = "join_test"F

    # geef aan welke velden behouden blijven
    fieldmappings = arcpy.FieldMappings()

    # Add all fields from inputs.
    fieldmappings.addTable(targetFeatures)
    fieldmappings.addTable(joinFeatures)

    velden = ['naam_dwp', 'n', 'D', 'gamma_p', 'gamma_w', 'theta', 'd70', 'd70m', 'k', 'sterktefactor', 'mw', 'v', 'hp',
              'dpip', 'DL', 'deltaH', 'L', 'verval', 'F1', 'F2', 'F3', 'kritiek_vv', 'optredend_vv', 'kv_ov',
              'Shape_Length', 'type_lijn', 'uniek_id', 'RASTERVALU', 'z_max', 'bron_hp','koppel_id','dv_nummer']

    # definieer te behouden velden
    keepers = velden

    # verwijder overige velden
    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    # voer de spatial join uit
    arcpy.SpatialJoin_analysis(targetFeatures, joinFeatures, outfc, "#", "#", fieldmappings)

    print "nieuwe koppeling gemaakt met dijkvakindeling"

def select_lines():
    # verwijder oude data
    if arcpy.Exists("eindresultaat"):
        arcpy.DeleteFeatures_management("eindresultaat")
    else:
        pass
    print "oude eindresultaatlaag verwijderd"

    # selecteer het lijnstuk wat tussen de gekozen lijnen ligt
    arcpy.MakeFeatureLayer_management("join_test", "join_test_temp")
    arcpy.SelectLayerByAttribute_management("join_test_temp", "NEW_SELECTION", '"type_lijn" = 0')
    arcpy.CopyFeatures_management("join_test_temp", "eindresultaat")


    # join dijkvak en dijktraject op basis van koppel_id
    arcpy.JoinField_management("eindresultaat", "koppel_id", dijkvakindeling, "koppel_id",
                               ["dv_nummer", "dijktraject"])




    print "nieuwe eindresultaatlaag gemaakt"



def sellmeijer_aangepast():

    # STUK TESTCODE OM RIJEN MET OVERLAPPENDE BUFFERPOLYGONS TE VERWIJDEREN #

    deleter_velden = ['uniek_id','gemiddelde_z']
    with arcpy.da.UpdateCursor("eindresultaat", deleter_velden) as deleter:
        for row in deleter:
            if row[1] is None:
                deleter.deleteRow()
            else:
                pass
    # -------------------------------------------------------------


    # geef aan welk bestand gebruikt gaat worden voor de formule
    global output_run
    fc = "eindresultaat"
    outfc = "basis_2m_90m_mg"
    output_run = outfc

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

    velden2 = ['naam_dwp', 'n', 'D', 'gamma_p', 'gamma_w', 'theta', 'd70', 'd70m', 'k', 'sterktefactor', 'mw', 'v', 'hp',
              'dpip', 'DL', 'deltaH', 'L', 'verval', 'F1', 'F2', 'F3', 'kritiek_vv', 'optredend_vv', 'kv_ov',
              'Shape_Length', 'uniek_id','z_max', 'bron_hp']


    with arcpy.da.UpdateCursor(fc, velden2) as cursor:

        # als er geen geldige parameters zijn voor het dijkvak, skip dan dpip berekening
        for row in cursor:
            row[0] = row[25]
            cursor.updateRow(row)
            #if row[25] is None:
                #row[13] = None
                #cursor.updateRow(row)
            #else:
                #pass


            # bereken dpip met check voor waarden van z_max groter dan 0
            if row[26] > 0:
              row[26] = -(row[26])
              cursor.updateRow(row)
            else:
              pass
            row[13] = row[12]-row[26]
            cursor.updateRow(row)
            dpip = row[13]
            #definieer L (dit is de lengte van de lijn)
            row[16] = row[24]
            cursor.updateRow(row)
            #definieer de overige parameters
            naam_dwp = row[0]
            n = row[1]
            D = row[2]
            gamma_p = row[3]
            gamma_w = row[4]
            theta = row[5]
            d70 = row[6]
            d70m = row[7]
            k = row[8]
            sterktefactor = row[9]
            mw = row[10]
            v = row[11]
            hp = row[12]
            L = row[16]


            #alleen rekenen als er geldige parameters aanwezig zijn
            if row[0] is not None:

                #calculate kappa
                kappa = row[11] / 9.81 * row[8]
                #calculate verval
                row[17] = row[10]-row[12]
                cursor.updateRow(row)
                #recalculate DL
                DL = D / L
                row[14] = DL
                #calculate deltaH
                deltaH = mw-hp
                row[15] = deltaH
                #calculate F1
                row[18] = gamma_p/gamma_w*n*math.tan(theta*math.pi/180)
                cursor.updateRow(row)
                #calculate F2
                row[19] = ((d70/d70m)**0.4)*(d70m/((kappa*L)**0.333))
                cursor.updateRow(row)
                #calculate F3
                row[20] = 0.91*DL**((0.28/(DL**(2.8)-1))+0.04)
                cursor.updateRow(row)
                #calculate kritiek verval
                row[21] = (L*row[18]*row[19]*row[20])/sterktefactor
                cursor.updateRow(row)
                #calculate optredend verval
                row[22] = row[17]-(0.3*dpip)
                cursor.updateRow(row)
                #calculate oordeel #uitzetten!
                # if dpip > 4:
                #     row[23] = 100
                # else:
                row[23] = row[21]-row[22]
                cursor.updateRow(row)
                # print "profiel met uniek_id "+str(row[25])+" is berekend"
            else:
                pass

        # velden toevoegen voor beta berekening
        inFeatures = "eindresultaat"
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

        arcpy.CopyFeatures_management("eindresultaat", outfc)

        print "sellmeijer script doorlopen voor alle profielen"

# L-sectie
def split_berekende_profielen():
    # intersect voor puntenlagen
    # output_run = "eindresultaat"
    # maak punten op L1/L2
    inFeatures = [output_run, 'buitenteenlijn_safe']
    clusterTolerance = 0
    intersectOutput = "punten_buiten"
    arcpy.Intersect_analysis(inFeatures, intersectOutput, "", clusterTolerance, "point")

    # maak punten op L2/L3
    inFeatures = [output_run, 'binnenteenlijn_safe']
    clusterTolerance = 0
    intersectOutput = "punten_binnen"
    arcpy.Intersect_analysis(inFeatures, intersectOutput, "", clusterTolerance, "point")

    # split
    inFeatures = output_run
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


def koppel_losse_delen():

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


def join_velden_aan_resultaten():
    # output_run = "eindresultaat"
    arcpy.JoinField_management(output_run, "uniek_id", "join_L1", "uniek_id",
                               ["L_voor"])
    arcpy.JoinField_management(output_run, "uniek_id", "join_L2", "uniek_id",
                               ["L_dijk"])
    arcpy.JoinField_management(output_run, "uniek_id", "join_L3", "uniek_id",
                               ["L_achter"])


def calc_r_exit():
    # output_run = "eindresultaat"
    fieldName4 = "dempingsfactor"
    fieldPrecision = 2
    arcpy.AddField_management(output_run, fieldName4, "DOUBLE", fieldPrecision, field_is_nullable="NULLABLE")

    velden = ["dpip","D","k","hp","mw","L_voor","L_dijk","L_achter","dempingsfactor"]

    with arcpy.da.UpdateCursor(output_run, velden) as cursor:


        for row in cursor:

            # workaround dpip
            if row[0] < 0:
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

# Beta-sectie
def bereken_beta():
    inFeatures = output_run


    # bereken waardes

    bmax = 3.72 # vaste parameter
    sf = 1.0 # vaste parameter
    fields = ['y_pip', 'beta_dsn_piping', 'kritiek_vv', 'optredend_vv', 'hp', 'mw', 'dpip', 'y_up', 'beta_dsn_opbarsten',
              'beta_max', 'toelichting_beta', 'beta_min', 'dempingsfactor']

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


            #beta_opbarsten = (0.27*bmax+math.log(yup/0.48))/0.46






#uitvoer volgorde scripts:

koppel_hoogte_zandlaag()
knoop_gekb_profielen()
points_at_lines()
splitlines()
koppeling()
select_lines()

samenvoegen_sloten()
buffer_uittredepunten()
zonal_statistics_sloten()
koppelen_statistics()

sellmeijer_aangepast()

split_berekende_profielen()
koppel_losse_delen()
verwijder_lege_velden()
voeg_nieuwe_velden_toe()
join_velden_aan_resultaten()
calc_r_exit()

bereken_beta()




