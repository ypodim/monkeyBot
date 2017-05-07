import socket
import time
import json

class Servos(object):
    """docstring for Servos"""
    def __init__(self):
        super(Servos, self).__init__()
        self.PWMpins = [17, 18, 27, 22, 23, 24]
        self.pwm = [45] * len(self.PWMpins)
        self.yawPin = self.PWMpins[0]
        self.pitchPin = self.PWMpins[1]
        self.MIN_WIDTH = 650
        self.MAX_WIDTH = 2000
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.initPWM()
        print("servos initialized")

    def initPWM(self):
        try:
            with open("servo.position") as f:
                self.pwm = json.loads(f.read()).get("pwm")
        except:
            pass

        for servo in xrange(len(self.PWMpins)):
            self.send(servo, self.pwm[servo])
        print("PWMs initialized")

    def angle2pulse(self, angle):
        angle = int(angle)
        return self.MIN_WIDTH + 1.0 * angle * (self.MAX_WIDTH - self.MIN_WIDTH) / 90
        # pulse = max(self.MIN_WIDTH, pulse)
        # return min(self.MAX_WIDTH, pulse)

    def savePosition(self, servo, angle):
        self.pwm[servo] = angle
        with open("servo.position", "w") as f:
            f.write(json.dumps(dict(pwm=self.pwm)))

    def absolutePosition(self, servo, angle):
        self.send(servo, angle)

    def relativePosition(self, servo, angleStep):
        angle = self.pwm[servo] + angleStep
        self.absolutePosition(servo, angle)

    def send(self, servo, angle):
        angle = max(0, angle)
        angle = min(90, angle)
        self.savePosition(servo, angle)
        pulse = self.angle2pulse(angle)
        pin = self.PWMpins[servo]
        rawMsg = "%c%04d" % (48+pin, pulse)
        # rawMsg = self.formatPinPulse(self.PWMpins[servo], angle)
        self.sendRaw(rawMsg)

    def sendRaw(self, message):
        UDP_IP = "127.0.0.1"
        UDP_PORT = 8888
        # print(message)
        self.sock.sendto(message, (UDP_IP, UDP_PORT))