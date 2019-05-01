from __future__ import print_function
from __future__ import division
import cv2 as cv
import argparse
import numpy as np
import math


alpha_slider_max = 255
title_window = 'Edge Detector'

def isEdge(image, i, j, grade):
	edge = False
	if (image[i][j]>grade):
		if (i!=0):
			if (image[i-1][j]<=grade):
				edge = True
		if (i!=len(image)-1):
			if (image[i+1][j]<=grade):
				edge = True
		if (j!=0):
			if (image[i][j-1]<=grade):
				edge = True	
		if (j!=len(image[i])-1):
			if (image[i][j+1]<=grade):
				edge = True	
	return edge

def on_trackbar(val):
    dst = cv.Canny(np.asarray(blur),val,val)
    cv.imshow(title_window, dst)


parser = argparse.ArgumentParser(description='Code for Adding a Trackbar to our applications tutorial.')
parser.add_argument('--input1', help='Path to the first input image.', default='img_base10.png')
args = parser.parse_args()

### read image
fname = " base/"+args.input1
src1 = cv.imread(fname,0)
if src1 is None:
    print('Could not open or find the image: ', args.input1)
    exit(0)

### apply thresholding to original image 
threshold1 = input("input an thresholding value: ")
threshold1 = int(threshold1)
for i in range(len(src1)):
	for j in range(len(src1[i])):
		if (src1[i][j]< 255 and src1[i][j] > threshold1):
			src1[i][j] = 255
		else:
			src1[i][j] = 0

### apply Gaussian Blur to resulting image
blur = cv.GaussianBlur(src1,(5,5),1)
fname = "image/img_stroke_%d.png" %(threshold1)
cv.imwrite(fname, blur)


'''
Create trackBar window for edge detection
'''
cv.namedWindow(title_window)
trackbar_name = 'Alpha x %d' % alpha_slider_max
cv.createTrackbar(trackbar_name, title_window , 0, alpha_slider_max, on_trackbar)

cv.waitKey()

cv.destroyAllWindows()

### input a final value for edge detection
val = input("input an edge detection threshold value: ")
val = int(val)
dst = cv.Canny(np.asarray(blur),val,val)
fname = "image/edge_"+str(val)+".png"
cv.imwrite(fname, dst)

cv.imwrite("image/final.png", np.array(blur))