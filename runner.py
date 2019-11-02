import gc
gc.collect()
from basisfuncties import *

arcpy.env.overwriteOutput = True


arcpy.env.workspace = r'D:\GIS\test.gdb'

profielen = 'profielen_reg'
invoerpunten = 'punten_profielen'
uitvoerpunten = 'punten_profielen_z'
stapgrootte_punten = 1
raster = r'D:\GIS\losse rasters\ahn3clip\ahn3clip_safe'
trajectlijn = 'lijn_regionaal'
code = 'dv_nummer'
resultfile = "C:/Users/Vincent/Desktop/testprofielen.xls"



# copy_trajectory_lr(trajectlijn,code)
# set_measurements_trajectory(profielen,trajectlijn,code,stapgrootte_punten)
# extract_z_arcpy(invoerpunten,uitvoerpunten,raster)
# add_xy(uitvoerpunten,code)
# to_excel(uitvoerpunten,resultfile)


puntenset = 'punten_binnenkruin'
# create_contour_lines(trajectlijn,raster,'contour_safe',0.5)
# snap_to_contour(puntenset,'contour_safe','near')

kruinhoogte_groepen(uitvoerpunten,stapgrootte_punten)
max_kruinhoogte(uitvoerpunten,profielen)

