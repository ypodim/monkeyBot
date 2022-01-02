#!/usr/bin/env python
import cv2
import numpy as np
import time
from threading import Thread
from queue import Queue
from datetime import datetime

def putIterationsPerSec(frame, iterations_per_sec):
    """
    Add iterations per second text to lower-left corner of a frame.
    """

    cv2.putText(frame, "{:.0f} iterations/sec".format(iterations_per_sec),
        (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
    return frame

class CountsPerSec:
    """
    Class that tracks the number of occurrences ("counts") of an
    arbitrary event and returns the frequency in occurrences
    (counts) per second. The caller must increment the count.
    """

    def __init__(self):
        self._start_time = None
        self._num_occurrences = 0

    def start(self):
        self._start_time = datetime.now()
        return self

    def increment(self):
        self._num_occurrences += 1

    def countsPerSec(self):
        elapsed_time = (datetime.now() - self._start_time).total_seconds()
        return self._num_occurrences / elapsed_time if elapsed_time > 0 else 0

class UsbCamera(object):

    """ Init camera """
    def __init__(self, dev=0):
        # select first video device in system
        self.cam = cv2.VideoCapture(dev)
        # set camera resolution
        self.w = 1024
        self.h = 768
        # set crop factor
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.h)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.w)
        # load cascade file
        self.face_cascade = cv2.CascadeClassifier('face.xml')
        self.running = True
        self.q = Queue(maxsize=100)
    def start(self):
        Thread(target=self.run, args=()).start()
        return self
    def stop(self):
        self.running = False
    def run(self):
        while self.running:
            jpeg, image = self.get_frame(True)
            self.q.put(image)

    def set_resolution(self, new_w, new_h):
        """
        functionality: Change camera resolution
        inputs: new_w, new_h - with and height of picture, must be int
        returns: None ore raise exception
        """
        if isinstance(new_h, int) and isinstance(new_w, int):
            # check if args are int and correct
            if (new_w <= 800) and (new_h <= 600) and \
               (new_w > 0) and (new_h > 0):
                self.h = new_h
                self.w = new_w
            else:
                # bad params
                raise Exception('Bad resolution')
        else:
            # bad params
            raise Exception('Not int value')

    def get_frame(self, fdenable):
        """
        functionality: Gets frame from camera and try to find feces on it
        :return: byte array of jpeg encoded camera frame
        """
        success, image = self.cam.read()
        if success:
            # scale image
            image = cv2.resize(image, (self.w, self.h))
            if fdenable:
                # resize image for speeding up recognize
                gray = cv2.resize(image, (320, 240))
                # make it grayscale
                gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
                # face cascade detector
                faces = self.face_cascade.detectMultiScale(gray)
                # draw rect on face arias
                scale = float(self.w / 320.0)
                count = 0
                for f in faces:
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    x, y, z, t = [int(float(v) * scale) for v in f]
                    cv2.putText(image, str(x) + ' ' + str(y), (0, (self.h - 10 - 25 * count)), font, 1, (0, 0, 0), 2)
                    count += 1
                    cv2.rectangle(image, (x, y), (x + z, y + t), (255, 255, 255), 2)
        else:
            image = np.zeros((self.h, self.w, 3), np.uint8)
            cv2.putText(image, 'No camera', (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
        # encoding picture to jpeg
        
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes(), image


if __name__=='__main__':
    cam = UsbCamera(1).start()
    cps = CountsPerSec().start()
    
    last_image = None
    while 1:
        grabbed_frame = False
        try:
            image = cam.q.get(block=False)
            last_image = image
            grabbed_frame = True
        except:
            if last_image is None:
                continue
        frame = putIterationsPerSec(last_image, cps.countsPerSec())
        cv2.imshow("the pol", frame)
        if grabbed_frame:
            cam.q.task_done()
        cps.increment()
        key = cv2.waitKey(1)
        if key == ord('q'):
            cam.stop()
            break

