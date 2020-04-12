import os
import arcpy
import pandas as pd
import xml.dom.minidom as minidom


files = r'C:\Users\Vincent\Desktop\testmapXml'
arcpy.env.workspace = r'D:\GoogleDrive\WSRL\goTest.gdb'
gdb = r'D:\GoogleDrive\WSRL\goTest.gdb'
arcpy.env.overwriteOutput = True


puntenlaag = 'testBoringen5m'

soortenGrofGef = ['Z','G']
soortenGrofXml = ['matigSiltigZand', 'zwakSiltigZand','sterkZandigeLeem','zwakZandigeLeem']
maxGrof = 2
maxSlap = 0.5

class boringXml(object):
    def __init__(self, file):
        self.file = file

    def readFile(self, file):
        naam = file.split('.xml')[0]
        inXml = os.path.join(files, file)
        xml = minidom.parse(inXml)

        return xml

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


        print x,y,zMv

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
            print df
            return df


class boringMainXml(object):
    def __init__(self,files,puntenlaag, gdb):
        self.files = files
        self.puntenlaag = puntenlaag
        self.gdb = gdb

    def execute(self):
        # # maak nieuwe puntenlaag in gdb
        # arcpy.CreateFeatureclass_management(gdb, puntenlaag, "POINT", spatial_reference=28992)
        # arcpy.AddField_management(puntenlaag, 'naam', "TEXT")
        # arcpy.AddField_management(puntenlaag, 'zMv', "DOUBLE", 2, field_is_nullable="NULLABLE")
        # arcpy.AddField_management(puntenlaag, 'dikteDeklaag', "DOUBLE", 2, field_is_nullable="NULLABLE")
        # arcpy.AddField_management(puntenlaag, 'topZandNAP', "DOUBLE", 2, field_is_nullable="NULLABLE")
        # arcpy.AddField_management(puntenlaag, 'soortOnder', "TEXT")
        # arcpy.AddField_management(puntenlaag, 'zOnderNAP', "DOUBLE", 2, field_is_nullable="NULLABLE")
        #
        # cursor = arcpy.da.InsertCursor(puntenlaag,
        #                                ['naam', 'zMv', 'dikteDeklaag', 'topZandNAP', 'soortOnder', 'zOnderNAP',
        #                                 'SHAPE@XY'])





        for file in os.listdir(files):
            boring = boringXml(file)
            xml = boring.readFile(file)
            boring.getBase(xml)
            boring.createDF(xml)
            # naam = file[1]
            # base = boring.getBase(lines)
            # x, y, zMv, lijstMetingen, sep = base

test = boringMainXml(files,puntenlaag,gdb)
test.execute()
