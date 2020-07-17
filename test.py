import arcpy 
from os import listdir, path
import os
from itertools import groupby

def average(lijst):
    return sum(lijst) / len(lijst)


arcpy.env.workspace = r'C:\Users\Vincent\Desktop\davidpunten\STPH\tempdavid.gdb'
gdb = r'C:\Users\Vincent\Desktop\davidpunten\STPH\tempdavid.gdb'
arcpy.env.overwriteOutput = True




featureclasses = arcpy.ListRasters()
waterlopen = 'waterlopenDavid'
rasterAhn = 'ahn3clipsh1'
rasterLijst = []

for item in featureclasses:
    if item.startswith('waterloopRaster') or item.startswith('ahn'):
        print item
        rasterLijst.append(item)


        



def insertAhn(rasterLijst,waterlopen,rasterAhn):

    # clip totaalgebied uit ahn
    arcpy.Clip_management(rasterAhn, "", "clipWaterlopen", waterlopen, "-3,402823e+038", "NONE",
                            "MAINTAIN_EXTENT")
    rasterLijst.append("clipWaterlopen")

    # merge rasterlijst
    sr = arcpy.SpatialReference(28992) # assuming this is youy spatial reference  
    arcpy.MosaicToNewRaster_management(rasterLijst, arcpy.env.workspace, "rasterTotaal",
                                        sr, "32_BIT_FLOAT", "0,5", "1", "LAST", "FIRST")

    print "Losse rasters samengevoegd in invoer-raster"

insertAhn(rasterLijst,waterlopen,rasterAhn)

# dct = {}

# # Bepaal groepsnummer
# with arcpy.da.UpdateCursor('pandenPuntenZ', ['grid_code', 'RASTERVALU', 'averageZ']) as cursor:
#         for k, g in groupby(cursor, lambda x: x[0]):
#             group = None 
#             listz = []
#             for row in g:
#                 if row[1] is None:
#                     pass
#                 else:
#                     # print row[1]
#                     listz.append(row[1])
#                     group = row[0]
#             if listz:
#                 dct[group] = round(average(listz),2)
    



# del cursor


# with arcpy.da.UpdateCursor('pandenPuntenZ', ['grid_code', 'RASTERVALU', 'averageZ']) as cursor:
#     for row in cursor:
#         if int(row[0]) in dct:
            
#             row[2] = dct[int(row[0])]
#             cursor.updateRow(row)




























# files = r'D:\Projecten\WSRL\goSH\goSH\wsrl\sonderingen'
# fc = 'sonderingenDinoSafe'
# fieldsIn = ['naam']

# arcpy.env.workspace = r'C:\Users\Vincent\Desktop\lengteprofielen_sh\SPROK_STER.gdb'
# gdb = r'C:\Users\Vincent\Desktop\lengteprofielen_sh\SPROK_STER.gdb'
# arcpy.env.overwriteOutput = True


# featureclasses = arcpy.ListFeatureClasses()
# list = ['boring_lagen','boringen','L_LP_boringen','L_LP_legenda','L_LP_maaiveld','L_LP_sonderingen',
# 'L_LP_sonderingen_legenda','P_LP_boring_legenda','P_LP_boring_waterspanning','P_LP_dijkpaal','P_LP_sondering_legenda','P_LP_sonderingen',
# 'P_LP_volumegewichten','PG_LP_bodemopbouw','PG_LP_boringen','PG_LP_rivierduin','PG_PL_DALOUD','PG_PL_OUDDOM','sondering_lagen','sonderingen'
# ]

# for fc in list:
#     arcpy.DeleteFeatures_management(fc)


# # list folders in directory
# itemsFolder = listdir(files)
# nameList = []
# fcList = []

# for item in itemsFolder:
#     itemname = str(item).strip('.txt')
#     nameList.append(itemname)

# # list items in featureclass
# with arcpy.da.SearchCursor(fc,fieldsIn) as cursor:
#     for row in cursor:
#         fcList.append(str(row[0]))



# # compare 

# for item in nameList:
#     if item in fcList:
#         pass
#     else:
#         rem = path.join(files,item+'.txt')
#         # nieuwenaam = rem.replace('.txt', '.gef')
#         # output = os.rename(rem, nieuwenaam)
       
#         # os.remove(rem)


# for gef in os.listdir(files):
#     if gef.endswith(".txt"):

#         ingef = os.path.join(files, gef)
#         if not os.path.isfile(ingef): continue
#         nieuwenaam = ingef.replace('.txt', '.gef')
#         output = os.rename(ingef, nieuwenaam)
#     # elif gef.endswith(".GEF"):
    #     ingef = os.path.join(files, gef)
    #     if not os.path.isfile(ingef): continue
    #     nieuwenaam = ingef.replace('.GEF', '.txt')
    #     output = os.rename(ingef, nieuwenaam)