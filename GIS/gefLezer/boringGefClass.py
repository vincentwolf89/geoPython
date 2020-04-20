import os
import arcpy
import pandas as pd


files = r'D:\Projecten\WSRL\GoSprok\WSRL_eigen\HB'
arcpy.env.workspace = r'D:\GoogleDrive\WSRL\sprok_sterrenschans.gdb'
gdb = r'D:\GoogleDrive\WSRL\sprok_sterrenschans.gdb'
arcpy.env.overwriteOutput = True





puntenlaag = 'hbSprokWSRL'

soortenGrofGef = ['Z','G']
maxGrof = 5
minSlap = 0.5
grensHoogte = 0 # in m NAP

class boringGef(object):
    def __init__(self, file):
        self.file = file

    def readFile(self, file):
        naam = file.split('.txt')[0]
        ingef = os.path.join(files, file)
        gef = open(ingef, "r")

        # remove blank lines
        lines = (line.rstrip() for line in gef)
        lines = list(line for line in lines if line)
        # print naam
        return lines, naam

    def getBase(self,lines):
        # lijst voor meetgedeelte
        lijstMetingen = []
        # ophalen benodigde data
        for item in lines:
            if item.startswith('#'):
                # bepalen separator
                if item.startswith('#COLUMNSEP'):
                    sep = item.strip()[-1:]
                # ophalen locatiegegevens
                if item.startswith('#XYID'):
                    coLocs = item.split(',')
                    x = float(coLocs[1])
                    y = float(coLocs[2])

                if item.startswith('#ZID'):
                    zMv = round(float(item.split(',')[1]), 2)
            # anders doorgaan met metingen opbouw
            else:
                lijstMetingen.append(item)

        # check of voldoende informatie aanwezig is om door te gaan
        try:
            x, y, zMv
            coords = True
        except NameError:
            print "Geen coordinaten gevonden"
            coords = None
            # break
        try:
            sep
        except NameError:
            sep = ' '

        if lijstMetingen:
            metingen = True
            pass
        else:
            print "Geen metingen gevonden"
            # break

        if coords is True and metingen is True:
            return x,y,zMv, lijstMetingen, sep
        else:
            return None

    def createDF(self,lijstMetingen,sep):
        index = 0
        indexLijst = []
        bovenkantLijst = []
        onderkantLijst = []
        soortenLijst = []

        for item in lijstMetingen:
            onderdelen = item.split(sep)
            bovenkant = float(onderdelen[0])
            onderkant = float(onderdelen[1])

            # skip -9999 of rare waardes
            for item in onderdelen:
                if item.startswith("'"):
                    soort = item[1]
                    break



            print soort
            # soort = (onderdelen[2])[1]

            indexLijst.append(index)
            bovenkantLijst.append(bovenkant)
            onderkantLijst.append(onderkant)
            soortenLijst.append(soort)
            index += 1

        del bovenkant, onderkant, soort, index

        # opbouw pandas df
        dctMeting = {'index': indexLijst, 'bovenkant': bovenkantLijst, 'onderkant': onderkantLijst,
                     'soort': soortenLijst}
        df = pd.DataFrame(dctMeting)
        df['laagDikte'] = abs(df['bovenkant'] - df['onderkant'])
        return df

    def cleanDF(self,df,soortenGrofGef, minSlap,naam,zMv,grensHoogte):

        indexLijstSlap = []
        laagNummerLijstSlap = []
        bovenkantLijstSlap = []
        laagdikteLijstSlap = []
        slappeLaag = 0
        slappelaagNummer = 0

        for index, row in df.iterrows():
            bovenkant = df.iloc[index]['bovenkant']
            onderkant = df.iloc[index]['onderkant']
            soort = df.iloc[index]['soort']
            laagDikte = df.iloc[index]['laagDikte']


            if soort in soortenGrofGef:
                slappelaagNummer +=1
                slappeLaag = 0

            if soort not in soortenGrofGef:

                indexLijstSlap.append(index)
                slappeLaag += laagDikte

                laagNummerLijstSlap.append(slappelaagNummer)
                bovenkantLijstSlap.append(bovenkant)
                laagdikteLijstSlap.append(slappeLaag)







        dctSlap =  {'index': indexLijstSlap,'laagNummer': laagNummerLijstSlap, 'bovenkant': bovenkantLijstSlap,'laagdikte':laagdikteLijstSlap}
        dfSlap = pd.DataFrame(dctSlap)

        groupedSlap = dfSlap.groupby('laagNummer')

        dropLijst = []
        for group in groupedSlap:
            laagdikteSlap = group[1]['laagdikte'].max()
            indexWaardes = group[1]['index'].tolist()
            lijstIndexWaardes = []
            if indexWaardes:
                for item in indexWaardes:
                    lijstIndexWaardes.append(int(item))

            if laagdikteSlap < minSlap and lijstIndexWaardes:
                # print "droppen", naam
                # print lijstIndexWaardes
                for item in lijstIndexWaardes:
                    dropLijst.append(item)

        if dropLijst:
            df = df.drop(dropLijst)
            df = df.reset_index(drop=True)

        # verwijder rijen met hoogtes onder grenshoogte
        dropLijstGrens = []
        if zMv < grensHoogte:
            pass
        else:
            for index, row in df.iterrows():
                if zMv-row['onderkant'] < grensHoogte:
                    dropLijstGrens.append(index)

        if dropLijstGrens:
            df = df.drop(dropLijstGrens)
            df = df.reset_index(drop=True)




        return df

    def findValues(self,df,soortenGrofGef,maxGrof,zMv,naam,x,y):
        indexLijstGrof = []
        laagNummerLijstGrof = []
        bovenkantLijstGrof = []
        laagdikteLijstGrof = []
        groveLaag = 0
        grovelaagNummer = 0


        for index, row in df.iterrows():
            bovenkant = df.iloc[index]['bovenkant']
            onderkant = df.iloc[index]['onderkant']
            soort = df.iloc[index]['soort']
            laagDikte = df.iloc[index]['laagDikte']

            if soort in soortenGrofGef:
                indexLijstGrof.append(index)
                groveLaag += laagDikte

                laagNummerLijstGrof.append(grovelaagNummer)
                bovenkantLijstGrof.append(bovenkant)
                laagdikteLijstGrof.append(groveLaag)

            if soort not in soortenGrofGef:
                grovelaagNummer += 1
                groveLaag = 0


        dctGrof = {'index': indexLijstGrof, 'laagNummer': laagNummerLijstGrof, 'bovenkant': bovenkantLijstGrof,
                   'laagdikte': laagdikteLijstGrof}
        dfGrof = pd.DataFrame(dctGrof)




        groupedGrof = dfGrof.groupby('laagNummer')


        for group in groupedGrof:
            if group[1]['laagdikte'].max() > maxGrof:
                deklaag = round(group[1]['bovenkant'].min(), 2)
                topzand = round(zMv - abs(deklaag), 2)
                soortOnder = df.iloc[-1]['soort']
                zOnder = round(zMv - abs(df.iloc[-1]['onderkant']), 2)
                print deklaag, naam, "gelimiteerd"
                break

        # toevoegen standaard op waar zetten, tenzij lege meting
        toevoegen = True

        try:
            deklaag, topzand, soortOnder, zOnder
            indicatieTZ = "Aanwezig"
        except NameError:
            try:
