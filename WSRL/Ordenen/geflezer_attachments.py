import arcpy
import arceditor
import pandas as pd
import numpy as np
import math
import os, sys


# from basisfuncties import*
arcpy.env.workspace = r'D:\Projecten\WSRL\goSafeTemp.gdb'
gdb = r'D:\Projecten\WSRL\goSafeTemp.gdb'
arcpy.env.overwriteOutput = True


gefmap_origin = "C:\Users\Vincent\Desktop\gef"
gef_extensie = ".gef"

gefmap = r'C:\Users\Vincent\Desktop\dinosafe'
puntenlaag = 'sonderingenDinoSafe2020'
nan = -9999

def gef_txt(gefmap, gef_extensie):
    for gef in os.listdir(gefmap):
        ingef = os.path.join(gefmap, gef)
        if not os.path.isfile(ingef): continue
        nieuwenaam = ingef.replace(gef_extensie, '.txt')
        output = os.rename(ingef, nieuwenaam)

def gef_to_gis(gefmap, puntenlaag, gefmap_origin,gef_extensie):
    # create leeg df
    velden = ['naam', 'x_rd', 'y_rd', 'z_nap', 'datum', 'bedrijf']
    df = pd.DataFrame(columns=velden)
    index = 0




    # open gef uit map
    for file in os.listdir(gefmap):
        ingef = os.path.join(gefmap, file)
        gef = open(ingef, "r")
        # df = pd.DataFrame(columns=['naam', 'x_rd', 'y_rd', 'z_nap', 'datum', 'bedrijf'])
        name = file.strip(".txt")

        for regel in gef:

            if regel.startswith('#XYID'):
                id_loc = regel.split(",")
                x = float(id_loc[1])
                y = float(id_loc[2])

            if regel.startswith('#ZID'):
                id_z = regel.split(",")
                z_mv = float(id_z[1])


            # if regel.startswith('#MEASUREMENTTEXT= 13') or regel.startswith('#MEASUREMENTTEXT = 13') or regel.startswith('#MEASUREMENTTEXT =13'):
            #     id_c = regel.split(',')
            #     company = str(id_c[1])
            #     print company

            if regel.startswith('#MEASUREMENTTEXT= 16') or regel.startswith('#MEASUREMENTTEXT = 16') or regel.startswith('#MEASUREMENTTEXT =16'):
                id_d = regel.split(",")
                date = str(id_d[1])


            # afvangen probleemgevallen
            try:
                company
            except NameError:
                if regel.startswith('#COMPANYID'):
                    id_c = regel.split(",")
                    company = str(id_c[0]).strip("#COMPANYID=")
                    print company


            try:
                date
            except NameError:
                if regel.startswith('#STARTDATE='):
                    id_d = regel.split("=")
                    date = str(id_d[1])



        # check voor op te nemen velden
        try:
            name
            index += 1
            df.loc[index, 'naam'] = name
        except NameError:
            pass

        try:
            x
            df.loc[index, 'x_rd'] = x
            del x
        except NameError:
            pass

        try:
            y
            df.loc[index, 'y_rd'] = y
            del y
        except NameError:
            pass

        try:
            z_mv
            df.loc[index, 'z_nap'] = z_mv
            del z_mv
        except NameError:
            pass
        try:
            date
            df.loc[index, 'datum'] = date
            del date
        except NameError:
            pass

        try:
            company

            df.loc[index, 'bedrijf'] = company
            del company
        except NameError:
            pass







    # maak featureclass
    arcpy.CreateFeatureclass_management(gdb, puntenlaag, "POINT", spatial_reference=28992)
    velden_gis = ['naam', 'x_rd', 'y_rd', 'z_nap', 'datum', 'bedrijf','origin']
    int_velden = ["x_rd","y_rd","z_nap"]
    for veld in velden_gis:
        if veld in int_velden:
            arcpy.AddField_management(puntenlaag, veld, "DOUBLE", 2, field_is_nullable="NULLABLE")
        if veld not in int_velden and veld is not "origin":
            arcpy.AddField_management(puntenlaag, veld, "TEXT")
        if veld is "origin":
            arcpy.AddField_management(puntenlaag, veld, "TEXT", field_length=200)







    # open de insertcursor
    velden_cursor = ['naam', 'x_rd', 'y_rd', 'z_nap', 'datum', 'bedrijf','origin','SHAPE@XY']
    cursor = arcpy.da.InsertCursor(puntenlaag, velden_cursor)

    for index, row in df.iterrows():
        naam = row['naam']
        x = row['x_rd']
        y = row['y_rd']
        z = row['z_nap']
        datum = row['datum']
        bedrijf = row['bedrijf']
        origin = gefmap_origin+"/"+row['naam']+gef_extensie
        invoegen = naam,x,y,z,datum,bedrijf,origin,(x,y)

        cursor.insertRow(invoegen)

    # voeg gef toe als bijlage



    # Process: Generate Attachment Match Table
    # arcpy.GenerateAttachmentMatchTable_management(test2, testmap_gef, tester, "naam", "", "RELATIVE")
    # arcpy.EnableAttachments_management(puntenlaag) # enable attachments



    # Process: Add Attachments
    # arcpy.AddAttachments_management(gef_test, "OBJECTID", gef_test__2_, "OBJECTID", "origin", gefmap_origin)
    # arcpy.DeleteField_management(puntenlaag,"origin")
    print "Laag met grondonderzoek gemaakt"
def attach_gef(puntenlaag):
    arcpy.EnableAttachments_management(puntenlaag) # enable attachments
    arcpy.AddAttachments_management(puntenlaag, "OBJECTID", puntenlaag, "OBJECTID", "origin", "")
    arcpy.DeleteField_management(puntenlaag,"origin")
    print "Bijlages toegevoegd"

gef_txt(gefmap, gef_extensie)
gef_to_gis(gefmap,puntenlaag,gefmap_origin, gef_extensie)
attach_gef(puntenlaag)
