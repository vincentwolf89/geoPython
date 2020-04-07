import arcpy
from basisfuncties import average, generate_profiles

class gpWaterloop(object):

    def __init__(self, waterloop,idWaterloop,bodemLijn):

        # hier alle lagen opbouwen zodat deze niet meer in het hoofdscript gebouwd hoeven worden?
        self.waterloop = waterloop
        self.idWaterloop = idWaterloop


    def rasterBuitenkant(self, waterloop, bufferBuitenkant, rasterAhn):

        rasterOut = "rasterBuitenkant"+str(self.idWaterloop)

        arcpy.Buffer_analysis(self.waterloop, "tempBufferWl", bufferBuitenkant, "OUTSIDE_ONLY", "FLAT", "NONE",
                              "", "PLANAR")
        # raster clippen met bufferzone
        arcpy.Clip_management(rasterAhn, "",
                              "tempRasterBuitenkant", "tempBufferWl", "-3,402823e+038", "ClippingGeometry",
                              "MAINTAIN_EXTENT")
        # focal stats op bufferclip
        buitenRaster = arcpy.gp.FocalStatistics_sa("tempRasterBuitenkant", rasterOut, "Rectangle 4 4 CELL", "MEAN",
                                    "DATA")

        print "Focal buffer-raster gemaakt voor {}".format(waterloop)
        return buitenRaster


    def smoothWaterloop(self,waterloop,smooth):
        arcpy.FeatureToLine_management(waterloop, "templijnWaterloop")
        lineSmooth = arcpy.SmoothLine_cartography("templijnWaterloop", "lineSmooth", "PAEK", smooth, "FIXED_CLOSED_ENDPOINT",
                                     "NO_CHECK")
        polySmooth = arcpy.SmoothPolygon_cartography(waterloop, "polySmooth", "PAEK", smooth, "FIXED_ENDPOINT", "NO_CHECK")
        return lineSmooth, polySmooth


    def bepaalInsteek(self, waterloop, buitenRaster,minLengteSegment,codeWaterloop,lineSmooth,waterloopLijn):
        # lijn van omtrek waterloop
        arcpy.FeatureToLine_management(waterloop, "templijnWaterloop")


        ## lijn splitsen en hoogte koppelen van oever:
        # simplify line
        arcpy.SimplifyLine_cartography("templijnWaterloop", "templijnWaterloopSimp", "POINT_REMOVE", "0.6 Meters",
                                       "FLAG_ERRORS", "KEEP_COLLAPSED_POINTS", "CHECK")

        # lijn splitten op vertices
        arcpy.SplitLine_management("templijnWaterloopSimp", "templijnWaterloopSimpSplit")

        # punten over lijn iedere 0.5 m
        arcpy.GeneratePointsAlongLines_management("templijnWaterloopSimpSplit", "tempPunten", "DISTANCE",
                                                  "0,5 Meters", "", "")

        # punten extracten uit focal stats...
        arcpy.gp.ExtractValuesToPoints_sa("tempPunten", buitenRaster, "tempPuntenInsteek", "NONE",
                                          "VALUE_ONLY")


        # verwijder lijnen die in waterloop liggen (aansluitingen)
        # selecteer punten op lijnstuk, als meer dan 3/4 van de punten geen z-waarde heeft, lijnstuk deleten
        arcpy.MakeFeatureLayer_management("tempPuntenInsteek", "tempPuntenInsteekFL")

        with arcpy.da.UpdateCursor("templijnWaterloopSimpSplit", ['SHAPE@', 'z_nap', 'SHAPE@LENGTH']) as cursor:

            for row in cursor:

                arcpy.SelectLayerByLocation_management("tempPuntenInsteekFL", 'intersect', row[0])
                arcpy.CopyFeatures_management("tempPuntenInsteekFL", "tempSelectiePunten")

                # verwijder aansluitstukken
                aantalZ = 0.1  #
                aantalNan = 0.1
                lijstZ = []
                with arcpy.da.SearchCursor("tempSelectiePunten",
                                           ['RASTERVALU', 'z_nap', 'OBJECTID']) as cursorWaterloop:
                    for rowWaterloop in cursorWaterloop:
                        if rowWaterloop[0] is None:
                            aantalNan += 1
                        else:
                            aantalZ += 1
                            lijstZ.append(rowWaterloop[0])

                del cursorWaterloop

                if aantalNan / aantalZ > 0.25 and row[2] < minLengteSegment:
                    # print "Aansluiting eruitgehaald"
                    cursor.deleteRow()

        ## koppel gemiddelde hoogte van 10 laagste punten aan lijnstukken als z-waarde

        # zoek laagste 15 waardes per waterloop
        with arcpy.da.UpdateCursor("tempPuntenInsteek", ['RASTERVALU', 'z_nap', 'OBJECTID'],
                                   sql_clause=(None, "ORDER BY RASTERVALU ASC")) as cursor:
            aantalPunten = 0
            lijstPunten = []

            for row in cursor:
                if row[0] is None:
                    cursor.deleteRow()
                else:
                    if aantalPunten < 15:
                        lijstPunten.append(row[0])
                        aantalPunten += 1

                    elif aantalPunten == 15:
                        zNapOg = average(lijstPunten)
                        break

        # koppel gemiddelde laaste waarde terug aan hele waterloop
        try:
            zNapOg
            with arcpy.da.UpdateCursor("templijnWaterloopSimpSplit", ['z_nap']) as cursor:
                for row in cursor:
                    # global insteekHoogte
                    insteekHoogte = round(zNapOg, 2)
                    row[0] = insteekHoogte
                    cursor.updateRow(row)

            # # voeg losse lijndelen weer samen
            arcpy.Dissolve_management("templijnWaterloopSimpSplit", "tempDissolve", [codeWaterloop, "z_nap"], "", "MULTI_PART",
                                      "DISSOLVE_LINES")

            arcpy.Copy_management("tempDissolve", "templijnWaterloopSimpSplit")

            # maak veld aan voor onderdeel-waterloop
            arcpy.AddField_management("templijnWaterloopSimpSplit", 'onderdeel', "TEXT", field_length=50)
            arcpy.CalculateField_management("templijnWaterloopSimpSplit", "onderdeel", "\"insteek\"", "PYTHON")

            # update lineSmooth
            with arcpy.da.UpdateCursor(lineSmooth, ['z_nap']) as cursor:
                for row in cursor:
                    row[0] = insteekHoogte
                    cursor.updateRow(row)
            del cursor

            arcpy.AddField_management(waterloop, "insteekHoogte", "DOUBLE", 2, field_is_nullable="NULLABLE")
            with arcpy.da.UpdateCursor(waterloop, ['insteekHoogte']) as cursor:
                for row in cursor:
                    row[0] = insteekHoogte
                    cursor.updateRow(row)
            del cursor
            print "Gemiddelde insteekhoogte van {}m bepaald voor {}".format(insteekHoogte, waterloop)


            arcpy.Copy_management(lineSmooth,waterloopLijn)
            return insteekHoogte

        except NameError:
            return None

    def bepaalBodemlijn(self,waterloop,smoothWaterloopLine, smoothWaterloopPoly, distMiniBuffer, tolerance, bodemLijn):
        if arcpy.Exists(smoothWaterloopLine):
            # euclidean raster
            arcpy.gp.EucDistance_sa(smoothWaterloopLine, "tempEuclidean", "", "0,05", "")
            # slope euclidean raster
            arcpy.gp.Slope_sa("tempEuclidean", "tempSlope", "DEGREE", "1")
            # rastercalc
            raster = arcpy.Raster("tempSlope")
            outRaster = raster <= 42
            outRaster.save("tempRastercalc")

            ## clip raster with polygon
            # eerst minibuffer op polygoon
            arcpy.Buffer_analysis(smoothWaterloopPoly, "tempBufferSmooth", distMiniBuffer, "OUTSIDE_ONLY", "FLAT", "NONE",
                                  "", "PLANAR")
            # minibuffer binnekant bewaren
            listOid = []
            arcpy.FeatureToLine_management("tempBufferSmooth", "tempBufferSmoothLijn")
            with arcpy.da.SearchCursor("tempBufferSmoothLijn", "OID@") as cursor:
                for row in cursor:
                    listOid.append(row[0])
            del cursor
            try:
                listOid[-2]
                oid = listOid[-2]
                with arcpy.da.UpdateCursor("tempBufferSmoothLijn", "OID@") as cursor:
                    for row in cursor:
                        if row[0] == oid:
                            pass
                        else:
                            cursor.deleteRow()
                # terugvertaling buffer naar binnenvlak
                arcpy.FeatureToPolygon_management("tempBufferSmoothLijn", "tempBufferSmoothPoly")


                arcpy.Clip_management("tempRastercalc", "", "tempClipper", "tempBufferSmoothPoly", "127",
                                      "ClippingGeometry", "MAINTAIN_EXTENT")
                # clip to polygon
                arcpy.RasterToPolygon_conversion("tempClipper", "tempPoly", "SIMPLIFY", "Value")
                # remove items with gridcode 0
                with arcpy.da.UpdateCursor("tempPoly", ["gridcode", "SHAPE@AREA"]) as cursor:
                    for row in cursor:
                        if row[0] is 0 or row[1] < 0.1:
                            cursor.deleteRow()
                        else:
                            pass

                ## middenlijn maken vanuit raster ##
                # poly to line
                arcpy.FeatureToLine_management("tempPoly", "tempPolyLijn")
                # split line at vertices
                arcpy.SplitLine_management("tempPolyLijn", "tempPolyLijnSplit")

                # select only bodempart
                arcpy.MakeFeatureLayer_management("tempPolyLijnSplit", "tempPolyLijnSplitFL")

                # niet smoothline pakken?
                arcpy.SelectLayerByLocation_management("tempPolyLijnSplitFL", "INTERSECT", smoothWaterloopLine, tolerance,
                                                       "NEW_SELECTION", "INVERT")
                arcpy.CopyFeatures_management("tempPolyLijnSplitFL", bodemLijn)

                # maak veld aan voor onderdeel-waterloop
                arcpy.AddField_management(bodemLijn, 'onderdeel', "TEXT", field_length=50)
                arcpy.CalculateField_management(bodemLijn, "onderdeel", "\"bodem\"", "PYTHON")



                # add field for bodemhoogte
                arcpy.AddField_management(bodemLijn, "z_nap", "DOUBLE", 2, field_is_nullable="NULLABLE")


                # delete features
                arcpy.Delete_management("tempEuclidean")
                arcpy.Delete_management("tempClipper")
                arcpy.Delete_management("tempRastercalc")


                bodemItems = int(arcpy.GetCount_management(bodemLijn).getOutput(0))
                if bodemItems is not 0:
                    print "Bodemlijn gemaakt voor {}".format(waterloop)
                    return bodemLijn
                else:
                    return None


            except IndexError:
                return None
        else:
            return None

    def bepaalMinimaleBreedte(self, waterloop, insteekLijn, bodemLijn,insteekHoogte,bodemDiepte, bodemDiepteSmal, maxBreedteSmal):
        ## profiles along line ##
        # dissolve bodemlijn
        arcpy.Dissolve_management(bodemLijn, "tempDissolveBodemlijn", "onderdeel", "", "MULTI_PART",
                                  "DISSOLVE_LINES")
        generate_profiles(5, 50, 50, "tempDissolveBodemlijn", "onderdeel", 0, "tempProfielenBodem")

        # isect profiles met line_smooth
        arcpy.Intersect_analysis(["tempProfielenBodem", insteekLijn], "tempIsect", "ALL", "", "POINT")
        # split profiles
        arcpy.SplitLineAtPoint_management("tempProfielenBodem", "tempIsect", 'splitProfielen', 0.2)
        # select only water part
        arcpy.MakeFeatureLayer_management('splitProfielen', 'tempSplitProfielen')
        arcpy.SelectLayerByLocation_management('tempSplitProfielen', "INTERSECT", "tempDissolveBodemlijn", 0.1,
                                               "NEW_SELECTION", "")

        arcpy.CopyFeatures_management('tempSplitProfielen', 'tempWaterProfielen')

        lijstBreedtes = []
        with arcpy.da.SearchCursor("tempWaterProfielen", ["SHAPE@LENGTH"]) as cursor:
            for row in cursor:
                if row[0] > 0 and row[0] is not None:
                    lijstBreedtes.append(row[0])
                else:
                    pass
        try:
            gemiddeldeBreedte = round(average(lijstBreedtes), 2)

        except NameError:
            gemiddeldeBreedte = 0.5


        arcpy.AddField_management(waterloop, 'soortWaterloop', "TEXT", field_length=50)

        # indien smalle waterloop
        if gemiddeldeBreedte <= maxBreedteSmal:

            # bodemhoogte bodemlijn aanpassen
            with arcpy.da.UpdateCursor(bodemLijn, ['z_nap']) as cursor:
                for row in cursor:
                    bodemHoogte = insteekHoogte - bodemDiepteSmal
                    row[0] = bodemHoogte
                    cursor.updateRow(row)
            del cursor
            arcpy.CalculateField_management(waterloop, "soortWaterloop", "\"smal\"", "PYTHON")
            arcpy.AddField_management(waterloop, "bodemHoogte", "DOUBLE", 2, field_is_nullable="NULLABLE")
            with arcpy.da.UpdateCursor(waterloop, ["bodemHoogte"]) as cursor:
                for row in cursor:
                    row[0] = bodemHoogte
                    cursor.updateRow(row)
            del cursor

        # indien brede waterloop
        if gemiddeldeBreedte > maxBreedteSmal:
            # bodemhoogte bodemlijn aanpassen
            with arcpy.da.UpdateCursor(bodemLijn, ['z_nap']) as cursor:
                for row in cursor:
                    bodemHoogte = insteekHoogte - bodemDiepte
                    row[0] = bodemHoogte
                    cursor.updateRow(row)
            del cursor

            arcpy.CalculateField_management(waterloop, "soortWaterloop", "\"breed\"", "PYTHON")

            arcpy.AddField_management(waterloop, "bodemHoogte", "DOUBLE", 2, field_is_nullable="NULLABLE")
            with arcpy.da.UpdateCursor(waterloop, ["bodemHoogte"]) as cursor:
                for row in cursor:
                    row[0] = bodemHoogte
                    cursor.updateRow(row)
            del cursor

        print "Gemiddelde breedte voor {} is {}m".format(waterloop, gemiddeldeBreedte)

        return bodemDiepte, bodemHoogte


    def bufferWaterloop(self, waterloop, waterloopPolySmooth, standaardTalud, bodemDiepte, bodemHoogte, insteekLijn, bufferLijn):
        # set talud to standard
        talud = standaardTalud

        print "Er wordt voor {} een bodemdiepte van {}m gebruikt".format(waterloop, bodemDiepte)

        # bepaal bufferafstand talud
        bufferAfstandTalud = abs(bodemDiepte / talud)  # buffer afstand volgens talud, tot bodemdiepte
        arcpy.Buffer_analysis(waterloopPolySmooth, "tempBuffer", -bufferAfstandTalud, "OUTSIDE_ONLY", "ROUND", "NONE", "","PLANAR")

        arcpy.FeatureToLine_management("tempBuffer", "tempBufferlijn")

        # with arcpy.da.UpdateCursor("temp_bufferlijn", ['z_nap']) as cursor:
        #     for row in cursor:
        #         bodemHoogte = insteekHoogte-bodemDiepte
        #         row[0] = bodemHoogte
        #         cursor.updateRow(row)
        # del cursor

        print "Buffer gemaakt met afstand van {}m en bodemdiepte {}m".format(bufferAfstandTalud, bodemDiepte)

        # maak veld aan voor onderdeel-waterloop
        arcpy.AddField_management("tempBufferlijn", 'onderdeel', "TEXT", field_length=50)
        arcpy.CalculateField_management("tempBufferlijn", "onderdeel", "\"onderkant_talud\"", "PYTHON")

        #### verwijder bufferlijn die matcht met waterlooplijn!! ####
        arcpy.MakeFeatureLayer_management("tempBufferlijn", "tempBufferlijnFL")
        arcpy.SelectLayerByLocation_management("tempBufferlijnFL", "INTERSECT", insteekLijn, 0.1,
                                               "NEW_SELECTION", "INVERT")

        arcpy.CopyFeatures_management("tempBufferlijnFL", bufferLijn)

        # update features
        with arcpy.da.UpdateCursor(bufferLijn, ['z_nap']) as cursor:
            for row in cursor:
                row[0] = bodemHoogte
                cursor.updateRow(row)

        del cursor
        print "Binnen-buffer gemaakt voor {}".format(waterloop)


    def maakRaster(self,waterloop, waterloopLijn, bufferLijn, bodemLijn,waterloopLijn3D, tin,rasterWaterloop, waterloopPolySmooth, rasterLijst):
        # merge insteeklijn met taludlijn en bodemlijn
        arcpy.Merge_management([waterloopLijn,bufferLijn,bodemLijn], "tempTotaalLijn")

        # feature to 3d
        arcpy.FeatureTo3DByAttribute_3d("tempTotaalLijn", waterloopLijn3D, "z_nap")

        # tin
        arcpy.CreateTin_3d(tin, "", "{} z_nap Hard_Line <None>".format(waterloopLijn3D), "DELAUNAY")
        # tin to raster
        arcpy.TinRaster_3d(tin, "tempRasterWaterloop", "FLOAT", "LINEAR", "CELLSIZE 0,1", "1")


        # clip raster met waterloop poly en verwijder oude raster
        arcpy.Clip_management("tempRasterWaterloop", "",
                              rasterWaterloop, waterloopPolySmooth, "-3,402823e+038", "ClippingGeometry",
                              "MAINTAIN_EXTENT")

        arcpy.Delete_management("tempRasterWaterloop")

        rasterLijst.append(rasterWaterloop)

        print "Raster gemaakt voor {}".format(waterloop)



