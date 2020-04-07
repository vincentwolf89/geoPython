import arcpy
from geoprocesWaterloop import gpWaterloop, gpGeneral

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r'D:\GoogleDrive\WSRL\testWaterlopen.gdb'

global bufferBuitenkant, rasterAhn, codeWaterloop

bufferBuitenkant = 3
minLengteSegment = 15
distMiniBuffer = -0.2
tolerance = 0.3
bodemDiepte = 1
bodemDiepteSmal = 0.5
maxBreedteSmal = 3
standaardTalud = 0.5


smooth = "10 Meters"
rasterAhn = r'D:\Projecten\WSRL\grote_data\ahn3SProk.gdb\ahn3ClipSprok'
codeWaterloop = "id_string"

class Basis(object):

    def __init__(self, waterlopenInvoer):
        self.waterlopen = gpGeneral().aggregateInput(waterlopenInvoer)
        # self.waterlopen = gpBasis(waterlopenInvoer).aggregateInput()
        self.cursor = arcpy.da.SearchCursor(self.waterlopen, ['SHAPE@', codeWaterloop])

    def execute(self):


        # lijst met totaal aantal rasters
        rasterLijst = []

        for row in self.cursor:

            # id waterloop
            idWaterloop = row[1]


            # geometrien per waterloop als uitvoerlagen
            waterloop = "waterloop" + str(idWaterloop)
            bodemLijn = "waterloopBodemlijn" + str(idWaterloop)
            bufferLijn = "waterloopBufferlijn" + str(idWaterloop)
            waterloopLijn = "waterloopLijn" + str(idWaterloop)
            waterloopLijn3D = "waterloopLijn3D" + str(idWaterloop)
            tin = "D:/GoogleDrive/WSRL/tin/waterloop"+str(idWaterloop)
            rasterWaterloop = "waterloopRaster" + str(idWaterloop)

            # selectie waterlopen
            where = '"' + codeWaterloop + '" = ' + "'" + str(idWaterloop) + "'"
            arcpy.Select_analysis(self.waterlopen, waterloop, where)

            # voeg veld toe voor z_nap
            arcpy.AddField_management(waterloop,"z_nap","DOUBLE", 2, field_is_nullable="NULLABLE")

            ## geoprocessing ##
            gpObject = gpWaterloop(waterloop,idWaterloop,bodemLijn)

            # maak raster buitenkant
            rasterBuitenkant = gpObject.rasterBuitenkant(waterloop,bufferBuitenkant,rasterAhn)

            # smooth geometrie
            waterloopSmooth = gpObject.smoothWaterloop(waterloop,smooth)
            waterloopLineSmooth = waterloopSmooth[0] # smooth line
            waterloopPolySmooth = waterloopSmooth[1] # smooth poly

            # bepaal insteek (templayer)
            insteekHoogte = gpObject.bepaalInsteek(waterloop,rasterBuitenkant, minLengteSegment, codeWaterloop, waterloopLineSmooth,waterloopLijn)
            bodemLijn = gpObject.bepaalBodemlijn(waterloop,waterloopLijn, waterloopPolySmooth, distMiniBuffer, tolerance, bodemLijn)



            # check of bodemlijn bestaat en geometrien bevat
            if insteekHoogte is not None and bodemLijn is not None:

                # bepaal minimale breedte en bodemhoogte
                bodem = gpObject.bepaalMinimaleBreedte(waterloop, waterloopLijn, bodemLijn, insteekHoogte, bodemDiepte, bodemDiepteSmal,maxBreedteSmal)
                _bodemDiepte = bodem[0]
                _bodemHoogte = bodem[1]

                # buffer waterloop
                gpObject.bufferWaterloop(waterloop,waterloopPolySmooth,standaardTalud,_bodemDiepte,_bodemHoogte,waterloopLijn,bufferLijn)

                # genereer raster van drie geometrien (insteek-talud en bodemlijn)
                gpObject.maakRaster(waterloop,waterloopLijn, bufferLijn, bodemLijn,waterloopLijn3D, tin,rasterWaterloop, waterloopPolySmooth, rasterLijst)
            else:
                print "Geen raster gemaakt voor {} vanwege ontbreken onderdeel/onderdelen".format(waterloop)


        # maak totaalraster
        if rasterLijst:
            gpGeneral().insertAhn(rasterLijst,self.waterlopen,rasterAhn)
        else:
            pass








if __name__ == "__main__":

    setWaterlopen = Basis("SprokWaterlopen")
    setWaterlopen.execute()

