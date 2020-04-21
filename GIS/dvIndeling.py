import arcpy

arcpy.env.workspace = r'D:\GoogleDrive\WSRL\sprok_sterrenschans.gdb'
arcpy.env.overwriteOutput = True

from basisfuncties import generate_profiles

code = 'code'
trajectlijn = 'trajectlijn'
dijkpalen = 'dpSprok'




class opbouw(object):
    def __init__(self, trajectlijn,code,dijkpalen):
        self.trajectlijn = trajectlijn
        self.code = code
        self.dijkpalen = dijkpalen
        self.profielen = "tempProfielen"

    def splitTrajectlijn(self):
        # profielen iedere 2 m
        generate_profiles(2,20,20,self.trajectlijn,self.code,0,self.profielen)
        # near vanuit dp naar profielen
        tempDp =arcpy.MakeFeatureLayer_management(self.dijkpalen, "tempDp")
        arcpy.Near_analysis(tempDp, self.profielen, "", "NO_LOCATION", "NO_ANGLE", "PLANAR")

        # itereer over dp en haal lijst met NEAR_FID op
        lijstProfielen = []
        with arcpy.da.SearchCursor(tempDp,"NEAR_FID") as cursor:
            for row in cursor:
                lijstProfielen.append(row[0])
        del cursor
        # verwijder profielen die niet in de lijst voorkomen
        with arcpy.da.UpdateCursor(self.profielen,"OID@") as cursor:
            for row in cursor:
                if int(row[0]) not in lijstProfielen:
                    cursor.deleteRow()
                else:
                    pass
        del cursor

        # intersect op punten profielen en trajectlijn
        arcpy.Intersect_analysis([self.profielen,self.trajectlijn],"tempIsect","ALL","","POINT")


test = opbouw(trajectlijn,code,dijkpalen)
test.splitTrajectlijn()
