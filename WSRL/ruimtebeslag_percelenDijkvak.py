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


alternatieven = ["ma1_vlakken","ma2_vlakken","ma3_vlakken","ma4_vlakken","ma5_vlakken"]
# alternatieven = ["ma1_vlakken"]


percelen_alternatieven = []
eigenaar_veld_uniek = "eigenaar_uniek"
objectid_uniek = "objectid_uniek"
eigenaar_velden = ["NAAM","VOORN","VOORV","VOORL","STRAAT","HUISNR","POSTCODE","WOONPLAATS",eigenaar_veld_uniek]

dct_ma = {"ma1":[],"ma2":[],"ma3":[],"ma4":[],"ma5":[]}


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
    
    # vul lijst met unieke id's voor latere terugkoppeling
    list_ma = dct_ma[naam_alternatief]
    tempCursor = arcpy.da.UpdateCursor(naam_alternatief_gekoppeld, [naam_alternatief,objectid_uniek])
    for tRow in tempCursor:
        # tRow[0] = "ja"
      
        list_ma.append(tRow[1])

        tempCursor.updateRow(tRow)

    del tempCursor



# voeg alles samen
arcpy.Merge_management(percelen_alternatieven,"percelen_totaal")

# verwijder identieke percelen
arcpy.DeleteIdentical_management("percelen_totaal", objectid_uniek, "", "0")

# koppel aan dijkvak
arcpy.SpatialJoin_analysis("percelen_totaal", priovakken, "percelen_totaal_dv", "JOIN_ONE_TO_ONE", "KEEP_ALL","","CLOSEST", "", "")




# koppel terug in welk alternatief ieder perceel voorkomt
ma1_list =  dct_ma["ma1"]
ma2_list =  dct_ma["ma2"]
ma3_list =  dct_ma["ma3"]
ma4_list =  dct_ma["ma4"]
ma5_list =  dct_ma["ma5"]

ma1_uniek = list(dict.fromkeys(ma1_list))
ma2_uniek = list(dict.fromkeys(ma2_list))
ma3_uniek = list(dict.fromkeys(ma3_list))
ma4_uniek = list(dict.fromkeys(ma4_list))
ma5_uniek = list(dict.fromkeys(ma5_list))

tempCursor = arcpy.da.UpdateCursor("percelen_totaal_dv", [objectid_uniek,"ma1"])
for tRow in tempCursor:
    if int(tRow[0]) in ma1_uniek:
        tRow[1] = "ja"
    else:
        tRow[1] = "nee"

    tempCursor.updateRow(tRow)

del tempCursor

tempCursor = arcpy.da.UpdateCursor("percelen_totaal_dv", [objectid_uniek,"ma2"])
for tRow in tempCursor:
    if int(tRow[0]) in ma2_uniek:
        tRow[1] = "ja"
    else:
        tRow[1] = "nee"

    tempCursor.updateRow(tRow)

del tempCursor

tempCursor = arcpy.da.UpdateCursor("percelen_totaal_dv", [objectid_uniek,"ma3"])
for tRow in tempCursor:
    if int(tRow[0]) in ma3_uniek:
        tRow[1] = "ja"
    else:
        tRow[1] = "nee"

    tempCursor.updateRow(tRow)

del tempCursor

tempCursor = arcpy.da.UpdateCursor("percelen_totaal_dv", [objectid_uniek,"ma4"])
for tRow in tempCursor:
    if int(tRow[0]) in ma4_uniek:
        tRow[1] = "ja"
    else:
        tRow[1] = "nee"

    tempCursor.updateRow(tRow)

del tempCursor

tempCursor = arcpy.da.UpdateCursor("percelen_totaal_dv", [objectid_uniek,"ma5"])
for tRow in tempCursor:
    if int(tRow[0]) in ma5_uniek:
        tRow[1] = "ja"
    else:
        tRow[1] = "nee"

    tempCursor.updateRow(tRow)

del tempCursor

##


# overbouw naar excel
arrayMa = arcpy.da.FeatureClassToNumPyArray("percelen_totaal_dv", (vaknamen, eigenaar_veld_uniek,"ma1","ma2","ma3","ma4","ma5"))
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

   
    


    # drop unieke waardes gebaseerd op eigenaar
    df_uniek = df_group.drop_duplicates(subset=[eigenaar_veld_uniek])


    # velden eigenaren
    df_uniek['voorletter'] = df_uniek[eigenaar_veld_uniek].str.split(',').str[0]
    df_uniek['voorvoegsel'] = df_uniek[eigenaar_veld_uniek].str.split(',').str[1]
    df_uniek['achternaam'] = df_uniek[eigenaar_veld_uniek].str.split(',').str[2]
    df_uniek['straat'] = df_uniek[eigenaar_veld_uniek].str.split(',').str[3]
    df_uniek['huisnummer'] = df_uniek[eigenaar_veld_uniek].str.split(',').str[4]
    df_uniek['postcode'] = df_uniek[eigenaar_veld_uniek].str.split(',').str[5]
    df_uniek['woonplaats'] = df_uniek[eigenaar_veld_uniek].str.split(',').str[6]
   

    # print df_uniek

    # "None" vervangen door "nee"
    df_uniek = df_uniek.replace("None", "nee")

    df_uniek.to_excel("{}{}.xlsx".format(output_excel,vaknaam_temp),columns=["voorletter","voorvoegsel","achternaam",
    "straat","huisnummer","postcode","woonplaats","ma1","ma2","ma3","ma4","ma5"], index=False)
    





