import arcpy

# fc = r"D:\Projecten\WSRL\safe\lengteprofielen_safe\safeLP.gdb\sonderingen"
# arcpy.DeleteFeatures_management(fc)

Tinput = r"C:\Users\Vincent\Desktop\lengteprofielen_sh\SPROK_STER.gdb\test" ###tabel van de liniear ref van de onderzoekspunten, zie file:///K:\WK_GOZ\02_proces\Lengteprofielen\SPST\VOLGEWICHT.xlsx als voorbeeld

Poutput = r"C:\Users\Vincent\Desktop\lengteprofielen_sh\SPROK_STER.gdb\P_LP_volumegewichten_nieuw" ###bestaande laag waar de punten naartoe worden geexporteerd, zie Sprok Sterreschans als voorbeeld

FIELDSinp = ["RID","MEAS","Distance","ALG__BORING_MONSTERNR_ID","BORING_XID","BORING_YID","BORING_MAAIVELDPEIL","CLAS_NEN5104","CLAS_MONSTERNIVEAU","CLAS_VOLUMEGEWICHT_NAT","CLAS_VOLUMEGEWICHT_VERZADIGD"]
#               0     1         2               3                       4           5               6                   7               8                       9                       10
FIELDSout = ["SHAPE@","RID","MEAS","Distance","ALG__BORING_MONSTERNR_ID","BORING_XID","BORING_YID","BORING_MAAIVELDPEIL","CLAS_NEN5104","CLAS_MONSTERNIVEAU","CLAS_VOLUMEGEWICHT_NAT","CLAS_VOLUMEGEWICHT_VERZADIGD"]

point = []

# offset label rechts
olR = 10



with arcpy.da.SearchCursor(Tinput,FIELDSinp) as Scur:
    for row in Scur:
        if row[8] == None:
            pass
        elif "VL" in row[3] or "BUT" in row[3] or "MBUB" in row[3]:
            Xcoord = row[1]+olR
            Ycoord = row[8]*10+300
            point = arcpy.Point(Xcoord,Ycoord)
            with arcpy.da.InsertCursor(Poutput,FIELDSout) as Icur:
                Icur.insertRow([point,row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]])
            del Icur
        elif "BIK" in row[3] or "BUK" in row[3] or "BITA" in row[3] or "BUTA" in row[3]:
            Xcoord = row[1]+olR
            Ycoord = row[8]*10
            point = arcpy.Point(Xcoord,Ycoord)
            with arcpy.da.InsertCursor(Poutput,FIELDSout) as Icur:
                Icur.insertRow([point,row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]])
            del Icur
        elif "BIT" in row[3] or "AL" in row[3] or "MBIB" in row[3]:
            Xcoord = row[1]+olR
            Ycoord = row[8]*10-300
            point = arcpy.Point(Xcoord,Ycoord)
            with arcpy.da.InsertCursor(Poutput,FIELDSout) as Icur:
                Icur.insertRow([point,row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]])
            del Icur
        else:
            pass
        point = []

del Scur