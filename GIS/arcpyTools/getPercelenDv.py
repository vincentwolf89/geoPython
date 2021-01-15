import arcpy
from arcpy.sa import *
sys.path.append('.')
import pandas as pd
import math
from itertools import groupby
import numpy as np
import re



arcpy.env.workspace = r"D:\Projecten\WSRL\safe\ruimtebeslag_januari2020.gdb"
arcpy.env.overwriteOutput = True

output_excel = r"C:/Users/Vincent/Desktop/ruimtebeslag_safe/output_excel/"

percelen_eigendommen = "percelen_eigendommen_500m"
priovakken = r"D:\Projecten\WSRL\basisdata.gdb\priovakken_safe_2021"
maatregelvlakken = r"D:\Projecten\WSRL\safe\ruimtebeslag_januari2020.gdb\MA1_vlakken_totaal"
vaknamen = "vaknaam_20"


# alternatieven = ["ma1_vlakken","ma2_vlakken","ma3_vlakken","ma4_vlakken","ma5_vlakken"]
alternatieven = ["ma1_vlakken"]


percelen_alternatieven = []
eigenaar_veld_uniek = "eigenaar_uniek"
eigenaar_velden = ["NAAM","VOORN","VOORV","VOORL","STRAAT","HUISNR","POSTCODE","WOONPLAATS",eigenaar_veld_uniek]




# selecteer percelen binnen alternatief, voor ieder alternatief
for alternatief in alternatieven:
    naam_alternatief = alternatief.split("_")[0]
    arcpy.MakeFeatureLayer_management(percelen_eigendommen, "temp_percelen") 
    arcpy.SelectLayerByLocation_management("temp_percelen", "INTERSECT", alternatief, "5 Meters", "NEW_SELECTION", "NOT_INVERT")

    naam_alternatief_gekoppeld = "percelen_{}".format(naam_alternatief)
    arcpy.CopyFeatures_management("temp_percelen", naam_alternatief_gekoppeld)
    percelen_alternatieven.append(naam_alternatief_gekoppeld)




    # maak eigenaar veld voor unieke selectie en koppel terug welk alternatief
    arcpy.AddField_management(naam_alternatief_gekoppeld,"eigenaar_uniek","TEXT", field_length=500)
    tempCursor = arcpy.da.UpdateCursor(naam_alternatief_gekoppeld, eigenaar_velden)
    for tRow in tempCursor:

        waardes = []

        achternaam_eigenaar = tRow[0]
        voornaam_eigenaar = tRow[1]
        voorvoegsel_eigenaar = tRow[2]
        voorletter_eigenaar = tRow[3]
        straat_eigenaar = tRow[4]
        huisnummer_eigenaar = tRow[5]
        postcode_eigenaar = tRow[6]
        woonplaats_eigenaar = tRow[7]

       
        if achternaam_eigenaar is None:
            achternaam_eigenaar = "_"
        if voornaam_eigenaar is None:
            voornaam_eigenaar = "_"
        if voorvoegsel_eigenaar is None:
            voorvoegsel_eigenaar = "_"
        if voorletter_eigenaar is None:
            voorletter_eigenaar = "_"
        if straat_eigenaar is None:
            straat_eigenaar = "_"
        if huisnummer_eigenaar is None:
            huisnummer_eigenaar = "_"
        if postcode_eigenaar is None:
            postcode_eigenaar = "_"
        if woonplaats_eigenaar is None:
            woonplaats_eigenaar = "_"


        unieke_eigenaar = voorletter_eigenaar+","+voorvoegsel_eigenaar+","+achternaam_eigenaar+","+straat_eigenaar+","+str(huisnummer_eigenaar)+","+postcode_eigenaar+","+woonplaats_eigenaar
        tRow[8] = unieke_eigenaar

        tempCursor.updateRow(tRow)

    del tempCursor
    
    # koppel alternatief terug
    tempCursor = arcpy.da.UpdateCursor(naam_alternatief_gekoppeld, naam_alternatief)
    for tRow in tempCursor:
        tRow[0] = "ja"

        tempCursor.updateRow(tRow)

    del tempCursor

    print naam_alternatief_gekoppeld


# voeg alles samen
arcpy.Merge_management(percelen_alternatieven,"percelen_totaal")

# verwijder identieke percelen
arcpy.DeleteIdentical_management("percelen_totaal", "UNIEK_ID", "", "0")

# koppel aan dijkvak
arcpy.SpatialJoin_analysis("percelen_totaal", priovakken, "percelen_totaal_dv", "JOIN_ONE_TO_ONE", "KEEP_ALL","","CLOSEST", "", "")

# overbouw naar excel
arrayMa = arcpy.da.FeatureClassToNumPyArray("percelen_totaal_dv", (vaknamen, eigenaar_veld_uniek))
dfMa = pd.DataFrame(arrayMa)
sortDfMa = dfMa.sort_values(by=[vaknamen],ascending=[True])

grouped = sortDfMa.groupby(vaknamen)

# over iedere groep itereren, per dijkvak
for group_name, df_group in grouped:
    vaknaam_temp = group_name

    vaknaam_temp = vaknaam_temp.replace(" ","_")
    vaknaam_temp = vaknaam_temp.replace("+","_")
    vaknaam_temp = vaknaam_temp.replace("(","_")
    vaknaam_temp = vaknaam_temp.replace(")","")
    vaknaam_temp = vaknaam_temp.replace(",","")
    vaknaam_temp = vaknaam_temp.replace("-","_")
    vaknaam_temp = vaknaam_temp.replace("/","")
    vaknaam_temp = vaknaam_temp.replace("__","_")


    df_unique = df_group.groupby(eigenaar_veld_uniek)[eigenaar_veld_uniek].nunique()

        

    df_unique.to_excel("{}{}.xlsx".format(output_excel,vaknaam_temp))
    






