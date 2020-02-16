import arcpy
import pandas as pd
import numpy as np
import math
import os, sys

# from basisfuncties import*
arcpy.env.workspace = r'D:\Projecten\WSRL\sprok_sterrenschans.gdb'
gdb = r'D:\Projecten\WSRL\sprok_sterrenschans.gdb'
arcpy.env.overwriteOutput = True

gefmap = r'C:\Users\Vincent\Desktop\sonderingen_test'
puntenlaag = 'gefmap_uitvoer_so'
max_dZ = 1 # maximale dikte grove laag bij boring
max_cws = 10 # maximale conusweerstand bij sondering
nan = -9999
soorten_grof = ['Z','G']



####### aantekeningen door te nemen
# indien onderkant grof stopt deklaag boven deze laag, conservatieve benadering.


def gef_txt(gefmap):
    for gef in os.listdir(gefmap):
        ingef = os.path.join(gefmap, gef)
        if not os.path.isfile(ingef): continue
        nieuwenaam = ingef.replace('.GEF', '.txt')
        output = os.rename(ingef, nieuwenaam)




def bovenkant_d_boring(gefmap, puntenlaag):
    # maak nieuwe puntenlaag in gdb
    arcpy.CreateFeatureclass_management(gdb, puntenlaag, "POINT", spatial_reference=28992)
    arcpy.AddField_management(puntenlaag, 'naam', "TEXT")
    arcpy.AddField_management(puntenlaag, 'dikte_deklaag', "DOUBLE", 2, field_is_nullable="NULLABLE")

    # open de insertcursor
    cursor = arcpy.da.InsertCursor(puntenlaag, ['naam', 'dikte_deklaag', 'SHAPE@XY'])

    # open gef uit map
    for file in os.listdir(gefmap):
        ingef = os.path.join(gefmap, file)
        gef = open(ingef, "r")

        # lagen zijn 0
        deklaag = 0
        grove_laag = 0

        # definieer lege lijsten
        bovenkant = []
        onderkant = []
        type_laag = []
        laag = []
        bovenkant_grof = []


        for regel in gef:
            if regel.startswith('#') or regel.isspace() == True: # negeer regels met #
                if regel.startswith('#XYID'):
                    ids = regel.split(',')
                    x = float(ids[1])
                    y = float(ids[2])

                else:
                    pass
            else:
                #
                delen = regel.split(';')
                soort = delen[2]
                soort_global = soort[1]
                bovenkant_ = float(delen[0])
                onderkant_ = float(delen[1])
                dikte_laag = abs(bovenkant_-onderkant_)

                # vul lijsten voor opbouw df
                bovenkant.append(bovenkant_)
                onderkant.append(onderkant_)
                type_laag.append(soort_global)
                laag.append(dikte_laag)



        # maak df van lijsten via dict
        dict = {'bovenkant': bovenkant, 'onderkant': onderkant, 'type': type_laag,'dikte_laag': laag}
        df = pd.DataFrame(dict)
        df['type_onderliggend'] = df['type'].shift(-1)
        df['dikte_onderliggend'] = df['dikte_laag'].shift(-1)


        # afvangen dubbele grove laag onderkant
        lasttype = df.loc[len(df)-1, 'type']
        last_d = float(df.loc[len(df) - 1, 'dikte_laag'])  # niet direct nodig?
        s_lasttype = df.loc[len(df) - 2, 'type']
        s_last_d = float(df.loc[len(df) - 2, 'dikte_laag'])


        if lasttype in soorten_grof and s_lasttype in soorten_grof:
            max_index = len(df)-3
        elif lasttype in soorten_grof and s_lasttype not in soorten_grof:
            max_index = len(df)-2
        elif s_lasttype in soorten_grof and s_last_d <= max_dZ:
            max_index = len(df) - 1
        else:
            if lasttype not in soorten_grof and s_lasttype not in soorten_grof:
                max_index = len(df)-1




        # bepaal grove laag
        for index, row in df.iterrows():
            t = row['type']
            d = row['dikte_laag']

            if t in soorten_grof:
                grove_laag += d
                bovenkant_grof.append(index)
            if t not in soorten_grof:
                grove_laag = 0
                bovenkant_grof = []

            if grove_laag > max_dZ:
                max_index = bovenkant_grof[0]-1
                break


        # bepaal dikte deklaag
        for index, row in df.iterrows():
            d = row['dikte_laag']

            # als grove laag aanwezig is, dikker dan maatgevend:
            if grove_laag > max_dZ and index <= max_index:
                deklaag += d
            # als grove laag niet dikker is dan maatgevend
            if grove_laag < max_dZ and index <= max_index:
                deklaag += d

        print "deklaag is", deklaag, x,y, file
        invoegen = (str(file), deklaag, (x, y))



        cursor.insertRow(invoegen)



