## This script will look for all the layers that have feature selected in them in the TOC and export them in seperated shapefile.
##output layer name will be the original name+ _selected e.g. luzon_loss_selected
import arcpy


test1 = arcpy.mapping.MapDocument(r'C:\Users\vince\Desktop\test_mxd.mxd')
test2 = r'C:\Users\vince\Desktop\test'  ##folder path of output
def batch_export_layers(mxd, output_folder):

    arcpy.env.overwriteOutput = True
    df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
    layers = arcpy.mapping.ListLayers(mxd, "*", df)
    for layer in layers:
        # Sel = arcpy.Describe(layer)
        # if Sel.FIDset:
        arcpy.FeatureClassToFeatureClass_conversion(layer, output_folder, layer.name, "", "", "")

batch_export_layers(test1,test2)