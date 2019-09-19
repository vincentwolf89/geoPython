import arcpy
import pandas as pd
import numpy as np
from rdp import rdp
from numpy import trapz
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import statsmodels.api as sm

# from scipy.signal import savgol_filter


arcpy.env.overwriteOutput = True
arcpy.env.workspace = 'C:/Users/vince/Desktop/GIS/profielscript_final.gdb'

# invoer = 'testset_25m'
invoer = 'profielen_maatgevend_punten_z_join2'


def count(list1, xbi, r):
    c = 0
    # traverse in the list1
    for x in list1:
        # condition check
        if x>= l and x<= r:
            c+= 1
    return c

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

list_id_bk1 = []
list_id_bk2 = []

list_voorland_totaal = []
list_achterland_totaal = []
list_kruinhoogte_totaal = []

plot = [1,2,52,9,85,701,801,802,900,905,345] # te plotten profiel of range

for name, group in grouped:
    if name in plot:
        aflopend = group.sort(['afstand'], ascending=False)
        oplopend = group.sort(['afstand'], ascending=True)

        list_x = []
        list_y = []

        achterland = []

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

        simplified_trajectory = rdp(points, epsilon=0.2)  # default = epsilon = 0.3
        simplified_trajectory2 = rdp(points, epsilon=0.5)
        sx, sy = simplified_trajectory.T
        sx2, sy2 = simplified_trajectory2.T
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

        # kruin
        for index, row in oplopend.iterrows():
            afstand_kruin = row['afstand']
            if afstand_kruin > -8 and afstand_kruin < 1:
                gem_kruin.append(row['z_ahn'])
            else:
                pass

        if not gem_achterland:
            gem_achterland_hoogte = average(list_achterland_totaal)  # neem gemiddelde van alle profielen
        else:
            gem_achterland_hoogte = average(gem_achterland)  # bepaal gemiddelde hoogte per profiel

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
            if afstand < -15 and hoogte < gem_achterland_hoogte + 0.5:  # default = +1
                x_bit = afstand
                y_bit = hoogte
                break

        # bepaal buitenteen
        for index, row in totaal_df_sort_2.iterrows():
            afstand = row['afstand']
            hoogte = row['hoogte']
            if afstand > 5 and hoogte < gem_voorland_hoogte + 1:
                x_but = afstand
                y_but = hoogte
                break

        # bepaal binnenkruin
        for index, row in totaal_df_sort_2.iterrows():
            afstand = row['afstand']
            hoogte = row['hoogte']
            if afstand > -20 and hoogte > gem_kruinhoogte -0.5 and afstand < -5:  # SLEUTELEN!!!
                x_bik = afstand
                y_bik = hoogte
                break

        # b bepaal buitenkruin
        for index, row in totaal_df_sort.iterrows():
            afstand = row['afstand']
            hoogte = row['hoogte']
            if afstand < 3 and hoogte > gem_kruinhoogte - 1:
                x_buk = afstand
                y_buk = hoogte
                break


        # check voor fouten
        try:
            x_bit, y_bit, x_bik, y_bik, x_but, y_but, x_buk, y_buk

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





            # bereken wel/geen berm
            ## sx versie

            x_bit_but = abs(x_bik - x_bit)
            y_bit_but = y_bik - y_bit
            x_ahn = []
            y_ahn = []
            # print x_bit_but, y_bit_but

            for item in points:
                if item[0] <= x_bik and item[0] >= x_bit:
                    x_ahn.append(item[0])
                    y_ahn.append(item[1] - y_bit)
                else:
                    pass

            # afstand_test = abs(min(x_ahn)-max(x_ahn))
            # print x_bit_but, afstand_test

            area_driehoek = 0.5 * (x_bit_but * y_bit_but)
            area_profiel = trapz(y_ahn, x_ahn)
            # print area_driehoek, area_profiel
            #
            maxi = max(area_driehoek, area_profiel)
            difference = abs(area_profiel - area_driehoek)
            # print difference
            #

            # for index, row in totaal_df_sort.iterrows():
            #     checker = (row['afstand'] -2)
            #     if checker < x_bik:
            #         check_y = row['hoogte']
            #


            # # testcode onderkant berm #
            # for index, row in totaal_df_sort_2.iterrows():
            #     if row['afstand'] == x_bit:
            #         h1 = y_bit
            #         basis = index+1
            #         basis2 = index+2
            #
            # for index, row in totaal_df_sort_2.iterrows():
            #     if index == basis and abs(x_bit+5) > 5:
            #         h2 = row['hoogte']
            #         x2 = row['afstand']
            #
            #         verschil_x = abs(x_bit-x2)
            #         verschil_y = abs(h1-h2)
            #
            #
            #
            # for index, row in totaal_df_sort_2.iterrows():
            #     if index == basis2 and abs(x_bit+5) > 5:
            #     # if index == basis2 and abs(x_bit + 5) > 5:
            #         h3 = row['hoogte']
            #         x3 = row['afstand']
            #         verschil_y2 = abs(h1-h3)
            #
            #
            # print verschil_y, verschil_y2
            #
            # if verschil_x < 5 and x2 < x_bik and x3 < x_bik:
            #     bermknik1_x = x3
            #     bermknik1_y = h3
            # else:
            #     if verschil_y < 4 and x2 < x_bik and x3 < x_bik:
            #         bermknik1_x = x2
            #         bermknik1_y = h2

            #testcode onderkant berm

            # check berm:
            list_i = []
            for index, row in totaal_df_sort_2.iterrows():
                if row['afstand'] < x_bik and row['afstand'] > x_bit:
                    list_i.append(index)

            if len(list_i) > 1 and abs(x_bit-x_bik) > 10:
                print 'berm aanwezig'

                #bovenkant berm
                for index, row in totaal_df_sort.iterrows():
                    if row['afstand'] == x_bik:
                        # y_boven = y_bit
                        i_boven1 = index - 1
                        i_boven2 = index - 2

                for index, row in totaal_df_sort.iterrows():
                    if index == i_boven1 and row['afstand'] > x_bit:
                        x_boven1 = row['afstand']
                        y_boven1 = row['hoogte']
                        verschil_y_boven1 = abs(y_bik - y_boven1)
                        verschil_x_boven1 = abs(x_bik - x_boven1)

                for index, row in totaal_df_sort.iterrows():
                    if index == i_boven2 and row['afstand'] > x_bit:
                        x_boven2 = row['afstand']
                        y_boven2 = row['hoogte']
                        verschil_x_boven2 = abs(x_bik - x_boven2)
                        verschil_y_boven2 = abs(y_bik - y_boven2)
                        verschil_indexes_y = abs(y_boven1 - y_boven2)
                        verschil_indexes_x = abs(x_boven1 - x_boven2)

                if verschil_indexes_y < 1 and verschil_indexes_x < 5:
                    bermknik2_x = x_boven2
                    bermknik2_y = y_boven2
                else:
                    bermknik2_x = x_boven1
                    bermknik2_y = y_boven1


                #onderkant berm
                for index, row in totaal_df_sort_2.iterrows():
                    if row['afstand'] == x_bit:
                        # h1 = y_bit
                        i_onder1 = index+1
                        i_onder2 = index+2

                for index, row in totaal_df_sort_2.iterrows():
                    if index == i_onder1 and row['afstand'] > x_bit:
                        x_onder1 = row['afstand']
                        y_onder1 = row['hoogte']
                        verschil_y_onder1 = abs(y_bit-y_onder1)
                        verschil_x_onder1 = abs(x_bit-x_onder1)



                for index, row in totaal_df_sort_2.iterrows():
                    if index == i_onder2 and row['afstand'] > x_onder1:
                        x_onder2 = row['afstand']
                        y_onder2 = row['hoogte']
                        verschil_x_onder2 = abs(x_bit - x_onder2)
                        verschil_y_boven2 = abs(y_bit - y_onder2)
                        verschil_indexes_yo = abs(y_onder1-y_onder2)
                        verschil_indexes_xo = abs(x_onder1 - x_onder2)

                # if abs(y_onder1-y_bit) > 1 and verschil_indexes_xo > 1:
                if verschil_indexes_xo < 2 and verschil_index_yo < 1:
                    bermknik1_x = x_onder2
                    bermknik1_y = y_onder2
                else:
                    bermknik1_x = x_onder1
                    bermknik1_y = y_onder1

                #
                # if verschil_indexes_yo < 1 and verschil_indexes_xo < 5:
                #     bermknik1_x = x_onder2
                #     bermknik1_y = y_onder2
                # else:
                #     bermknik1_x = x_onder1
                #     bermknik1_y = y_onder1


            else:
                print 'geen berm aanwezig'








        if x_bit is not None:
            der = savgol_filter(list_y, 3, 1)
            window = 5
            der2 = savgol_filter(der,window_length=5,polyorder =3, deriv=2)

            max_der2 = np.max(np.abs(der2))
            large = np.where(np.abs(der2) > max_der2 / 2)[0]
            gaps = np.diff(large) > window
            begins = np.insert(large[1:][gaps], 0, large[0])
            ends = np.append(large[:-1][gaps], large[-1])
            changes = ((begins + ends) / 2).astype(np.int)

            # window_length = window, polyorder = 2, deriv = 2
            fig = plt.figure(figsize=(25, 2))
            ax = fig.add_subplot(111)
            ax.plot(list_x, list_y)
            ax.plot(list_x,der)
            ax.plot(list_x, der2)
            ax.plot(changes, der2[changes], 'ro')
            # ax.plot(sx, sy, 'gx-', label='simplified trajectory')
            # ax.plot(sx2, sy2, 'bx-', label='simplified trajectory2')
            # ax.plot(x_bit, y_bit, 'bo')
            # ax.plot(x_but, y_but, 'bo')
            # ax.plot(x_bik, y_bik, 'bo')
            # ax.plot(x_buk, y_buk, 'bo')

            try:
                bermknik2_x
            except NameError:
                bermknik2_x = None
                bermknik2_y = None
            try:
                bermknik1_x
            except NameError:
                bermknik1_x = None
                bermknik1_y = None


            if bermknik1_x is not None:
                ax.plot(bermknik1_x, bermknik1_y, 'ro', label = 'onderkant berm')
            else:
                pass
            if bermknik2_x is not None:
                ax.plot(bermknik2_x, bermknik2_y, 'go', label = 'bovenkant berm')
            else:
                pass
            # ax.plot(sx[idx], sy[idx], 'ro', markersize=7, label='turning points')
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.legend(loc='best')
            plt.show()

            del bermknik2_x, bermknik2_y, bermknik1_x, bermknik1_y


        # # verwijder waardes
        del x_bit, y_bit, x_but, y_but, x_bik, y_bik, x_buk, y_buk
        print "Profiel " + str(name) + " is klaar"
    else:
        pass
