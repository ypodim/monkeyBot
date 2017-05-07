import threading
import time
import random
import cv2
from Camera import PiVideoStream

class FPS:
    lastTstamp = time.time()
    fps = 0
    lastFps = 0
    def update(self):
        fps = int(1.0 / (time.time() - self.lastTstamp))
        fps = (self.lastFps + fps)/2
        self.lastFps = fps
        self.fps = "%sfps" % fps
        self.lastTstamp = time.time()
    def get(self):
        return self.fps

class ImageProcessor(threading.Thread):
    def __init__(self):
        super(ImageProcessor, self).__init__()
        self.running = True
        self.callbacks = {}
        self.fps = FPS()
        self.center = dict(x=None, y=None)
        self.radius = None
        self.dimensions = (0, 0)
    
    def process(self, frame):
        greenLower = (150,50,50)
        greenUpper = (170,255,255)
        # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, greenLower, greenUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # find contours in the mask and initialize the current
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        radius = None
        x = None
        y = None
        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            x, y, radius = int(x), int(y), int(radius)
            
        return x, y, radius

    def run(self):
        vs = PiVideoStream()
        self.dimensions = vs.camera.resolution
        vs.start()
        time.sleep(2.0)
         
        while self.running:
            self.fps.update()
            frame = vs.read()
            x, y, radius = self.process(frame)

            # Invert Y axis because camera is upside down
            # if y is not None:
            #     y = vs.camera.resolution[0] - y

            # print x, y, radius, self.fps.get()
            self.radius = radius
            self.center = dict(x=x, y=y)
         
        # do a bit of cleanup
        vs.stop()
        print("camera terminated")

    def register(self, event, callback):
        self.callbacks[event] = callback

    def die(self):
        self.running = False