###################### HIER DOORBOUWEN VOOR CHECK VANUIT ONDERKANT ############################################
                df.iloc[-1]

                soortOnder = df.iloc[-1]['soort']
                if soortOnder in soortenGrofGef:
                    dfReversed = df.iloc[::-1]

                    for index, row in dfReversed.iterrows():
                        if row['soort'] not in soortenGrofGef:
                            deklaag = round(row['onderkant'],2)
                            topzand = round(zMv-abs(deklaag),2)
                            indicatieTZ = "Mogelijk aanwezig"
                            print "Mogelijke waarde topzand gevonden, deklaag aangepast"
                            break
                try:
                    topzand
                except NameError:
                    topzand = -999
                    indicatieTZ = "Niet aanwezig"
                    deklaag = round(float(df.iloc[-1]['onderkant']), 2)


##########################################################################

                # print "Geen limiet gevonden, wel een meting", naam
                # deklaag = round(float(df.iloc[-1]['onderkant']), 2)
                # topzand = -999
                soortOnder = df.iloc[-1]['soort']
                zOnder = round(zMv - abs(df.iloc[-1]['onderkant']), 2)
            except IndexError:
                print "Lege meting", naam
                toevoegen = False





        if toevoegen is False:
            return None
        else:
            invoegen = (str(naam), zMv, deklaag, topzand, indicatieTZ, soortOnder, zOnder, (x, y))
            return invoegen












