import os
import arcpy
import pandas as pd

arcpy.env.workspace = r"D:\Projecten\WSRL\sterreschans_heteren\GIS\data.gdb"

profielen = "profielen_totaal"
buitenPunten = "buitentalud_profielen_totaal_puntenz"

dfProfiles = pd.DataFrame() 
dfProfiles.loc[0, "mean_angle"]= None


arrayProfile = arcpy.da.FeatureClassToNumPyArray(buitenPunten, ['profielnum','RASTERVALU'])
inputDf = pd.DataFrame(arrayProfile)

inputDf = inputDf.dropna()

sortInputDf = inputDf.sort_values(by=['profielnum'],ascending=[True])

grouped = sortInputDf.groupby('profielnum')

for group_name, df_group in grouped:

    mean_angle = df_group['RASTERVALU'].mean()
    
    profielnr = group_name

    print profielnr, mean_angle
    dfProfiles.loc[profielnr] = mean_angle



tempCursor = arcpy.da.UpdateCursor(profielen, ['profielnum','slope'])
for row in tempCursor:
    profielnummer = int(row[0])
    mean_angle = dfProfiles.loc[profielnummer]['mean_angle']

    row[1] = round(mean_angle,2)
    tempCursor.updateRow(row)

del tempCursor


