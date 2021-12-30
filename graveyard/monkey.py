#!/usr/bin/env python

import tornado.ioloop
import tornado.web
import tornado.template
import tornado.autoreload
from modules.sensors import Sensors
from modules.actuators import Actuators
from modules.brain import Brain

class Monkey:
    def __init__(self):
        self.sensors = Sensors()
        self.actuators = Actuators()
        self.actuators.start()
        self.brain = Brain(self.sensors, self.actuators)
    def interval(self):
        self.brain.think()
    def die(self):
        self.sensors.die()
        self.actuators.die()

print("starting app")
monkey = Monkey()

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")
        # data = dict(data=monkey.sensors.getValues())
    def post(self):
        rawDirection = self.get_argument("direction")
        speed = self.get_argument("speed")
        self.write("speed: %s  direction: %s\n" % (speed, rawDirection))

class SettingsHandler(tornado.web.RequestHandler):
    def post(self):
        tracking = 0
        if self.get_argument("tracking") == "true": tracking = 1
        monkey.brain.AI.tracking = tracking
        self.write("ok")

class ActuatorHandler(tornado.web.RequestHandler):
    def post(self, actuator):
        if actuator.startswith("servo"):
            servo = self.get_argument("servo")
            result = ""
            if servo not in ["up", "down", "left", "right"]:
                self.write(dict(error="unrecognized servo: %s" % servo))
                return
            elif servo == "up":
                result = monkey.actuators.pitch(5)
            elif servo == "down":
                result = monkey.actuators.pitch(-5)
            elif servo == "left":
                result = monkey.actuators.yaw(-5)
            elif servo == "right":
                result = monkey.actuators.yaw(5)
            self.write(dict(result=result))
        elif actuator == "motor":
            if self.get_argument("direction") == "motor_right": 
                direction = 1
            else: 
                direction = -1
            monkey.actuators.motor(direction)
        else:
            self.write(dict(data=actuator))

def main():
    settings = dict(debug=True, autoreload=True, template_path="html", static_path="static")
    app = tornado.web.Application([
        (r"/", MainHandler),
        (r"/actuator/(.*)", ActuatorHandler),
        (r"/settings", SettingsHandler),
        (r'/favicon.ico', tornado.web.StaticFileHandler),
        (r'/static/', tornado.web.StaticFileHandler),
    ], **settings)
    app.listen(7213)
    ioloop = tornado.ioloop.IOLoop().instance()
    tornado.ioloop.PeriodicCallback(monkey.interval, 25).start()
    try:
        ioloop.start()
    except KeyboardInterrupt:
        print("bailing")
        monkey.die()

if __name__ == "__main__":
    main()
