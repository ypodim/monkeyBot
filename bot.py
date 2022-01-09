#!/usr/bin/env python3

import board

import numpy as np
import cv2

from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import picamera
from collections import namedtuple
from sound import Sounds

class Point:
    def __init__(self, a, b):
        self.a = int(a)
        self.b = int(b)
    def __str__(self):
        return f"Point <{self.a},{self.b}>"
class Waypoints:
    def __init__(self):
        self.points = []
        self.index = -1
    def add(self, p: Point):
        self.points.append(p)
    def next(self):
        if len(self.points) == 0 or self.index == len(self.points)-1:
            return None
        self.index += 1
        return self.points[self.index]
    def current(self):
        if len(self.points) == 0 or self.index < 0 or self.index == len(self.points):
            return None
        return self.points[self.index]
    def isDone(self):
        return self.index == len(self.points) - 1

class Motor:
    def __init__(self, confdict):
        config = namedtuple("motorConf", confdict.keys())(*confdict.values())
        self.speedDelay = config.speedDelay
        self.minPos = config.minPos
        self.maxPos = config.maxPos
        self.pos = 0
        self.targetPos = 0
        self.dir = stepper.FORWARD
        self.loop = config.loop
        self.style = stepper.DOUBLE
        self.name = config.name # motor name
        self.stepper = config.stepper
        self.state = "ok"
        self.stepper.release()
    def setPos(self, targetPos, clb, delay=0.001):
        self.state = "running"
        self.targetPos = min(targetPos, self.maxPos)
        self.targetPos = max(targetPos, self.minPos)
        self.clb = clb
        # print(f"{self.name}: at {self.pos} - target {self.targetPos}")
        self.loop.call_later(delay, self.step)
    def step(self):
        if self.targetPos == self.pos:
            self.state = "ok"
            # self.stepper.release()
            self.loop.call_later(0.5, self.stepper.release)
            self.clb(self.name)
            return

        self.setDir(self.targetPos > self.pos)
        self.stepper.onestep(direction=self.dir, style=self.style)
        
        if self.dir == stepper.FORWARD:  self.pos += 1
        if self.dir == stepper.BACKWARD: self.pos -= 1
        # print(f"{self.name}: new pos {self.pos} - target {self.targetPos}")
        self.loop.call_later(self.speedDelay, self.step)

    def setDir(self, direction: bool):
        if direction: self.dir = stepper.FORWARD
        else:         self.dir = stepper.BACKWARD
    def hold(self):
        self.stepper.onestep(style=1000)
    def cleanup(self):
        self.stepper.release()

class Bot:
    def __init__(self, loop):
        self.loop = loop
        self.steppers = MotorKit(address=0x61, i2c=board.I2C())
        self.pwms = MotorKit(address=0x60, i2c=board.I2C())
        self.sound = Sounds()
        self.light = Light(self.pwms.motor4)
        # self.sound.play_preset("hi")

        motorAconf = dict(
            name="motorA",
            speedDelay=0.005,
            minPos=-400,
            maxPos=400,
            stepper=self.steppers.stepper1,
            loop=self.loop)
        motorBconf = dict(
            name="motorB",
            speedDelay=0.002,
            minPos=-1200,
            maxPos=1200,
            stepper=self.steppers.stepper2,
            loop=self.loop)
        self.A = Motor(motorAconf)
        self.B = Motor(motorBconf)
        self.wp = Waypoints()

    def readyClb(self, motor_name, delay=1):
        if self.A.state == "ok" and self.B.state == "ok":
            # print(f"both done with {self.wp.current()}")
            self.sound.play_preset("bye")
            if self.wp.isDone():
                pass
            else:
                p = self.wp.next()
                print(f"continuing with {p}")
                self.A.setPos(p.a, self.readyClb, delay=delay)
                self.B.setPos(p.b, self.readyClb, delay=delay)
        else:
            if self.A.state != "ok":
                # print("motorA still working: %s" % self.A.state)
                pass
            if self.B.state != "ok":
                # print("motorB still working: %s" % self.B.state)
                pass

    def play_twitch(self, actions):
        for a in actions:
            self.wp.add(Point(a[0], a[1]))
        p = self.wp.next()
        self.A.setPos(p.a, self.readyClb)
        self.B.setPos(p.b, self.readyClb)

    def run(self, cmd):
        rangeA = 170
        rangeB = 50
        actions = []
        if cmd == "peek_up_left": actions = [(0,-50), (0,0)]
        if cmd == "peek_right": actions = [(-50,0), (0,0)]
        if cmd == "down": self.B.setPos(self.B.pos + 10, self.readyClb)
        if cmd == "up": actions = self.B.setPos(self.B.pos - 10, self.readyClb)
        if cmd == "holdb": self.B.hold()
        if cmd == "releaseb": self.B.hold()
        if cmd == "light": self.light.toggle()
        if cmd == "sound": self.sound.play_preset("bye")
        if cmd == "test": pass

        if actions:
            self.play_twitch(actions)

        # segB = 3
        # for i in range(segB):
        #     rb = int(-0.5*rangeB) + i*int(rangeB/(segB-1))

        #     segA = 5
        #     for i in range(segA):
        #         ra = rangeA - i*int(2*rangeA/(segA-1))
        #         print(ra, rb)
        #         self.wp.add(Point(ra, rb))

    def cleanup(self):
        self.A.cleanup()
        self.B.cleanup()
        print("bot cleaned up")

class Light:
    def __init__(self, pwm):
        self.on = False
        self.pwm = pwm
    def toggle(self):
        if self.on:
            self.pwm.throttle = 0
        else:
            self.pwm.throttle = 0.1

        self.on = not self.on


class Eye:
    def __init__2(self):
        self.c = picamera.PiCamera()
        self.c.resolution = (1024, 768)
        # self.c.framerate = 30
        image = np.empty((1024 * 768 * 3,), dtype=np.uint8)
        self.c.capture(image, 'yuv')
        image = image.reshape((1024, 768, 3))
        # image.tofile("one.bin")
        img = Image.fromstring('L', imgSize, image, 'raw', 'F;16')
        img.save("foo.png")
        
    def __init__(self):
        cap = cv2.VideoCapture(0) # video capture source camera (Here webcam of laptop) 
        ret,frame = cap.read() # return a single frame in variable `frame`
        cv2.imwrite('c1.png', frame)
        cap.release()
        print("done")


    def snapshot(self):
        camera = PiCamera()
        camera.start_preview()
        print("waiting for warmup...")
        # sleep(5)
        camera.capture('/home/pi/ws/test/image.jpg')
        print("took pic. Stopping camera...")
        camera.stop_preview()
        print("stopped camera")


if __name__=="__main__":
    try:
        # e = Eye()
        import time
        import tornado.ioloop

        b = Bot(tornado.ioloop.IOLoop.current())
        # b.run()
        b.pwms.motor4.throttle = 0.1
        time.sleep(3)
        b.pwms.motor4.throttle = None

    except KeyboardInterrupt:
        print("exiting")

    b.cleanup()
