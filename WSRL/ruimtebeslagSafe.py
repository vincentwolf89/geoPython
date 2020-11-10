import arcpy

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"D:\Projecten\WSRL\safe\ruimtebeslag.gdb"

# hele excel inlezen voor MA
excelMA = r"C:\Users\Vincent\Desktop\MAs_revisited_MA1.xlsx"

arcpy.ExcelToTable_conversion(excelMA, "tabelMA1", "MA1")
arcpy.Copy_management("basisDV","ma1bs1")
arcpy.JoinField_management("ma1bs1", "dijkvakken", "tabelMA1", "dijkvakken", "zone;plaats;aantal_ma;bs1_afstand;bs1_locatie;bs1_soort;bs1_toepassing;bs1_vorm;bs1_type")

# t/m bs5 alle rijen waar afstand niet geldt verwijderen
cursor = arcpy.da.UpdateCursor("ma1bs1","bs1_afstand")
for row in cursor:
    if row[0] == None:
        cursor.deleteRow()
    else:
        pass
# offsets maken 

