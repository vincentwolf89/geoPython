import arcpy

arcpy.env.workspace = r'D:\GoogleDrive\WSRL\sprok_sterrenschans.gdb'
arcpy.env.overwriteOutput = True

from basisfuncties import generate_profiles

code = 'code'
trajectlijn = 'trajectlijn'
dijkpalen = 'dpSprok'
dijkpaalNaam = 'dpNaam'

# in te lezen excel





class opbouw(object):
    def __init__(self, trajectlijn,code,dijkpalen,dijkpaalNaam):
        self.trajectlijn = trajectlijn
        self.code = code
        self.dijkpalen = dijkpalen
        self.profielen = "tempProfielen"
        self.trajectlijnSplit = "splitTrajectlijn"
        self.dijkpaalNaam = dijkpaalNaam

    def splitTrajectlijn(self):
        # profielen iedere 2 m
        generate_profiles(2,20,20,self.trajectlijn,self.code,0,self.profielen)
        # near vanuit dp naar profielen
        arcpy.CopyFeatures_management(self.dijkpalen, "tempDp")
        # tempDp =arcpy.MakeFeatureLayer_management(self.dijkpalen, "tempDp")
        arcpy.Near_analysis("tempDp", self.profielen, "", "NO_LOCATION", "NO_ANGLE", "PLANAR")

        # itereer over dp en haal lijst met NEAR_FID op
        lijstProfielen = []
        with arcpy.da.SearchCursor("tempDp","NEAR_FID") as cursor:
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
        # split trajectlijn op punten
        arcpy.SplitLineAtPoint_management(self.trajectlijn, "tempIsect", self.trajectlijnSplit, 0.2)

        ## koppel dp aan startpunt lijn ##
        # join field van dpcode
        arcpy.JoinField_management("tempIsect", "TARGET_FID", "tempDp", "NEAR_FID",
                                   self.dijkpaalNaam)



        # punten op startpunten van trajectlijnsplit
        arcpy.FeatureVerticesToPoints_management(self.trajectlijnSplit, "tempStartPoints", "START")
        # join punten aan tempIsect
        arcpy.SpatialJoin_analysis("tempStartPoints", "tempIsect", "tempJoin",
                                   "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "CLOSEST", "", "")

        # join start dp aan trajectlijnsplit

        arcpy.JoinField_management(self.trajectlijnSplit, "OBJECTID", "tempJoin", "OBJECTID",
                                   self.dijkpaalNaam)




    def makeTrajectory(self):

        # calculate "tot" field
        arcpy.CalculateField_management(self.trajectlijnSplit, "tot", "!Shape_Length!", "PYTHON")
        # create route splittrajectlijn
        arcpy.CreateRoutes_lr(self.trajectlijnSplit, self.dijkpaalNaam, "tempRoutes", "TWO_FIELDS", "van", "tot",
                              "", "1", "0", "IGNORE", "INDEX")
        # route event layer voor lokaliseren punten
        routeLayer = arcpy.MakeRouteEventLayer_lr("tempRoutes", self.dijkpaalNaam, "dvIndelingTest", "code POINT offsetVan",
                                     "tempLayerPuntenFL", "", "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE",
                                     "LEFT", "POINT")

        arcpy.CopyFeatures_management(routeLayer, "tempLayerPunten")
        del routeLayer
        # split trajectlijn
        arcpy.SplitLineAtPoint_management(self.trajectlijn, "tempLayerPunten", "tempIndeling", 0.5)

        # join van field
        arcpy.FeatureVerticesToPoints_management("tempIndeling", "tempStartPoints", "START")
        arcpy.SpatialJoin_analysis("tempStartPoints", "tempLayerPunten", "tempJoin",
                                   "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "CLOSEST", "", "")

        arcpy.JoinField_management("tempIndeling", "OBJECTID", "tempJoin", "OBJECTID", "dpVan")


        # join tot field
        arcpy.AlterField_management("tempLayerPunten", "dpVan", "dpTot", "", "TEXT", "50", "NULLABLE", "false")
        arcpy.FeatureVerticesToPoints_management("tempIndeling", "tempEndPoints", "END")
        arcpy.SpatialJoin_analysis("tempEndPoints", "tempLayerPunten", "tempJoin",
                                   "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "CLOSEST", "", "")

        arcpy.JoinField_management("tempIndeling", "OBJECTID", "tempJoin", "OBJECTID",
                                   "dpTot")

        # join dv field
        arcpy.JoinField_management("tempIndeling", "dpVan", "dvIndelingTest", "dpVan", "dV")

        # clean up
        existingFields = arcpy.ListFields("tempIndeling")
        neededFields = ["OBJECTID", "SHAPE","SHAPE_Length", "dV","dpVan", "dpTot"]
        for field in existingFields:
            if field.name not in neededFields:
                arcpy.DeleteField_management("tempIndeling", field.name)

        with arcpy.da.UpdateCursor("tempIndeling",["dpVan","dpTot"]) as cursor:
            for row in cursor:
                if row[0] == row[1]:
                    cursor.deleteRow()
                else:
                    pass

















test = opbouw(trajectlijn,code,dijkpalen,dijkpaalNaam)
test.splitTrajectlijn()
test.makeTrajectory()