class gpGeneral:

    def aggregateInput(self,waterlopenInvoer):
        arcpy.AggregatePolygons_cartography(waterlopenInvoer, "waterlopenTemp", "0,01 Meters",
                                            "0 SquareMeters", "0 SquareMeters", "NON_ORTHOGONAL", "",
                                            "temptabel")

        arcpy.AddField_management("waterlopenTemp", 'id_string', "TEXT", field_length=50)
        arcpy.CalculateField_management("waterlopenTemp", "id_string", '!OBJECTID!', "PYTHON")
        waterlopen = arcpy.Copy_management("waterlopenTemp",waterlopenInvoer)

        print "Aanliggende waterloop-polygonen gemerged"
        return waterlopen

    def insertAhn(self,rasterLijst,waterlopen,rasterAhn):

        # clip totaalgebied uit ahn
        arcpy.Clip_management(rasterAhn, "", "clipWaterlopen", waterlopen, "-3,402823e+038", "NONE",
                              "MAINTAIN_EXTENT")
        rasterLijst.append("clipWaterlopen")

        # merge rasterlijst
        arcpy.MosaicToNewRaster_management(rasterLijst, arcpy.env.workspace, "rasterTotaal",
                                           "", "32_BIT_FLOAT", "0,5", "1", "LAST", "FIRST")

        print "Losse rasters samengevoegd in invoer-raster"