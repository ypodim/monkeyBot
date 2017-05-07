import threading
import time
import random
import Adafruit_DHT
# import Adafruit_DHT; Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 4)

class Thermometer(threading.Thread):
    def __init__(self, pin):
        super(Thermometer, self).__init__()
        self.temperature = 0
        self.humidity = 0
        self.running = True
        self.pin = pin
        
    def run(self):
        while self.running:
            self.humidity, self.celsious = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, self.pin)
            if not self.humidity is not None and self.temperature is not None:
                print('Failed to get reading. Try again!')
            else:
                self.temperature = (self.celsious * 9.0 / 5) + 32
                # print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(self.temperature, self.humidity))
                
            time.sleep(10)
        print("Thermometer terminated")

    def getValues(self):
        return dict(temperature=self.temperature, humidity=self.humidity)

    def die(self):
        self.running = False