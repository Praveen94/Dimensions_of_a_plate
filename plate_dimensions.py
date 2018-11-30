from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import math

def midpoint(ptA, ptB):
	return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

img_path = "images/calibrated/calibresult.png"


# load the image, convert it to grayscale, and blur it slightly
image = cv2.imread(img_path)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (7, 7), 0)

# perform edge detection, then perform a dilation + erosion to
# close gaps in between object edges
edged = cv2.Canny(gray, 50, 100)
edged = cv2.dilate(edged, None, iterations=1)
edged = cv2.erode(edged, None, iterations=1)
cv2.imshow("Edged",edged)

# find contours in the edge map
cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_NONE)
cnts = cnts[0] if imutils.is_cv2() else cnts[1]

# sort the contours from left-to-right and initialize the
# 'pixels per metric' calibration variable
(cnts, _) = contours.sort_contours(cnts)
pixelsPerMetric = None

# loop over the contours individually
for c in cnts:
	# if the contour is not sufficiently large, ignore it
	if cv2.contourArea(c) < 20:
		continue


	# compute the rotated bounding box of the contour
	orig = image.copy()
	box = cv2.minAreaRect(c)

	#print("contour ",c)
	arc_length = cv2.arcLength(c, True)
	print("arc length is ", arc_length)

	cv2.drawContours(orig, c, -1, (0, 255, 0), 3)
	print("c",c)
	sorted_contours_x = sorted(c, key=lambda k: [k[0][0], k[0][1]])
	sorted_contours_y = sorted(c, key=lambda k: [k[0][1], k[0][0]])
	


	print("the top-right point is", sorted_contours_x[-1])
	print("the bottom-left point is", sorted_contours_x[0])
	print("the bottom-right point is", sorted_contours_y[-1])
	print("the top-left point is", sorted_contours_y[0])
	print("total-contour-points_left",)
	left_mdpt_x=(sorted_contours_y[0][0][0]+sorted_contours_x[0][0][0])/2
	left_mdpt_y=(sorted_contours_y[0][0][1]+sorted_contours_x[0][0][1])/2
	right_mdpt_x=(sorted_contours_x[-1][0][0]+sorted_contours_y[-1][0][0])/2
	right_mdpt_y=(sorted_contours_x[-1][0][1]+sorted_contours_y[-1][0][1])/2

	cv2.circle(orig, (int(sorted_contours_y[0][0][0]), int(sorted_contours_y[0][0][1])), 1, (0, 0, 255), -1) # top left
	cv2.circle(orig, (int(sorted_contours_x[-1][0][0]), int(sorted_contours_x[-1][0][1])), 1, (0, 0, 255), -1)  # top right
	cv2.circle(orig, (int(sorted_contours_y[-1][0][0]), int(sorted_contours_y[-1][0][1])), 1, (0, 0, 255), -1)  # bottom right
	cv2.circle(orig, (int(sorted_contours_x[0][0][0]), int(sorted_contours_x[0][0][1])), 1, (0, 0, 255), -1)  # bottom left
	cv2.circle(orig, (int(left_mdpt_x), int(left_mdpt_y)), 3, (0, 0, 255), -1)
	cv2.circle(orig, (int(right_mdpt_x), int(right_mdpt_y)), 3, (0, 0, 255), -1)



	top_len=math.sqrt((sorted_contours_y[0][0][0]- sorted_contours_x[-1][0][0])**2 + (sorted_contours_y[0][0][1]- sorted_contours_x[-1][0][1])**2)
	bottom_len = math.sqrt((sorted_contours_x[0][0][0]- sorted_contours_y[0][0][0])**2 + (sorted_contours_x[0][0][1]- sorted_contours_y[0][0][1])**2)
	diag_len= math.sqrt((sorted_contours_x[0][0][0]- sorted_contours_y[0][0][0])**2 + (sorted_contours_x[0][0][1]- sorted_contours_y[0][0][1])**2)
	print("top len",top_len)

	l1 = math.sqrt((sorted_contours_y[0][0][0]- sorted_contours_x[-1][0][0])**2 + (sorted_contours_y[0][0][1]- sorted_contours_x[-1][0][1])**2)
	l2 = math.sqrt((left_mdpt_x-right_mdpt_x)**2 + (left_mdpt_y-right_mdpt_y)**2)
	l3 = math.sqrt((sorted_contours_x[0][0][0]- sorted_contours_y[-1][0][0])**2 + (sorted_contours_x[0][0][1]- sorted_contours_y[-1][0][1])**2)
	d1 = math.sqrt((sorted_contours_y[0][0][0]- sorted_contours_y[-1][0][0])**2 + (sorted_contours_y[0][0][1]- sorted_contours_y[-1][0][1])**2)
	d2 = math.sqrt((sorted_contours_x[-1][0][0]- sorted_contours_x[0][0][0])**2 + (sorted_contours_x[-1][0][1]- sorted_contours_x[0][0][1])**2)


	pixelsPerMetric = top_len / 100.11
	dimL1 = l1 / pixelsPerMetric
	dimL3 = l3 / (pixelsPerMetric)
	dimD1 = d1 / (pixelsPerMetric)
	dimD2 = d2 / (pixelsPerMetric)
	dimL2 = l2 / pixelsPerMetric
	print("l1",dimL1)
	print("l2",dimL2)
	print("l3",dimL3)
	print("d1",dimD1)
	print("d2",dimD2)
	print("Diagonal lengths are",dimD1,dimD2)
	
	
	cv2.putText(orig, "{:.1f}mm".format(dimL1),
	  	(int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
	  	 0.65, (255, 255, 255), 2)

	cv2.putText(orig, "{:.1f}mm".format(dimL2),
				(int(tlblX+20), int(tlblY)), cv2.FONT_HERSHEY_SIMPLEX,
				0.65, (255, 255, 255), 2)
    
	cv2.putText(orig, "{:.1f}mm".format(dimL3),
				(int(blbrX - 15), int(blbrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
				0.65, (255, 255, 255), 2)
    

	# show the output image
	cv2.imshow("Image", orig)
	cv2.waitKey(0)