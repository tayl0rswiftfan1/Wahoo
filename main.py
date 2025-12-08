import cv2
import numpy as np
import matplotlib.pyplot as plt

'''
#loading the image
image = cv2.imread("JRC.png") #destination of the photo or whatever

#gay the image
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
cv2.imwrite("gray.png", gray)

#guassian blur the photo ... (input array, kernel size, and how much blur you can get)
blur = cv2.GaussianBlur(gray, (7,7), 10)
cv2.imwrite("blur.png", blur)

#thresholding to crate a binary mask
thresh = cv2.threshold(gray, 0, 255,  cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
cv2.imwrite("uhh.png", thresh)


kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
cv2.imwrite("kern.png", kernel)

dilate = cv2.dilate(thresh, kernel, iterations=1)
cv2.imwrite("dilate.png", dilate)

# create binary mask, only external contours,  compress points
contours, heiarchy = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#draw the contours
imageContors = cv2.drawContours(image, contours, -1, (0, 255, 0), 2)  # green contours
cv2.imwrite("contours.png", imageContors)

'''

'''
#thresholding check

def thresholding(imgpath):

#whats the image!
    image = cv2.imread(imgpath)
    #image to grayscale (skip this instead use HSV)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    threshOptions = [cv2.THRESH_BINARY, cv2.THRESH_BINARY_INV, cv2.THRESH_TOZERO, cv2.THRESH_TRUNC]
    titles = ["BINARY", "BINARY_INV", "TOZERO", "TRUNC"]

    plt.figure(figsize=(8, 8))

#show the threshold

    for i in range(len(threshOptions)):
        retVal, thresh = cv2.threshold(gray, 185, 255, threshOptions[i])

        plt.subplot(2, 2, i+1)
        plt.imshow(thresh, cmap='gray')
        plt.title(titles[i])
        plt.axis("off")

    plt.tight_layout()
    plt.show()

thresholding("JRC.png")

'''

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