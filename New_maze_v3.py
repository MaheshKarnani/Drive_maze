#new maze all on pi. tested success. rare i2c remote io error 121 due to servo kit
#2021Dec
#1st
from __future__ import print_function
import serial
# import keyboard
import time
import RPi.GPIO as GPIO
import os
import pandas as pd
import statistics as stats
import sys
from datetime import datetime
import numpy as np
import qwiic_tca9548a
import qwiic_rfid
import PyNAU7802
import smbus2
from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)

#Choose "Animal" or "Test" below
trial_type = "Animal"
#trial_type = "Test"
print(trial_type)
if trial_type == "Test":
    subjects = ["Stick_X"]
if trial_type == "Animal":  
    subjects = ["335490249236" ,"x", "y"] #out of study,  ""

#general variables
nest_timeout=10000 #nest choice timeout in ms
scale_interval_scan=500 #scan interval in ms when sensing
weighing_time=1000 #duration of weight aqcuisition in ms

#drink module
lick_in_port=4
lick_out_port=17
GPIO.setup(lick_in_port, GPIO.IN)
GPIO.setup(lick_out_port, GPIO.OUT)
water_duration=0.1 # in s 0.05s=10ul

#run module
wheel_in_port=18
GPIO.setup(wheel_in_port, GPIO.IN)
clkLastState=GPIO.input(wheel_in_port)
cycle=1200 #cycle on running wheel gives approx this many counts 1200 600b 90 copal;
run_clk_start = 0
wheel_break=13
wheel_close_angle=10
wheel_open_angle=40
wheel_duration=120000

#social module
social_hatch=12
social_close_angle=128
social_open_angle=50
social_duration=15000

#food module
FED_in=14 #input to FED3 - dispense
FED_out=15#output from FED3 - pellet retrieved
GPIO.setup(FED_out, GPIO.IN)
GPIO.setup(FED_in, GPIO.OUT)

#beams
#SEM
b0=20
b1=16
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
d2=6
d3=7
d4=4
d5=5
d6=2
d7=3
d8=0
d9=1
d10=8
d11=9
doorl=[d0,d1,d2,d3,d4,d5,d6,d7,d8,d9,d10,d11,social_hatch]
print(doorl)
entry_doors=[d0,d2,d4,d6,d8,d10]
print(entry_doors)
exit_doors=[d1,d3,d5,d7,d9,d11]
print(exit_doors)

