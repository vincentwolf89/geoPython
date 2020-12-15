
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


uitvoerpunten = "testpunten"



df = pd.DataFrame()
arrayTest = arcpy.da.FeatureClassToNumPyArray(uitvoerpunten, ('profielnummer','afstand','x','y','z_ahn'))
dfTest = pd.DataFrame(arrayTest)
sortTest = dfTest.sort_values(by=['profielnummer','afstand'],ascending=[True,True])

grouped = sortTest.groupby('profielnummer')
countcolums = 0
# iterate over each group
for group_name, df_group in grouped:
    
    countrows = 0

    for row_index, row in df_group.iterrows():
        x_column = "X{}".format(countrows)
        y_column = "Y{}".format(countrows)
        z_column = "Z{}".format(countrows)

        df.loc[countcolums,'LOCATIONID'] = row[0] 
        df.loc[countcolums, x_column]= row['x']
        df.loc[countcolums, y_column]= row['y']
        df.loc[countcolums, z_column]= row['z_ahn']

        countrows +=1
    countcolums += 1

# print df
df.set_index('LOCATIONID', inplace=True)
df.to_excel(r'C:\Users\Vincent\Desktop\dam_pandas.xlsx')  