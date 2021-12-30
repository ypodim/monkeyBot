import time
import RPi.GPIO as gpio

class Stepper(object):
    """docstring for Stepper motor"""
    def __init__(self, stepPin, dirPIn):
        super(Stepper, self).__init__()
        self.speed = 0
        self.stepPin, self.dirPIn = stepPin, dirPIn
        gpio.setup(self.stepPin, gpio.OUT)
        gpio.setup(self.dirPIn, gpio.OUT)
        print("stepper initialized")

    def step(self, step, direction=gpio.HIGH):
        gpio.output(self.dirPIn, direction)
        
        for i in range(10):
            time.sleep(0.001)
        for i in range(step):
            gpio.output(self.stepPin, gpio.HIGH)
            time.sleep(0.001)
            gpio.output(self.stepPin, gpio.LOW)
            time.sleep(0.001)

def main():
    gpio.setmode(gpio.BCM)
    gpio.setwarnings(False)
    stepper = Stepper(stepPin=4, dirPIn=3)
    stepper.step(100, 0)
    gpio.cleanup()

if __name__=="__main__":
    main()
