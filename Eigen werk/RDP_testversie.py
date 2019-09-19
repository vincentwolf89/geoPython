import arcpy
import pandas as pd
import numpy as np
import rdp
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy.signal import savgol_filter






arcpy.env.overwriteOutput = True
arcpy.env.workspace = 'C:/Users/vince/Desktop/GIS/profielscript_final.gdb'

invoer = 'profielen_maatgevend_punten_z_join2'


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

grouped = sort.groupby('koppel_id')

list_id_bt = []
list_id_bk = []
list_id_buk = []
list_id_but = []

for name, group in grouped:
    x = group['afstand'].tolist()
    z = group['z_ahn'].tolist()
    # print type(x)



# zoek de binnenteen
    x_bt = []
    z_bt = []

    for index, row in group.iterrows():
        afstand = row['afstand']
        zb = row['z_ahn']

        if afstand > -50 and afstand <-10:
            # print row['afstand'], row['z_ahn']
            xbt, zbt = row['afstand'], row['z_ahn']
            x_bt.append(xbt), z_bt.append(zbt)

    points_binnenteen = np.c_[x_bt, z_bt]
    simplified_bt = np.array(rdp.rdp(points_binnenteen.tolist(), tolerance))
    # print simplified
    sx_bt, sy_bt = simplified_bt.T
    #print sx
    # compute the direction vectors on the simplified curve
    directions = np.diff(simplified_bt, axis=0)
    theta = angle(directions)
    # Select the index of the points with the greatest theta
    # Large theta is associated with greatest change in direction.
    idx_bt = np.where(theta > min_angle)[0] + 1

    binnenteen = sx_bt[1]

    for index, row in group.iterrows():
        if row['afstand'] == binnenteen:
            id_bt = row['TARGET_FID']
            list_id_bt.append(id_bt)
            binnenteen_y = row['z_ahn']

# zoek de binnenkruin
    x_bk = []
    z_bk = []

    for index, row in group.iterrows():
        afstand = row['afstand']
        # zb = row['z_ahn']

        if afstand > -17 and afstand <-5:
            # print row['afstand'], row['z_ahn']
            xbk, zbk = row['afstand'], row['z_ahn']
            x_bk.append(xbk), z_bk.append(zbk)

    points_binnenkruin = np.c_[x_bk, z_bk]
    simplified_bk = np.array(rdp.rdp(points_binnenkruin.tolist(), tolerance))
    # print simplified
    sx_bk, sy_bk = simplified_bk.T
    #print sx
    # compute the direction vectors on the simplified curve
    directions = np.diff(simplified_bk, axis=0)
    theta = angle(directions)
    # Select the index of the points with the greatest theta
    # Large theta is associated with greatest change in direction.
    idx_bk = np.where(theta > min_angle)[0] + 1

    binnenkruin = sx_bk[1]



    for index, row in group.iterrows():
        if row['afstand'] == binnenkruin:
            id_bk = row['TARGET_FID']
            list_id_bk.append(id_bk)

            binnenkruin_y = row['z_ahn']


# zoek de buitenkruin
    x_buk = []
    z_buk = []

    for index, row in group.iterrows():
        afstand = row['afstand']
        # zbuk = row['z_ahn']

        if afstand > -6 and afstand < 3:
            # print row['afstand'], row['z_ahn']
            xbuk, zbuk = row['afstand'], row['z_ahn']
            x_buk.append(xbuk), z_buk.append(zbuk)

    points_buitenkruin = np.c_[x_buk, z_buk]
    simplified_buk = np.array(rdp.rdp(points_buitenkruin.tolist(), tolerance))
    # print simplified
    sx_buk, sy_buk = simplified_buk.T
    #print sx
    # compute the direction vectors on the simplified curve
    directions = np.diff(simplified_buk, axis=0)
    theta = angle(directions)
    # Select the index of the points with the greatest theta
    # Large theta is associated with greatest change in direction.
    idx_buk = np.where(theta > min_angle)[0] + 1

    buitenkruin = sx_buk[1]

    for index, row in group.iterrows():
        if row['afstand'] == buitenkruin:
            id_buk = row['TARGET_FID']
            list_id_buk.append(id_buk)

            buitenkruin_y = row['z_ahn']

