#new maze all on pi.
#2021Nov
#5th
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

nest_timeout=10000 #nest choice timeout in ms

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

slowness=2 #milliseconds to wait between alternating doorset servo strokes

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
current=[90,90,90,90,90,90,90,90,90,90,90,90]
target=[90,90,90,90,90,90,90,90,90,90,90,90]
d_turn=1
d_stroke=1

millis = int(round(time.time() * 1000))
door_timer=millis
mode=0

while True:
    #command loop changes targets
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
        leave_flag='False'  
    if mode==3: #maze operational
        print("in maze")
        if not leave_flag and not GPIO.input(beaml[2]) or ...: #enter any unit
            leave_flag='True'

        if not GPIO.input(beaml[2]): #enter unit1
            target[doorl[2]] = closel[doorl[2]]
            target[doorl[3]] = openl[doorl[3]]
        if not GPIO.input(beaml[3]): #exit
            target[doorl[2]] = openl[doorl[2]]
            target[doorl[3]] = closel[doorl[3]]        
        if not GPIO.input(beaml[4]): #enter unit2
            target[doorl[4]] = closel[doorl[4]]
            target[doorl[5]] = openl[doorl[5]]
        if not GPIO.input(beaml[5]): #exit
            target[doorl[4]] = openl[doorl[4]]
            target[doorl[5]] = closel[doorl[5]]   
        if not GPIO.input(beaml[6]): #enter unit3
            target[doorl[6]] = closel[doorl[6]]
            target[doorl[7]] = openl[doorl[7]]
        if not GPIO.input(beaml[7]): #exit
            target[doorl[6]] = openl[doorl[6]]
            target[doorl[7]] = closel[doorl[7]]   
        if not GPIO.input(beaml[8]): #enter unit4
            target[doorl[8]] = closel[doorl[8]]
            target[doorl[9]] = openl[doorl[9]]
        if not GPIO.input(beaml[9]): #exit
            target[doorl[8]] = openl[doorl[8]]
            target[doorl[9]] = closel[doorl[9]]   
        if not GPIO.input(beaml[10]): #enter unit5
            target[doorl[10]] = closel[doorl[10]]
            target[doorl[11]] = openl[doorl[11]]
        if not GPIO.input(beaml[11]): #exit
            target[doorl[10]] = openl[doorl[10]]
            target[doorl[11]] = closel[doorl[11]]   
        
        if not GPIO.input(beaml[1]) and leave_flag: #leave maze
            target[doorl[0]] = openl[doorl[0]]
            target[doorl[1]] = closel[doorl[1]]
            mode=4
    if mode==4: #wait for exit
        if w<10 and GPIO.input(beaml[0]):
             target[doorl[0]] = closel[doorl[0]]
             target[doorl[1]] = closel[doorl[1]]
             nest_timer=int(round(time.time() * 1000))
             mode=5
    if mode==5: #wait for nest choice time out
        millis = int(round(time.time() * 1000))
        if millis-door_timer>nest_timeout:
            mode==0

    #motor loop moves two doors at a time
    #set up a door loop. if not at target, move to target. two at a time.
    d_state=np.subtract(target,current)
    print(abs(d_state))
    if max(abs(d_state))>2:                 #if doors are not at target
        millis = int(round(time.time() * 1000))
        if millis-door_timer>slowness:      #if movement is slow enough
            if d_turn==1:                   #if it's this doorset's turn
                doorset=entry_doors
                d_turn=2
            else:                           #or the other doorset
                doorset=exit_doors
                d_turn=1
            for x in doorset:               #find door out of target
                if abs(d_state[x])>2:       #
                    if d_stroke==1:         #if it's this stroke direction's turn
                        current[x] = current[x]+3*(target[x]-current[x])/abs(target[x]-current[x])
                        d_stroke=2
                    else:                   #or the other stroke direction
                        current[x] = current[x]-2*(target[x]-current[x])/abs(target[x]-current[x])
                        d_stroke=1
                    kit.servo[a].angle = current[x]             #movement
                    d_state=np.subtract(target,current)
                    d_turn=2
                    door_timer=millis
