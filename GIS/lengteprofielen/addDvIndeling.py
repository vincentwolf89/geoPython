import arcpy
arcpy.env.overwriteOutput = True


arcpy.env.workspace = r'D:\Projecten\WSRL\safe\lengteprofielen_safe\safeLP.gdb'

dijkVakken = r'D:\GoogleDrive\WSRL\safe_basis.gdb\dv_indeling_sept_2019'
Mline = 'BASISLIJN_ML_SAFE'

# locate dijkvakken op basislijn, zonder offset
arcpy.LocateFeaturesAlongRoutes_lr(dijkVakken, Mline, "rid", "20 Meters", "dvTabelLoc", "RID LINE FMEAS TMEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")



