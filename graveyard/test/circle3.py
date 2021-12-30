from collections import deque
import numpy as np
import imutils
import cv2
import time

# green
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)
# redish
# greenLower = (150,50,50)
# greenUpper = (170,255,255)
# red
greenLower = (160, 100, 100)
greenUpper = (190, 255, 255)

pts = deque(maxlen=32)
camera = cv2.VideoCapture(0)

prevx = 0
prevy = 0
while True:
      # grab the current frame
      (grabbed, frame) = camera.read()
 
      # resize the frame, blur it, and convert it to the HSV
      # color space
      # frame = imutils.resize(frame, width=600)
      # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
      hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
 
      # construct a mask for the color "green", then perform
      # a series of dilations and erosions to remove any small
      # blobs left in the mask
      mask = cv2.inRange(hsv, greenLower, greenUpper)
      mask = cv2.erode(mask, None, iterations=2)
      mask = cv2.dilate(mask, None, iterations=2)
      # find contours in the mask and initialize the current
      # (x, y) center of the ball
      cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)[-2]
      center = None
 
      # only proceed if at least one contour was found
      if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)

            a = 0.5
            x = a*x + (1-a)*prevx
            y = a*y + (1-a)*prevy
            prevx = x
            prevy = y
            
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
 
            # only proceed if the radius meets a minimum size
            if radius > 10:
                  # draw the circle and centroid on the frame,
                  # then update the list of tracked points
                  cv2.circle(frame, (int(x), int(y)), int(radius),
                        (0, 255, 255), 2)
                  cv2.circle(frame, center, 5, (0, 0, 255), -1)
 
      # update the points queue
      pts.appendleft(center)

      # loop over the set of tracked points
      for i in xrange(1, len(pts)):
            # if either of the tracked points are None, ignore
            # them
            if pts[i - 1] is None or pts[i] is None:
                  continue
 
            # otherwise, compute the thickness of the line and
            # draw the connecting lines
            thickness = int(np.sqrt(32 / float(i + 1)) * 2.5)
            cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
 
      # show the frame to our screen
      cv2.imshow("Frame", frame)
      key = cv2.waitKey(1) & 0xFF
 
      # if the 'q' key is pressed, stop the loop
      if key == ord("q"):
            break
 
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()

