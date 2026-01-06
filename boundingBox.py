'''
Name: Spencer
Date: 12/8/25
About: colour threshold an image and create bounding box for the object. 
This can be used in order to do something useful 

'''

import cv2
import numpy as np
import os
import platform #check the os of the user
import matplotlib.pyplot as plt

#to convert dcm -> jpg
import pydicom
from PIL import Image


'''
Convert the DCM image file into a PNG (Lossless Compression)
@param file (string): file path inserted 
'''

def convType (file):

    #read in the dicom file
    image = pydicom.dcmread(file)

    #only look at the image part of the dcm file by converting it into an array
    #convert pixels to floats to avoid under/overflow information loss
    image = image.pixel_array.astype(float)

    #img rescaling, convert all negative pixels into 0 and normalize between (0-255), converted into floats
    imgRescale = (np.maximum(image,0) / image.max()) * 255

    #convert floats into integers
    final = np.uint8(imgRescale)
    final = Image.fromarray(final)
    final.show()

    #save as png
    final.save(file + ".png")

    #return filename.png
    return file + ".png"





''' 
Look to automating the folder input
--> can be improved to make a GUI to select the folder 
--> user input requires exact directory

'''
def getDirectory ():

    #opSys = platform.system()
    #set the path of nothing
    path = ""
    while True:

        path = input("Input the Path: ")

        if os.path.isdir(path):
            print( "The path is : " + path)
            return path

        else:
            print("no path found! ")

''' 
Run through each image in folder to get the path
@param folderPath (str): folder path 

'''
def runImages (folderPath):

    #for files in the path
    #dirRoot: current directory path
    #dirNames: subdirectories within path
    #dirFiles: non-directory files within path
    for dirRoot, dirNames, dirFiles in os.walk(folderPath):
        for file in dirFiles:
            #make it so that it only takes the specific file type (.dcm)
            if file.endswith(".dcm"):
                completePath = os.path.join(dirRoot, file)
                #print(completePath)

            #need to convert dcm -> png (lossless)
                convType(completePath)

            #call colourThreshold



''' 
Run through each image and create the threshold masks
@param imgpath (str): image path 

'''
def colourThreshold (imgpath):

    image = cv2.imread(imgpath)

    #creating arrays for upper and lower bound (H,S,V)
    upperBound = np.array([190, 255, 255])
    lowerBound = np.array([10, 10, 10])

    #convert the image into HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    #creating the mask through HSV bounding via upper and lower bound
    mask = cv2.inRange(hsv, lowerBound, upperBound)
    cv2.imwrite('mask.png', mask)


    #creating the bounding box

    #start by finding contours (num and where)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #takes 2 outputs

    #for each contour create a bounding rectangle around it (in this case there is only 1)
    for object in contours:
        x, y, w, h = cv2.boundingRect(object)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imwrite("contoured.png", image)

#Testing
#colourThreshold("JRC.png")
#colourThreshold("laburm.png")

runImages(getDirectory())