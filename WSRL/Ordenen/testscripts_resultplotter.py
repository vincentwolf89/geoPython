import arcpy
import os
import numpy
from arcpy.sa import *
from itertools import groupby
import math
import matplotlib.pyplot as plt
from os import path
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# from scipy.misc import imread
# import matplotlib.cbook as cbook
from PIL import Image
import seaborn as sns

sns.set_style("darkgrid")
arcpy.env.overwriteOutput = True
arcpy.env.workspace = 'C:/Users/vince/Desktop/GIS/stph_testomgeving.gdb'


def select_area():
    # Get map document object (ensure map document is open and the right data frame is active)
    mxd = arcpy.mapping.MapDocument('C:/Users/vince/Desktop/testmxd_plaatje.mxd')

    # Get data frame object
    df = arcpy.mapping.ListDataFrames(mxd, "*")[0]

    # Get df's spatial reference object
    spatialRef = df.spatialReference

    # Get data frame extent
    frameExtent = df.extent

    inWorkspace = 'C:/Users/vince/Desktop/GIS/stph_testomgeving.gdb'
    # Process: create new Visible Extent Polygon feature class to use to clip from your dataset.
    arcpy.CreateFeatureclass_management(inWorkspace, "Visible_Extent_Polygon", "POLYGON", "", "DISABLED", "DISABLED",
                                        "", "", "0", "0", "0")
    VisExtPoly = os.path.join(inWorkspace, "Visible_Extent_Polygon")
    VisExtPoly2 = os.path.join(inWorkspace, "Visible_Extent_Polygon2")

    # Process: create a current visible extent polygon and copy it into the new feature class. # This section of code takes the frameExtent, creates an array, and then converts the array to a polygon feature class.

    marge = (frameExtent.XMax-frameExtent.XMin)/50

    XMAX = frameExtent.XMax
    XMIN = frameExtent.XMin
    YMAX = frameExtent.YMax
    YMIN = frameExtent.YMin

    XMAX1 = frameExtent.XMax - marge
    XMIN1 = frameExtent.XMin + marge
    YMAX1 = frameExtent.YMax - marge
    YMIN1 = frameExtent.YMin + marge

    pnt1 = arcpy.Point(XMIN, YMIN)
    pnt2 = arcpy.Point(XMIN, YMAX)
    pnt3 = arcpy.Point(XMAX, YMAX)
    pnt4 = arcpy.Point(XMAX, YMIN)

    pnt11 = arcpy.Point(XMIN1, YMIN1)
    pnt22 = arcpy.Point(XMIN1, YMAX1)
    pnt33 = arcpy.Point(XMAX1, YMAX1)
    pnt44 = arcpy.Point(XMAX1, YMIN1)

    array = arcpy.Array()
    array.add(pnt1)
    array.add(pnt2)
    array.add(pnt3)
    array.add(pnt4)
    array.add(pnt1)

    array2 = arcpy.Array()
    array2.add(pnt11)
    array2.add(pnt22)
    array2.add(pnt33)
    array2.add(pnt44)
    array2.add(pnt11)

    polygon = arcpy.Polygon(array)  # creates polygon object
    polygon2 = arcpy.Polygon(array2)
    print(type(polygon))
    arcpy.CopyFeatures_management(polygon, VisExtPoly)
    arcpy.CopyFeatures_management(polygon2, VisExtPoly2)

    # Process: make feature layer so the visible extent polygon can be used as an input to Select Layer by Location.
    arcpy.MakeFeatureLayer_management(VisExtPoly, "VisExtPoly_fl")
    arcpy.MakeFeatureLayer_management(VisExtPoly2, "VisExtPoly_f2")


    # Process: Make Feature Layer for your large dataset of interest (in my case, a roads network) to be selected by visible extent
    arcpy.MakeFeatureLayer_management('run_25_02_2019', 'run_25_02_2019_temp')


    # Process: Select Layer By Location - FTEN roads
    arcpy.SelectLayerByLocation_management('run_25_02_2019_temp', "INTERSECT", VisExtPoly, "", "NEW_SELECTION",
                                           "NOT_INVERT")



    # Process: Copy selected FTEN roads to FC, then clear the selection
    arcpy.CopyFeatures_management('run_25_02_2019_temp', 'testje', "", "0", "0",
                                  "0")  # creates the actual feature class in the .gdb
    arcpy.SelectLayerByAttribute_management('run_25_02_2019_temp', "CLEAR_SELECTION")




    inFeatures = ['testje', 'dijkvakindeling_versie_43_stph']
    clusterTolerance = 0
    intersectOutput = "punten_test"
    arcpy.Intersect_analysis(inFeatures, intersectOutput, "", clusterTolerance, "point")

    arcpy.FeatureToPoint_management("punten_test", "punten_test_point")

    arcpy.AddXY_management("punten_test_point")
    arcpy.AlterField_management("punten_test_point", 'POINT_X', 'x')
    arcpy.AlterField_management("punten_test_point", 'POINT_Y', 'y')
    fieldPrecision = 2
    arcpy.AddField_management("punten_test_point", "x_as", "DOUBLE", fieldPrecision)



    # selecteer alleen de punten binnen het marge-kader
    arcpy.MakeFeatureLayer_management('punten_test_point', 'punten_test_point_temp')
    arcpy.SelectLayerByLocation_management('punten_test_point_temp', "INTERSECT", VisExtPoly2, "", "NEW_SELECTION", "NOT_INVERT")

    # Process: Copy selected FTEN roads to FC, then clear the selection
    arcpy.CopyFeatures_management('punten_test_point_temp', 'punten_geselecteerd', "", "0", "0",
                                  "0")  # creates the actual feature class in the .gdb






    input = "punten_geselecteerd"
    velden = ['uniek_id', 'kv_ov', 'x', 'y', 'x_as']

    arr = arcpy.da.FeatureClassToNumPyArray(input, ('uniek_id', 'kv_ov', 'x', 'y'))
    df = pd.DataFrame(arr)

    rij = df['x'].idxmin()
    x_min = df.ix[rij]['x']
    y_min = df.ix[rij]['y']

    with arcpy.da.UpdateCursor(input, velden) as cursor:
        for row in cursor:
            row[4] = row[2] - x_min
            cursor.updateRow(row)

    arr2 = arcpy.da.FeatureClassToNumPyArray(input, ('uniek_id', 'kv_ov', 'x', 'y', 'x_as'))
    df2 = pd.DataFrame(arr2)
    # outpath = "C:/Users/vince/Desktop/"
    #
    # # print df[df.columns[0]]
    # # print df['kv_ov']
    #
    list_x = df2['x_as']
    list_y = df2['kv_ov']
    list_x2 = df2['x']



    xmin = min(list_x2)
    xmax = max(list_x2)
    xdist = xmin-(frameExtent.XMin)
    xdist_p = xdist/1100

    xdist1 = (frameExtent.XMax)-xmax
    xdistp_1 = xdist1/990
    print xdist
    print xdist1

    lengte_extend = (frameExtent.XMax-frameExtent.XMin)
    xperclinks = ((xdist/lengte_extend)*100)/35
    xpercrechts = ((xdist1/lengte_extend)*100)/35

    print xperclinks
    print xpercrechts

    xs, ys = zip(*sorted(zip(list_x, list_y), key=lambda x: x[0]))

    plt.rcParams["figure.figsize"] = [16.53, 11.7]
    # dpi = 300
    # figsize = (1587 / dpi, 1123 / dpi)
    # plt.rcParams["figure.figsize"] = figsize

    fig, ax = plt.subplots()

    # plt.subplots_adjust(left=0.12)
    # ax.set_ymargin(0.9)
    # ax.set_xmargin(0.15)
    # plt.subplots_adjust(left=0.06)
    #ax.plot(xs, 0, '-ok', color='black')
    ax.plot(xs, ys, '-ok', color='black')

    def set_xmargin(ax, left=0.0, right=0.0):
        ax.set_xmargin(0)
        #ax.autoscale_view()
        lim = ax.get_xlim()
        delta = np.diff(lim)
        left = lim[0] - delta * left
        right = lim[1] + delta * right
        ax.set_xlim(left, right)


    ax.set_ymargin(0.5)
    set_xmargin(ax, left=xdist_p, right=xdistp_1)
    # set_xmargin(ax, left=xperclinks, right=xpercrechts)
    # fig.patch.set_visible(False)
    ax.tick_params(axis="y", direction="in", pad=-30)
    ax.tick_params(axis="x", direction="in", pad=-15)

    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["top"].set_visible(False)

    ax.axes.get_xaxis().set_visible(False)
    # ax.axis('off')


    plt.savefig('C:/Users/vince/Desktop/testfig.png', bbox_inches = 'tight', pad_inches=0.12, dpi=300)
    # plt.savefig('C:/Users/vince/Desktop/testfig.png', pad_inches=2, dpi=300, bbox_inches='tight')
    Image.open('C:/Users/vince/Desktop/testfig.png').convert('RGB').save('C:/Users/vince/Desktop/testfig.jpg')


