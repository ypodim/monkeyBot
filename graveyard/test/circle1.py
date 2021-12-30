import cv2
import numpy as np

img = cv2.imread('pic1.jpg')
img = cv2.medianBlur(img,5)
# cimg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
himg = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
gimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

boundaries = [
	# ([17, 15, 100], [50, 56, 200]),
	# ([86, 31, 4], [220, 88, 50]),
	# ([25, 146, 190], [62, 174, 250]),
	# ([103, 86, 65], [145, 133, 128])
	([310,32,35], [330,32,35])
]
for (lower, upper) in boundaries:
	# create NumPy arrays from the boundaries
	lower = np.array(lower, dtype=np.uint8)
	upper = np.array(upper, dtype=np.uint8)
 
	# find the colors within the specified boundaries and apply
	# the mask
	mask = cv2.inRange(himg, lower, upper)
	output = cv2.bitwise_and(img, img, mask=mask)
 
	# show the images
	cv2.imshow("images", np.hstack([img, output]))
	cv2.waitKey(0)

circles = cv2.HoughCircles(img,cv2.cv.CV_HOUGH_GRADIENT,1,20,param1=50,param2=30,minRadius=0,maxRadius=0)

circles = np.uint16(np.around(circles))
for i in circles[0,:]:
    # draw the outer circle
    cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
    # draw the center of the circle
    cv2.circle(img,(i[0],i[1]),2,(0,0,255),3)
    print i

cv2.imshow('detected circles',cimg)
cv2.waitKey(0)
cv2.destroyAllWindows()