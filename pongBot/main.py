#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks import ev3brick as brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
import math

import ubinascii, ujson, urequests, utime

# Write your program here
ev3 = EV3Brick()
ev3.speaker.beep()

#set up ports
distSen = UltrasonicSensor(Port.S1)
chuck = Motor(Port.A)
yoss = Motor(Port.B)

top_cup = 115 #height of top of cup
start_pos = 200 #height of start
sens_pos = 70 #x position of sensor
theta = 45 #launch angle (degrees)

g = 9807 #mm/s^2
C = .42 #constant multiplier for speed to fit physical model

#coefficients for AI model
A_ai = 1.4416
B_ai = 124.88

#coefficients for AI bounce model
A_bounce = .9731
B_bounce = 25.31

Key = 'W1McA79Y5bhBiXBz2sebRV_fWZS84BmxcfTl1ks8rR'

#systemlink functions

def SL_setup():
     urlBase = "https://api.systemlinkcloud.com/nitag/v2/tags/"
     headers = {"Accept":"application/json","x-ni-api-key":Key}
     return urlBase, headers
     
def Put_SL(Tag, Type, Value):
     urlBase, headers = SL_setup()
     urlValue = urlBase + Tag + "/values/current"
     propValue = {"value":{"type":Type,"value":Value}}
     try:
          reply = urequests.put(urlValue,headers=headers,json=propValue).text
     except Exception as e:
          print(e)         
          reply = 'failed'
     return reply

def Get_SL(Tag):
     urlBase, headers = SL_setup()
     urlValue = urlBase + Tag + "/values/current"
     try:
          value = urequests.get(urlValue,headers=headers).text
          data = ujson.loads(value)
          #print(data)
          result = data.get("value").get("value")
     except Exception as e:
          print(e)
          result = 'failed'
     return result
     
def Create_SL(Tag, Type):
     urlBase, headers = SL_setup()
     urlTag = urlBase + Tag
     propName={"type":Type,"path":Tag}
     try:
          urequests.put(urlTag,headers=headers,json=propName).text
     except Exception as e:
          print(e)

#use the AI algorithm to choose a speed
def AI_speed(dist): 
    speed = A_ai * dist + B_ai
    return speed

#AI algorithm for bouncing the ball into the cup
def bounce_AI(dist):
    speed = A_bounce * dist + B_bounce
    return speed

#use a physics model to choose a speed
def phys_speed(dist,C): 
     #v = Rx / (sqrt(2/g) * cos(theta) * sqrt(Ry - Rx*tan(theta) - Roy))
     speed = dist / (math.sqrt(2/g) * math.cos(math.radians(theta)) * math.sqrt(abs(top_cup - dist * math.tan(math.radians(theta)) - start_pos)))

     #below 120 the ultrasonic sensor thinks it's closer than it is
     #increase C to compensate
     if dist < 120:
          C = .465

     speed = C * speed

     #below 30 the ultrasonic sensor data is essentially useless - set speed for dunk
     if dist < 30:
          speed = 200

     print('speed: ' + str(speed))
     return speed

#function for throwing the ball at a given speed
def yeet(speed):
    chuck.run(speed)
    yoss.run(speed)
    wait(3000)
    chuck.stop()
    yoss.stop()


while True:
    #if fire is pressed on the dashboard
    if Get_SL('Fire') == '1':
        mode = Get_SL('pong_mode')

        #use AI model
        if mode == '1':
            print('ai')
            dist = distSen.distance()
            print('distance: ' + str(dist))
            speed = AI_speed(dist)
            yeet(speed)

        #use physics model
        elif mode == '0':
            print('physics')
            dist = distSen.distance() - sens_pos
            print('distance: ' + str(dist))
            speed = phys_speed(dist, C)
            yeet(speed)

        #use bouncing model
        elif mode == '2':
            print('bounce')
            dist = distSen.distance()
            print('distance: ' + str(dist))
            speed = bounce_AI(dist)
            yeet(speed)

        #reset the fire tag
        Put_SL('Fire', 'INT', '0')