#set up gpio
for x in range(0, 12):
    GPIO.setup(beaml[x], GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set an input pin and initial value to be pulled low (off)
for x in [1,3,5,7]:
    GPIO.setup(beaml[x], GPIO.IN)
slowness=4 #milliseconds to wait between alternating door servo strokes

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
target10 = 178
target11 = 170
openl=[target0,target1,target2,target3,target4,target5,target6,target7,target8,target9,target10,target11,social_open_angle]

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
closel=[target0,target1,target2,target3,target4,target5,target6,target7,target8,target9,target10,target11,social_close_angle]

#initialize current and target degrees for doors
current=[96,96,96,96,96,96,96,84,96,96,96,96,96]
target=[90,90,90,90,90,90,90,90,90,90,90,90,90]

d_turn=1
d_stroke=[1,1,1,1,1,1,1,1,1,1,1,1,1]
d=11

millis = int(round(time.time() * 1000))
door_timer=millis
mode=-6

#init mux
print("\ninit SparkFun TCA9548A \n")
test = qwiic_tca9548a.QwiicTCA9548A()
if test.is_connected() == False:
    print("The Qwiic TCA9548A device isn't connected to the system. Please check your connection", \
        file=sys.stderr)
test.list_channels()
time.sleep(0.5)
test.enable_channels([0,7])
test.list_channels()
time.sleep(0.5)

#init RFID
print("\ninit RFID")
my_RFID = qwiic_rfid.QwiicRFID(0x7C)
if my_RFID.begin() == False:
    print("\nThe Qwiic RFID Reader isn't connected to the system. Please check your connection", file=sys.stderr)
else:
    print("\nRFID reader connected!")

#init scale
# Create the bus
bus = smbus2.SMBus(1)
# Create the scale and initialize it.. hardware defined address is 0x2A. mux required for multiple
scale = PyNAU7802.NAU7802()
if scale.begin(bus):
    print("Scale connected!\n")
else:
    print("Can't find the scale, exiting ...\n")
    exit()
# Calculate the zero offset
print("Calculating scale zero offset...")
scale.calculateZeroOffset()
print("The zero offset is : {0}\n".format(scale.getZeroOffset()))
print("Put a known mass on the scale.")
cal = float(input("Mass in kg? "))
# Calculate the calibration factor
print("Calculating the calibration factor...")
scale.calculateCalibrationFactor(cal)
print("The calibration factor is : {0:0.3f}\n".format(scale.getCalibrationFactor()))

#init flags
rec_licks_flag=False
water_flag=False
social_flag=False
wheel_flag=False
rec_wheel_flag=False
food_flag=False
animal_found_flag=False

#define functions
class SaveData:
    def append_weight(self,m,w,animaltag):

        weight_list = {
        "m": [],
        "w": [],
        "Date_Time": []
        }
        weight_list.update({'m': [m]})
        weight_list.update({'w': [w]})
        weight_list.update({'Date_Time': [datetime.now()]})
        
        df_w = pd.DataFrame(weight_list)
        print(df_w)
        animaltag=str(animaltag)
        if not os.path.isfile(animaltag + "_weight.csv"):
            df_w.to_csv(animaltag + "_weight.csv", encoding="utf-8-sig", index=False)
            print("File created sucessfully")
        else:
            df_w.to_csv(animaltag + "_weight.csv", mode="a+", header=False, encoding="utf-8-sig", index=False)
            print("File appended sucessfully")
        
    def append_event(self,amount_consumed,latency_to_consumption,event_type,animaltag):
        """
        Function used to save event parameters to a .csv file
        example use save.append_event("", "", "initialize", animaltag)
        """
        global event_list

        event_list = {
            "Date_Time": [],
            "amount_consumed": [],
            "latency_to_consumption": [],
            "Type" : [],   
        }
        amount_consumed=str(amount_consumed)
        latency_to_consumption=str(latency_to_consumption)
        
        event_list.update({'amount_consumed': [amount_consumed]})
        event_list.update({'latency_to_consumption': [latency_to_consumption]})
        event_list.update({'Type': [event_type]})
        event_list.update({'Date_Time': [datetime.now()]})

        df_e = pd.DataFrame(event_list)
        animaltag=str(animaltag)
        if not os.path.isfile(animaltag + "_events.csv"):
            df_e.to_csv(animaltag + "_events.csv", encoding="utf-8-sig", index=False)
        else:
            df_e.to_csv(animaltag + "_events.csv", mode="a+", header=False, encoding="utf-8-sig", index=False)

#execution loop
while True:
    #command loop changes door targets
    if mode==-6: #safe startup
        slowness=500
        d_state=np.subtract(target,current)
        if max(abs(d_state))<3:           
            slowness=4
            mode=-1            
            kit.servo[wheel_break].angle = wheel_close_angle
            GPIO.output(FED_in,True) # give a pellet
            GPIO.output(lick_out_port,True) # give a water drop
            time.sleep(water_duration)
            GPIO.output(lick_out_port,False)
            GPIO.output(FED_in,False)
            kit.servo[wheel_break].angle = wheel_open_angle
            print("initialized")
            save = SaveData()
            for x in range(np.size(subjects)):
                animaltag=subjects[x]
                save.append_event("", "", "initialize", animaltag)
    if mode==-1: #prep        
        target[doorl[2]] = closel[doorl[2]]
        target[doorl[3]] = openl[doorl[3]]
        d_state=np.subtract(target,current)
        if max(abs(d_state))<3:
            print("u1 ready")
            mode=-2
    if mode==-2: #prep       
        target[doorl[4]] = closel[doorl[4]]
        target[doorl[5]] = openl[doorl[5]]
        d_state=np.subtract(target,current)
        if max(abs(d_state))<3:
            print("u2 ready")
            mode=-3
    if mode==-3: #prep       
        target[doorl[6]] = closel[doorl[6]]
        target[doorl[7]] = openl[doorl[7]]
        d_state=np.subtract(target,current)
        if max(abs(d_state))<3:
            print("u3 ready")
            mode=-4
    if mode==-4: #prep       
        target[doorl[8]] = closel[doorl[8]]
        target[doorl[9]] = openl[doorl[9]]
        d_state=np.subtract(target,current)
        if max(abs(d_state))<3:
            print("u4 ready")
            mode=-5
    if mode==-5: #prep       
        target[doorl[10]] = closel[doorl[10]]
        target[doorl[11]] = openl[doorl[11]]
        d_state=np.subtract(target,current)
        if max(abs(d_state))<3:
            print("u5 ready")
            mode=0
            print("m0")
    if mode==0: #SEM open for entry        
        target[doorl[0]] = openl[doorl[0]]
        target[doorl[1]] = closel[doorl[1]]
        if not GPIO.input(beaml[0]) and GPIO.input(beaml[1]):
            mode=1
            print("m1")
            w=int(10)
            generic_timer=int(round(time.time() * 1000))
            animal_found_flag=False
    if mode==1: #SEM trapped for id        
        target[doorl[0]] = closel[doorl[0]]
        target[doorl[1]] = closel[doorl[1]]
        #id and wscan
        millis = int(round(time.time() * 1000))
        tag=0
        if millis-generic_timer>500 and not animal_found_flag: #scan RFID every 500ms
            generic_timer=int(round(time.time() * 1000))
            tag = int(my_RFID.get_tag())
        if tag==335490249236:
            animal_found_flag=True
            print("\nfound animal: ")
            print(tag)
            animaltag=tag
            weight_aqcuisition_timer=int(round(time.time() * 1000))
            m=[] #mass measurement points
            d_state=np.subtract(target,current) #check where doors are
            if max(abs(d_state))<3: #if doors at target, move on
                mode=2
                print("m2")
    if mode==2:
        while int(round(time.time() * 1000))-weight_aqcuisition_timer<weighing_time:
            n=scale.getWeight() * 1000
            m.append(n)
            print("Acquired Mass is {0:0.3f} g".format(n))
        w=stats.mean(m)
        print(w)
        if w<10:
            mode=0
            print("m0")
        if w>40:
            mode=0
            print("m0")
        if w>10 and w<40:
            save.append_weight(w,m,animaltag)                               
            mode=3
            print("m3")
            w=int(10)
    if mode==3: #SEM open to maze
        target[doorl[1]] = openl[doorl[1]]
        mode=4
        print("m4")        
        maze_entry_flag=False #animal must change this flag to exit maze = enter at least one pod
        pod_entry_flag=False  #flag for detecting each beam break only once
        save.append_event("", "", "block_start", animaltag)
    if mode==4: #maze operational
        millis = int(round(time.time() * 1000)) #for access timers
        if not maze_entry_flag:
            if not GPIO.input(beaml[2]) or not GPIO.input(beaml[4]) or not GPIO.input(beaml[6]) or not GPIO.input(beaml[8]) or not GPIO.input(beaml[10]) :# or ...: #enter any unit
                maze_entry_flag=True
                print("in maze")
        if not GPIO.input(beaml[2]) and not pod_entry_flag: #enter unit1
            pod_entry_flag=True
            print("unit1")
            target[doorl[3]] = closel[doorl[3]]
            target[doorl[2]] = openl[doorl[2]]
            save.append_event("", "", "enter_explore", animaltag)
            unit1_timer=int(round(time.time() * 1000))
        if not GPIO.input(beaml[3]) and pod_entry_flag: #exit
            pod_entry_flag=False
            print("ex1")
            target[doorl[3]] = openl[doorl[3]]
            target[doorl[2]] = closel[doorl[2]]
            exploration_consumed = int(round(time.time() * 1000))-unit1_timer
            save.append_event(exploration_consumed, "", "exit_explore", animaltag)
        if not GPIO.input(beaml[4]) and not pod_entry_flag: #enter unit2
            pod_entry_flag=True
            print("unit2")
            target[doorl[5]] = closel[doorl[5]]
            target[doorl[4]] = openl[doorl[4]]
            save.append_event("", "", "enter_run", animaltag)
            unit2_timer=int(round(time.time() * 1000))
            rec_wheel_flag=True
            limit=cycle
            kit.servo[wheel_break].angle = wheel_open_angle
            wheel_timer=int(round(time.time() * 1000))
            wheel_flag=True
            save_flag=True
            latency_to_run=[]  
            counter=0
        if rec_wheel_flag:
            #record running wheel 
            clkState=GPIO.input(wheel_in_port)
            if clkState != clkLastState:
                counter += 1  
                clkLastState = clkState
            if save_flag and counter>limit/4: #detect latency to run start at first quarter revolution
                latency_to_run = int(round(time.time() * 1000))-unit2_timer
                save_flag=False
                print("run start")
                save.append_event("", "", "run", animaltag) 
            if counter >= limit:
                print(counter)    
                limit=counter+cycle
        #millis called above
        if wheel_flag and millis-wheel_timer>wheel_duration:
            kit.servo[wheel_break].angle = wheel_close_angle
            wheel_flag=False
        if not GPIO.input(beaml[5]) and pod_entry_flag: #exit
            pod_entry_flag=False
            print("ex2")
            target[doorl[5]] = openl[doorl[5]]
            target[doorl[4]] = closel[doorl[4]]
            rec_wheel_flag=False
            wheel_flag=False
            revs=counter/cycle
            save.append_event(revs, latency_to_run, "exit_run", animaltag)
        if not GPIO.input(beaml[6]) and not pod_entry_flag: #enter unit3
            pod_entry_flag=True
            print("unit3")
            target[doorl[7]] = closel[doorl[7]]
            target[doorl[6]] = openl[doorl[6]]
            food_timer=int(round(time.time() * 1000))
            save.append_event("", "", "enter_feed", animaltag)
            food_flag=True
            GPIO.output(FED_in,False)
            pellets=0
        if food_flag and GPIO.input(FED_out): #rec delay to feed
            save.append_event("", "", "retrieve_pellet", animaltag) 
            food_delay=int(round(time.time() * 1000))-food_timer
            print("food delay was")
            print(food_delay)
            food_flag=False
            pellets=1
        if not GPIO.input(beaml[7]) and pod_entry_flag: #exit
            pod_entry_flag=False
            print("ex3")
            target[doorl[7]] = openl[doorl[7]]
            target[doorl[6]] = closel[doorl[6]]
            save.append_event(pellets, food_delay, "exit_feed", animaltag)
            GPIO.output(FED_in,True) #prep next pellet
        if not GPIO.input(beaml[9]) and not pod_entry_flag: #enter unit4            
            pod_entry_flag=True
            print("unit4")
            target[doorl[9]] = closel[doorl[9]]
            target[doorl[8]] = openl[doorl[8]]
            target[doorl[12]] = openl[doorl[12]]#social
            save.append_event("", "", "enter_social", animaltag)
            social_timer=int(round(time.time() * 1000))
            social_flag=True
        #millis called above
        if social_flag and millis-social_timer>social_duration:
            target[doorl[12]] = closel[doorl[12]]
            social_flag=False
        if not GPIO.input(beaml[8]) and pod_entry_flag: #exit
            pod_entry_flag=False
            print("ex4")
            target[doorl[9]] = openl[doorl[9]]
            target[doorl[8]] = closel[doorl[8]]
            social_consumed=int(round(time.time() * 1000))-social_timer
            save.append_event(social_consumed, "", "exit_social", animaltag)
            social_flag=False
        if not GPIO.input(beaml[10]) and not pod_entry_flag: #enter unit5
            pod_entry_flag=True
            print("unit5")
            target[doorl[11]] = closel[doorl[11]]
            target[doorl[10]] = openl[doorl[10]]
            save.append_event("", "", "enter_drink", animaltag)
            lick_timer=int(round(time.time() * 1000))
            rec_licks_flag=True
            water_flag=True
            licks=0
        if rec_licks_flag:
            #record licking
            if GPIO.input(lick_in_port):
                licks=licks+1
                if water_flag:
                    drink_delay=int(round(time.time() * 1000))-lick_timer
                    save.append_event("", "", "drink", animaltag) 
                    GPIO.output(lick_out_port,True) # give a water drop
                    time.sleep(water_duration)
                    GPIO.output(lick_out_port,False)
                    print("drink delay was")
                    print(drink_delay)
                    water_flag=False
        if not GPIO.input(beaml[11]) and pod_entry_flag: #exit
            pod_entry_flag=False
            print("ex5")
            target[doorl[11]] = openl[doorl[11]]
            target[doorl[10]] = closel[doorl[10]]
            rec_licks_flag=False
            save.append_event(licks, drink_delay, "exit_drink", animaltag)
        
        if not GPIO.input(beaml[0]) and maze_entry_flag: #leave maze
            target[doorl[0]] = openl[doorl[0]]
            target[doorl[1]] = closel[doorl[1]]
            save.append_event("", "", "block_end", animaltag) 
            scale_timer=int(round(time.time() * 1000))
            mode=5
            print("m5")
    if mode==5: #wait for exit
        millis = int(round(time.time() * 1000))
        if millis-scale_timer>scale_interval_scan:
            w = scale.getWeight() * 1000
            print("Mass is {0:0.3f} g".format(w))
            scale_timer=int(round(time.time() * 1000))
        if w<10 and GPIO.input(beaml[1]):
            target[doorl[0]] = closel[doorl[0]]
            target[doorl[1]] = closel[doorl[1]]
            nest_timer=int(round(time.time() * 1000))
            mode=6
            print("m6")
    if mode==6: #wait for nest choice time out
        millis = int(round(time.time() * 1000))
        if millis-nest_timer>nest_timeout:
            for x in range(np.size(subjects)):
                animaltag=subjects[x]
                save.append_event("", "", "block_available", animaltag)
            mode=0
            print("m0")

    #motor loop moves two doors at a time
    #set up a door loop. if not at target, move to target. two at a time.
    d_state=np.subtract(target,current)
    if max(abs(d_state))>2:                 #if doors are not at target
        millis = int(round(time.time() * 1000))
        if millis-door_timer>slowness:      #if movement is slow enough  
            d=d+1      #cycle through doors
            if d==13:  #
                d=0    #
            if abs(d_state[d])>2: #if this door not at target
                if d_stroke[d]==1:         #if it's this stroke direction's turn
                    current[d] = current[d]+4*(target[d]-current[d])/abs(target[d]-current[d])
                    d_stroke[d]=2                    
                else:                   #or the other stroke direction
                    current[d] = current[d]-2*(target[d]-current[d])/abs(target[d]-current[d])
                    d_stroke[d]=1
                kit.servo[d].angle = current[d]             #movement                    
                door_timer=millis



