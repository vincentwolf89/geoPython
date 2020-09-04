import os
import arcpy
import pandas as pd


files = r'C:\Users\Vincent\Desktop\GEF\GEF'
arcpy.env.workspace = r'D:\Projecten\HDSR\2020\gisData\gefInlezen.gdb'
gdb = r'D:\Projecten\HDSR\2020\gisData\gefInlezen.gdb'
arcpy.env.overwriteOutput = True





puntenlaag = 'boringenHDSR'

soortenGrofGef = ['Z','G']
maxGrof = 5

# maak nieuwe puntenlaag in gdb
arcpy.CreateFeatureclass_management(gdb, puntenlaag, "POINT", spatial_reference=28992)
arcpy.AddField_management(puntenlaag, 'naam', "TEXT")
arcpy.AddField_management(puntenlaag, 'zMv', "DOUBLE", 2, field_is_nullable="NULLABLE")
arcpy.AddField_management(puntenlaag, 'dikteDeklaag', "DOUBLE", 2, field_is_nullable="NULLABLE")
arcpy.AddField_management(puntenlaag, 'topZandNAP', "DOUBLE", 2, field_is_nullable="NULLABLE")
arcpy.AddField_management(puntenlaag, 'soortOnder', "TEXT")
arcpy.AddField_management(puntenlaag, 'zOnderNAP', "DOUBLE", 2, field_is_nullable="NULLABLE")

# open de insertcursor
cursor = arcpy.da.InsertCursor(puntenlaag, ['naam','zMv', 'dikteDeklaag', 'topZandNAP','soortOnder', 'zOnderNAP', 'SHAPE@XY'])


for file in os.listdir(files):
    naam = file.split('.txt')[0]
    ingef = os.path.join(files, file)
    gef = open(ingef, "r")

    # remove blank lines
    lines = (line.rstrip() for line in gef)
    lines = list(line for line in lines if line)

    # lijst voor meetgedeelte
    lijstMetingen = []

    # ophalen benodigde data
    for item in lines:

        if item.startswith('#'):
            # bepalen separator
            if item.startswith('#COLUMNSEP'):
                sep = sep = item.strip()[-1:]

            # ophalen locatiegegevens
            if item.startswith('#XYID'):
                coLocs = item.split(',')
                x = float(coLocs[1])
                y = float(coLocs[2])

            if item.startswith('#ZID'):
                zMv = round(float(item.split(',')[1]),2)
        # anders doorgaan met metingen opbouw
        else:
            lijstMetingen.append(item)

    # check of voldoende informatie aanwezig is om door te gaan
    try:
        x, y, zMv
    except NameError:
        print "Geen coordinaten gevonden"
        break
    if lijstMetingen:
        pass
    else:
        print "Geen metingen gevonden"
        break

    index = 0
    indexLijst = []
    bovenkantLijst = []
    onderkantLijst = []
    soortenLijst = []

    for item in lijstMetingen:
        onderdelen = item.split(sep)
        bovenkant = float(onderdelen[0])
        onderkant = float(onderdelen[1])
        soort = (onderdelen[2])[1]

        indexLijst.append(index)
        bovenkantLijst.append(bovenkant)
        onderkantLijst.append(onderkant)
        soortenLijst.append(soort)
        index+=1

    del bovenkant, onderkant,soort, index


    # opbouw pandas df
    dctMeting = {'index': indexLijst,'bovenkant': bovenkantLijst, 'onderkant': onderkantLijst, 'soort': soortenLijst}
    df = pd.DataFrame(dctMeting)
    df['laagDikte'] = abs(df['bovenkant']-df['onderkant'])

    dctGrof = {}
    indexLijstGrof = []
    laagNummerLijstGrof = []
    bovenkantLijstGrof = []
    laagdikteLijstGrof = []

    groveLaag = 0
    grovelaagNummer = 0

    for index, row in df.iterrows():
        bovenkant = df.iloc[index]['bovenkant']
        onderkant = df.iloc[index]['onderkant']
        soort = df.iloc[index]['soort']
        laagDikte = df.iloc[index]['laagDikte']


        if soort in soortenGrofGef:
            indexLijstGrof.append(index)
            groveLaag+= laagDikte

            laagNummerLijstGrof.append(grovelaagNummer)
            bovenkantLijstGrof.append(bovenkant)
            laagdikteLijstGrof.append(groveLaag)

        if soort not in soortenGrofGef:
            grovelaagNummer += 1
            groveLaag = 0



    dctGrof = {'index': indexLijstGrof,'laagNummer': laagNummerLijstGrof, 'bovenkant': bovenkantLijstGrof,'laagdikte':laagdikteLijstGrof}
    dfGrof = pd.DataFrame(dctGrof)


    grouped = dfGrof.groupby('laagNummer')

    for group in grouped:
        if group[1]['laagdikte'].max() > maxGrof:
            deklaag = round(group[1]['bovenkant'].min(),2)
            topzand = round(zMv-abs(deklaag),2)
            soortOnder = df.iloc[-1]['soort']
            zOnder = round(zMv-abs(df.iloc[-1]['onderkant']),2)

            break
        else:
            deklaag = round(float(df.iloc[-1]['onderkant']),2)
            topzand = -999
            soortOnder = df.iloc[-1]['soort']
            zOnder = round(zMv-abs(df.iloc[-1]['onderkant']),2)

            # print deklaag, naam
            break
    print deklaag, naam
    invoegen = (str(naam), zMv, deklaag, topzand, soortOnder, zOnder, (x, y))
    cursor.insertRow(invoegen)





