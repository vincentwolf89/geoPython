import arcpy
import pandas as pd
import numpy as np
import math
import os, sys
import xml.dom.minidom as minidom

# from basisfuncties import*
arcpy.env.workspace = r'D:\GoogleDrive\WSRL\werk.gdb'
gdb = r'D:\GoogleDrive\WSRL\werk.gdb'
arcpy.env.overwriteOutput = True

files = r'C:\Users\Vincent\Desktop\sonderingen_safe'



puntenlaag = 'safeSonderingen'
max_dZ = 1.0 # maximale dikte grove laag bij boring
max_cws = 10 # maximale conusweerstand bij sondering
nan = -999


soorten_grof_gef = ['Z','G']
soorten_grof_xml = ['matigSiltigZand', 'zwakSiltigZand','sterkZandigeLeem','zwakZandigeLeem']





def gef_txt(files):
    for gef in os.listdir(files):
        if gef.endswith(".gef"):

            ingef = os.path.join(files, gef)
            if not os.path.isfile(ingef): continue
            nieuwenaam = ingef.replace('.gef', '.txt')
            output = os.rename(ingef, nieuwenaam)
            print "Extensie veranderd van .gef naar .txt voor {}".format(gef)
        elif gef.endswith(".GEF"):

            ingef = os.path.join(files, gef)
            if not os.path.isfile(ingef): continue
            nieuwenaam = ingef.replace('.GEF', '.txt')
            output = os.rename(ingef, nieuwenaam)
            print "Extensie veranderd van .GEF naar .txt voor {}".format(gef)


