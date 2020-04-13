import os
import arcpy
import pandas as pd


files = r'C:\Users\Vincent\Desktop\GO_WoS\sonderingen'
arcpy.env.workspace = r'D:\GoogleDrive\WSRL\goTest.gdb'
gdb = r'D:\GoogleDrive\WSRL\goTest.gdb'
arcpy.env.overwriteOutput = True





puntenlaag = 'testSondering'

soortenGrofGef = ['Z','G']
maxGrof = 2
minSlap = 0.5

maxCws = 5

class sonderingGef(object):
    def __init__(self,file):
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
            return "Error"

    def createDF(self, lijstMetingen, sep):

        # definieer lege lijsten
        bovenkant = []
        cws = []


        for item in lijstMetingen:

            onderdelen = item.split("{}".format(sep))

            bovenkant_ = float(onderdelen[0])
            cws_ = float(onderdelen[1])

            bovenkant.append(bovenkant_)
            cws.append(cws_)

        # opbouw pandas df
        dctMeting = {'bovenkant': bovenkant, 'cws': cws}
        df = pd.DataFrame(dctMeting)
        df['onderkant'] = df['bovenkant'].shift(-1)
        # df['cws_onder'] = df['cws'].shift(-1)
        df['laagDikte'] = abs(df['bovenkant']-df['onderkant'])

        # df repareren
        defaultLaagDikte = df.iloc[0]['laagDikte']
        dropLijst = []
        for index, row in df.iterrows():
            if pd.isna(row['onderkant']):
                df.at[index, 'laagDikte'] = defaultLaagDikte
                df.at[index,'onderkant'] = (df.iloc[index]['bovenkant'])+defaultLaagDikte
            if row['cws'] < 0:
                dropLijst.append(index)
            #     df.at[index, 'cws'] = 0
            # if round(row['cws'],2) == 0.00:

        if dropLijst:
            df = df.drop(dropLijst)
            df = df.reset_index(drop=True)
        return df


    def cleanDF(self,df,maxCws, minSlap,naam):

        indexLijstSlap = []
        laagNummerLijstSlap = []
        bovenkantLijstSlap = []
        laagdikteLijstSlap = []
        slappeLaag = 0
        slappelaagNummer = 0

        for index, row in df.iterrows():
            bovenkant = df.iloc[index]['bovenkant']
            onderkant = df.iloc[index]['onderkant']
            cws = df.iloc[index]['cws']
            laagDikte = df.iloc[index]['laagDikte']


            if cws > maxCws:
                slappelaagNummer +=1
                slappeLaag = 0

            if cws < maxCws:

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
                # df = df.drop(lijstIndexWaardes)
                # df = df.reset_index(drop=True)
        if dropLijst:
            df = df.drop(lijstIndexWaardes)
            df = df.reset_index(drop=True)
        return df

    def findValues(self,df,maxCws,maxGrof,zMv,naam,x,y):
        indexLijstGrof = []
        laagNummerLijstGrof = []
        bovenkantLijstGrof = []
        laagdikteLijstGrof = []
        groveLaag = 0
        grovelaagNummer = 0


        for index, row in df.iterrows():
            bovenkant = df.iloc[index]['bovenkant']
            onderkant = df.iloc[index]['onderkant']
            cws = df.iloc[index]['cws']

            laagDikte = df.iloc[index]['laagDikte']

            if cws > maxCws:

                indexLijstGrof.append(index)
                groveLaag += laagDikte

                laagNummerLijstGrof.append(grovelaagNummer)
                bovenkantLijstGrof.append(bovenkant)
                laagdikteLijstGrof.append(groveLaag)

            if cws < maxCws:

                grovelaagNummer += 1
                groveLaag = 0


        dctGrof = {'index': indexLijstGrof, 'laagNummer': laagNummerLijstGrof, 'bovenkant': bovenkantLijstGrof,
                   'laagdikte': laagdikteLijstGrof}
        dfGrof = pd.DataFrame(dctGrof)





        groupedGrof = dfGrof.groupby('laagNummer')


        for group in groupedGrof:
            maxDikte = group[1]['laagdikte'].max()
            if maxDikte > maxGrof:
                print maxDikte
                deklaag = round(group[1]['bovenkant'].min(), 2)
                topzand = round(zMv - abs(deklaag), 2)
                soortOnder = df.iloc[-1]['cws']
                zOnder = round(zMv - abs(df.iloc[-1]['onderkant']), 2)
                print deklaag, naam, "gelimiteerd"
                break



        try:
            deklaag, topzand, soortOnder, zOnder
        except NameError:
            print "Geen limiet gevonden"
            deklaag = round(float(df.iloc[-1]['onderkant']), 2)
            topzand = -999
            soortOnder = df.iloc[-1]['cws']
            zOnder = round(zMv - abs(df.iloc[-1]['onderkant']), 2)





        invoegen = (str(naam), zMv, deklaag, topzand, soortOnder, zOnder, (x, y))
        return invoegen



class sonderingMainGef(object):
    def __init__(self,files,puntenlaag, gdb):
        self.files = files
        self.puntenlaag = puntenlaag
        self.gdb = gdb



    def execute(self):

        # maak nieuwe puntenlaag in gdb
        arcpy.CreateFeatureclass_management(gdb, puntenlaag, "POINT", spatial_reference=28992)
        arcpy.AddField_management(puntenlaag, 'naam', "TEXT")
        arcpy.AddField_management(puntenlaag, 'zMv', "DOUBLE", 2, field_is_nullable="NULLABLE")
        arcpy.AddField_management(puntenlaag, 'dikteDeklaag', "DOUBLE", 2, field_is_nullable="NULLABLE")
        arcpy.AddField_management(puntenlaag, 'topZandNAP', "DOUBLE", 2, field_is_nullable="NULLABLE")
        arcpy.AddField_management(puntenlaag, 'cwsOnder', "TEXT")
        arcpy.AddField_management(puntenlaag, 'zOnderNAP', "DOUBLE", 2, field_is_nullable="NULLABLE")

        cursor = arcpy.da.InsertCursor(puntenlaag,
                                       ['naam', 'zMv', 'dikteDeklaag', 'topZandNAP', 'cwsOnder', 'zOnderNAP',
                                        'SHAPE@XY'])


        for file in os.listdir(files):
            sondering = sonderingGef(file)
            file = sondering.readFile(file)
            lines = file[0]
            naam = file[1]
            base = sondering.getBase(lines)
            x, y, zMv, lijstMetingen, sep = base

            dfRaw = sondering.createDF(lijstMetingen, sep)

            dfClean = sondering.cleanDF(dfRaw,maxCws,minSlap,naam)
            gisLayer = sondering.findValues(dfClean, maxCws, maxGrof, zMv, naam, x, y)

            cursor.insertRow(gisLayer)
            print naam + " is toegevoegd"


test = sonderingMainGef(files,puntenlaag,gdb)
test.execute()
