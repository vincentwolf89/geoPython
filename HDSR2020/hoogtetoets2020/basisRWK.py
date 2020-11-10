import arcpy

arcpy.env.workspace = r'D:\Projecten\HDSR\2019\oplevering_v3.1\oplevering_v3.1.gdb'


########### stappen deelklus ###########

# 1: bepaal afstand traject

# 2: bepaal gemiddeld verval : gemiddelde kerende hoogte (?)
# 3: bepaal afstand voldoende: aantal voldoende profielen*tussenafstand profielen (25m)
# 4: bepaal afstand onvoldoende: aantal onvoldoende profielen*tussenafstand profielen (25m)
# 5: bepaal type kering: handmatig



invoerVelden = ["SHAPE@","Naam","Shape_Length"]
profielVelden = ["profielnummer"]




class basisProces(object):

    def __init__(self, trajectenInvoer):
        self.trajecten = (trajectenInvoer)
        self.cursor = arcpy.da.UpdateCursor(self.trajecten, invoerVelden)

    def execute(self):


        # lijst = []

        for row in self.cursor:

            # bepaal id van traject
            idTraject = row[1]
            

            # open profielenfc en itereer over alle profielen binnen traject
            profielen = "profielen_{}".format(idTraject)
            
            profielCursor = arcpy.da.SearchCursor(profielen, profielVelden)
            
            for row in profielCursor:
                # bepaal BIT-hoogte
                # bepaal kruinhoogte
                # bepaal kerende hoogte
                # bepaal voldoende/onvoldoende


            




            # print (idTraject)
            # row[3] = row[2]
            # self.cursor.updateRow(row)


            # geometrien per waterloop als uitvoerlagen
            # waterloop = "waterloop" + str(idWaterloop)
            # bodemLijn = "waterloopBodemlijn" + str(idWaterloop)
            # bufferLijn = "waterloopBufferlijn" + str(idWaterloop)
            # waterloopLijn = "waterloopLijn" + str(idWaterloop)




class
if __name__ == "__main__":

    test = basisProces("RWK_areaal_2024")
    test.execute()