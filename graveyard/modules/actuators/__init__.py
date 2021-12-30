from Servos import Servos
from Motors import Motors
from Buzzer import Buzzer
from Light import Light
import threading
import time
import RPi.GPIO as gpio

# blue  pwmb 5
# green   bin2 6
# yellow  bin1 12
# orange  ain1 13
# red   ain2 19
# brown pwma 16

class Pin:
    ain1 = 13
    ain2 = 19
    pwmA = 16
    bin1 = 12
    bin2 = 6
    pwmB = 5

gpio.setmode(gpio.BCM)
gpio.setup(Pin.pwmA, gpio.OUT)
gpio.setup(Pin.ain1, gpio.OUT)
gpio.setup(Pin.ain2, gpio.OUT)
gpio.setup(Pin.pwmB, gpio.OUT)
gpio.setup(Pin.bin1, gpio.OUT)
gpio.setup(Pin.bin2, gpio.OUT)

gpio.output(Pin.bin1, gpio.HIGH) # Light: do NOT modify
gpio.output(Pin.bin2, gpio.LOW)  # Light: do NOT modify

class Actuators(threading.Thread):
    """docstring for Actuators"""
    def __init__(self):
        super(Actuators, self).__init__()

        self.pwmA = gpio.PWM(Pin.pwmA, 50)
        self.pwmB = gpio.PWM(Pin.pwmB, 100)
        self.pwmA.start(0) # Motors
        self.pwmB.start(0) # Light

        self.servos = Servos()
        self.motors = Motors(self.pwmA, Pin.ain1, Pin.ain2)
        self.light = Light(self.pwmB)
        self.buzzer = Buzzer()
        self.running = True
        print("actuators initialized")

    def run(self):
        while self.running:

            time.sleep(0.05)
        print("Actuators signing off")
        self.pwmA.stop()
        self.pwmB.stop()
        gpio.cleanup()

    def die(self):
        self.running = False

    def chirp(self, ignorePeriod=5):
        self.buzzer.buzz(ignorePeriod)

    def goLeft(self, duration, blocking=False):
        return self.motors.goLeft(duration, blocking)

    def yaw(self, angleStep):
        self.servos.relativePosition(0, angleStep)

    def getYaw(self):
        return self.servos.pwm[0]

    def motor(self, step):
        return self.motors.move(step)

    def pitch(self, angleStep):
        self.servos.relativePosition(1, angleStep)

    def getPitch(self):
        return self.servos.pwm[1]

