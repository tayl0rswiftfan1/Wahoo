'''
Name: Spencer
Date: 12/8/25
Last Modified: 1/12/26
About: colour threshold an image and create bounding box for the object. 
This can be used in order to do something useful 

'''

import cv2
import numpy as np
import json
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
Creating a file to store the each patient file 
@param jsonPath (str): path for the json file, should save local 

'''
def processedFile (jsonPath):
    patientFile = "processed.json"

    # load once
    if os.path.exists(jsonPath):
        with open(jsonPath, "r") as f:
            #reuturn file
            return json.load(f)
    #if no file
    return {}




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

i think it may need a third param : patient ID -- for folder creation
@param patientID (str): should be the file path for the patienID folder

'''

def convType2 (medImg, segImg):

    #reading the medical image and the segmenation
    medImage = itk.ReadImage(medImg)
    segImage = itk.ReadImage(segImg)

    #use numpy to get the array of images and seg.. output shape is [z,y,x]
    medImageArray = itk.GetArrayFromImage(medImage)
    segImageArray = itk.GetArrayFromImage(segImage)

    #line up the slice with the seg (temporary select one slice)
    sliceLayer =  medImageArray.shape[0] // 2 #set arb middle slice

    #this can be looped for all slices
    #for sliceLayer in range (medImageArray.shape[0]):

    #line up slices (@ selected slice)
    imgSlice = medImageArray [sliceLayer]
    segSlice = segImageArray [sliceLayer]

    #manually normalize CT image slice
    imgSliceNormd = np.clip(imgSlice, -1000, 3000)

    #add 1000 to the HU to get rid of the negative pixels, *255 scales to 8-bit img
    imgSliceNormd = ((imgSliceNormd + 1000)/ 4000 * 255).astype(np.uint8)

    #convert the ct to BGR
    colourCT = cv2.cvtColor(imgSliceNormd, cv2.COLOR_GRAY2BGR)

    #get the amount of labels from the seg masks @ slice.. i guess this works
    numLabels = np.unique(segSlice)

    for label in numLabels:

        #for each label tag.. overlay the mask @ slice, treated as the tag, so implant = 1 and bone seg = 2 (hopefully)
        if label == 1:

            #put the mask on (BGR colouring)
            colourCT [segSlice == label] = [0,255,0] #green


        #this is for the bone seg if correct
        elif label == 2:

            #put the mask on (BGR colouring)
            colourCT [segSlice == label] = [0,150,255] #orange

    #convert to img
    colourCT = Image.fromarray(colourCT)


    #save images within a new folder
    outputFolder = os.path.join((os.path.dirname(medImg)), "output")
    #handles if the folder already exists
    os.makedirs(outputFolder, exist_ok = True)

    #file name saved as a png for now
    fileName = "SegCT" + str(sliceLayer) + ".png"
    savePath = os.path.join(outputFolder, fileName)

    #savee
    colourCT.save(savePath)


    #call boudning box function (maybe)..
    colourThreshold(savePath, str(sliceLayer))


    #return the path of the image so it can be used by colourThreshold
    return savePath



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

    #accessing json file for name storage and folder path
    patientFilePath = "processed.json"
    processed = processedFile(patientFilePath)


    #for files in the path
    #dirRoot: current directory path (folder)
    #dirNames: subdirectories within path (other folders in folder)
    #dirFiles: non-directory files within path (files in folder)
    for dirRoot, dirNames, dirFiles in os.walk(folderPath):

        #name of the last folder it was in (ie.. Patient001)
        patientID = os.path.basename(os.path.dirname(dirRoot))

        # check to see if case is in the file directory and processed
        if patientID in processed and processed[patientID].get("processed"):
            print(f"Skipping {patientID} (.. Already processed)")
            continue

        #set up the seg and image path
        imagePath = " "
        segPath = " "


        for file in dirFiles:
            #make it so that it only takes the specific file type (.nrrd) *changed to nrrd
            if file.endswith(".dcm"):
                #this is the complete file path
                completePath = os.path.join(dirRoot, file)
                completePath = fr'{completePath}'
                print(completePath)

                #look for segmentation file and image file
                if "seg" in file.lower():
                    segPath = completePath

                else:
                    imagePath = completePath


        #if folder contains both the seg path and the image path
        if segPath and imagePath:
            print(f"Prcessing {patientID}")

                  
        #need to convert nnrd -> png (lossless) * think about maybe using tiff?

            #call colour threshold to threshold the images while calling convtype2 to convert the nrrd files into something useful
            convType2(imagePath, segPath) #third param for convtype2

            #tag for the json file
            processed [patientID] = {
                "Image Path" : imagePath,
                "Seg Path" : segPath,
                "Processed" : True
            }

            #tag it int the json file
            with open(patientFilePath, "w") as f:
                json.dump(processed, f)

        else:
            print(f"error with something in {patientID}")




''' 
Run through each image and create the threshold masks
@param imgpath (str): image path 
@param sliceLayer (str): Slice number the file saving 
(this could be nice)
@param outputFolderPath (str): path of the output folder 

'''
def colourThreshold (imgpath, sliceLayer):

    image = cv2.imread(imgpath)

    #creating arrays for upper and lower bound (H,S,V)
    upperBound = np.array([190, 255, 255])
    lowerBound = np.array([10, 10, 10])

    #convert the image into HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    #creating the mask through HSV bounding via upper and lower bound
    mask = cv2.inRange(hsv, lowerBound, upperBound)
    #cv2.imwrite('mask.png', mask)


    #creating the bounding box

    #start by finding contours (num and where)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #takes 2 outputs

    #for each contour create a bounding rectangle around it (in this case there is only 1)
    for object in contours:
        x, y, w, h = cv2.boundingRect(object)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    #cv2.imwrite("contoured.png", image)


    #save images within a new folder (boundedOutput) folder
    outputFolder = os.path.join((os.path.dirname(imgpath)), "boundedOutput")
    #handles if the folder already exists
    os.makedirs(outputFolder, exist_ok = True)

    #saving the images with PIL
    image = Image.fromarray(image)

    #save path into the new folder
    fileName = "BoundedSegCT" + sliceLayer + ".png"
    savePath = os.path.join(outputFolder, fileName)

    #savee
    image.save(savePath)


#Testing
#colourThreshold("JRC.png")
#colourThreshold("laburm.png")

runImages(getDirectory())