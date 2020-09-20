import os
import arcpy
import pandas as pd

files = r'C:\Users\Vincent\Desktop\a7f3d94b-e499-4a01-aa69-46d31f0bfcbc\GEF'
arcpy.env.workspace = r'D:\Projecten\WSRL\safe\safeGOinv.gdb'
gdb = r'D:\Projecten\WSRL\safe\safeGOinv.gdb'
arcpy.env.overwriteOutput = True


puntenlaag = 'goBROsept2020'

arcpy.CreateFeatureclass_management(gdb, puntenlaag, "POINT", spatial_reference=28992)
arcpy.AddField_management(puntenlaag, 'Naam', "TEXT")
arcpy.AddField_management(puntenlaag, 'Soort', "TEXT")
arcpy.AddField_management(puntenlaag, 'rdX', "DOUBLE", 2, field_is_nullable="NULLABLE")
arcpy.AddField_management(puntenlaag, 'rdY', "DOUBLE", 2, field_is_nullable="NULLABLE")
cursor = arcpy.da.InsertCursor(puntenlaag,['Naam', 'Soort', 'rdX', 'rdY','SHAPE@XY'])

def gefTxt(files):
    for gef in os.listdir(files):
        if gef.endswith(".gef"):

            ingef = os.path.join(files, gef)
            if not os.path.isfile(ingef): continue
            nieuwenaam = ingef.replace('.gef', '.txt')
            output = os.rename(ingef, nieuwenaam)
        elif gef.endswith(".GEF"):
            ingef = os.path.join(files, gef)
            if not os.path.isfile(ingef): continue
            nieuwenaam = ingef.replace('.GEF', '.txt')
            output = os.rename(ingef, nieuwenaam)




def readFile(file):
    naam = file.split('.txt')[0]
    ingef = os.path.join(files, file)
    gef = open(ingef, "r")

    # remove blank lines
    lines = (line.rstrip() for line in gef)
    lines = list(line for line in lines if line)

    for item in lines:
        if item.startswith('#REPORTCODE') or item.startswith('#PROCEDURECODE'):
            if 'BORE' in item:
                soort = 'Boring'
            if 'CPT' in item:
                soort = 'Sondering'
            if 'BORE' not in item and 'CPT' not in item:
                soort = 'Onbekend'
       
        if item.startswith('#XYID'):
            
            rdX = item.split(',')[1]
            rdY = item.split(',')[2]
            rdX = rdX.replace(" ", "")
            rdY = rdY.replace(" ", "")




    try:
        soort
    except NameError:
        soort = 'Onbekend'

    try:
        rdX, rdY
        if rdX.startswith('0') or rdY.startswith('0'):
            print 'Geen geldige coordinaten gevonden voor {}'.format(naam)
            pass
        else:
            rdX = float(rdX)
            rdY = float(rdY)

            while rdX > 999999:
                rdX = rdX/10
          

            while rdY > 999999:
                rdY = rdY/10

            while rdX < 100000:
                rdX = rdX*10
            while rdY < 100000:
                rdY = rdY*10


            print 'geldige coordinaten gevonden'
            cursor.insertRow([naam, soort, rdX,rdY,(rdX,rdY)])
            print naam, soort, rdX,rdY

    except NameError:
        pass







    

    #return lines, naam

# gefTxt(files)

for gef in os.listdir(files):
    readFile(gef)
    