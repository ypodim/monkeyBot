import time
import RPi.GPIO as gpio

class Motors(object):
    """docstring for Motors"""
    def __init__(self, pwm, ain1, ain2):
        super(Motors, self).__init__()
        self.speed = 0
        self.pwm, self.ain1, self.ain2 = pwm, ain1, ain2
        print("motors initialized")

    def goLeft(self, deadline, blocking, speed=10):
        startTime = time.time()
        if blocking:
            while startTime + deadline > time.time():
                time.sleep(0.01)
        else:
            self.targetSpeed = speed
            self.deadline = 0

        self.speed = -abs(speed)

    def goRight(self, speed=10):
        self.speed = abs(speed)

    def move(self, step):
        if step == 0:
            return 0
        direction = gpio.HIGH if step > 0 else gpio.LOW
        gpio.output(self.ain1, direction)
        gpio.output(self.ain2, not direction)
        for i in xrange(15):
            self.pwm.ChangeDutyCycle(i)
            time.sleep(0.05)
        time.sleep(0.5)
        for i in xrange(15):
            self.pwm.ChangeDutyCycle(15-i)
            time.sleep(0.05)
        self.pwm.ChangeDutyCycle(0)

    def stop(self):
        self.speed = 0


def main():
    print("Ok")
if __name__=="__main__":
    main()
