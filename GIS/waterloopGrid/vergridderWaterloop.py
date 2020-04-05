import arcpy
from geoproces_Waterloop import gp

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r'C:\Users\Vincent\Documents\ArcGIS\testDB.gdb'

global bufferBuitenkant, rasterAhn, codeWaterloop

bufferBuitenkant = 3
minLengteSegment = 15
distMiniBuffer = -0.2
tolerance = 0.3
bodemDiepte = 1
bodemDiepteSmal = 0.5
maxBreedteSmal = 2
standaardTalud = 0.5


smooth = "10 Meters"
rasterAhn = r'C:\Users\Vincent\Desktop\ahn3clip_safe'
codeWaterloop = "id_string"

class Basis(object):

    def __init__(self, waterlopen):
        self.waterlopen = waterlopen
        self.cursor = arcpy.da.SearchCursor(waterlopen, ['SHAPE@', codeWaterloop])

    def execute(self):

        for row in self.cursor:

            idWaterloop = row[1]
            waterloop = "waterloop" + str(idWaterloop)
            bodemLijn = "waterloopBodemlijn" + str(idWaterloop)
            bufferLijn = "waterloopBufferlijn" + str(idWaterloop)
            where = '"' + codeWaterloop + '" = ' + "'" + str(idWaterloop) + "'"
            arcpy.Select_analysis(self.waterlopen, waterloop, where)
            # voeg veld toe voor z_nap
            arcpy.AddField_management(waterloop,"z_nap","DOUBLE", 2, field_is_nullable="NULLABLE")


            # geoprocessing
            gpObject = gp(waterloop,idWaterloop,bodemLijn)

            # maak raster buitenkant
            rasterBuitenkant = gpObject.rasterBuitenkant(waterloop,bufferBuitenkant,rasterAhn)

            # smooth geometrie
            waterloopSmooth = gpObject.smoothWaterloop(waterloop,smooth)
            waterloopLineSmooth = waterloopSmooth[0] # smooth line
            waterloopPolySmooth = waterloopSmooth[1] # smooth poly

            # bepaal insteek (templayer)
            insteek = gpObject.bepaalInsteek(waterloop,rasterBuitenkant, minLengteSegment, codeWaterloop, waterloopLineSmooth)
            insteekLijn = insteek[0]
            insteekHoogte = insteek[1]

            # bepaal bodemlijn (geen templayer ivm check)
            gpObject.bepaalBodemlijn(waterloop,insteekLijn, waterloopPolySmooth, distMiniBuffer, tolerance, bodemLijn)

            # bepaal minimale breedte en bodemhoogte
            bodem = gpObject.bepaalMinimaleBreedte(waterloop, insteekLijn, bodemLijn, insteekHoogte, bodemDiepte, bodemDiepteSmal,maxBreedteSmal)
            _bodemDiepte = bodem[0]
            _bodemHoogte = bodem[1]

            # buffer waterloop
            gpObject.bufferWaterloop(waterloop,waterloopPolySmooth,standaardTalud,_bodemDiepte,_bodemHoogte,insteekLijn,bufferLijn)




        # print "Buiten loop"



if __name__ == "__main__":

    test = Basis("testvlakken")
    test.execute()

# test.printResult()