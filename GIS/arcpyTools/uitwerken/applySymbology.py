import arcpy

arcpy.env.workspace = r'C:\Users\Vincent\Desktop\lengteprofielen_safe\safeLP.gdb'

fields = ["OBJECTID","ALG__BORING_MONSTERNR_ID","BORING_XID","BORING_YID","BORING_MAAIVELDPEIL","CLAS_NEN5104","CLAS_MONSTERNIVEAU","CLAS_VOLUMEGEWICHT_NAT","CLAS_VOLUMEGEWICHT_VERZADIGD"]

fc = "boringen2020classificatie"
veldenObject = arcpy.ListFields(fc)
velden = []
    
for veld in veldenObject:
    if veld.name in fields:
        print veld.name
    else:
        arcpy.DeleteField_management(fc,veld.name)




    # velden.append(str(veld.name))
# mxd = arcpy.mapping.MapDocument("CURRENT")  
# df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]  
# layers = arcpy.mapping.ListLayers(mxd,"",df)  


# layernames = []
# for layer in layers:
#     if layer.name.startswith("profielen_"):

#         layernames.append(str(layer.name))

# in_symbology_layer = 'profielenTotaalKH'

# for item in layernames:
#     arcpy.ApplySymbologyFromLayer_management(item,in_symbology_layer)  


# out = r"C:\Users\Vincent\Dropbox\Wolfwater\SAFE_eindsprint\Vigerend\04_gis\dropboxdbSafe.gdb"
# mxd = arcpy.mapping.MapDocument("CURRENT")  
# df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]  
# layers = arcpy.mapping.ListLayers(mxd,"",df)  

# tabel = r'D:\Projecten\HDSR\2020\gisData\werkdatabase.gdb\tempnamen'

# layernames = []
# for layer in layers:
    
    # arcpy.CopyFeatures_management(layer, out+"\{}".format(layer.name))
    # if layer.name.startswith("profielen_deelgebied"):
        # split = layer.name.split('profielen_deelgebied')

        # print layer.name, split[1]
        # arcpy.CalculateField_management(layer, "nrKering", split[1], "PYTHON")
        
        
        # arcpy.AddField_management(layer, 'nrKering', "DOUBLE", 2, field_is_nullable="NULLABLE")
        # arcpy.CalculateField_management(layer, "nrKering", split[1], "PYTHON")
        # arcpy.DeleteField_management(layer,'naamKering')
        # arcpy.JoinField_management(layer, 'nrKering', tabel, 'nrKering', 'naamKering')
        # arcpy.JoinField_management(layer, int(str(split[1])), tabel, "nrKering", "nrKering;naamKering")
        # arcpy.DeleteField_management(layer,'naam')
       
        