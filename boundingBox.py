'''
Name: Spencer
Date: 12/8/25
Last Modified: 1/8/26
About: colour threshold an image and create bounding box for the object. 
This can be used in order to do something useful 

'''

import cv2
import numpy as np
import os
import platform #check the os of the user
import matplotlib.pyplot as plt

#to convert dcm -> png
import pydicom
from PIL import Image

#to convert nrrd -> png
import SimpleITK as itk
from PIL.ImageColor import colormap

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
    final.save(file + ".png") #save in folder
    #print (file + ".png")

    #return filename.png
    return file + ".png"


'''
Convert Nrrd file into PNG, this takes both the segmentation mask and the medical image (CT) and converts it into a PNG 
@param medImg (str): nrrd file path of the medical image 
@param segImg (str): nrrd file paht of the segmentaion mask 
'''

def convType2 (medImg, segImg):

    #reading the medical image and the segmenation
    medImage = itk.ReadImage(medImg)
    segImage = itk.ReadImage(segImg)

    #use numpy to get the array of images and seg.. output shape is [z,y,x]
    medImageArray = itk.GetArrayFromImage(medImage)
    segImageArray = itk.GetArrayFromImage(segImage)

    #line up the slice with the seg
    slice =  medImageArray.shape[0] // 2 #set arb middle slice

    #this can be looped for all slices

    #line up slices (@ selected slice)
    imgSlice = medImageArray [slice]
    segSlice = segImageArray [slice]

    '''
    #slice normalization .. idk
    imgSliceNormd = cv2.normalize(imgSlice, None, 0, 255, cv2.NORM_MINMAX)
    imgSliceNormd = imgSlice.astype(np.uint8)
    '''
    #manually normalize CT image slice
    imgSliceNormd = np.clip(imgSlice, -1000, 3000)

    #add 1000 to the HU to get rid of the negative pixels, *255 scales to 8-bit img
    imgSliceNormd = ((imgSliceNormd + 1000)/ 4000 * 255).astype(np.uint8)

    #overlay the mask @ slice.. binary mask
    overlayMask = (segSlice == 1)

    #convert the ct to BGR
    colourCT = cv2.cvtColor(imgSliceNormd, cv2.COLOR_GRAY2BGR)

    #put the mask on
    colourCT [overlayMask] = [0,255,0]

    #save the file
    cv2.imwrite("seg+CT.png", colourCT)







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