#!/usr/bin/python

import RPi.GPIO as GPIO
from time import sleep
import serial
import re

def checksum(sentence):
    calc_cksum = 0
    for s in sentence:
        calc_cksum ^= ord(s)
    return '*'+hex(calc_cksum)[-2:].upper()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP) #SWITCH
GPIO.setup(4, GPIO.OUT) #LED

pushed = False
serialinit = False

ser = serial.Serial("/dev/ttyUSB0", 4800)

while True:
    if GPIO.input(18) == False and not pushed:
        pushed = True
    if GPIO.input(18) == True and pushed:
        pushed = False
    try:
        line = ser.readline()
        line = line.decode("ISO-8859-1")
        if pushed:
            if re.match("^\$..HDT", line):
                s = line.split(",")
                heading = float(s[1])
                heading = (heading + 180) % 360
                s[1] = "%.2f" % heading
                s[2] = "T"
                chk = checksum(','.join(s)[1:])
                ser.write(bytes(','.join(s)+chk+"\r\n", "UTF-8"))
            else:
                ser.write(bytes(line, "UTF-8"))
        else:
            ser.write(bytes(line, "UTF-8"))
    except:
        pass
        sleep(.2)

    if pushed:
        GPIO.output(4, 1)
    else:
        GPIO.output(4, 0)

