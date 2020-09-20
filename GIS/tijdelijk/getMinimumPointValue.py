import arcpy
from itertools import groupby

arcpy.env.workspace = r'D:\GoogleDrive\WSRL\safe_temp.gdb'
arcpy.env.overwriteOutput = True

uittredepunten = "uittredePuntenZoneZ"
minpunten = "minPuntenZoneStph"
fields = ["profielnummer","RASTERVALU",'OBJECTID']
# elevList = [z[0] for z in arcpy.da.SearchCursor (uittredepunten, ["RASTERVALU"])]  

IDlist = []

with arcpy.da.SearchCursor(uittredepunten, fields) as cursor:
                for k, g in groupby(cursor, lambda x: x[0]):
                    
                    hoogtes = {}
                    for row in g:
                        if row[1] == -999:
                            pass
                        else:
                            hoogtes[row[2]] = row[1]

                    # for row in g:
                    #     try:
                    #         int(row[0])
                    #         hoogtes.append(row[1])

                    #     except:
                    #         pass
                        
                    if hoogtes:

                        # print hoogtes
                        minOID = min(hoogtes, key=hoogtes.get)
                        IDlist.append(minOID)


                    del hoogtes
                    print round(k)

print IDlist


del cursor

with arcpy.da.UpdateCursor(minpunten, fields) as cursor:
    for row in cursor:
        if int(row[2]) in IDlist:
            pass
        else:
            cursor.deleteRow()