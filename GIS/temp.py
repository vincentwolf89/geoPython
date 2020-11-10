import arcpy
from arcpy.sa import *
sys.path.append('.')


from basisfuncties import average, generate_profiles_onpoints
arcpy.env.workspace = r"D:\GoogleDrive\WSRL\safe_temp.gdb"
arcpy.env.overwriteOutput = True

points = r'C:\Users\Vincent\Documents\ArcGIS\Default.gdb\koppelingDV_FeatureVerticesT'
profielen = r'D:\Projecten\WSRL\safe\ruimtebeslag.gdb\middenProfielen'

trajectlijn = r'D:\GoogleDrive\WSRL\safe_basis.gdb\buitenkruinlijn_safe_wsrl'
generate_profiles_onpoints(points,trajectlijn,profielen,"traject")