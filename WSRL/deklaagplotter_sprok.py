import arcpy
import matplotlib.pyplot as plt
import numpy as np
arcpy.env.overwriteOutput = True

from basisfuncties import*
arcpy.env.workspace = r'D:\GoogleDrive\WSRL\sprok_sterrenschans.gdb'

trajectlijn = 'trajectlijn'
code = 'code'
profielen = 'profielen_go_boringen_dp' # hier zijn de null-values all uit, zie laag-dp voor totaalset!
boringen_samen = 'dino_boringen_samen_bufferzone'
# profielen_op_lijn(10,210,0,trajectlijn,code,profielen)

# search cursor
def calc_deklaag():
    with arcpy.da.UpdateCursor(profielen, ['SHAPE@', 'profielnummer', 'gemiddelde_deklaag']) as cursor:
        for row in cursor:
            profiel = row
            deklaag = []
            arcpy.MakeFeatureLayer_management(boringen_samen, 'templaag_boringen')
            arcpy.SelectLayerByLocation_management('templaag_boringen', "WITHIN_A_DISTANCE", row[0], "20 Meters", "NEW_SELECTION", "NOT_INVERT")
            arcpy.CopyFeatures_management('templaag_boringen', 'boringen_selectie')
            # print arcpy.GetCount_management("boringen_selectie")
            with arcpy.da.SearchCursor("boringen_selectie", ['dikte_deklaag']) as sCursor:
                for srow in sCursor:
                    deklaag.append(srow[0])

            if deklaag:
                average_deklaag = sum(deklaag) / len(deklaag)

                row[2] = average_deklaag
                cursor.updateRow(row)
                print "deklaag is gemiddeld ", average_deklaag, " bij profielnummer", row[1]
                print "aantal boringen bekeken ", len(deklaag)
                # print "gemiddelde deklaag is " + str(average_deklaag) + " bij profiel "+ str(row[1])
            else:
                deklaag = None
                print "Geen boringen in de buurt bij ", row[1]

        del cursor, sCursor


def plotter():
    array_results = arcpy.da.FeatureClassToNumPyArray(profielen, ('MEAS','gemiddelde_deklaag','RFTIDENT'))
    df = pd.DataFrame(array_results)
    df_plot = df.dropna()
    sort_results = df_plot.sort_values(['MEAS'], ascending=[True])

    # dijkpalen goedzetten
    df_dp = pd.DataFrame(
        {'dp': sort_results['RFTIDENT'],
         'MEAS': sort_results['MEAS']})

    df_dp = df_dp[::20]
    dp_lijst = df_dp['dp'].tolist()
    dp_MEAS_lijst = df_dp['MEAS'].tolist()


    plt.style.use('seaborn-whitegrid')
    fig = plt.figure(figsize=(40, 4))

    ax1 = fig.add_subplot(111, label ="1")
    ax1.plot(sort_results['MEAS'],sort_results['gemiddelde_deklaag'])



    ax1.set_xticks(dp_MEAS_lijst)
    ax1.set_xticklabels(dp_lijst,rotation=45)
    # plt.show()
    plt.savefig(r'C:\Users\Vincent\Desktop\test_dp.png', pad_inches=0.02, dpi=300, bbox_inches='tight')
    plt.close()

calc_deklaag()
# plotter()

