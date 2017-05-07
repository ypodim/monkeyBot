from Stream import PiVideoStream
import time
import cv2
 
vs = PiVideoStream()
vs.start()
time.sleep(2.0)
 
while 1:
    frame = vs.read()
 
 
# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()