def save_area():
    mxd = arcpy.mapping.MapDocument('C:/Users/vince/Desktop/testmxd_plaatje.mxd')
    arcpy.mapping.ExportToJPEG(mxd, 'C:/Users/vince/Desktop/plot.jpg')
    del mxd



def dubbel_plot():
    # Image.open('testplot.png').save('testplot.jpg','JPEG')
    boven = 'C:/Users/vince/Desktop/plot.jpg'
    onder = 'C:/Users/vince/Desktop/testfig.jpg'

    list_im = [boven, onder]
    imgs = [Image.open(i) for i in list_im]
    # # pick the image which is the smallest, and resize the others to match it (can be arbitrary image shape here)
    min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
    # imgs_comb = np.hstack( (np.asarray( i.resize(min_shape) ) for i in imgs ) )
    #
    # # save that beautiful picture
    # imgs_comb = PIL.Image.fromarray( imgs_comb)
    # imgs_comb.save( 'Trifecta.jpg' )
    #
    # # for a vertical stacking it is simple: use vstack
    imgs_comb = np.vstack((np.asarray(i.resize(min_shape)) for i in imgs))
    imgs_comb = Image.fromarray(imgs_comb)
    imgs_comb.save('C:/Users/vince/Desktop/tempje.jpg')
    #




select_area()

save_area()

dubbel_plot()
