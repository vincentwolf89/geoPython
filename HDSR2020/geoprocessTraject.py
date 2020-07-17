import arcpy

arcpy.env.workspace = r'D:\Projecten\HDSR\2020\gisData\oplevering_v3.1.gdb'


invoerVelden = ["SHAPE@","Naam","Shape_Length"]
trajecten = "RWK_areaal_2024"

class gpFuncties(object):
    def __init__(self, trajectId):
        self.trajectId = trajectId
        self.trajectProfielen = "profielen_{}".format(trajectId)
        self.trajectBit = "binnenteen_{}".format(trajectId) 


    
    
    def koppelZBit(self):
        trajectId = self.trajectId
        trajectProfielen = self.trajectProfielen
        trajectBit = self.trajectBit

        # verander veldnaam van bit naar z_bit

        if arcpy.Exists(trajectBit):  
            
            # pas veldnaam aan in trajectBit
            veldenBitObject = arcpy.ListFields(trajectBit)
            veldenBit = []
    
            for veld in veldenBitObject:
                veldenBit.append(str(veld.name))
            

            for veld in veldenBit:
                zOud = "z_ahn"
                zNieuw = "zBit"

                if zOud in veld:
                    arcpy.AlterField_management(trajectBit,zOud,zNieuw,zNieuw)
                    veldenBit.remove(zOud)
                    veldenBit.append(zNieuw)
                    print "Veld '{}' aangepast naar '{}'".format(zOud,zNieuw)
                else:
                    pass

            ## koppel veld "zBit" aan profielen
            
            # profielen schoonmaken, eventueel aanwezig veld 'zBit' verwijderen
            veldenProfielenObject = arcpy.ListFields(trajectProfielen)
            veldenProfielen = []
            
            for veld in veldenProfielenObject:
                veldenProfielen.append(str(veld.name))
            
            if "zBit" in veldenProfielen:
                arcpy.DeleteField_management(trajectProfielen,"zBit")
            else:
                pass
           
           # maken van koppeling, indien veld aanwezig is in bitpunten
            if zNieuw in veldenBit:
                arcpy.JoinField_management(trajectProfielen, "profielnummer", trajectBit, "profielnummer",zNieuw) 
                print ("Veld '{}' gekoppeld aan profielen".format(zNieuw))
                return True
            else:
                print ("Veld 'zBit' is niet gevonden, geen koppeling gemaakt met profielen")
                return False
        else:
            return False

    
    def berekenKH(self):
        trajectId = self.trajectId
        trajectProfielen = self.trajectProfielen


        # profielen schoonmaken, eventueel aanwezig veld 'zBit' verwijderen
        veldenProfielenObject = arcpy.ListFields(trajectProfielen)
        veldenProfielen = []
        
        for veld in veldenProfielenObject:
            veldenProfielen.append(str(veld.name))
        
        if "kHm" in veldenProfielen:
            pass
        else:
            arcpy.AddField_management(trajectProfielen,"kHm","DOUBLE", 2, field_is_nullable="NULLABLE")
        
        # bereken KH
        profielVelden = ["zBit","maxKruinhoogte2014","kHm"]
        profielCursor = arcpy.da.UpdateCursor(trajectProfielen, profielVelden)
        for row in profielCursor:
            if row[0] is None or row[1] is None:
                # print "Waardes voor berekenen kerende hoogte bij '{}' ontbreken".format(trajectId)
                row[2] = -9999
                profielCursor.updateRow(row)
            else:   
                row[2] = round((row[1]-row[0]),2)
                profielCursor.updateRow(row)

        print ("Kerende hoogtes berekend voor '{}'".format(trajectId))


    


class basisProces(object):

    def __init__(self, trajecten, invoerVelden):
        self.trajecten = trajecten
        self.invoervelden = invoerVelden
        self.cursor = arcpy.da.UpdateCursor(self.trajecten, self.invoervelden)
        

    def execute(self):
        for row in self.cursor:
            trajectId = row[1]
            gpObject = gpFuncties(trajectId)
            bitKoppeling = gpObject.koppelZBit()
            if bitKoppeling is True:
                gpObject.berekenKH()
            else:
                pass
            
    


# test = basisProces(trajecten,invoerVelden)
# test.execute()
























# class functies(object):
#     @staticmethod
#     def functie(waarde):
#         print waarde


# class uitvoer(object):
#     def __init__(self,waarde):
#         self.waarde = waarde
#     def execute(self):
#         functies.functie(self.waarde)


# test = uitvoer("printwaarde")
# test.execute()