
import arcpy

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r'D:\Projecten\WW\test.gdb'

from basisfuncties import locate_profiles, generate_profiles, copy_trajectory_lr, set_measurements_trajectory,extract_z_arcpy



# generate_profiles(25,200,200,"buitenkruinlijn_safe_wsrl","traject",5,"profielenTotaal")

# locate_profiles("profielenTotaal","dp_100m_totaal","route_dp_safe","koppeling","profielnummer","profielenSafeTotaal")


generate_profiles(25,100,100,"trajectlijn_dummy","traject",5,"profielen_dummy")
copy_trajectory_lr("trajectlijn_dummy","traject")

set_measurements_trajectory("profielen_dummy","trajectlijn_dummy","traject",0.5,5)

invoerpunten = "punten_profielen"
uitvoerpunten = "punten_profielen_z"
raster = "trainraster"
extract_z_arcpy(invoerpunten,uitvoerpunten,raster)