# zoek de buitenteen
    x_but = []
    z_but = []

    for index, row in group.iterrows():
        afstand = row['afstand']
        # zbuk = row['z_ahn']

        if afstand > 5 and afstand < 15:
            # print row['afstand'], row['z_ahn']
            xbut, zbut = row['afstand'], row['z_ahn']
            x_but.append(xbut), z_but.append(zbut)

    points_buitenteen = np.c_[x_but, z_but]
    simplified_but = np.array(rdp.rdp(points_buitenteen.tolist(), tolerance))
    # print simplified
    sx_but, sy_but = simplified_but.T
    # print sx
    # compute the direction vectors on the simplified curve
    directions = np.diff(simplified_but, axis=0)
    theta = angle(directions)
    # Select the index of the points with the greatest theta
    # Large theta is associated with greatest change in direction.
    idx_but = np.where(theta > min_angle)[0] + 1

    buitenteen = sx_but[1]

    for index, row in group.iterrows():
        if row['afstand'] == buitenteen:
            id_but = row['TARGET_FID']
            list_id_but.append(id_but)

            buitenteen_y = row['z_ahn']


    #---------------------------testcode----------------------------
    z_smooth = savgol_filter(z, 3, 1)
    points = np.c_[x, z_smooth]
    simplified = np.array(rdp.rdp(points.tolist(), tolerance))
    # print simplified

    # print(len(simplified))
    sx, sy = simplified.T
    #-----------------------------------------------------------------


    fig = plt.figure(figsize=(25, 2))
    ax = fig.add_subplot(111)
    #


    ax.plot(binnenteen,binnenteen_y, 'bo')
    ax.plot(binnenkruin,binnenkruin_y, 'bo')
    ax.plot(buitenkruin,buitenkruin_y,'bo')
    ax.plot(buitenteen,buitenteen_y, 'bo')
    ax.plot(x, z, 'b-', label='original path')

    # lowess = sm.nonparametric.lowess(z, x, frac=0.05)
    # ax.plot(lowess[:, 0], lowess[:, 1])
    # ax.plot(sx, sy, 'g--', label='simplified path')



    # ax.plot(x_bk, z_bk, 'b-', label='original path')
    # ax.plot(sx_bk, sy_bk, 'g--', label='simplified path')
    # ax.plot(sx_bk[idx_bk], sy_bk[idx_bk], 'ro', markersize=3, label='turning points')
    # # ax.invert_yaxis()
    # plt.legend(loc='best')
    plt.show()

print list_id_bt

arcpy.MakeFeatureLayer_management(invoer, 'punten_binnenteen_temp')
punten_bt = arcpy.SelectLayerByAttribute_management('punten_binnenteen_temp', "ADD_TO_SELECTION", "OBJECTID in (" + str(list_id_bt)[1:-1] + ")")
arcpy.CopyFeatures_management('punten_binnenteen_temp', 'punten_binnenteen')

arcpy.MakeFeatureLayer_management(invoer, 'punten_binnenkruin_temp')
punten_bk = arcpy.SelectLayerByAttribute_management('punten_binnenkruin_temp', "ADD_TO_SELECTION", "OBJECTID in (" + str(list_id_bk)[1:-1] + ")")
arcpy.CopyFeatures_management('punten_binnenkruin_temp', 'punten_binnenkruin')

arcpy.MakeFeatureLayer_management(invoer, 'punten_buitenkruin_temp')
punten_bik = arcpy.SelectLayerByAttribute_management('punten_buitenkruin_temp', "ADD_TO_SELECTION", "OBJECTID in (" + str(list_id_buk)[1:-1] + ")")
arcpy.CopyFeatures_management('punten_buitenkruin_temp', 'punten_buitenkruin')

arcpy.MakeFeatureLayer_management(invoer, 'punten_buitenteen_temp')
punten_but = arcpy.SelectLayerByAttribute_management('punten_buitenteen_temp', "ADD_TO_SELECTION", "OBJECTID in (" + str(list_id_but)[1:-1] + ")")
arcpy.CopyFeatures_management('punten_buitenteen_temp', 'punten_buitenteen')