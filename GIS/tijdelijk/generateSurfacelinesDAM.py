
import sys
sys.path.append('.')


import arcpy
import math
from arcpy.sa import *
import xlwt
import pandas as pd
from itertools import groupby
# uitzetten melding pandas
pd.set_option('mode.chained_assignment', None)
# from basisfuncties import*

arcpy.env.workspace = r'D:\Projecten\HDSR\2020\gisData\inputDAM.gdb'
arcpy.env.overwriteOutput = True


uitvoerpunten = "punten_profielen_z"


def generate_surfacelines(uitvoerpunten):

    # data inlezen
    baseDf = pd.DataFrame()
    inputArray = arcpy.da.FeatureClassToNumPyArray(uitvoerpunten, ('profielnummer','afstand','x','y','z_ahn'))
    inputDf = pd.DataFrame(inputArray)
    inputDf = inputDf.dropna()
    sortInputDf = inputDf.sort_values(by=['profielnummer','afstand'],ascending=[True,True])

    # groeperen per profielnummer

    grouped = sortInputDf.groupby('profielnummer')

    # kolommen, beginnen op 0
    countcolums = 0

    # over iedere groep itereren
    for group_name, df_group in grouped:
        
        # rijnummer, beginnen op 0
        countrows = 0

        for row_index, row in df_group.iterrows():
            x_column = "X{}".format(countrows)
            y_column = "Y{}".format(countrows)
            z_column = "Z{}".format(countrows)

            baseDf.loc[countcolums,'LOCATIONID'] = row[0] 
            baseDf.loc[countcolums, x_column]= row['x']
            baseDf.loc[countcolums, y_column]= row['y']
            baseDf.loc[countcolums, z_column]= row['z_ahn']

            countrows +=1
        countcolums += 1


    # wegschrijven data 
    # print df
    baseDf.set_index('LOCATIONID', inplace=True)
    # baseDf.to_excel(r'C:\Users\Vincent\Desktop\dam_pandas.xlsx')  
    baseDf.to_csv(r'C:\Users\Vincent\Desktop\dam_surfacelines.csv', sep=';',decimal='.')


generate_surfacelines(uitvoerpunten)