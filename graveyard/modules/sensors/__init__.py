from ImageProcessor import ImageProcessor
from Thermometer import Thermometer
from ADC import ADC

class Sensors(object):
    """docstring for Sensors"""
    def __init__(self):
        super(Sensors, self).__init__()
        
        thermoPin = 4

        self.ip = ImageProcessor()
        self.ip.start()
        self.adc = ADC()
        self.adc.start()
        # self.thermometer = Thermometer(thermoPin)
        # self.thermometer.start()
        print("sensors initialized")

    def die(self):
        self.ip.die()
        self.adc.die()
        # self.thermometer.die()

    def getValues(self):
        return dict(adc=self.adc.values, thermo=self.thermometer.getValues())

    def registerCameraEvent(self, event, callback):
        self.ip.register(event, callback)