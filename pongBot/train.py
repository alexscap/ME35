#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks import ev3brick as brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

# Write your program here
ev3 = EV3Brick()
ev3.speaker.beep()

#setup ports
distSen = UltrasonicSensor(Port.S1)
chuck = Motor(Port.A)
yoss = Motor(Port.B)

#initial speed
speed = 100

#file to write to
f = open('training_bounce.txt', 'a')

#throwing function
def yeet(speed):
    chuck.run(speed)
    yoss.run(speed)
    wait(3000)
    chuck.stop()
    yoss.stop()


while True:
    #run next trial when center button pressed
    if Button.CENTER in brick.buttons():
        speed += 50
        dist = distSen.distance()
        yeet(speed)

    #when right button pressed, record last trial
    elif Button.RIGHT in brick.buttons():
        f.write('\n' + str(dist) + ', ' + str(speed))
        wait(1000)
        
    #exit code when left button pushed
    elif Button.LEFT in brick.buttons():
        break
