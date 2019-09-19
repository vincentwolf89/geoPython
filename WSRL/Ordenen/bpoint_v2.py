import arcpy
import pandas as pd
import numpy as np
from rdp import rdp
import matplotlib.pyplot as plt
import statsmodels.api as sm

# from scipy.signal import savgol_filter


arcpy.env.overwriteOutput = True
arcpy.env.workspace = 'C:/Users/vince/Desktop/GIS/profielscript_final.gdb'

# invoer = 'testset_25m'
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
    return np.arccos((dir1 * dir2).sum(axis=1) / (
        np.sqrt((dir1 ** 2).sum(axis=1) * (dir2 ** 2).sum(axis=1))))


# tolerance = 0.20
# min_angle = np.pi*0.02


array = arcpy.da.FeatureClassToNumPyArray(invoer, ('TARGET_FID', 'profielnummer', 'afstand', 'z_ahn'))

df = pd.DataFrame(array)

sort = df.sort(['afstand'])

grouped = df.groupby('profielnummer')

list_id_bit = []
list_id_bik = []
list_id_buk = []
list_id_but = []
list_voorland_totaal = []
list_achterland_totaal = []
list_kruinhoogte_totaal = []

for name, group in grouped:

    aflopend = group.sort(['afstand'], ascending=False)
    oplopend = group.sort(['afstand'], ascending=True)

    list_x = []
    list_y = []

    achterland =[]

    for index, row in group.iterrows():
        if np.isnan(row['z_ahn']):
            pass
        else:
            x = row['afstand']
            y = row['z_ahn']
            list_x.append(x)
            list_y.append(y)

    for index, row in group.iterrows():
        if np.isnan(row['z_ahn']):
            pass
        else:
            if row['afstand'] > -100 and row['afstand'] < -30:
                achterland.append(row['z_ahn'])
            else:
                pass


    points = np.c_[list_x, list_y]

    simplified_trajectory = rdp(points, epsilon=0.3)
    sx, sy = simplified_trajectory.T


    # Define a minimum angle to treat change in direction
    # as significant (valuable turning point).
    min_angle = np.pi / 60  # 35

    # Compute the direction vectors on the simplified_trajectory.
    directions = np.diff(simplified_trajectory, axis=0)
    theta = angle(directions)

    # Select the index of the points with the greatest theta.
    # Large theta is associated with greatest change in direction.
    idx = np.where(theta > min_angle)[0] + 1


    # bepaal gemiddelde hoogtes voor drie locaties
    gem_achterland = []
    gem_voorland = []
    gem_kruin = []


    # achterland
    for index, row in oplopend.iterrows():
        if np.isnan(row['z_ahn']):
            pass
        else:
            afstand_achterland = row['afstand']
            if afstand_achterland > -70 and afstand_achterland < -30:
                gem_achterland.append(row['z_ahn'])
            else:
                pass

    # voorland
    for index, row in oplopend.iterrows():
        if np.isnan(row['z_ahn']):
            pass
        else:
            afstand_voorland = row['afstand']
            if afstand_voorland > 15 and afstand_voorland < 60:
                gem_voorland.append(row['z_ahn'])
            else:
                pass

    #kruin
    for index, row in oplopend.iterrows():
        afstand_kruin = row['afstand']
        if afstand_kruin > -8 and afstand_kruin < 1:
            gem_kruin.append(row['z_ahn'])
        else:
            pass

    if not gem_achterland:
        gem_achterland_hoogte = average(list_achterland_totaal) # neem gemiddelde van alle profielen
    else:
        gem_achterland_hoogte = average(gem_achterland) #bepaal gemiddelde hoogte per profiel



    if not gem_voorland:
        gem_voorland_hoogte = average(list_voorland_totaal)
    else:
        gem_voorland_hoogte = average(gem_voorland)

    if not gem_kruin:
        gem_kruinhoogte = average(list_kruinhoogte_totaal)
    else:
        gem_kruinhoogte = average(gem_kruin)


    list_achterland_totaal.append(gem_achterland_hoogte)
    list_voorland_totaal.append(gem_voorland_hoogte)
    list_kruinhoogte_totaal.append(gem_kruinhoogte)





    # maak nieuw dataframe aan op basis van karakteristieke punten RDP
    totaal_afstand = []
    totaal_hoogte = []

    for item in np.nditer(sx):
        if np.isnan(item):
            pass
        else:
            for index, row in oplopend.iterrows():
                afstand = row['afstand']
                hoogte = row['z_ahn']
                if item == afstand:
                    totaal_afstand.append(afstand)
                    totaal_hoogte.append(row['z_ahn'])

    totaal_df = pd.DataFrame(
        {'afstand': totaal_afstand,
         'hoogte': totaal_hoogte})

    # sorteer dataframes om in verschillende volgordes over dijk te lopen
    totaal_df_sort = totaal_df.sort(['afstand'], ascending=False)
    totaal_df_sort_2 = totaal_df.sort(['afstand'], ascending=True)


    # bepaal binnenteen
    for index, row in totaal_df_sort.iterrows():
        afstand = row['afstand']
        hoogte = row['hoogte']
        if afstand < -15 and hoogte < gem_achterland_hoogte + 1:
            x_bit = afstand
            y_bit = hoogte
            break

    # bepaal buitenteen
    for index, row in totaal_df_sort_2.iterrows():
        afstand = row['afstand']
        hoogte = row['hoogte']
        if afstand > 5 and hoogte < gem_voorland_hoogte+1:
            x_but = afstand
            y_but = hoogte
            break

    # bepaal binnenkruin
    for index, row in totaal_df_sort_2.iterrows():
        afstand = row['afstand']
        hoogte = row['hoogte']
        if afstand > -20 and hoogte > gem_kruinhoogte -1:
            x_bik = afstand
            y_bik = hoogte
            break

    #b bepaal buitenkruin
    for index, row in totaal_df_sort.iterrows():
        afstand = row['afstand']
        hoogte = row['hoogte']
        if afstand < 3 and hoogte > gem_kruinhoogte -1:
            x_buk = afstand
            y_buk = hoogte
            break





    # plotsectie

    fig = plt.figure(figsize=(25, 2))
    ax = fig.add_subplot(111)
    ax.plot(list_x,list_y)
    ax.plot(sx, sy, 'gx-', label='simplified trajectory')
    ax.plot(x_bit, y_bit, 'bo')
    ax.plot(x_but, y_but, 'bo')
    ax.plot(x_bik, y_bik, 'bo')
    ax.plot(x_buk, y_buk, 'bo')
    # ax.plot(sx[idx], sy[idx], 'ro', markersize=7, label='turning points')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend(loc='best')
    plt.show()




    # check voor fouten
    try:
        x_bit, y_bit, x_bik, y_bik, x_but, y_but, x_buk ,y_buk

    except NameError:
        x_bit = None
        y_bit = None
        x_bik = None
        y_bik = None
        x_but = None
        y_but = None
        x_buk = None
        y_buk = None

    if x_bit is not None:
        for index, row in group.iterrows():
            afstand = row['afstand']
            if afstand == x_bit:
                id_bit = row['TARGET_FID']
                list_id_bit.append(id_bit)
            if afstand == x_bik:
                id_bik = row['TARGET_FID']
                list_id_bik.append(id_bik)
            if afstand == x_buk:
                id_buk = row['TARGET_FID']
                list_id_buk.append(id_buk)
            if afstand == x_but:
                id_but = row['TARGET_FID']
                list_id_but.append(id_but)

    print "Profiel "+str(name)+" is klaar"

    # verwijder waardes
    del x_bit, y_bit, x_but, y_but, x_bik, y_bik, x_buk, y_buk


# export naar GIS
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