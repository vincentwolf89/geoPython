import gc
gc.collect()
from basisfuncties import *

arcpy.env.overwriteOutput = True


arcpy.env.workspace = r'D:\Projecten\HDSR\data\werk.gdb'

profiel_interval = 15
profiel_lengte = 35
profielen = 'profielen_regionaal'
invoerpunten = 'punten_profielen'
uitvoerpunten = 'punten_profielen_z'
stapgrootte_punten = 0.5
afronding = 1
raster = r'D:\Projecten\HDSR\data\ahn_hdsr.gdb\AHN3grondfilter'
trajectlijn = 'test_traject_hdsr_5'
code = 'SUBSECT_ID'
resultfile = r"C:\Users\Vincent\Desktop\testprofielen.xls"
uitvoer_maxpunten = 'max_kruinhoogte'

profiel_lengte_land = 20
profiel_lengte_rivier = 10

generate_profiles(profiel_interval, profiel_lengte_land, profiel_lengte_rivier, trajectlijn,code,profielen)
# copy_trajectory_lr(trajectlijn,code)
# set_measurements_trajectory(profielen,trajectlijn,code,stapgrootte_punten)
# extract_z_arcpy(invoerpunten,uitvoerpunten,raster)
# add_xy(uitvoerpunten,code)
# to_excel(uitvoerpunten,resultfile)
#
# kruinhoogte_groepen(uitvoerpunten,stapgrootte_punten,afronding,code)
# max_kruinhoogte(uitvoerpunten,profielen,code,uitvoer_maxpunten)





puntenset = 'punten_binnenkruin'
# create_contour_lines(trajectlijn,raster,'contour_safe',0.5)
# snap_to_contour(puntenset,'contour_safe','near')