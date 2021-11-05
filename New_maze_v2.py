#new maze all on pi.
#2021Oct
#30th
import serial
import time
import RPi.GPIO as GPIO
import os
import pandas as pd
import statistics as stats
import sys
from datetime import datetime
import numpy as np
from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)

#beams
#SEM
b0=20
b1=19
#unit1
b2=6
b3=12
#unit2
b4=23
b5=24
#unit3
b6=25
b7=5
#unit4
b8=21
b9=26
#unit5
b10=22
b11=13
beaml=(b0,b1,b2,b3,b4,b5,b6,b7,b8,b9,b10,b11)

#doors
d0=10
d1=11
d2=0
d3=1
d4=2
d5=3
d6=4
d7=5
d8=6
d9=7
d10=8
d11=9
doorl=(d0,d1,d2,d3,d4,d5,d6,d7,d8,d9,d10,d11)
entry_doors=(d0,d2,d4,d6,d8,d10)
exit_doors=(d1,d3,d5,d7,d9,d11)

#set up gpio
for x in range(0, 12):
    GPIO.setup(beaml[x], GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set an input pin and initial value to be pulled low (off)

slowness=4 #milliseconds to wait between 1deg servo movement

current0=90
current1=90
#open list
target0 = 40
target1 = 68
target2 = 15
target3 = 170
target4 = 40
target5 = 40
target6 = 40
target7 = 165
target8 = 20
target9 = 57
target10 = 175
target11 = 170
openl=(target0,target1,target2,target3,target4,target5,target6,target7,target8,target9,target10,target11)

#CLOSE list
target0 = 127
target1 = 163
target2 = 125
target3 = 70
target4 = 145
target5 = 150
target6 = 155
target7 = 60
target8 = 145
target9 = 145
target10 = 80
target11 = 60
closel=(target0,target1,target2,target3,target4,target5,target6,target7,target8,target9,target10,target11)

#initialize current and target degrees for doors
current=(90,90,90,90,90,90,90,90,90,90,90,90)
target=(90,90,90,90,90,90,90,90,90,90,90,90)
i=1
j=1

millis = int(round(time.time() * 1000))
timer0=millis+2
timer1=millis
mode=0

while True:
    if mode==0: #SEM open for entry
        target[doorl[0]] = openl[doorl[0]]
        if not GPIO.input(beaml[1]):
            mode=1
    if mode==1: #SEM trapped for id
        target[doorl[0]] = closel[doorl[0]]
        target[doorl[1]] = closel[doorl[1]]
        #id and scan
        if w<10:
            mode=0
        if w>40:
            mode=0
        if w>10 and w<40:
            mode=2
    if mode==2: #SEM open to maze
        target[doorl[1]] = openl[doorl[1]]
        mode=3
        
    if mode==3: #maze operational
        print("in maze")
        
        
        
    
    
    
    
    
    
    
    
    #########################################################################3
    millis = int(round(time.time() * 1000))
    
    for x in entry_doors:
        if not GPIO.input(beaml[x]):
            #print("26low CLOSE")
            target[doorl[x]] = openl[doorl[x]]
            target[doorl[x+1]] = closel[doorl[x+1]]
            
    for y in exit_doors:
        if not GPIO.input(beaml[y]):
            #print("21low open")
            target[doorl[y]] = closel[doorl[y]]
            target[doorl[y-1]] = openl[doorl[y-1]]
    
    #print(millis-timer0)

#3deg precision servo target movements
        
    if i==1:        
        if abs(target0-current0)>2 and millis-timer0>slowness:
            current0 = current0+3*(target0-current0)/abs(target0-current0)
            kit.servo[a].angle = current0
            i=2
            timer0=millis
    else:
        if millis-timer0>slowness:
            if target0-current0 != 0:
                current0 = current0-2*(target0-current0)/abs(target0-current0)
                kit.servo[a].angle = current0
            i=1
            timer0=millis

    if j==1:
        if abs(target1-current1)>2 and millis-timer1>slowness: 
            current1 = current1+3*(target1-current1)/abs(target1-current1)
            kit.servo[b].angle = current1
            j=2
            timer1=millis
    else:
        if millis-timer1>slowness:
            if target1-current1 != 0:
                current1 = current1-2*(target1-current1)/abs(target1-current1)
                kit.servo[b].angle = current1
            j=1
            timer1=millis

        
