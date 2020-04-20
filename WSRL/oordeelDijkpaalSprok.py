import arcpy

arcpy.env.workspace = r'D:\GoogleDrive\WSRL\sprok_sterrenschans.gdb'
arcpy.env.overwriteOutput = True

bufferDist = 100

class koppelCat(object):
    def __init__(self,trajectOordeelIn, bufferDist, uitvoerPunten,dijkpalen):
        self.trajectOordeelIn = trajectOordeelIn
        self.trajectOordeeluit = "trajectOordeelCat"
        self.uitvoerPunten = uitvoerPunten
        self.bufferDist = bufferDist
        self.dijkpalen = dijkpalen

    def trajectCatKoppeling(self):
        # add field for categorie oordeel
        arcpy.AddField_management(self.trajectOordeelIn, 'oordeelCat', "TEXT", field_length=50)
        # feature to point
        arcpy.FeatureVerticesToPoints_management(self.trajectOordeelIn, "tempSplitPunten", "START")
        # split line at point
        arcpy.SplitLineAtPoint_management(self.trajectOordeelIn, "tempSplitPunten", self.trajectOordeeluit, 0.5)

        dctOordeel = {}

        # open cursor
        cursor = arcpy.da.UpdateCursor(self.trajectOordeeluit, ['SHAPE@','OID@', 'oordeelCat','eindoordeelPiping'])
        for row in cursor:
            segment = row[0]
            # buffer segment
            arcpy.Buffer_analysis(segment, "tempBuffer", (bufferDist), "RIGHT", "FLAT", "NONE", "", "PLANAR")

            # select all outputpoints in buffer
            arcpy.MakeFeatureLayer_management(self.uitvoerPunten, "uitvoerpuntenFL")
            arcpy.SelectLayerByLocation_management("uitvoerpuntenFL", "INTERSECT", "tempBuffer", 0,
                                                   "NEW_SELECTION", "NOT_INVERT")
            arcpy.CopyFeatures_management("uitvoerpuntenFL", "tempBufferPunten")

            # get most frequent oordeel
            oordeel = str(row[3])
            freq = 0
            voldoende = ["Iv", "IIv", "IIIv"]

            if oordeel == "voldoende":
                arcpy.Frequency_analysis("tempBufferPunten", "tempFreq", "Eindoordeel", "")
                with arcpy.da.UpdateCursor("tempFreq",['Eindoordeel']) as tCursor:
                    for tRow in tCursor:
                        if tRow[0] not in voldoende:
                            tCursor.deleteRow()
                        else:
                            pass
                with arcpy.da.SearchCursor("tempFreq",["FREQUENCY","Eindoordeel"]) as fCursor:
                    for fRow in fCursor:
                        if fRow[0] > freq:
                            freq = fRow[0]
                            oordeel = fRow[1]
                        else:
                            break
            else:

                arcpy.Frequency_analysis("tempBufferPunten", "tempFreq", "Eindoordeel", "")
                with arcpy.da.UpdateCursor("tempFreq",['Eindoordeel']) as tCursor:
                    for tRow in tCursor:
                        if tRow[0] in voldoende:
                            tCursor.deleteRow()
                        else:
                            pass
                with arcpy.da.SearchCursor("tempFreq",["FREQUENCY","Eindoordeel"]) as fCursor:
                    for fRow in fCursor:
                        if fRow[0] > freq:
                            freq = fRow[0]
                            oordeel = fRow[1]
                        else:
                            break

            print freq, oordeel

            del fCursor, tCursor
            oid = int(row[1])
            dctOordeel[oid] = str(oordeel)




        del cursor

        with arcpy.da.UpdateCursor(self.trajectOordeeluit,["OID@","oordeelCat"]) as cursor:
            for row in cursor:
                row[1] = dctOordeel[row[0]]
                cursor.updateRow(row)

        # join dijkpalen to nearest oordeel from line
        arcpy.SpatialJoin_analysis(self.dijkpalen, self.trajectOordeeluit, "oordeelDp", "JOIN_ONE_TO_ONE", "KEEP_ALL", "",
                                   match_option="CLOSEST")


test = koppelCat("oordeel_hoofd_v3", bufferDist, "oordeelHoofd","dpSprok")
test.trajectCatKoppeling()



