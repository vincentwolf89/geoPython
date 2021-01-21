import arcpy
import os
import math
from arcpy.sa import *
from itertools import groupby
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import operator

import sys
sys.path.append('.')

from basisfuncties import average



from basisfuncties import generate_profiles, copy_trajectory_lr

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"D:\Projecten\WSRL\safe\profielenLek.gdb"
workspace = r"D:\Projecten\WSRL\safe\profielenLek.gdb"

baseFigures = r"C:/Users/Vincent/Desktop/profielen_lekbodem/output_figures/"




trajectlijn = "leklijn_demo"
code = "traject"
hoogtedata = "lekraster_safe_totaal_2020"
profiel_interval = 200
profiel_lengte_land = 200
profiel_lengte_rivier = 200
toetsniveau = -0.5

profielen = "profielenLekRaster"
refprofielen = "refprofielenLekRaster"
refprofielenpunten = "refprofielenPuntenStart"


def maak_basisprofielen(profiel_interval,profiel_lengte_land,profiel_lengte_rivier,trajectlijn,code,profielen):
    ## 1 referentieprofielen maken
    
    # generate_profiles(profiel_interval=profiel_interval,profiel_lengte_land=140,profiel_lengte_rivier=1000,trajectlijn=trajectlijn,code=code,
    # toetspeil=toetsniveau,profielen="tempRefProfielen")
    
    ## 2 normale profielen maken 


    generate_profiles(profiel_interval=profiel_interval,profiel_lengte_land=profiel_lengte_land,profiel_lengte_rivier=profiel_lengte_rivier,trajectlijn=trajectlijn,code=code,
    toetspeil=0,profielen="tempProfielen")



    # routes maken profielen
    profielCursor = arcpy.da.UpdateCursor("tempProfielen", ["van","tot","SHAPE@LENGTH"])
    for tRow in profielCursor:
        lengte = tRow[2]
        tRow[0] = 0
        tRow[1] = lengte
        profielCursor.updateRow(tRow)

    
    del profielCursor
    arcpy.CreateRoutes_lr("tempProfielen", "profielnummer", profielen,"TWO_FIELDS", "van", "tot", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")

    # voeg veld toe voor eindoordeel en overhoogte
    arcpy.AddField_management(profielen,"inpassing","TEXT", field_length=100)
    arcpy.AddField_management(profielen,"overhoogte","DOUBLE", 2, field_is_nullable="NULLABLE")


    print "basisprofielen gemaakt"

def maak_referentieprofielen(profielen,refprofielenpunten,toetsniveau):

    profielnummers= [z[0] for z in arcpy.da.SearchCursor (profielen, ["profielnummer"],sql_clause=(None, 'ORDER BY profielnummer ASC'))]

    if arcpy.Exists("refProfielTabel"):
        arcpy.Delete_management("refProfielTabel")

    arcpy.CreateTable_management(workspace, "refProfielTabel", "", "")
   
   
    arcpy.AddField_management("refProfielTabel","profielnummer", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management("refProfielTabel","locatie","TEXT", field_length=50)
    arcpy.AddField_management("refProfielTabel","afstand","DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management("refProfielTabel","z_ref","DOUBLE", 2, field_is_nullable="NULLABLE")

    refPuntenCursor = arcpy.da.InsertCursor("refProfielTabel", ["profielnummer","locatie","afstand","z_ref"])
  
    

    for profielnummer in profielnummers:
        
        # vanuit linkeroever, dummy afmetingen

        p1 = 0
        p2 = 0.5
        p3 = 3
        p4 = 25.8
        p5 = 71.4
        p6 = 94.2
        p7 = 96.7
        p8 = 97.2

        # p1 = 0
        # p2 = 10
        # p3 = 30
        # p4 = 40
    
        z_rivierwaterstand = toetsniveau
       
        

        refPuntenCursor.insertRow([profielnummer,"p1",p1,toetsniveau])
        refPuntenCursor.insertRow([profielnummer,"p2",p2,toetsniveau-3])
        refPuntenCursor.insertRow([profielnummer,"p3",p3,toetsniveau-4])
        refPuntenCursor.insertRow([profielnummer,"p4",p4,toetsniveau-5.6])
        refPuntenCursor.insertRow([profielnummer,"p5",p5,toetsniveau-5.6])
        refPuntenCursor.insertRow([profielnummer,"p6",p6,toetsniveau-4])
        refPuntenCursor.insertRow([profielnummer,"p7",p7,toetsniveau-3])
        refPuntenCursor.insertRow([profielnummer,"p8",p8,toetsniveau])
       
        # refPuntenCursor.insertRow([profielnummer,"p1",p1,z_rivierwaterstand])
        # refPuntenCursor.insertRow([profielnummer,"p2",p2,z_bodemSchip])
        # refPuntenCursor.insertRow([profielnummer,"p3",p3,z_bodemSchip])
        # refPuntenCursor.insertRow([profielnummer,"p4",p4,z_rivierwaterstand])



    del refPuntenCursor

    
    arcpy.MakeRouteEventLayer_lr(profielen, "profielnummer", "refProfielTabel", "profielnummer POINT afstand", "temproutelayer", "", "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
    arcpy.CopyFeatures_management("temproutelayer", refprofielenpunten)
    arcpy.Delete_management("temproutelayer")

    print "referentieprofielen gemaakt"

def fit_referentieprofiel(profielen,refprofielenpunten, hoogtedata, toetsniveau, basefigures):


    ## stringveld aanmaken voor profielen en refprofielen voor individuele selectie
    arcpy.AddField_management(profielen,"profielnummer_str","TEXT", field_length=50)
    # arcpy.AddField_management(refprofielen,"profielnummer_str","TEXT", field_length=50)
    arcpy.AddField_management(refprofielenpunten,"profielnummer_str","TEXT", field_length=50)
    
    # dictionary voor terugkoppeling oordeel
    oordeelDct = {}


    profielCursor = arcpy.da.UpdateCursor(profielen,["profielnummer","profielnummer_str"])
    for pRow in profielCursor:
        pRow[1] = "profiel_"+str(int(pRow[0]))

        profielCursor.updateRow(pRow)
    
    del profielCursor

    profielCursor = arcpy.da.UpdateCursor(refprofielenpunten,["profielnummer","profielnummer_str"])
    for pRow in profielCursor:
        pRow[1] = "profiel_"+str(int(pRow[0]))

        profielCursor.updateRow(pRow)
    
    del profielCursor

    # ref_afstand toevoegen voor koppeling df
    fields = [f.name for f in arcpy.ListFields(refprofielenpunten)]

    if "afstand_ref" in fields:
        pass
    else:
        arcpy.AddField_management(refprofielenpunten,"afstand_ref","DOUBLE", 2, field_is_nullable="NULLABLE")


    tempCursor = arcpy.da.UpdateCursor(refprofielenpunten, ["afstand","afstand_ref"])
    for tRow in tempCursor:
            tRow[0] = round(tRow[0] * 2) / 2
            tRow[1] = round(tRow[0] * 2) / 2
            tempCursor.updateRow(tRow)
    del tempCursor


    # per profiel verder werken
    with arcpy.da.SearchCursor(profielen,["SHAPE@","profielnummer_str"]) as profielCursor:
        for pRow in profielCursor:

            profielnummer = str(pRow[1])
   
            tempprofiel = "tempprofiel"
            temprefpunten = "temprefpunten"
            temprefprofiel = "temprefprofiel"
            tempbandbreedte = "tempbandbreedte"

                
            # selecteer betreffend profiel en kopieer naar tijdelijke laag
            where = '"' + 'profielnummer_str' + '" = ' + "'" + profielnummer + "'"
            arcpy.Select_analysis(profielen, tempprofiel, where)


            # selecteer referentiepunten van betreffend profiel en kopieer naar tijdelijke laag
            arcpy.Select_analysis(refprofielenpunten, temprefpunten, where)
            # arcpy.JoinField_management(temprefpunten,"profielnummer","kruindelenTraject","profielnummer","maxBreedte")


            # # selecteer betreffend referentieprofiel voor localisatie profielpunten
            # arcpy.Select_analysis(refprofielen, temprefprofiel, where)
    

            # creer routes voor punten profiel, dit is het echte profiel en NIET het refprofiel...! 
            arcpy.AddField_management(tempprofiel,"van","DOUBLE", 2, field_is_nullable="NULLABLE")
            arcpy.AddField_management(tempprofiel,"tot","DOUBLE", 2, field_is_nullable="NULLABLE")
            
            tempCursor = arcpy.da.UpdateCursor(tempprofiel, ["van","tot","SHAPE@LENGTH"])
            for tRow in tempCursor:
                lengte = tRow[2]
                tRow[0] = 0
                tRow[1] = lengte
                tempCursor.updateRow(tRow)
            
            del tempCursor
            arcpy.CreateRoutes_lr(tempprofiel, "profielnummer_str", 'tempRoute',"TWO_FIELDS", "van", "tot", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")

            

            # profiel voorzien van z-waardes op afstand van 0.5 m
            arcpy.GeneratePointsAlongLines_management("tempRoute", "puntenRoute", "DISTANCE", Distance= 0.5)
        
            # profielpunten lokaliseren
            arcpy.LocateFeaturesAlongRoutes_lr("puntenRoute", "tempRoute", "profielnummer_str", "0,1 Meters", "profileRouteTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
            arcpy.JoinField_management("puntenRoute","OBJECTID","profileRouteTable","OBJECTID","MEAS")
            arcpy.AlterField_management("puntenRoute", 'MEAS', 'afstand')


            # z-waarde aan profielpunten koppelen (indien aanwezig)
            arcpy.CheckOutExtension("Spatial")
            ExtractValuesToPoints("puntenRoute", hoogtedata, "puntenRouteZ","INTERPOLATE", "VALUE_ONLY")
            arcpy.AlterField_management("puntenRouteZ", 'RASTERVALU', 'z_raster')


            # afstand afronden op .05 m om koppeling te garanderen in df
            tempCursor = arcpy.da.UpdateCursor("puntenRouteZ", ["afstand"])
            for tRow in tempCursor:
                tRow[0] = round(tRow[0] * 2) / 2
                tempCursor.updateRow(tRow)
            del tempCursor


            ## plotten 
            
            # gewone profiel
            arrayProfile = arcpy.da.FeatureClassToNumPyArray("puntenRouteZ", ('afstand','z_raster'))
            profileDf = pd.DataFrame(arrayProfile)
            sortProfileDf = profileDf.sort_values(by=['afstand'],ascending=[True])

            # referentieprofiel
            arrayRefProfile = arcpy.da.FeatureClassToNumPyArray("temprefpunten", ('profielnummer','afstand','afstand_ref','z_ref'))
            refDf = pd.DataFrame(arrayRefProfile)
            sortrefDf = refDf.sort_values(by=['profielnummer','afstand_ref'],ascending=[True, True])

      

            # plotbereik instellen
            minPlotX = sortProfileDf['afstand'].min()-10
            maxPlotX = sortProfileDf['afstand'].max()+10

            minPlotY = sortProfileDf['z_raster'].min()-5
            # check of refprofiel zichtbaar is in plot
            if minPlotY >= toetsniveau:
                minPlotY = toetsniveau -2
            maxPlotY = sortProfileDf['z_raster'].max()+1


            # minimale en maximale afstanden bepalen voor opbouw basisdataframe
            minList = [sortProfileDf['afstand'].min(),sortrefDf['afstand'].min()]
            maxList = [sortProfileDf['afstand'].max(),sortrefDf['afstand_ref'].max()]
            minAfstand = min(minList)
            maxAfstand = max(maxList)


            baseList = np.arange(minAfstand, maxAfstand, 0.5).tolist()
            baseSeries = pd.Series(baseList) 


            # opbouw dataframe
            frame = {'afstand': baseSeries} 
            baseDf = pd.DataFrame(frame) 

            # koppelen dataframes profielen en refprofielen
            baseMerge1 = baseDf.merge(sortProfileDf, on=['afstand'],how='outer')
            baseMerge2 = baseMerge1.merge(sortrefDf, on=['afstand'],how='outer')

            
            # verschil bepalen tussen gewone profiel en referentieprofiel
            firstAfstand = baseMerge2['afstand_ref'].first_valid_index()
            lastAfstand = baseMerge2['afstand_ref'].last_valid_index()

            # interpoleren van punten tussen de vier referentiepunten
            baseMerge2.loc[firstAfstand:lastAfstand, 'afstand_ref'] = baseMerge2.loc[firstAfstand:lastAfstand, 'afstand_ref'].interpolate()
            baseMerge2.loc[firstAfstand:lastAfstand, 'z_ref'] = baseMerge2.loc[firstAfstand:lastAfstand, 'z_ref'].interpolate()



            baseMerge2['difference'] = abs(baseMerge2.z_ref) - abs(baseMerge2.z_raster)


            
            
            # plot opbouwen
            plt.style.use('seaborn-whitegrid') #seaborn-ticks
            fig = plt.figure(figsize=(80, 10))
            ax1 = fig.add_subplot(111, label ="1")
            
            ax1.plot(baseMerge2['afstand'],baseMerge2['z_raster'],label="Vaarwegmeting Lek 2020",color="dimgrey",linewidth=5)
            ax1.axhline(toetsniveau, color='blue', linestyle='--',linewidth=5,label="Waterstand [{} m NAP]".format(toetsniveau))

            
            
            # check of referentiepunten aanwezig zijn
            aantalRefpunten = int(arcpy.GetCount_management(temprefpunten)[0])
            if aantalRefpunten > 0:
                ingepastRefprofiel = True
            if aantalRefpunten == 0:
                ingepastRefprofiel = False



            # zuid- en noordzijde als grenzen gebruiken 
            knipNan = baseMerge2[baseMerge2['z_raster'].notna()]
            noordGrensRaster = knipNan['afstand'].max()
            zuidGrensRaster = knipNan['afstand'].min()

            ax1.axvline(noordGrensRaster, color='coral', linestyle=':',linewidth=4,label="Datagrens zuidzijde")
            ax1.axvline(zuidGrensRaster, color='seagreen', linestyle=':',linewidth=4, label="Datagrens noordzijde")


            # itereren tot referentieprofiel past, indien mogelijk en nodig
            iteraties = 1

            indexEindInit = baseMerge2['z_ref'].last_valid_index()
            eindInit = baseMerge2.iloc[indexEindInit]['afstand']

            resterend = round(abs(eindInit-noordGrensRaster))-0.5
            
            isectTest = (baseMerge2['difference'] > 0).values.any()
            
            ## alleen verdergaan als p1 op op rivierwaarts van zuidzijde ligt
            zuidzijdeRefprofiel = round(float(baseMerge2['afstand_ref'].min()),1)
            if zuidzijdeRefprofiel >= zuidGrensRaster:
                grensTest = False
            if zuidzijdeRefprofiel < zuidGrensRaster:
                grensTest = True

            ## doorschuiven tot p1 op grens zuidzijde ligt
            while (grensTest == True or isectTest == True) and resterend > 0:



                # print "Iteratie {}".format(iteraties)

                # schuif het refprofiel naar rechts en test op isects

                baseMerge2['afstand_ref'] = baseMerge2['afstand_ref'].shift(+1)
                baseMerge2['z_ref'] = baseMerge2['z_ref'].shift(+1)
               
                baseMerge2['test'] = np.where((baseMerge2['z_ref'] < baseMerge2['z_raster']), -1, np.nan)
                isectTest = (baseMerge2['test'] == -1).values.any()
        

                # optellen 
                iteraties += 1
                resterend -= 0.5
                # print resterend
                
                # zuidzijderefprofiel optellen
                indexZuidzijdeRefProfiel = baseMerge2['z_ref'].first_valid_index()
                zuidzijdeRefprofiel = baseMerge2.iloc[indexZuidzijdeRefProfiel]['afstand']
         

                if zuidzijdeRefprofiel >= zuidGrensRaster:
                    grensTest = False

                
                baseMerge2['test'] = np.where((baseMerge2['z_ref'] < baseMerge2['z_raster']), -1, np.nan)
                isectTest = (baseMerge2['test'] == -1).values.any()

  

        



            
            
                
            if grensTest == False and isectTest == False:
                print "profiel past", profielnummer
                # plot groen profiel, profiel past
                ax1.plot(baseMerge2['afstand'],baseMerge2['z_ref'],'-',label="Initieel passend profiel", color="forestgreen",linewidth=4,zorder=99)
                
                
                # kopieer dataframe
                baseMerge3 = baseMerge2.copy()

             


                # bepaal iteratiebereik hoogtes
                minMeting = baseMerge3['z_raster'].min()
                maxHoogte = toetsniveau

                hoogteVerschil = abs(minMeting-maxHoogte)
                hoogtes = np.arange(0,hoogteVerschil,0.2)
               
                
                # eerste snijtest, niet noodzakelijk want zou al moeten kloppen
                baseMerge3['test'] = np.where((baseMerge3['z_ref'] < baseMerge3['z_raster']), -1, np.nan)
                isectTest = (baseMerge3['test'] == -1).values.any()
                

                # overhoogte
                aantal_pogingen = 0
                hoogte_pogingen = []

              
                hoogte_bovenkant_dct = {}
                df_hoogte_bovenkant = pd.DataFrame(columns=['iteratie','hoogte_bovenkant','df'])

                # start iteraties
                while isectTest == False and resterend > 0:

                    baseMerge3['afstand_ref'] = baseMerge3['afstand_ref'].shift(+1)
                    baseMerge3['z_ref'] = baseMerge3['z_ref'].shift(+1)

                    testlist = []

                    
                   
                    
                    
         

                    for hoogte in hoogtes:
                        

                     
                        baseMerge4 = baseMerge3.copy()
                        baseMerge4['z_ref_lower'] = baseMerge4['z_ref']- hoogte
                        baseMerge4['test_lower'] = np.where((baseMerge4['z_ref_lower'] < baseMerge4['z_raster']), -1, np.nan)
                        isectTestLower = (baseMerge4['test_lower'] == -1).values.any()


                        

                       

                        if isectTestLower == False:
                            testlist.append(baseMerge4)

                         


                     

               


                            # ax1.plot(baseMerge4['afstand'],baseMerge4['z_ref_lower'],'--',label="dummy", color="black",linewidth=3)
                        else:
                            pass

                  

               
                    
                    

                    if testlist:
                        ax1.plot(testlist[-1]['afstand'],testlist[-1]['z_ref_lower'],'--',label='_nolegend_',color="black", linewidth=1,zorder=0)

                        aantal_pogingen += 1
                        hoogte_bovenkant = testlist[-1]['z_ref_lower'].max()
                        hoogte_pogingen.append(hoogte_bovenkant)

                        
                        hoogte_bovenkant_dct[aantal_pogingen] = [hoogte_bovenkant,testlist[-1]]
                        df_hoogte_bovenkant.loc[aantal_pogingen] =  [aantal_pogingen, hoogte_bovenkant,testlist[-1]]



                        


                    else:
                        
                        ax1.plot(baseMerge3['afstand'],baseMerge3['z_ref'],'--',label='_nolegend_', color="grey",linewidth=1,zorder=0)

                        aantal_pogingen += 1
                        hoogte_pogingen.append(baseMerge3['z_ref'].max())


                    
            
                    baseMerge3['test'] = np.where((baseMerge3['z_ref'] < baseMerge3['z_raster']), -1, np.nan)
                    isectTest = (baseMerge3['test'] == -1).values.any()

                    # optellen 
                    iteraties += 1
                    resterend -= 0.5
                    # print resterend


                # print list(hoogte_bovenkant_min)
                # print hoogte_bovenkant_min.keys()
                # print min(hoogte_pogingen)

                # zoeken naar max-group
                try:
                    min_bovenkant = round(min(hoogte_pogingen),1)
                    df_hoogte_min = pd.DataFrame(columns = ['groupnr','df'])
                    groupnr = 1 

                    hoogte_start = df_hoogte_bovenkant['hoogte_bovenkant'].iloc[0]
                    for index, row in df_hoogte_bovenkant.iterrows():
            
                        if round(row['hoogte_bovenkant'],1) == min_bovenkant:
                            hoogte_start = round(row['hoogte_bovenkant'],1)
                            groupnr = groupnr
                            df_hoogte_min.loc[index] = [groupnr,row['df']]
                        else:
                            groupnr += 1

                    
                    # print df_hoogte_min['groupnr']
                    grouped = df_hoogte_min.groupby('groupnr')

                    dct_max = {}

                    for group_name, df_group in grouped:
                        groep_grootte = len(df_group.index)
                        dct_max[group_name] = [groep_grootte,df_group]

                        # print group_name
                    

                    max_groupname = max(dct_max.iteritems(), key=operator.itemgetter(1))[0]

                    max_group = dct_max[max_groupname][0]

                    print max_group,max_groupname
                    midden_groep = int(max_group/2)

                    # opnieuw zoeken naar max_group
                    for group_name, df_group in grouped:
                        if group_name == max_groupname:
                            max_df = df_group['df'].iloc[midden_groep]
        
                            ax1.plot(max_df['afstand'],max_df['z_ref_lower'],'-',label="Best passende profiel", color="yellow",linewidth=4,zorder=100)
                except:
                    pass
                        
                        


         


                


 
                        


             



                if aantal_pogingen > 0:
                    gemiddelde_hoogte = average(hoogte_pogingen)

                    overhoogte = round(toetsniveau-gemiddelde_hoogte,2)
                    print "gemiddelde overhoogte is {}m".format(overhoogte)  
                    oordeelDct[profielnummer] = ["voldoende ruimte", overhoogte]
                else:
                    overhoogte = 0
                    oordeelDct[profielnummer] = ["voldoende ruimte", overhoogte]

            

            
                    
                ax1.text(0.5, 0.2, 'Gemiddelde overhoogte: {}m'.format(overhoogte), horizontalalignment='center',
                verticalalignment='center', transform=ax1.transAxes, zorder=100,fontsize=40)
        

            # terugkoppeling oordeel aan gislaag

            else:
                print "profiel past niet", profielnummer
                oordeelDct[profielnummer] = ["onvoldoende ruimte", -999]

   

            

            
            
            # for oRow in oordeelCursor:



            ax1.legend(frameon=False, loc='lower right',prop={'size': 20})
            plt.savefig("{}/{}.png".format(basefigures,profielnummer))
            plt.close()

            print profielnummer, oordeelDct[profielnummer]

    oordeelCursor = arcpy.da.UpdateCursor(profielen,['profielnummer_str','inpassing','overhoogte'])

    for oRow in oordeelCursor:
        profielnummer_temp = str(oRow[0])
        

        
        oRow[1] = oordeelDct[profielnummer_temp][0] 
        oRow[2] = oordeelDct[profielnummer_temp][1] 

        oordeelCursor.updateRow(oRow)

    del oordeelCursor
   



# maak_basisprofielen(profiel_interval=profiel_interval,profiel_lengte_land=profiel_lengte_land,profiel_lengte_rivier=profiel_lengte_rivier,trajectlijn=trajectlijn,code=code,profielen=profielen)
# maak_referentieprofielen(profielen=profielen,refprofielenpunten=refprofielenpunten,toetsniveau=toetsniveau)
fit_referentieprofiel(profielen=profielen,refprofielenpunten=refprofielenpunten,hoogtedata=hoogtedata,toetsniveau=toetsniveau,basefigures=baseFigures)




