import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
import arcpy
import pandas as pd
import numpy as np
from scipy.interpolate import UnivariateSpline
import scipy.signal
# from rdp import rdp

arcpy.env.workspace = r'D:\Projecten\HDSR\data\test_batch.gdb'
arcpy.env.overwriteOutput = True

def average(lijst):
    return sum(lijst) / len(lijst)

stapgrootte_punten = 2
max_talud = 0.2
max_voorland = -75
min_voorland = -25
max_achterland = 10
min_achterland = 5
code = 'SUBSECT_ID'
invoer = 'punten_profielen_z_125E'


array = arcpy.da.FeatureClassToNumPyArray(invoer, ('OBJECTID','profielnummer',code, 'afstand', 'z_ahn'))
df = pd.DataFrame(array)
df2 = df.dropna()
sorted = df2.sort_values(['profielnummer', 'afstand'], ascending=[True, True])
grouped = sorted.groupby('profielnummer')

list_id_bik = []
list_id_buk = []
list_id_bit = []
# list_id_but = []

afstand_bik = 5
afstand_buk = -5
afstand_maxkruin = 0.2
for name, group in grouped:
    # maximale kruinhoogte
    max_kruin = max(group['z_ahn'])

    landzijde = group.sort_values(['afstand'], ascending=False) #afnemend, landzijde
    rivierzijde = group.sort_values(['afstand'], ascending=True) #toenemend, rivierzijde



    # bik
    for index, row in landzijde.iterrows():
        if row['z_ahn'] > max_kruin-afstand_maxkruin and row['afstand'] < afstand_bik and row['afstand']>0:
            x_bik = row['afstand']
            y_bik = row['z_ahn']
            list_id_bik.append(row['OBJECTID'])
            break


    # buk
    for index, row in rivierzijde.iterrows():
        if row['z_ahn'] > max_kruin-afstand_maxkruin and row['afstand']> afstand_buk and row['afstand'] <0:
            x_buk = row['afstand']
            y_buk = row['z_ahn']
            list_id_buk.append(row['OBJECTID'])
            break

    # # bit
    # # maaiveldhoogte achterland
    # mv_achterland_lijst = []
    # for index, row in landzijde.iterrows():
    #     if row['afstand'] > min_achterland and row['afstand'] < max_achterland :
    #         mv_achterland_lijst.append(row['z_ahn'])
    # mv_achterland = average(mv_achterland_lijst)
    # # print mv_achterland
    # row_iterator = rivierzijde.iterrows()
    # _, last = row_iterator.next()  # take first item from row_iterator
    # for i, row in row_iterator:
    #
    #     hoogte1 = last['z_ahn']
    #     hoogte2 = row['z_ahn']
    #     afstand1 = last['afstand']
    #     afstand2 = row['afstand']
    #     delta_h = abs(hoogte1 - hoogte2)
    #     delta_a = abs(afstand1 - afstand2)
    #     talud = delta_h / delta_a
    #     if afstand2 > 0 and afstand2 < max_achterland and hoogte2 < mv_achterland + 0.5 and talud < max_talud:
    #         x_bit = row['afstand']
    #         y_bit = row['z_ahn']
    #         list_id_bit.append(row['OBJECTID'])
    #         print row['afstand']
    #         break
    #     last = row

    # x1 = group['afstand']
    # y1 = group['z_ahn']
    #
    #
    #
    #
    #
    #
    #
    # fig = plt.figure(figsize=(25, 2))
    # ax = fig.add_subplot(111)
    # ax.plot(x1, y1, linewidth=2, color="red")
    #
    # try:
    #     x_bik
    #     ax.plot(x_bik, y_bik, 'ro', markersize=6)
    # except NameError:
    #     pass
    #
    # try:
    #     x_buk
    #     ax.plot(x_buk, y_buk, 'ro', markersize=6)
    # except NameError:
    #     pass
    # try:
    #     x_bit
    #     ax.plot(x_bit, y_bit, 'ro', markersize=6)
    # except NameError:
    #     pass
    # try:
    #     x_but
    #     ax.plot(x_but, y_but, 'ro', markersize=6)
    # except NameError:
    #     pass
    # plt.show()
    #
    #
    #
    #
    #
    #
    #
    # try:
    #     x_buk
    #     del x_buk, y_buk
    # except NameError:
    #     pass
    #
    # try:
    #     x_bik
    #     del x_bik, y_bik
    # except NameError:
    #     pass
    # try:
    #     x_but
    #     del x_but, y_but
    # except NameError:
    #     pass
    # try:
    #     x_bit
    #     del x_bit, y_bit
    # except NameError:
    #     pass




# wegschrijven naar gis

# binnenkruin
arcpy.MakeFeatureLayer_management(invoer, 'punten_binnenkruin_temp')
punten_bik = arcpy.SelectLayerByAttribute_management('punten_binnenkruin_temp', "ADD_TO_SELECTION","OBJECTID in (" + str(list_id_bik)[1:-1] + ")")
arcpy.CopyFeatures_management('punten_binnenkruin_temp', 'punten_binnenkruin')

# buitenkruin
arcpy.MakeFeatureLayer_management(invoer, 'punten_buitenkruin_temp')
punten_buk = arcpy.SelectLayerByAttribute_management('punten_buitenkruin_temp', "ADD_TO_SELECTION","OBJECTID in (" + str(list_id_buk)[1:-1] + ")")
arcpy.CopyFeatures_management('punten_buitenkruin_temp', 'punten_buitenkruin')



# arcpy.MakeFeatureLayer_management(invoer, 'punten_binnenteen_temp')
# punten_bit = arcpy.SelectLayerByAttribute_management('punten_binnenteen_temp', "ADD_TO_SELECTION",
#                                                      "OBJECTID in (" + str(list_id_bit)[1:-1] + ")")
# arcpy.CopyFeatures_management('punten_binnenteen_temp', 'punten_binnenteen')