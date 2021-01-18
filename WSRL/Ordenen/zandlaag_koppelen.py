#importeer modules
import arcpy
import os
import xlrd
arcpy.env.overwriteOutput = True

arcpy.env.workspace = r'C:/Users/vince/Desktop/GIS/zandlagen_safe.gdb'


#maak dictionary om namen te genereren
aantallen = [0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,21,22,23,24,25,27,28,29,30,31,33,34,35,36,37,38]
#define dictionary to work with
join_lijst = []

for i in aantallen:
    mergenaam = "zandlagen_aangepast_xls_xz"+str(i)+"_route"
    join_lijst.append(mergenaam)



keys = aantallen
values = join_lijst


#print join_lijst



tuple(keys)
tuple(values)
dictionary = dict(zip(keys, values))


#definieer het bestand waaraan gekoppeld wordt
basis = "C:/Users/vince/Desktop/GIS/stph_testomgeving.gdb/stph_25m"

def samenvoegen():
    for key in dictionary:
        targetFeatures = basis
        joinFeatures = dictionary[key]
        outfc = "join_"+dictionary[key]

        # regel de fieldmapping...
        fieldmappings = arcpy.FieldMappings()
        fieldmappings.addTable(targetFeatures)
        fieldmappings.addTable(joinFeatures)

        # ...met de te behouden velden
        keepers = ["uniek_id","z"+str(key)]

        #verwijder onnodige velden
        for field in fieldmappings.fields:
            if field.name not in keepers:
                fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))


        #daarna kan de koppeling worden gemaakt...
        arcpy.SpatialJoin_analysis(targetFeatures, joinFeatures, outfc, "#", "#", fieldmappings,"INTERSECT")
        print "join "+str(dictionary[key])+" done"

#deze werkt nog niet goed, iedere kolom wordt overschreven



def koppel_z_waarden():
    #koppel z waardes
    arcpy.MakeFeatureLayer_management(basis, "stph_25m_temp1")

    for key in dictionary:
        set = "join_"+dictionary[key]
        nummer = str(key)
        arcpy.MakeFeatureLayer_management(set, "item_temp")

    # Set the local parameters
        inFeatures = "stph_25m_temp1"
        joinField = "uniek_id"

        joinTable = "item_temp"
        fieldList = ["z"+nummer]

        arcpy.JoinField_management(inFeatures, joinField, joinTable, joinField, fieldList)
        print "laag "+str(key)+" compleet"
    arcpy.CopyFeatures_management("stph_25m_temp1","stph_25m_test")


def max_z():
    #definieer het basisbestand
    fc = "stph_25m_test"
    #en de velden die in de cursor worden gebruikt


    velden = ["z0","z1","z3","z4","z5","z6","z7","z8","z9","z10","z11","z12","z13","z14","z15","z16","z17","z18",
              "z21","z22","z23","z24","z25","z27","z28","z29","z30","z31","z33","z34","z35","z36","z37","z38","z_max"]



    #itereer over de rijen met de updatecursor
    with arcpy.da.UpdateCursor(fc, velden) as cursor:
        for row in cursor:

            #maak een lijst van alle z-waarden in de rij
            list = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],
            row[14],row[15],row[16],row[17],row[18],row[19],row[20],row[21],row[22],row[23],row[24],row[25],row[26],row[27],
                    row[28],row[29],row[30],row[31],row[32],row[33],row[33],row[34]]

            #en kies hieruit de maximale
            max_value = max(list)
            row[34] = max_value
            cursor.updateRow(row)

samenvoegen()
koppel_z_waarden()
max_z()