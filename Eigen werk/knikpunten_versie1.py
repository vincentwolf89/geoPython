import arcpy
import pandas as pd
import numpy as np
import rdp
import matplotlib.pyplot as plt
import statsmodels.api as sm
# from scipy.signal import savgol_filter






arcpy.env.overwriteOutput = True
arcpy.env.workspace = 'C:/Users/vince/Desktop/GIS/profielscript_final.gdb'

# invoer = 'profielen_maatgevend_punten_z_join2'
invoer = 'profielen_maatgevend_punten_z_join2'

def average(lijst):
    return sum(lijst) / len(lijst)

def angle(directions):
    """
    Returns the angles between vectors.

    Parameters:
    dir is a 2D-array of shape (N,M) representing N vectors in M-dimensional space.

    The return value is a 1D-array of values of shape (N-1,), with each value
    between 0 and pi.

    0 implies the vectors point in the same direction
    pi/2 implies the vectors are orthogonal
    pi implies the vectors point in opposite directions
    """
    dir2 = directions[1:]
    dir1 = directions[:-1]
    return np.arccos((dir1*dir2).sum(axis=1)/(
        np.sqrt((dir1**2).sum(axis=1)*(dir2**2).sum(axis=1))))

tolerance = 0.20
min_angle = np.pi*0.02




array = arcpy.da.FeatureClassToNumPyArray(invoer, ('TARGET_FID','koppel_id', 'afstand', 'z_ahn'))

df = pd.DataFrame(array)

sort = df.sort(['afstand'])

grouped = df.groupby('koppel_id')

list_id_bik = []
list_id_bit = []
list_id_buk = []
list_id_but = []

dct = {}

for name, group in grouped:

    aflopend = group.sort(['afstand'], ascending=False)
    oplopend = group.sort(['afstand'], ascending=True)

    x = oplopend['afstand'].tolist()
    z = oplopend['z_ahn'].tolist()
# zoek de binnenkruin

    x_bk = []
    z_bk = []
    list_ahn = []
    for index, row in oplopend.iterrows():
        z_ahn = row['z_ahn']
        list_ahn.append(z_ahn)
#
    maximum = (max(list_ahn))
    maximum2 = maximum-0.3
    maximum3 = maximum-1.5

    for index, row in oplopend.iterrows():
        afstand = row['afstand']
        z_ahn = row['z_ahn']
        # print row['afstand']

        if afstand >-12 and afstand <-3 and z_ahn > maximum2:
            x_bik, y_bik = afstand, z_ahn
            # print "poging 1"
            break

    try:
        x_bik
    except NameError:
        for index, row in group.iterrows():
            afstand = row['afstand']
            z_ahn = row['z_ahn']
            # print row['afstand']

            if afstand > -12 and afstand < -3 and z_ahn > maximum3:
                x_bik, y_bik = afstand, z_ahn
                # print "poging 2"
                break



    # print x_bik


    # zoek de buitenkruin

    list_ahn = []
    for index, row in aflopend.iterrows():
        z_ahn = row['z_ahn']
        list_ahn.append(z_ahn)
    #
    maximum = (max(list_ahn))
    maximum2 = maximum - 0.3
    maximum3 = maximum - 1.5

    for index, row in aflopend.iterrows():
        afstand = row['afstand']
        z_ahn = row['z_ahn']
        # print row['afstand']

        if afstand > -3 and afstand < 7 and z_ahn > maximum2:
            x_buk, y_buk = afstand, z_ahn
            # print "poging 1"
            break

    try:
        x_buk
    except NameError:
        for index, row in group.iterrows():
            afstand = row['afstand']
            z_ahn = row['z_ahn']
            # print row['afstand']

            if afstand > -3 and afstand < 7 and z_ahn > maximum3:
                x_buk, y_buk = afstand, z_ahn
                # print "poging 2"
                break
            else:
                print "error buitenkruin"+str(name)
                break
    # print x_buk

    # zoek de buitenteen

    list_voorland = []
    for index, row in oplopend.iterrows():
        if np.isnan(row['z_ahn']):
            pass
        else:
            z_ahn = row['z_ahn']

        if row['afstand'] > 20 and row['afstand'] < 70:
            z_voorland = row['z_ahn']
            list_voorland.append(z_voorland)
# -----------------------------------
    if len(list_voorland) == 0:
        list_voorland = [1,1,1]
# -----------------------------------
    voorlandhoogte = average(list_voorland)
    voorland1 = voorlandhoogte + 0.8
    # maximum3 = maximum - 1.5

    for index, row in oplopend.iterrows():
        afstand = row['afstand']
        z_ahn = row['z_ahn']
        # print row['afstand']

        if afstand > 8 and afstand < 25 and z_ahn < voorland1:
            x_but, y_but = afstand, z_ahn
            # print "poging 1"
            break


    try:
        x_but
    except NameError:
        print "error buitenteen"+str(name)


    # zoek de binnenteen

    list_achterland = []
    for index, row in aflopend.iterrows():
        z_ahn = row['z_ahn']
        if row['afstand'] > -100 and row['afstand'] < -30:
            z_achterland = row['z_ahn']
            list_achterland.append(z_achterland)
    # -----------------------------------
    if len(list_achterland) == 0:
        list_achterland = [1, 1, 1]
    # -----------------------------------
    achterlandhoogte = average(list_achterland)
    achterland1 = achterlandhoogte + 0.4
    # maximum3 = maximum - 1.5

    for index, row in aflopend.iterrows():
        afstand = row['afstand']
        z_ahn = row['z_ahn']
        # print row['afstand']

        if afstand > -50 and afstand < -8 and z_ahn < achterland1:
            x_bit, y_bit = afstand, z_ahn
            # print "poging 1"
            break

    try:
        x_bit
    except NameError:
        print "error_x_bit" + str(name)






























    try:
        x_bik
    except NameError:
        x_bik = None
    try:
        x_buk
    except NameError:
        x_buk = None
    try:
        x_but
    except NameError:
        x_but = None
    try:
        x_bit
    except NameError:
        x_bit = None

    if x_bik is not None and x_buk is not None and x_but is not None and x_bit is not None:


