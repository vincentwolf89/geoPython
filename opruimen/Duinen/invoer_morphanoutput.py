import arcpy
import os

arcpy.env.workspace = r'C:\Users\vince\Desktop\GIS\13_1_invoer.gdb'


folder = r'C:\Users\vince\Desktop\klaarzetten 13-1\uitvoer\maatgevende_afslagpunten'

spRef = "PROJCS['RD_New',GEOGCS['GCS_Amersfoort',DATUM['D_Amersfoort',SPHEROID['Bessel_1841',6377397.155,299.1528128]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Double_Stereographic'],PARAMETER['False_Easting',155000.0],PARAMETER['False_Northing',463000.0],PARAMETER['Central_Meridian',5.38763888888889],PARAMETER['Scale_Factor',0.9999079],PARAMETER['Latitude_Of_Origin',52.15616055555555],UNIT['Meter',1.0]];-30515500 -30279500 10000;-100000 10000;-100000 10000;0,001;0,001;0,001;IsHighPrecision"




afslagpunten = 'JARKUS_maatgevend_afslagpunt_Iv'
grensprofiel = 'grensprofiel_Iv'

def import_morphan_output():
    for filename in os.listdir(folder):
        file = (os.path.join(folder, filename))
        outlayer = 'templaag_'+filename
        savedlayer = filename.replace('.csv','')

        outloc = r'C:\Users\vince\Desktop\GIS\13_1_invoer.gdb'
        arcpy.MakeXYEventLayer_management(file, 'x in RD', 'y in RD', outlayer, spRef, "")
        arcpy.FeatureClassToFeatureClass_conversion(outlayer,outloc,savedlayer)

def find_normativ_boundaryprofile():
    # pandas dataframe maatgevend
    # pandas dataframe grensprofielen

    with arcpy.da.SearchCursor(afslagpunten, ['maatgevend_jaar','locatie']) as cursor:
        for row in cursor:
            jaar = row[0]
            locatie= row[1]


            for fc in arcpy.ListFeatureClasses():
                if grensprofiel in str(fc) and 'tussenraaien' not in str(fc):
                    with arcpy.da.UpdateCursor(fc, ['jaar','locatie']) as cursor2:
                        for rij in cursor2:
                            if rij[0] == jaar and rij[1]==locatie:
                                print rij[1]

                            else:
                                if rij[1] == locatie and rij[0] is not jaar:
                                    cursor2.deleteRow()

                else:
                    pass

    totaal_jarkus = []
    for fc in arcpy.ListFeatureClasses():
        if grensprofiel in str(fc) and 'tussenraaien' not in str(fc):
            totaal_jarkus.append(fc)

    arcpy.Merge_management(totaal_jarkus, "samenvoeging_" + str(afslagpunten))


# find_normativ_boundaryprofile()

# arcpy.PointsToLine_management('tussenraaien_afslagpunten_iiv', 'lijn_tussenraaien_afslagpunten_iiv', "Jaar", "locatie", "NO_CLOSE")