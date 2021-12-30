import time

class AI:
    def __init__(self, sensors, actuators):
        self.sensors = sensors
        self.actuators = actuators
        self.tracking = 0
        self.ball = None

        self.sensors.registerCameraEvent("red", self.callback)
        self.sensors.registerCameraEvent("green", self.callback)
        print "AI is up an thinking"

    def think(self):
        if not self.tracking:
            return

        threshold = 5
        ball = dict(radius=self.sensors.ip.radius, center=self.sensors.ip.center, fps=self.sensors.ip.fps.get())
        x = ball.get("center").get("x")
        y = ball.get("center").get("y")
        
        if ball.get("radius") is None or self.ball is None:
            self.ball = ball
            return

        prev_x = self.ball.get("center").get("x")
        prev_y = self.ball.get("center").get("y")

        if prev_x is None or prev_y is None:
            print "this should not happen again!"
            self.ball["center"] = ball.get("center")
            return

        # if abs(x - prev_x) > 50 or abs(y - prev_y) > 50:
        #     print "ignoring", x, prev_x, y, prev_y
        #     return

        a = 0.2
        x = a*x + (1-a)*prev_x
        y = a*y + (1-a)*prev_y

        y1 = self.sensors.ip.dimensions[1]/2 - threshold
        y2 = self.sensors.ip.dimensions[1]/2 + threshold
        print "%d (%d %d %d) yaw:%d pitch:%d %d" % (x, y1, y, y2, self.actuators.getYaw(), self.actuators.getPitch(), ball.get("radius"))

        step = 3
        delay = 0.2
        if x > self.sensors.ip.dimensions[0]/2 + threshold:
            print "go right!"
            self.actuators.yaw(step)
            time.sleep(delay)
            self.ball.get("center")["x"] = x
        if x < self.sensors.ip.dimensions[0]/2 - threshold:
            print "go left!"
            self.actuators.yaw(-step)
            time.sleep(delay)
            self.ball.get("center")["x"] = x
        if y > self.sensors.ip.dimensions[1]/2 + threshold:
            print "go up!"
            self.actuators.pitch(step)
            time.sleep(delay)
            self.ball.get("center")["y"] = y
        if y < self.sensors.ip.dimensions[1]/2 - threshold:
            print "go down!"
            self.actuators.pitch(-step)
            time.sleep(delay)
            self.ball.get("center")["y"] = y

        self.ball["radius"] = ball.get("radius")
        
        
    def callback(self, event):
        print("Saw %s!" % event)