# -------------------------------TESTCODE
        list_x_bit_gem = []
        key = name
        dct[name] = (name, x_bit,y_bit)
        for key, val in dct.items():
            if key == name-1:
                waarde1 = val[1]
                list_x_bit_gem.append(waarde1)

            else:
                waarde1 = x_bit
                list_x_bit_gem.append(waarde1)

        for key, val in dct.items():
            if key == name-2:
                waarde2 = val[1]
                list_x_bit_gem.append(waarde2)
            else:
                waarde2 = x_bit
                list_x_bit_gem.append(waarde2)

        for key, val in dct.items():
            if key == name-3:
                waarde3 = val[1]
                list_x_bit_gem.append(waarde3)
            else:
                waarde3 = x_bit
                list_x_bit_gem.append(waarde3)

        for key, val in dct.items():
            if key == name-4:
                waarde4 = val[1]
                list_x_bit_gem.append(waarde4)
            else:
                waarde4 = x_bit
                list_x_bit_gem.append(waarde4)

        for key, val in dct.items():
            if key == name-5:
                waarde5 = val[1]
                list_x_bit_gem.append(waarde5)
            else:
                waarde5 = x_bit
                list_x_bit_gem.append(waarde5)

        gemiddelde_binnenteen = round(average(list_x_bit_gem))
        print gemiddelde_binnenteen

        # print gemiddelde_binnenteen
        # print len(list_x_bit_gem)
        # x_bit = gemiddelde_binnenteen

        for index, row in aflopend.iterrows():
            afstand = row['afstand']
            z_ahn = row['z_ahn']
            if afstand == gemiddelde_binnenteen or afstand == (gemiddelde_binnenteen-1):
                print afstand, name
                y_bit_gem = z_ahn
                x_bit_gem = afstand

                break





#--------------------------------

        for index, row in group.iterrows():
            if row['afstand'] == x_bik:
                id_bik = row['TARGET_FID']
                list_id_bik.append(id_bik)
#
        for index, row in group.iterrows():
            if row['afstand'] == x_buk:
                id_buk = row['TARGET_FID']
                list_id_buk.append(id_buk)
#
        for index, row in group.iterrows():
            if row['afstand'] == x_but:
                id_but = row['TARGET_FID']
                list_id_but.append(id_but)

        for index, row in group.iterrows():
            if row['afstand'] == x_bit_gem:
                id_bit = row['TARGET_FID']
                list_id_bit.append(id_bit)


        # fig = plt.figure(figsize=(25, 2))
        # ax = fig.add_subplot(111)
        # #
        # #     ax.plot(x_bit,y_bit, 'bo')
        #
        # ax.plot(x_bik, y_bik, 'bo')
        # ax.plot(x_buk, y_buk, 'bo')
        # ax.plot(x_but, y_but, 'bo')
        # ax.plot(x_bit, y_bit, 'bo')
        # ax.plot(x_bit_gem, y_bit_gem, 'r+')
        # #     ax.plot(x_but,y_but, 'bo')
        # #
        # #
        # ax.plot(x, z, 'b-', label='original path')
        # plt.show()





        del x_bik, y_bik, x_buk, y_buk, x_but, y_but, x_bit, y_bit, x_bit_gem, y_bit_gem

    else:
        pass






arcpy.MakeFeatureLayer_management(invoer, 'punten_binnenkruin_temp')
punten_bik = arcpy.SelectLayerByAttribute_management('punten_binnenkruin_temp', "ADD_TO_SELECTION", "OBJECTID in (" + str(list_id_bik)[1:-1] + ")")
arcpy.CopyFeatures_management('punten_binnenkruin_temp', 'punten_binnenkruin')
# #
arcpy.MakeFeatureLayer_management(invoer, 'punten_buitenkruin_temp')
punten_buk = arcpy.SelectLayerByAttribute_management('punten_buitenkruin_temp', "ADD_TO_SELECTION", "OBJECTID in (" + str(list_id_buk)[1:-1] + ")")
arcpy.CopyFeatures_management('punten_buitenkruin_temp', 'punten_buitenkruin')
# #
arcpy.MakeFeatureLayer_management(invoer, 'punten_buitenteen_temp')
punten_but = arcpy.SelectLayerByAttribute_management('punten_buitenteen_temp', "ADD_TO_SELECTION", "OBJECTID in (" + str(list_id_but)[1:-1] + ")")
arcpy.CopyFeatures_management('punten_buitenteen_temp', 'punten_buitenteen')

arcpy.MakeFeatureLayer_management(invoer, 'punten_binnenteen_temp')
punten_bit = arcpy.SelectLayerByAttribute_management('punten_binnenteen_temp', "ADD_TO_SELECTION", "OBJECTID in (" + str(list_id_bit)[1:-1] + ")")
arcpy.CopyFeatures_management('punten_binnenteen_temp', 'punten_binnenteen')