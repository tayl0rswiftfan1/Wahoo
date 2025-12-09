import cv2
import numpy as np
import matplotlib.pyplot as plt

'''
Name: Spencer
Date: 12/8/25
About: colour threshold an image and create bounding box for the object. 
This can be used in order to do something useful 

'''

#Look to automating the file input
##

def colourThreshold (imgpath):

    image = cv2.imread(imgpath)

    #creating arrays for upper and lower bound (H,S,V)
    upperBound = np.array([90, 255, 255])
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

colourThreshold("JRC.png")