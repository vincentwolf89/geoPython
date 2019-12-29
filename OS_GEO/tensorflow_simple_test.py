#https://towardsdatascience.com/neural-network-for-satellite-data-classification-using-tensorflow-in-python-a13bcf38f3e1

import os
import numpy as np
from tensorflow import keras
from pyrsgis import raster
from pyrsgis.convert import changeDimension
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, precision_score, recall_score

# output directory
os.chdir(r"D:\DL\sample_data_vincent\output")

# bestandsnamen
train_raster = r'D:\DL\sample_data_vincent\rasters\los_vast_clip.tif'
trainvlakken = r'D:\DL\sample_data_vincent\rasters\schier_classify_clip.tif'
test_raster = r'D:\DL\sample_data_vincent\rasters\los_vast_clip.tif'


# Read the rasters as array
ds1, train_raster = raster.read(train_raster, bands='all')
ds2, trainvlakken = raster.read(trainvlakken, bands=1)
ds3, test_raster = raster.read(test_raster, bands='all')

# Print the size of the arrays
print("Bangalore Multispectral image shape: ", train_raster.shape)
print("Bangalore Binary built-up image shape: ", trainvlakken.shape)
print("Hyderabad Multispectral image shape: ", test_raster.shape)

# Clean the labelled data to replace NoData values by zero
trainvlakken = (trainvlakken == 1).astype(int)

# Reshape the array to single dimensional array
train_raster = changeDimension(train_raster)
trainvlakken = changeDimension (trainvlakken)
test_raster = changeDimension(test_raster)
nBands = train_raster.shape[1]
# nBands = 3
print (nBands)

print("train_raster image shape: ", train_raster.shape)
print("train_vlakken image shape: ", trainvlakken.shape)
print("test_raster image shape: ", test_raster.shape)

# Split testing and training datasets
xTrain, xTest, yTrain, yTest = train_test_split(train_raster, trainvlakken, test_size=0.4, random_state=42)

print(xTrain.shape)
print(yTrain.shape)

print(xTest.shape)
print(yTest.shape)

# Normalise the data
xTrain = xTrain / 255.0
xTest = xTest / 255.0
test_raster = test_raster / 255.0

print (xTrain.shape[1])
print (xTest.shape[1])
print (test_raster.shape[1])
# # Reshape the data
xTrain = xTrain.reshape((xTrain.shape[0], 1, xTrain.shape[1]))
xTest = xTest.reshape((xTest.shape[0], 1, xTest.shape[1]))
test_raster = test_raster.reshape((test_raster.shape[0], 1, test_raster.shape[1]))


# Print the shape of reshaped data
print(xTrain.shape, xTest.shape, test_raster.shape)
#
# Define the parameters of the model
model = keras.Sequential([
    keras.layers.Flatten(input_shape=(1, nBands)),
    keras.layers.Dense(14, activation='relu'),
    keras.layers.Dense(5, activation='softmax')])





# Define the accuracy metrics and parameters
model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])

# Run the model
model.fit(xTrain, yTrain, epochs=2)

# Predict for test data
yTestPredicted = model.predict(xTest)
yTestPredicted = yTestPredicted[:,1]

# Calculate and display the error metrics
yTestPredicted = (yTestPredicted>0.5).astype(int)
cMatrix = confusion_matrix(yTest, yTestPredicted)
pScore = precision_score(yTest, yTestPredicted)
rScore = recall_score(yTest, yTestPredicted)


print("Confusion matrix: for 14 nodes\n", cMatrix)
print("\nP-Score: %.3f, R-Score: %.3f" % (pScore, rScore))

predicted = model.predict(test_raster)
predicted = predicted[:,1]

y_proba = model.predict(test_raster)
y_classes = keras.np_utils.probas_to_classes(y_proba)
print (y_classes)


# Predict new data and export the probability raster
prediction = np.reshape(predicted, (ds3.RasterYSize, ds3.RasterXSize))
outFile = 'schier_predict.tif'
raster.export(prediction, ds3, filename=outFile, dtype='float')