class boringMainGef(object):
    def __init__(self,files,puntenlaag, gdb):
        self.files = files
        self.puntenlaag = puntenlaag
        self.gdb = gdb

    def gefTxt(self,files):
        for gef in os.listdir(files):
            if gef.endswith(".gef"):

                ingef = os.path.join(files, gef)
                if not os.path.isfile(ingef): continue
                nieuwenaam = ingef.replace('.gef', '.txt')
                output = os.rename(ingef, nieuwenaam)
            elif gef.endswith(".GEF"):
                ingef = os.path.join(files, gef)
                if not os.path.isfile(ingef): continue
                nieuwenaam = ingef.replace('.GEF', '.txt')
                output = os.rename(ingef, nieuwenaam)




    def execute(self):
        # maak nieuwe puntenlaag in gdb
        arcpy.CreateFeatureclass_management(gdb, puntenlaag, "POINT", spatial_reference=28992)
        arcpy.AddField_management(puntenlaag, 'naam', "TEXT")
        arcpy.AddField_management(puntenlaag, 'zMv', "DOUBLE", 2, field_is_nullable="NULLABLE")
        arcpy.AddField_management(puntenlaag, 'dikteDeklaag', "DOUBLE", 2, field_is_nullable="NULLABLE")
        arcpy.AddField_management(puntenlaag, 'topZandNAP', "DOUBLE", 2, field_is_nullable="NULLABLE")
        arcpy.AddField_management(puntenlaag, 'indicatieTZ', "TEXT")
        arcpy.AddField_management(puntenlaag, 'soortOnder', "TEXT")
        arcpy.AddField_management(puntenlaag, 'zOnderNAP', "DOUBLE", 2, field_is_nullable="NULLABLE")

        cursor = arcpy.da.InsertCursor(puntenlaag,
                                       ['naam', 'zMv', 'dikteDeklaag', 'topZandNAP','indicatieTZ', 'soortOnder', 'zOnderNAP',
                                        'SHAPE@XY'])


        # gef to txt
        self.gefTxt(files)

        for file in os.listdir(files):
            boring = boringGef(file)
            file = boring.readFile(file)
            lines = file[0]
            naam = file[1]
            base = boring.getBase(lines)
            if base is not None:
                x, y, zMv, lijstMetingen, sep = base
                dfRaw = boring.createDF(lijstMetingen, sep)
                dfClean = boring.cleanDF(dfRaw, soortenGrofGef, minSlap, naam,zMv,grensHoogte)
                gisLayer = boring.findValues(dfClean, soortenGrofGef, maxGrof, zMv, naam, x, y)

                if gisLayer is None or zMv < grensHoogte:
                    pass
                else:
                    cursor.insertRow(gisLayer)
                    print naam + " is toegevoegd"
            else:
                pass








test = boringMainGef(files,puntenlaag,gdb)
test.execute()


