import gc
gc.collect()
from basisfuncties import *

arcpy.env.overwriteOutput = True


arcpy.env.workspace = r'D:\Projecten\HDSR\data\werk.gdb'

profielen = 'testprofielen_hdsr'
invoerpunten = 'punten_profielen'
uitvoerpunten = 'punten_profielen_z'
stapgrootte_punten = 0.5
afronding = 1
raster = r'D:\Projecten\HDSR\data\ahn_hdsr.gdb\AHN3grondfilter'
trajectlijn = 'test_traject_hdsr'
code = 'dv_nummer'
resultfile = r"C:\Users\Vincent\Desktop\testprofielen.xls"



# copy_trajectory_lr(trajectlijn,code)
# set_measurements_trajectory(profielen,trajectlijn,code,stapgrootte_punten)
# extract_z_arcpy(invoerpunten,uitvoerpunten,raster)
# add_xy(uitvoerpunten,code)
# to_excel(uitvoerpunten,resultfile)

# kruinhoogte_groepen(uitvoerpunten,stapgrootte_punten,afronding)
# max_kruinhoogte(uitvoerpunten,profielen)





puntenset = 'punten_binnenkruin'
# create_contour_lines(trajectlijn,raster,'contour_safe',0.5)
# snap_to_contour(puntenset,'contour_safe','near')