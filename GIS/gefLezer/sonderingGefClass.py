import os
import arcpy
import pandas as pd


files = r'C:\Users\Vincent\Desktop\testmapSondering'
arcpy.env.workspace = r'D:\GoogleDrive\WSRL\goTest.gdb'
gdb = r'D:\GoogleDrive\WSRL\goTest.gdb'
arcpy.env.overwriteOutput = True





puntenlaag = 'testSonderingen'

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
        # lagen zijn 0
        deklaag = 0
        groveLaag = 0

        # checker voor aanwezigheid significante grove laag
        grof = None
        onderGrof = None
        # andere_sep = False

        # definieer lege lijsten
        bovenkant = []
        cws = []
        bovenkantGrof = []

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

        # onderste rij repareren
        defaultLaagDikte = df.iloc[0]['laagDikte']
        for index, row in df.iterrows():
            if pd.isna(row['onderkant']):
                df.at[index, 'laagDikte'] = defaultLaagDikte
                df.at[index,'onderkant'] = (df.iloc[index]['bovenkant'])+defaultLaagDikte


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

        for group in groupedSlap:
            laagdikteSlap = group[1]['laagdikte'].max()
            indexWaardes = group[1]['index'].tolist()
            lijstIndexWaardes = []
            if indexWaardes:
                for item in indexWaardes:
                    lijstIndexWaardes.append(int(item))

            if laagdikteSlap < minSlap:
                print "droppen", naam
                df = df.drop(lijstIndexWaardes)
                df = df.reset_index()
        return df



class sonderingMainGef(object):
    def __init__(self,files,puntenlaag, gdb):
        self.files = files
        self.puntenlaag = puntenlaag
        self.gdb = gdb



    def execute(self):


        for file in os.listdir(files):
            sondering = sonderingGef(file)
            file = sondering.readFile(file)
            lines = file[0]
            naam = file[1]
            base = sondering.getBase(lines)
            x, y, zMv, lijstMetingen, sep = base

            dfRaw = sondering.createDF(lijstMetingen, sep)





test = sonderingMainGef(files,puntenlaag,gdb)
test.execute()