def bovenkant_d_boring_gef(files, puntenlaag):
    # maak nieuwe puntenlaag in gdb
    arcpy.CreateFeatureclass_management(gdb, puntenlaag, "POINT", spatial_reference=28992)
    arcpy.AddField_management(puntenlaag, 'naam', "TEXT")
    arcpy.AddField_management(puntenlaag, 'typeOnder', "TEXT")
    arcpy.AddField_management(puntenlaag, 'dikte_deklaag', "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(puntenlaag, 'zOnderNAP', "DOUBLE", 2, field_is_nullable="NULLABLE")

    # open de insertcursor
    cursor = arcpy.da.InsertCursor(puntenlaag, ['naam', 'dikte_deklaag', 'typeOnder','zOnderNAP', 'SHAPE@XY'])

    # open gef uit map
    for file in os.listdir(files):
        naam = file.split('.txt')[0]
        ingef = os.path.join(files, file)
        gef = open(ingef, "r")

        # lagen zijn 0
        deklaag = 0
        grove_laag = 0
        andere_sep = False

        # definieer lege lijsten
        type = []
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

                # als andere separator wordt gebruikt
                elif regel.startswith("#COLUMNSEPARATOR"):
                    andere_sep = True
                    sep = regel.strip()[-1:]
                    # print "Kolomscheider is {}".format(sep)

                elif regel.startswith('#ZID'):
                    idz = regel.split(',')
                    z_mv = float(idz[1])
                    try:
                        onderkant_onderlaag

                        z_onderlaag = z_mv-abs(onderkant_onderlaag)
                    except NameError:
                        z_onderlaag = None

                    print "Boring {} heeft een maaiveldhoogte van {}m NAP en de onderste laag ligt op {}m NAP ".format(naam,z_mv,z_onderlaag)

                else:
                    pass
            else:

                if andere_sep is False:
                    delen = regel.split(' ')
                else:
                    delen = regel.split("{}".format(sep))





                # check of soortenkolom wordt meegenomen en niet nan-kolom
                for item in delen:
                    if item == delen[0] or item == delen[1] or item =="-9999.99":
                        pass
                    else:
                        try:
                            item[1]
                            if item[1].isupper():
                                soort = item
                                # print soort
                                break
                        except IndexError:
                            pass


                # check of boring goed gegaan is, anders stoppen
                if len(soort) > 1:
                    soort_global = soort[1]
                    bovenkant_ = float(delen[0])
                    onderkant_ = float(delen[1])
                    dikte_laag = abs(bovenkant_-onderkant_)

                    # print type(soort[2])

                    # vul lijsten voor opbouw df
                    bovenkant.append(bovenkant_)
                    onderkant.append(onderkant_)
                    type_laag.append(soort_global)
                    # type.append(soort) # specificatie laagtype
                    laag.append(dikte_laag)
                    stoppen = False
                else:
                    stoppen = True


        if stoppen is False:
            # maak df van lijsten via dict
            dict = {'bovenkant': bovenkant, 'onderkant': onderkant, 'type': type_laag,'dikte_laag': laag}
            df = pd.DataFrame(dict)
            # df['type_onderliggend'] = df['type'].shift(-1)
            # df['dikte_onderliggend'] = df['dikte_laag'].shift(-1)

            # als meer dan een laag geboord is:
            if len(df) > 1:

                # print df
                # afvangen dubbele grove laag onderkant 1a: defineer soorten en diktes
                lasttype = df.loc[len(df)-1, 'type']
                # last_d = float(df.loc[len(df) - 1, 'dikte_laag'])  # niet direct nodig?
                s_lasttype = df.loc[len(df) - 2, 'type']
                s_last_d = float(df.loc[len(df) - 2, 'dikte_laag'])



                # afvangen dubbele grove laag onderkant 1b: bepaal max index
                if lasttype in soorten_grof_gef and s_lasttype in soorten_grof_gef:
                    max_index = len(df)-3
                elif lasttype in soorten_grof_gef and s_lasttype not in soorten_grof_gef:
                    max_index = len(df)-2
                elif s_lasttype in soorten_grof_gef and lasttype not in soorten_grof_gef and s_last_d <= max_dZ:
                    max_index = len(df) - 1
                else:
                    if lasttype not in soorten_grof_gef and s_lasttype not in soorten_grof_gef:
                        max_index = len(df)-1




                # bepaal grove laag
                for index, row in df.iterrows():
                    t = row['type']
                    d = row['dikte_laag']

                    if t in soorten_grof_gef:
                        grove_laag += d
                        bovenkant_grof.append(index)
                    if t not in soorten_grof_gef:
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
                    if grove_laag <= max_dZ and index <= max_index:
                        deklaag += d


            elif len(df) is 1:
                t = df.loc[0, 'type']
                if t in soorten_grof_gef:
                    deklaag = 0
                if t not in soorten_grof_gef:
                    deklaag = df.loc[0, 'dikte_laag']

            else:
                if len(df) is 0:
                    deklaag = 0


            print "Deklaag heeft een dikte van {}m".format(deklaag)

            # onderste laag vinden
            gef = open(ingef, "r")
            rijen = gef.read().splitlines()
            try:
                onderste_rij = rijen[-1]
                onderkant_onderlaag = float(onderste_rij.split(sep)[1])
                # print onderkant_onderlaag
            except IndexError:
                onderkant_onderlaag = None
                print "Lege gef?"

            # NAP niveau onderkant berekenen
            try:
                z_mv, onderkant_onderlaag
                z_onderlaag = z_mv - abs(onderkant_onderlaag)
            except NameError:
                z_onderlaag = None




            if len(df) is 0:
                invoegen = (str(naam), deklaag, None,None, (x, y))
            else:
                invoegen = (str(naam), deklaag, type_laag[-1], z_onderlaag, (x, y))



            cursor.insertRow(invoegen)

        else:
            pass


def bovenkant_d_boring_xml(files, puntenlaag):
    # maak een nieuwe puntenlaag aan in de gdb
    arcpy.CreateFeatureclass_management(gdb, puntenlaag, "POINT", spatial_reference=28992)
    arcpy.AddField_management(puntenlaag, 'naam', "TEXT")
    arcpy.AddField_management(puntenlaag, 'typeOnder', "TEXT")
    arcpy.AddField_management(puntenlaag, 'dikte_deklaag', "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(puntenlaag, 'zOnderNAP', "DOUBLE", 2, field_is_nullable="NULLABLE")


    # open de insertcursor
    cursor = arcpy.da.InsertCursor(puntenlaag, ['naam', 'dikte_deklaag','typeOnder','zOnderNAP', 'SHAPE@XY'])

    # files
    for file in os.listdir(files):
        naam = file.split('.xml')[0]
        in_xml = os.path.join(files, file)
        xml = minidom.parse(in_xml)

        # lagen zijn 0
        deklaag = 0
        grove_laag = 0

        # get location coordinates from xml
        locations = xml.getElementsByTagName("ns8:deliveredLocation")
        for location in locations:
            # print coordinate
            coordinates = location.getElementsByTagName("gml:pos")

            for coordinate in coordinates:
                total = coordinate.childNodes[0].nodeValue
                parts = total.split(" ")
                x = float(parts[0])
                y = float(parts[1])

        # get maaiveldhoogte from xml
        hoogtes = xml.getElementsByTagName("ns9:offset")

        for hoogte in hoogtes:
            try:
                z_mv = float(hoogte.childNodes[0].nodeValue)
            except IndexError:
                z_mv = -999


        # get einddiepte from xml
        eindlaag = xml.getElementsByTagName("ns9:endDepth")
        for eindhoogte in eindlaag:
            try:
                onderkant_onderlaag = float(eindhoogte.childNodes[0].nodeValue)
            except IndexError:
                onderkant_onderlaag= -999
                print "Geen eindhoogte gevonde bij xml: {}".format(naam)

        # bereken einddiepte in m NAP
        if z_mv is not -999 and onderkant_onderlaag is not -999:
            z_onderlaag = z_mv-abs(onderkant_onderlaag)
        else:
            z_onderlaag = None



        # create pandas dataframe with layers
        type = []
        bovenkant = []
        onderkant = []

        bodemlagen = xml.getElementsByTagName("ns9:soilLayer")

        for bodemlaag in bodemlagen:

            bovenkanten = bodemlaag.getElementsByTagName("ns9:upperBoundary")
            onderkanten = bodemlaag.getElementsByTagName("ns9:lowerBoundary")
            typen = bodemlaag.getElementsByTagName("ns9:standardSoilName") # eerst horizonCode

            for item in typen:
                type.append(item.childNodes[0].nodeValue)
                test = item.childNodes[0].nodeValue
                # if test in soorten_grof_xml:
                #     print file




                break

            for item in bovenkanten:
                bovenkant.append(float(item.childNodes[0].nodeValue))

            for item in onderkanten:
                onderkant.append(float(item.childNodes[0].nodeValue))

        # alleen doorgaan als voor alles een waarde wordt gevonden
        if len(type) == len(onderkant) and len(onderkant) == len(bovenkant):

            dict = {'bovenkant': bovenkant, 'onderkant': onderkant, 'type': type}
            df = pd.DataFrame(dict)
            df['dikte_laag'] = abs(df['bovenkant'] - df['onderkant'])

            # als meer dan een laag geboord is:
            if len(df) > 1:

                # print df
                # afvangen dubbele grove laag onderkant 1a: defineer soorten en diktes
                lasttype = df.loc[len(df) - 1, 'type']
                # last_d = float(df.loc[len(df) - 1, 'dikte_laag'])  # niet direct nodig?
                s_lasttype = df.loc[len(df) - 2, 'type']
                s_last_d = float(df.loc[len(df) - 2, 'dikte_laag'])

                # afvangen dubbele grove laag onderkant 1b: bepaal max index
                if lasttype in soorten_grof_xml and s_lasttype in soorten_grof_xml:
                    max_index = len(df) - 3
                elif lasttype in soorten_grof_xml and s_lasttype not in soorten_grof_xml:
                    max_index = len(df) - 2
                elif s_lasttype in soorten_grof_xml and lasttype not in soorten_grof_xml and s_last_d <= max_dZ:
                    max_index = len(df) - 1
                else:
                    if lasttype not in soorten_grof_xml and s_lasttype not in soorten_grof_xml:
                        max_index = len(df) - 1

                # bepaal grove laag
                for index, row in df.iterrows():
                    t = row['type']
                    d = row['dikte_laag']

                    if t in soorten_grof_xml:
                        grove_laag += d
                        bovenkant_grof.append(index)
                    if t not in soorten_grof_xml:
                        grove_laag = 0
                        bovenkant_grof = []

                    if grove_laag > max_dZ:
                        max_index = bovenkant_grof[0] - 1
                        break

                # bepaal dikte deklaag
                for index, row in df.iterrows():
                    d = row['dikte_laag']

                    # als grove laag aanwezig is, dikker dan maatgevend:
                    if grove_laag > max_dZ and index <= max_index:
                        deklaag += d
                    # als grove laag niet dikker is dan maatgevend
                    if grove_laag <= max_dZ and index <= max_index:
                        deklaag += d



            elif len(df) is 1:
                t = df.loc[0, 'type']
                if t in soorten_grof_xml:
                    deklaag = 0
                if t not in soorten_grof_xml:
                    deklaag = df.loc[0, 'dikte_laag']

            else:
                if len(df) is 0:
                    deklaag = 0
            print "Boring {} heeft een maaiveldhoogte van {}m NAP en de onderste laag ligt op {}m NAP ".format(naam,
                                                                                                               z_mv,
                                                                                                               z_onderlaag)
            print "Deklaag heeft een dikte van {}m".format(deklaag)





            if len(df) is 0:
                invoegen = (str(naam), deklaag, None,None, (x, y))
            else:
                invoegen = (str(naam), deklaag, type[-1], z_onderlaag, (x, y))

            cursor.insertRow(invoegen)

        else:
            print "Ontbrekende waarden ", file

        del deklaag, x,y,type,z_onderlaag

def bovenkant_d_sondering(files,puntenlaag):
    # maak nieuwe puntenlaag in gdb
    arcpy.CreateFeatureclass_management(gdb, puntenlaag, "POINT", spatial_reference=28992)
    arcpy.AddField_management(puntenlaag, 'naam', "TEXT")
    arcpy.AddField_management(puntenlaag, 'dikte_deklaag', "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(puntenlaag, 'zOnderNAP', "DOUBLE", 2, field_is_nullable="NULLABLE")

    # open de insertcursor
    cursor = arcpy.da.InsertCursor(puntenlaag, ['naam', 'dikte_deklaag','zOnderNAP', 'SHAPE@XY'])

    # itereer over sonderingen in map
    for file in os.listdir(files):
        naam = file.split('.txt')[0]
        print naam
        ingef = os.path.join(files, file)
        gef = open(ingef, "r")


        # lagen zijn 0
        deklaag = 0
        grove_laag = 0

        # checker voor aanwezigheid significante grove laag
        grof = None
        onder_grof = None
        andere_sep = False

        # definieer lege lijsten
        bovenkant = []
        cws = []
        bovenkant_grof = []

        for regel in gef:
            regel = regel.strip()
            # uitroeptekens uit voorzorg verwijderen
            regel = regel.replace("!","")

            if regel.startswith('#') or regel.isspace() == True:
                # get xy
                if regel.startswith('#XYID'):
                    ids = regel.split(',')
                    x = float(ids[1])
                    y = float(ids[2])

                # als andere separator wordt gebruikt
                if regel.startswith("#COLUMNSEPARATOR"):
                    andere_sep = True
                    sep = regel.strip()[-1:]
                    # print "Kolomscheider is {}".format(sep)

                else:
                    # get maaiveldhoogte
                    if regel.startswith('#ZID'):
                        idz = regel.split(',')
                        z_mv = float(idz[1])
                        # print "Maaiveldhoogte is {}m".format(z_mv)
            else:

                if andere_sep is False:
                    delen = regel.split(' ')
                    sep = ' '
                else:
                    delen = regel.split("{}".format(sep))


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


        # afvangen nan values
        df = df.replace(nan, 0)
        df['dikte_laag'].fillna(0.01, inplace=True)
        # print df, file



        # check of sondering wel/niet stopt in grove laag. Indien het geval, neem het laatste snijpunt met grenswaarde
        df_invert = df.sort_index(ascending=False)
        last_cws = df.loc[len(df_invert)-1, 'cws']
        grenswaarde_lijst = []
        grenswaarde = None

        if last_cws < max_cws:
            pass
        else:
            for index, row in df_invert.iterrows():
                # print row['cws']
                grenswaarde_lijst.append(index)
                if row['cws'] <= max_cws:
                    grenswaarde_index = min(grenswaarde_lijst)
                    grenswaarde = df.loc[grenswaarde_index, 'onderkant']
                    # print z_mv-grenswaarde
                    break




        for index, row in df.iterrows():
            if row['cws'] <= max_cws and grenswaarde is None:
                grove_laag = 0
                bovenkant_grof = []
                deklaag = row['onderkant']
                grof = False
                continue
            elif row['cws'] <= max_cws and grenswaarde is not None:
                grove_laag = 0
                bovenkant_grof = []
                deklaag = grenswaarde
                grof = False
                onder_grof = True

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
                            grof = True
                    break



        if grof == True and onder_grof == False:
            print "Significante tussenzandlaag aanwezig, sondering stopt niet met grove laag ", naam
        if grof == True and onder_grof == True:
            print "Significante tussenzandlaag aanwezig, sondering stopt met grove laag ", naam

        if grof == False and onder_grof == False:
            print "Significante tussenzandlaag niet aanwezig, geen grove laatste laag ", naam

        # stel deklaag bij indien sondering stopt met grove laag
        if grof == False and onder_grof == True:
            deklaag = grenswaarde
            print "Deklaag bijgesteld: significante tussenzandlaag niet aanwezig, sondering stopt met grove laag ", naam

        # print "deklaag is", deklaag, x, y, file, z_mv-deklaag
        # print z_mv - deklaag, file


        # onderste laag vinden
        gef = open(ingef, "r")
        rijen = gef.read().splitlines()
        try:
            onderste_rij = rijen[-1]
            onderkant_onderlaag = float(onderste_rij.split(sep)[0])
            # print onderkant_onderlaag
        except IndexError:
            onderkant_onderlaag = None
            print "Lege gef?"

        # NAP niveau onderkant berekenen
        try:
            z_mv, onderkant_onderlaag
            print z_mv, onderkant_onderlaag
            z_onderlaag = z_mv-abs(onderkant_onderlaag)
        except NameError:
            z_onderlaag = None

        # check of coordinaten aanwezig zijn, anders skippen
        try:
            x,y
            invoegen = (str(naam), deklaag, z_onderlaag, (x, y))
            cursor.insertRow(invoegen)
        except NameError:
            pass

gef_txt(files)
# bovenkant_d_boring_gef(files,puntenlaag)


# bovenkant_d_boring_xml(files,puntenlaag)

bovenkant_d_sondering(files,puntenlaag)