def bovenkant_d_sondering(gefmap,puntenlaag):
    # maak nieuwe puntenlaag in gdb
    arcpy.CreateFeatureclass_management(gdb, puntenlaag, "POINT", spatial_reference=28992)
    arcpy.AddField_management(puntenlaag, 'naam', "TEXT")
    arcpy.AddField_management(puntenlaag, 'dikte_deklaag', "DOUBLE", 2, field_is_nullable="NULLABLE")

    # open de insertcursor
    cursor = arcpy.da.InsertCursor(puntenlaag, ['naam', 'dikte_deklaag', 'SHAPE@XY'])

    # itereer over sonderingen in map
    for file in os.listdir(gefmap):
        ingef = os.path.join(gefmap, file)
        gef = open(ingef, "r")

        # lagen zijn 0
        deklaag = 0
        grove_laag = 0

        # checker voor aanwezigheid significante grove laag
        grof = None

        # definieer lege lijsten
        bovenkant = []
        cws = []

        bovenkant_grof = []

        for regel in gef:
            if regel.startswith('#') or regel.isspace() == True:  # negeer regels met #
                if regel.startswith('#XYID'):
                    ids = regel.split(',')
                    x = float(ids[1])
                    y = float(ids[2])

                else:
                    if regel.startswith('#ZID'):
                        idz = regel.split(',')
                        z_mv = float(idz[1])
            else:
                #
                laagdikte = 0

                delen = regel.split(' ')
                bovenkant_ = float(delen[0])
                cws_ = float(delen[1])

                bovenkant.append(bovenkant_)
                cws.append(cws_)

        # maak df van lijsten via dict
        dict = {'bovenkant': bovenkant, 'cws': cws}
        df = pd.DataFrame(dict)
        df['onderkant'] = df['bovenkant'].shift(-1)
        df['cws_onder'] = df['cws'].shift(-1)
        df['dikte_laag'] = abs(df['bovenkant']-df['onderkant'])

        # df['dikte_onderliggend'] = df['dikte_laag'].shift(-1)

        # afvangen nan values
        df = df.replace(nan, 0)
        df['dikte_laag'].fillna(0.01, inplace=True)
        # print df, file

        for index, row in df.iterrows():
            if row['cws'] <= max_cws:
                grove_laag = 0
                bovenkant_grof = []
                deklaag = row['onderkant']
                grof = True


                continue
            else:
                grove_laag+= row['dikte_laag']
                bovenkant_grof.append(index)
                if grove_laag > max_dZ:
                    # print row['bovenkant'], bovenkant_grof[0], file
                    for index, row in df.iterrows():
                        if index == bovenkant_grof[0]:
                            # print z_mv-row['bovenkant'], "m - maaiveld"
                            # print row['bovenkant'], file
                            deklaag = row['onderkant']
                            grof = False


                    break


        if grof == False:
            print "zandlaag aanwezig"
        if grof == True:
            print "zandlaag niet aanwezig"
        print deklaag, file

        print "deklaag is", deklaag, x, y, file
        invoegen = (str(file), deklaag, (x, y))

        cursor.insertRow(invoegen)


bovenkant_d_sondering(gefmap,puntenlaag)