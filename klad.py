
import arcpy

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r'D:\GoogleDrive\WSRL\safe_basis.gdb'

from basisfuncties import locate_profiles, generate_profiles



# generate_profiles(25,200,200,"buitenkruinlijn_safe_wsrl","traject",5,"profielenTotaal")

locate_profiles("profielenTotaal","dp_100m_totaal","route_dp_safe","koppeling","profielnummer","profielenSafeTotaal")



