



import arcpy
import math
from arcpy.sa import *
import xlwt
import pandas as pd
from itertools import groupby
import numpy as np
# uitzetten melding pandas
pd.set_option('mode.chained_assignment', None)
# from basisfuncties import*

arcpy.env.workspace = r'D:\Projecten\HDSR\2020\gisData\inputDAM.gdb'
arcpy.env.overwriteOutput = True





uitvoerpunten = "cpointsPilot"

def change_cpointName(uitvoerpunten):
    # naamgeving cpoints veranderen voor dam
    tempCursor = arcpy.da.UpdateCursor(uitvoerpunten,['cPoint'])

    for tRow in tempCursor:
        
        if tRow[0] == "binnenteen":
            tRow[0] = "Teen dijk binnenwaarts"

        if tRow[0] == "buitenteen":
            tRow[0]= "Teen dijk buitenwaarts"
            
        if tRow[0] == "binnenkruin":
            tRow[0] = "Kruin binnentalud"

        if tRow[0] == "buitenkruin":
            tRow[0] = "Kruin buitentalud"

        if tRow[0] == "bovenkantBermBinnen":
            tRow[0] = "Insteek binnenberm"

        if tRow[0] == "bovenkantBermBuiten":
            tRow[0] = "Insteek buitenberm"

        if tRow[0] == "onderkantBermBinnen":
            tRow[0] = "Kruin binnenberm"

        if tRow[0] == "onderkantBermBuiten":
            tRow[0] = "Kruin buitenberm"

        if tRow[0] == "insteek_sloot_polderzijde_binnen":
            tRow[0] = "Insteek sloot polderzijde"

        if tRow[0] == "insteek_sloot_dijkzijde_binnen":
            tRow[0] = "Insteek sloot dijkzijde"

        if tRow[0] == "slootbodem_polderzijde_binnen":
            tRow[0] = "Slootbodem polderzijde"

        if tRow[0] == "slootbodem_dijkzijde_binnen":
            tRow[0] = "Slootbodem dijkzijde"
        

        # verwijder slootdelen buitenzijde


        if tRow[0] == "insteek_sloot_polderzijde_buiten":
            tempCursor.deleteRow()

        if tRow[0] == "insteek_sloot_dijkzijde_buiten":
            tempCursor.deleteRow()

        if tRow[0] == "slootbodem_polderzijde_buiten":
            tempCursor.deleteRow()

        if tRow[0] == "slootbodem_dijkzijde_buiten":
            tempCursor.deleteRow()
        
        tempCursor.updateRow(tRow)


        





def generate_cpoints(uitvoerpunten):


    # data inlezen
    baseDf = pd.DataFrame()
    inputArray = arcpy.da.FeatureClassToNumPyArray(uitvoerpunten, ('profielnummer','cPoint','afstand','x','y','z_ahn'))
    inputDf = pd.DataFrame(inputArray)
    inputDf = inputDf.dropna()
    sortInputDf = inputDf.sort_values(by=['profielnummer','afstand'],ascending=[True,True])





    # basiskolommen inbouwen
    basiskolommen = ["Maaiveld binnenwaarts","Insteek sloot polderzijde","Slootbodem polderzijde","Slootbodem dijkzijde","Insteek sloot dijkzijde",
    "Teen dijk binnenwaarts","Kruin binnenberm","Insteek binnenberm","Kruin binnentalud",
    "Verkeersbelasting kant binnenwaarts","Verkeersbelasting kant buitenwaarts","Kruin buitentalud",
    "Insteek buitenberm","Kruin buitenberm","Teen dijk buitenwaarts","Insteek geul","Teen geul","Maaiveld buitenwaarts"]


    baseColumnsTotal = []

    for column in basiskolommen:
        x_column = "X_{}".format(column)
        y_column = "Y_{}".format(column)
        z_column = "Z_{}".format(column)

        baseDf.loc[0,'LOCATIONID'] = None 
        baseDf.loc[0, x_column]= None
        baseDf.loc[0, y_column]= None
        baseDf.loc[0, z_column]= None




        baseColumnsTotal.append(x_column)
        baseColumnsTotal.append(y_column)
        baseColumnsTotal.append(z_column)



    # groeperen per profielnummer
    grouped = sortInputDf.groupby('profielnummer')

    # over iedere groep itereren en vullen met beschikbare data
    countrows = 0
    for group_name, df_group in grouped:
        
        # rijnummer, beginnen op 0
        

        for row_index, row in df_group.iterrows():
            x_column = "X_{}".format(row['cPoint'])
            y_column = "Y_{}".format(row['cPoint'])
            z_column = "Z_{}".format(row['cPoint'])

            baseDf.loc[countrows,'LOCATIONID'] = row[0] 
            baseDf.loc[countrows, x_column]= row['x']
            baseDf.loc[countrows, y_column]= row['y']
            baseDf.loc[countrows, z_column]= row['z_ahn']

            
        countrows +=1






    # check of iedere cel gevuld is, anders vullen met -1000
    for row_index, row in baseDf.iterrows():

        for baseColumn in baseColumnsTotal:
            test = row[baseColumn]
            if pd.notnull(test):
                pass
            else:
                baseDf.loc[row_index, baseColumn] = -1








    # wegschrijven data 
    baseDf.set_index('LOCATIONID', inplace=True) 
    baseDf.to_csv(r'C:\Users\Vincent\Desktop\dam_cpoints.csv', sep=';',decimal='.')



change_cpointName(uitvoerpunten)
generate_cpoints(uitvoerpunten)