# # selecteer percelen binnen alternatief, voor ieder alternatief
# for alternatief in alternatieven:
    
#     naam_alternatief = alternatief.split("_")[0]
#     arcpy.MakeFeatureLayer_management(perdelen_eigendommen, "temp_percelen") 
#     arcpy.SelectLayerByLocation_management("temp_percelen", "INTERSECT", alternatief, "5 Meters", "NEW_SELECTION", "NOT_INVERT")

#     naam_alternatief_gekoppeld = "percelen_{}".format(naam_alternatief)
#     arcpy.CopyFeatures_management("temp_percelen", naam_alternatief_gekoppeld)
    

    
#     # maak eigenaar veld voor unieke selectie
#     arcpy.AddField_management(naam_alternatief_gekoppeld,"eigenaar_uniek","TEXT", field_length=500)
#     tempCursor = arcpy.da.UpdateCursor(naam_alternatief_gekoppeld, eigenaar_velden)
#     for tRow in tempCursor:

#         waardes = []

#         achternaam_eigenaar = tRow[0]
#         voornaam_eigenaar = tRow[1]
#         voorvoegsel_eigenaar = tRow[2]
#         voorletter_eigenaar = tRow[3]
#         straat_eigenaar = tRow[4]
#         huisnummer_eigenaar = tRow[5]
#         postcode_eigenaar = tRow[6]
#         woonplaats_eigenaar = tRow[7]

       
#         if achternaam_eigenaar is None:
#             achternaam_eigenaar = "_"
#         if voornaam_eigenaar is None:
#             voornaam_eigenaar = "_"
#         if voorvoegsel_eigenaar is None:
#             voorvoegsel_eigenaar = "_"
#         if voorletter_eigenaar is None:
#             voorletter_eigenaar = "_"
#         if straat_eigenaar is None:
#             straat_eigenaar = "_"
#         if huisnummer_eigenaar is None:
#             huisnummer_eigenaar = "_"
#         if postcode_eigenaar is None:
#             postcode_eigenaar = "_"
#         if woonplaats_eigenaar is None:
#             woonplaats_eigenaar = "_"


#         unieke_eigenaar = achternaam_eigenaar+"_"+voorletter_eigenaar+"_"+voorvoegsel_eigenaar+"_"+straat_eigenaar+"_"+str(huisnummer_eigenaar)+"_"+postcode_eigenaar+"_"+woonplaats_eigenaar
#         tRow[8] = unieke_eigenaar

#         tempCursor.updateRow(tRow)

#     del tempCursor
#     print "unieke eigenaar aangemaakt"
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
#     percelen_alternatieven.append("percelen_{}".format(naam_alternatief))
#     print "Selectie van percelen gemaakt voor {}".format(naam_alternatief)

# # koppel per alternatief de dijkvakken aan de geselecteerde percelen
# for p_alternatief in percelen_alternatieven:
#     naam_alternatief_koppeling = "dv_{}".format(p_alternatief)
#     arcpy.SpatialJoin_analysis(p_alternatief, priovakken, naam_alternatief_koppeling, "JOIN_ONE_TO_ONE", "KEEP_ALL","","CLOSEST", "", "")
#     print "Selectie van percelen gekoppeld aan dijvakken voor {}".format(p_alternatief)

    
#     # overbouw naar excel
#     arrayMa = arcpy.da.FeatureClassToNumPyArray(naam_alternatief_koppeling, (vaknamen, eigenaar_veld_uniek))
#     dfMa = pd.DataFrame(arrayMa)
#     sortDfMa = dfMa.sort_values(by=[vaknamen],ascending=[True])
    




# bij elkaar vegen van alle alternatieven en identieke percelen verwijderen


    # grouped = sortDfMa.groupby(vaknamen)

    # # over iedere groep itereren
    # for group_name, df_group in grouped:

    #     print df_group

















    # with pd.ExcelWriter(output_excel+'sample.xlsx') as writer:  
    #     dfMa.to_excel(writer, sheet_name='x1')
    # For appending to the file, use the argument mode='a' in pd.ExcelWriter.

    # x2 = np.random.randn(100, 2)
    # df2 = pd.DataFrame(x2)
    # with pd.ExcelWriter('sample.xlsx', engine='openpyxl', mode='a') as writer:  
        # df2.to_excel(writer, sheet_name='x2')


 
















# split op basis van dijkvakken




# with arcpy.da.SearchCursor(priovakken,['SHAPE@',vaknamen]) as cursor:
#     for row in cursor:
        
#         id = row[1]
#         vaknaam = id

#         id = id.replace(" ","_")
#         id = id.replace("+","_")
#         id = id.replace("(","_")
#         id = id.replace(")","")
#         id = id.replace(",","")
#         id = id.replace("-","_")
#         id = id.replace("/","")
#         id = id.replace("__","_")

#         vaknaam_temp = id

    




#         trajectlijn = "priovak_{}".format(vaknaam_temp)

#         where = '"' + vaknamen + '" = ' + "'" + str(vaknaam) + "'"
#         arcpy.Select_analysis(priovakken, trajectlijn, where)
 



#         # selecteer maatregelvlakken binnen zone
#         arcpy.MakeFeatureLayer_management(maatregelvlakken, "temp_maatregelvlakken") 
#         arcpy.SelectLayerByLocation_management("temp_maatregelvlakken", "INTERSECT", trajectlijn, "10 Meters", "NEW_SELECTION", "NOT_INVERT")
#         arcpy.CopyFeatures_management("temp_maatregelvlakken", "test_selectie")

#         # selecteer percelen binnen zone maatregelvlak (10m)

#         break

#     # exporteer selectie naar excel (losse tab?)

