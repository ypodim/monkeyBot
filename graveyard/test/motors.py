#!/usr/bin/python3
import sys
import RPi.GPIO as gpio
import time

# blue  pwmb 5
# green   bin2 6
# yellow  bin1 12
# orange  ain1 13
# red   ain2 19
# brown pwma 16

ain1Pin = 13
ain2Pin = 19
pwmAPin = 16
bin1Pin = 12
bin2Pin = 6
pwmBPin = 5

gpio.setmode(gpio.BCM)
gpio.setup(pwmAPin, gpio.OUT)
gpio.setup(ain1Pin, gpio.OUT)
gpio.setup(ain2Pin, gpio.OUT)
gpio.setup(pwmBPin, gpio.OUT)
gpio.setup(bin1Pin, gpio.OUT)
gpio.setup(bin2Pin, gpio.OUT)

pwmA = gpio.PWM(pwmAPin, 50)
pwmB = gpio.PWM(pwmBPin, 100)

pwmA.start(0) # Motors
pwmB.start(0) # Light

gpio.output(bin1Pin, gpio.HIGH)
gpio.output(bin2Pin, gpio.LOW)

gpio.output(ain1Pin, gpio.LOW)
gpio.output(ain2Pin, gpio.HIGH)

# top = int(sys.argv[1])
pwmA.ChangeDutyCycle(10)
time.sleep(0.2)

pwmA.stop()
pwmB.stop()
gpio.cleanup()
