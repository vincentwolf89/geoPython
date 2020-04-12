import os
import arcpy
import pandas as pd
import xml.dom.minidom as minidom


files = r'C:\Users\Vincent\Desktop\testmapBoringenXML'
arcpy.env.workspace = r'D:\GoogleDrive\WSRL\goTest.gdb'
gdb = r'D:\GoogleDrive\WSRL\goTest.gdb'
arcpy.env.overwriteOutput = True


puntenlaag = 'testBoringenXml5m'

soortenGrofGef = ['Z','G']
soortenGrofXml = ['matigSiltigZand', 'zwakSiltigZand','sterkZandigeLeem','zwakZandigeLeem']
maxGrof = 0.5
minSlap = 0.5

class boringXml(object):
    def __init__(self, file):
        self.file = file

    def readFile(self, file):
        naam = file.split('.xml')[0]
        inXml = os.path.join(files, file)
        xml = minidom.parse(inXml)

        return xml, naam

    def getBase(self,xml):
        # get location coordinates from xml
        locations = xml.getElementsByTagName("ns8:deliveredLocation")
        for location in locations:
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
                zMv = float(hoogte.childNodes[0].nodeValue)
            except IndexError:
                zMv = -999


        # get einddiepte from xml
        eindLaag = xml.getElementsByTagName("ns9:endDepth")
        for eindHoogte in eindLaag:
            try:
                zOnderRel = float(eindHoogte.childNodes[0].nodeValue)
            except IndexError:
                zOnderRel= -999
                print "Geen eindhoogte gevonde bij xml: {}".format(naam)

        # bereken einddiepte in m NAP
        if zMv is not -999 and zOnderRel is not -999:
            zOnder = zMv-abs(zOnderRel)
        else:
            zOnder = None


        return x, y, zMv

    def createDF(self,xml):
        # create pandas dataframe with layers
        index = 0
        indexLijst = []
        bovenkantLijst = []
        onderkantLijst = []
        soortenLijst = []

        bodemLagen = xml.getElementsByTagName("ns9:soilLayer")

        for bodemLaag in bodemLagen:

            bovenkanten = bodemLaag.getElementsByTagName("ns9:upperBoundary")
            onderkanten = bodemLaag.getElementsByTagName("ns9:lowerBoundary")
            soorten = bodemLaag.getElementsByTagName("ns9:standardSoilName") # eerst horizonCode

            for item in soorten:
                soortenLijst.append(item.childNodes[0].nodeValue)
                test = item.childNodes[0].nodeValue
                # if test in soorten_grof_xml:
                #     print file
                break

            for item in bovenkanten:
                bovenkantLijst.append(float(item.childNodes[0].nodeValue))

            for item in onderkanten:
                onderkantLijst.append(float(item.childNodes[0].nodeValue))
                indexLijst.append(index)

                index += 1

        # alleen doorgaan als voor alles een waarde wordt gevonden
        if len(soortenLijst) == len(onderkantLijst) and len(onderkantLijst) == len(bovenkantLijst):

            # opbouw pandas df
            dctMeting = {'index': indexLijst, 'bovenkant': bovenkantLijst, 'onderkant': onderkantLijst,
                         'soort': soortenLijst}
            df = pd.DataFrame(dctMeting)
            df['laagDikte'] = abs(df['bovenkant'] - df['onderkant'])

            return df

    def cleanDF(self,df,soortenGrofXml, minSlap,naam):

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


            if soort in soortenGrofXml:
                slappelaagNummer +=1
                slappeLaag = 0

            if soort not in soortenGrofXml:

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
                # print deklaag, naam, "gelimiteerd"
                break
            else:
                deklaag = round(float(df.iloc[-1]['onderkant']), 2)
                topzand = -999
                soortOnder = df.iloc[-1]['soort']
                zOnder = round(zMv - abs(df.iloc[-1]['onderkant']), 2)

                # print deklaag, naam, "geen limiet"
                break

        try:
            deklaag, topzand, soortOnder, zOnder
        except NameError:
            deklaag = round(float(df.iloc[-1]['onderkant']), 2)
            topzand = -999
            soortOnder = df.iloc[-1]['soort']
            zOnder = round(zMv - abs(df.iloc[-1]['onderkant']), 2)

        # print group[1]['laagdikte'].max(), type(group[1]['index'])
        # for item in group[1]['index']:
        #     print item

        print deklaag, naam




        invoegen = (str(naam), zMv, deklaag, topzand, soortOnder, zOnder, (x, y))
        return invoegen


class boringMainXml(object):
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
        arcpy.AddField_management(puntenlaag, 'soortOnder', "TEXT")
        arcpy.AddField_management(puntenlaag, 'zOnderNAP', "DOUBLE", 2, field_is_nullable="NULLABLE")

        cursor = arcpy.da.InsertCursor(puntenlaag,
                                       ['naam', 'zMv', 'dikteDeklaag', 'topZandNAP', 'soortOnder', 'zOnderNAP',
                                        'SHAPE@XY'])





        for file in os.listdir(files):
            boring = boringXml(file)
            file = boring.readFile(file)
            xml = file[0]
            naam = file[1]
            base = boring.getBase(xml)
            x, y, zMv = base

            dfRaw = boring.createDF(xml)
            dfClean = boring.cleanDF(dfRaw, soortenGrofXml, minSlap, naam)
            gisLayer = boring.findValues(dfClean, soortenGrofXml, maxGrof, zMv, naam, x, y)
            # print dfClean
            cursor.insertRow(gisLayer)
            print naam+" is toegevoegd"


test = boringMainXml(files,puntenlaag,gdb)
test.execute()
