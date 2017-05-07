import cv2
import numpy as np
import sys

def resizeImage(img):
    dst = cv2.resize(img,None, fx=0.25, fy=0.25, interpolation = cv2.INTER_LINEAR)
    return dst

def analyze(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_blue = np.array([150,50,50])
    upper_blue = np.array([170,255,255])

    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    res = cv2.bitwise_and(img, img, mask=mask)

    cv2.imshow('img',img)
    cv2.imshow('mask',mask)
    cv2.imshow('res',res)
    # cv2.imwrite('output.jpg', mask)
    # k = cv2.waitKey(0)
    return res

def process(frame):
      # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
      hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
 
      mask = cv2.inRange(hsv, greenLower, greenUpper)
      mask = cv2.erode(mask, None, iterations=2)
      mask = cv2.dilate(mask, None, iterations=2)
      
      # find contours in the mask and initialize the current
      # (x, y) center of the ball
      cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
      center = None
      radius = None
      x = None
      y = None
      if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            
            if radius > 50:
                  M = cv2.moments(c)
                  center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
      return x, y, radius, center


img = cv2.imread("pic2.jpg")
# x, y, radius, center = process(img)

img = cv2.medianBlur(img,3)
masked = analyze(img)
gimg = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)

gimg = cv2.medianBlur(gimg,5)
ret, gimg = cv2.threshold(gimg,50,255,cv2.THRESH_BINARY)

circles = cv2.HoughCircles(gimg,cv2.cv.CV_HOUGH_GRADIENT,1,100,param1=100,param2=50,minRadius=70,maxRadius=150)

if circles != None and len(circles):
    circles = np.uint16(np.around(circles))
    for i in circles[0,:]:
        x, y, r = i
        # draw the outer circle
        cv2.circle(gimg,(i[0],i[1]),r,(255,255,255),2)
        # draw the center of the circle
        cv2.circle(gimg,(i[0],i[1]),2,(0,0,255),3)
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = "%s" % r
        cv2.putText(gimg,text,(x+r,i[1]), font, 1,(255,255,255),2)
        print i

cv2.imshow('detected circles',gimg)
cv2.waitKey(0)
cv2.destroyAllWindows()
