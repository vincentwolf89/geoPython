import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
import arcpy
import pandas as pd
import numpy as np
from scipy.interpolate import UnivariateSpline
import scipy.signal
from rdp import rdp

stapgrootte_punten = 0.5
max_talud = 0.2

max_voorland = -75
min_voorland = -25
max_achterland = 75
min_achterland = 25



def average(lijst):
    return sum(lijst) / len(lijst)



arcpy.env.workspace = r'D:\Projecten\WSRL\temp_sh.gdb'
arcpy.env.overwriteOutput = True


invoer = 'punten_profielen_z'


array = arcpy.da.FeatureClassToNumPyArray(invoer, ('OBJECTID','profielnummer','dijktraject', 'afstand', 'z_ahn'))
df = pd.DataFrame(array)
df2 = df.dropna()
sorted = df2.sort_values(['profielnummer', 'afstand'], ascending=[True, True])
grouped = sorted.groupby('profielnummer')

list_id_bik = []
list_id_buk = []
list_id_bit = []
list_id_but = []
for name, group in grouped:









    # maximale hoogte
    max_kruin = max(group['z_ahn'])



    landzijde = group.sort_values(['afstand'], ascending=False) #afnemend, landzijde

    rivierzijde = group.sort_values(['afstand'], ascending=True) #toenemend, rivierzijde

    # maaiveldhoogte achterland
    mv_achterland_lijst = []
    for index, row in landzijde.iterrows():
        if row['afstand'] > min_achterland and row['afstand'] < max_achterland :
            mv_achterland_lijst.append(row['z_ahn'])

    if mv_achterland_lijst:        
        mv_achterland = average(mv_achterland_lijst)
    else:
        break
    # print mv_achterland


    landzijde = group.sort_values(['afstand'], ascending=False) #afnemend, landzijde

    rivierzijde = group.sort_values(['afstand'], ascending=True) #toenemend, rivierzijde

    # maaiveldhoogte voorland
    mv_voorland_lijst = []
    for index, row in rivierzijde.iterrows():
        if row['afstand'] > max_voorland and row['afstand'] < min_voorland:
            mv_voorland_lijst.append(row['z_ahn'])
    mv_voorland = average(mv_achterland_lijst)
    # print mv_achterland

    # bik
    for index, row in landzijde.iterrows():
        if row['z_ahn'] > max_kruin-0.5:
            x_bik = row['afstand']
            y_bik = row['z_ahn']
            list_id_bik.append(row['OBJECTID'])
            break


    # buk
    for index, row in rivierzijde.iterrows():
        if row['z_ahn'] > max_kruin-0.5:
            x_buk = row['afstand']
            y_buk = row['z_ahn']
            list_id_buk.append(row['OBJECTID'])
            break

    # bit
    row_iterator = rivierzijde.iterrows()
    _, last = row_iterator.next()  # take first item from row_iterator
    for i, row in row_iterator:

        hoogte1 = last['z_ahn']
        hoogte2 = row['z_ahn']
        afstand1 = last['afstand']
        afstand2 = row['afstand']
        delta_h = abs(hoogte1-hoogte2)
        delta_a = abs(afstand1-afstand2)
        talud = delta_h/delta_a
        if afstand2 > 0 and hoogte2 < mv_achterland+0.5 and talud < max_talud:
            x_bit = row['afstand']
            y_bit = row['z_ahn']
            list_id_bit.append(row['OBJECTID'])
            print row['afstand']
            break
        last = row

    # but
    row_iterator2 = landzijde.iterrows()
    _, last = row_iterator2.next()  # take first item from row_iterator
    for i, row in row_iterator2:

        hoogte1 = last['z_ahn']
        hoogte2 = row['z_ahn']
        afstand1 = last['afstand']
        afstand2 = row['afstand']
        delta_h = abs(hoogte1-hoogte2)
        delta_a = abs(afstand1-afstand2)
        talud = delta_h/delta_a
        if afstand2 < 0 and hoogte2 < mv_voorland+1 and talud < max_talud and afstand2>-40:
            x_but = row['afstand']
            y_but = row['z_ahn']
            print row['afstand']
            list_id_but.append(row['OBJECTID'])
            break
        last = row




    x1 = group['afstand']
    y1 = group['z_ahn']







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







    try:
        x_buk
        del x_buk, y_buk
    except NameError:
        pass

    try:
        x_bik
        del x_bik, y_bik
    except NameError:
        pass
    try:
        x_but
        del x_but, y_but
    except NameError:
        pass
    try:
        x_bit
        del x_bit, y_bit
    except NameError:
        pass





arcpy.MakeFeatureLayer_management(invoer, 'punten_binnenkruin_temp')
punten_bik = arcpy.SelectLayerByAttribute_management('punten_binnenkruin_temp', "ADD_TO_SELECTION",
                                                     "OBJECTID in (" + str(list_id_bik)[1:-1] + ")")
arcpy.CopyFeatures_management('punten_binnenkruin_temp', 'punten_binnenkruin')
# #
arcpy.MakeFeatureLayer_management(invoer, 'punten_buitenkruin_temp')
punten_buk = arcpy.SelectLayerByAttribute_management('punten_buitenkruin_temp', "ADD_TO_SELECTION",
                                                     "OBJECTID in (" + str(list_id_buk)[1:-1] + ")")
arcpy.CopyFeatures_management('punten_buitenkruin_temp', 'punten_buitenkruin')
# #
arcpy.MakeFeatureLayer_management(invoer, 'punten_buitenteen_temp')
punten_but = arcpy.SelectLayerByAttribute_management('punten_buitenteen_temp', "ADD_TO_SELECTION",
                                                     "OBJECTID in (" + str(list_id_but)[1:-1] + ")")
arcpy.CopyFeatures_management('punten_buitenteen_temp', 'punten_buitenteen')

arcpy.MakeFeatureLayer_management(invoer, 'punten_binnenteen_temp')
punten_bit = arcpy.SelectLayerByAttribute_management('punten_binnenteen_temp', "ADD_TO_SELECTION",
                                                     "OBJECTID in (" + str(list_id_bit)[1:-1] + ")")
arcpy.CopyFeatures_management('punten_binnenteen_temp', 'punten_binnenteen')