# # export naar GIS
# arcpy.MakeFeatureLayer_management(invoer, 'punten_binnenkruin_temp')
# punten_bik = arcpy.SelectLayerByAttribute_management('punten_binnenkruin_temp', "ADD_TO_SELECTION", "OBJECTID in (" + str(list_id_bik)[1:-1] + ")")
# arcpy.CopyFeatures_management('punten_binnenkruin_temp', 'punten_binnenkruin')
# # #
# arcpy.MakeFeatureLayer_management(invoer, 'punten_buitenkruin_temp')
# punten_buk = arcpy.SelectLayerByAttribute_management('punten_buitenkruin_temp', "ADD_TO_SELECTION", "OBJECTID in (" + str(list_id_buk)[1:-1] + ")")
# arcpy.CopyFeatures_management('punten_buitenkruin_temp', 'punten_buitenkruin')
# # #
# arcpy.MakeFeatureLayer_management(invoer, 'punten_buitenteen_temp')
# punten_but = arcpy.SelectLayerByAttribute_management('punten_buitenteen_temp', "ADD_TO_SELECTION", "OBJECTID in (" + str(list_id_but)[1:-1] + ")")
# arcpy.CopyFeatures_management('punten_buitenteen_temp', 'punten_buitenteen')
#
# arcpy.MakeFeatureLayer_management(invoer, 'punten_binnenteen_temp')
# punten_bit = arcpy.SelectLayerByAttribute_management('punten_binnenteen_temp', "ADD_TO_SELECTION", "OBJECTID in (" + str(list_id_bit)[1:-1] + ")")
# arcpy.CopyFeatures_management('punten_binnenteen_temp', 'punten_binnenteen')
#
# arcpy.MakeFeatureLayer_management(invoer, 'punten_bk1_temp')
# punten_bk1 = arcpy.SelectLayerByAttribute_management('punten_bk1_temp', "ADD_TO_SELECTION", "OBJECTID in (" + str(list_id_bk1)[1:-1] + ")")
# arcpy.CopyFeatures_management('punten_bk1_temp', 'punten_bk1')
#
# arcpy.MakeFeatureLayer_management(invoer, 'punten_bk2_temp')
# punten_bk2 = arcpy.SelectLayerByAttribute_management('punten_bk2_temp', "ADD_TO_SELECTION", "OBJECTID in (" + str(list_id_bk2)[1:-1] + ")")
# arcpy.CopyFeatures_management('punten_bk2_temp', 'punten_bk2')