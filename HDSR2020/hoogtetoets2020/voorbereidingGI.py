import arcpy
import sys
sys.path.append('.')
import pandas as pd

from basisfuncties import average

arcpy.env.workspace = r'D:\Projecten\HDSR\2020\gisData\samenvoegingen.gdb'

arcpy.env.overwriteOutput = True

# featureclasses = arcpy.ListFeatureClasses()
# for fc in featureclasses:

#     name = str(fc)
#     if name.startswith('samenvoeging'):
#         arcpy.AddField_management(fc, 'naamKering', "TEXT")

data = arcpy.da.FeatureClassToNumPyArray('samenvoegingenMetVerval', ('mVol','mOnv','mNan','kHmGem','typeKering','naamKering','nrKering','gemVerval','Shape_Length'))
df = pd.DataFrame(data)
df.to_excel(r'D:\Projecten\HDSR\2020\deel_inventarisatie\uitvoer2.xlsx') 



def inventarisatieDG(featureclasses):


    for fc in featureclasses:
        name = str(fc)
        if name.startswith('deelgebied'):
            
            
            profielMerge = []

            profielenVoldoende = 0
            profielenOnvoldoende = 0
            profielenNan = 0
            kHmLijst = []

            veldenDeelgebiedObject = arcpy.ListFields(fc)
            veldenDeelgebied = []
            
            for veld in veldenDeelgebiedObject:
                veldenDeelgebied.append(str(veld.name))
            
            veldenNodig = ["mVol","mOnv","mNan","kHmGem"]

            for item in veldenNodig:
                if item in veldenDeelgebied:
                    pass
                else:
                    arcpy.AddField_management(fc,item,"DOUBLE", 2, field_is_nullable="NULLABLE")


            cursor = arcpy.da.SearchCursor(fc, "Naam")

            
            for row in cursor:
                profielen = "profielen_{}".format(row[0])
                
                
                if arcpy.Exists(profielen):


                    # check of kHm in profielen zit
                    veldenProfielenObject = arcpy.ListFields(profielen)
                    veldenProfielen = []
                    for veld in veldenProfielenObject:
                        veldenProfielen.append(str(veld.name))

                        if veld.name == "profielUniek":
                            arcpy.DeleteField_management(profielen,"profielUniek")
                        else:
                            pass

                    
                    if all(elem in veldenProfielen for elem in ["profielnummer","kHm","Naam"]):
                

                        # doorgaan
                        arcpy.AddField_management(profielen, 'profielUniek', "TEXT")
                        profielMerge.append(profielen)
                        profielCursor = arcpy.da.UpdateCursor(profielen, ["profielnummer","profielUniek","kHm","Naam"])
                        for row in profielCursor:
                            row[1] = row[3]+"_"+str(int(row[0]))

                            if row[2] >= 0:
                                profielenVoldoende +=1
                                kHmLijst.append(row[2])
                                
                                
                                
                            elif row[2] <= 0 and row[2] > -9999:
                                profielenOnvoldoende +=1
                                kHmLijst.append(row[2])
                                
                            else:  
                                if row[2] == -9999:
                                    profielenNan +=1

                        






                            profielCursor.updateRow(row)
                        del profielCursor
                    else:
                        # niet doorgaan
                        pass


                    
                    
                

                else:
                    pass
                


                
            if profielMerge:
                if len(profielMerge)>1:
                    arcpy.Merge_management(profielMerge, "profielen_{}".format(name))
                else:
                    arcpy.CopyFeatures_management(profielen, "profielen_{}".format(name))
                print ("profielen_{} gemaakt".format(name))

            else:
                pass
            

            cursorFinal = arcpy.da.UpdateCursor(fc, ["mVol","mOnv","mNan","kHmGem"])

            for row in cursorFinal:
                row[0] = profielenVoldoende * 25
                row[1] = profielenOnvoldoende *25
                row[2] = profielenNan * 25
                if kHmLijst:

                    row[3] = average(kHmLijst)
                else:
                    pass
                cursorFinal.updateRow(row)


            del cursor,profielMerge, profielenVoldoende, profielenOnvoldoende, profielenNan, cursorFinal, kHmLijst
            
            # dissolve
            arcpy.Dissolve_management(fc, "samenvoeging_"+name, ["mVol","mOnv","mNan","kHmGem"], "", "MULTI_PART", "DISSOLVE_LINES")
            

        else:
            pass

def koppelVerval(deelgebieden, totaalprofielen):

    for deelgebied in deelgebieden:
        name = deelgebied.strip("samenvoeging_deelgebied")
        
        
        # bereken gemiddelde verval van de betreffende profielen
        vervallijst = []
        profCur = arcpy.da.SearchCursor(totaalprofielen,['nrKering','verval'])

        for row in profCur:
            if row[0] is None or row[1]==-999:
                pass
            else:
                gebiedsnaam= str(int(row[0]))
                if name == gebiedsnaam:
                    vervallijst.append(round(row[1],2))
        
        gemVerval = round(average(vervallijst),2)
        print gemVerval, name

        # check of gemVerval in deelgebied zit
        veldenObject = arcpy.ListFields(deelgebied)
        velden = []
        for veld in veldenObject:
            velden.append(str(veld.name))

        for veld in velden:
            if veld == "gemVerval":
                arcpy.DeleteField_management(deelgebied,"gemVerval")
            else:
                pass
        
        
        arcpy.AddField_management(deelgebied,"gemVerval","DOUBLE", 2, field_is_nullable="NULLABLE")
        with arcpy.da.UpdateCursor(deelgebied, 'gemVerval') as cursor:
            for row in cursor:
                row[0] = gemVerval
                cursor.updateRow(row)



        del vervallijst, gemVerval, velden, cursor

        print "Gemiddeld verval berekend voor deelgebied {}".format(name)


# deelgebieden = []
# featureclasses = arcpy.ListFeatureClasses()
# for fc in featureclasses:

#     name = str(fc)
#     if name.startswith('samenvoeging'):
#         deelgebieden.append(name)



# profielen = r'D:\Projecten\HDSR\2020\gisData\basisData.gdb\profielenTotaal'

# koppelVerval(deelgebieden,profielen)


