import arcpy
from geoproces import gpWaterloop

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r'C:\Users\Vincent\Documents\ArcGIS\testDB.gdb'

global bufferBuitenkant, rasterAhn, codeWaterloop

bufferBuitenkant = 3
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
            where = '"' + codeWaterloop + '" = ' + "'" + str(idWaterloop) + "'"
            arcpy.Select_analysis(self.waterlopen, waterloop, where)
            # voeg veld toe voor z_nap
            arcpy.AddField_management(waterloop,"z_nap","DOUBLE", 2, field_is_nullable="NULLABLE")


            # geoprocessing
            gpObject = gpWaterloop(waterloop,idWaterloop)

            rasterBuitenkant = gpObject.rasterBuitenkant(bufferBuitenkant,rasterAhn)
            test = gpObject.printTest(rasterBuitenkant)





        # print "Buiten loop"



if __name__ == "__main__":

    test = Basis("testvlakken")
    test.execute()

# test.printResult()