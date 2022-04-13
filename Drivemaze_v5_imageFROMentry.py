#drivemaze v5, all servos on arduino, serial comm abc
#2022Feb
#02nd
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
GPIO.setmode(GPIO.BCM)
savepath="/home/pi/Documents/Data/"
#Choose "Animal" or "Test" below
#trial_type = "Test"
trial_type = "Animal"
print(trial_type)
if trial_type == "Test":
    subjects = ["335490249236"]
if trial_type == "Animal":  
    subjects = ["94331472" ,"x", "y"] #out of study,  ""

#general variables
heavy=40 #heavy limit for weight based sensing
scale_cal=13080150.000 #use a calibration code and 20g weight to find out
nest_timeout=300000 #nest choice timeout in ms
acquisition_end_timeout=10000 #scope timeout after return to nest
scale_interval_scan=500 #scan interval in ms when sensing
weighing_time=1000 #duration of weight aqcuisition in ms
safety_delay=2000 #ms delay to confirm putative maze exit

#timestamp miniscope frames
frame_in_port=5#10 
GPIO.setup(frame_in_port, GPIO.IN)
LastFrameState=GPIO.input(frame_in_port)
frame_counter=0

#trigger miniscope
start_scope_port=9
GPIO.setup(start_scope_port, GPIO.OUT)
GPIO.output(start_scope_port,False)

#drink module
water_reset_port=12
GPIO.setup(water_reset_port, GPIO.OUT)
lick_in_port=4
lick_out_port=17
GPIO.setup(lick_in_port, GPIO.IN)
GPIO.setup(lick_out_port, GPIO.OUT)
water_duration=100 # in ms 50ms=10ul
water_flag=False
water_stop_dose_flag=False

#run module
wheel_in_port=18
GPIO.setup(wheel_in_port, GPIO.IN)
clkLastState=GPIO.input(wheel_in_port)
cycle=1200 #cycle on running wheel gives approx this many counts 1200 600b 90 copal;
run_clk_start = 0
wheel_duration=120000

#food module
FED_in=14 #input to FED3 - dispense
FED_out=15#output from FED3 - pellet retrieved
GPIO.setup(FED_out, GPIO.IN)
GPIO.setup(FED_in, GPIO.OUT)

#social module
social_duration=15000

#beams
#SEM
b0=20
b1=16
#unit1
b2=11 #was 6 no read and 8 0V clamp
b3=7 #was 21 with +1V
#unit2
b4=23
b5=24
#unit3
b6=25
b7=19 #was 5 no read
#unit4
b8=21
b9=26
#unit5
b10=10#5#8#27#22 
b11=13
beaml=(b0,b1,b2,b3,b4,b5,b6,b7,b8,b9,b10,b11)

#set up gpio
for x in range(0, 12):
    GPIO.setup(beaml[x], GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set an input pin and initial value to be pulled low (off)
for x in [1,3,5,7,8,10,11]:
    GPIO.setup(beaml[x], GPIO.IN)
# for x in [10]:
#     GPIO.setup(beaml[x], GPIO.IN, pull_up_down=GPIO.PUD_UP)    

#serial to ard mega servos
ser = serial.Serial('/dev/ttyACM0', 9600)
#init mux
print("\ninit SparkFun TCA9548A \n")
test = qwiic_tca9548a.QwiicTCA9548A()
if test.is_connected() == False:
    print("The Qwiic TCA9548A device isn't connected to the system. Please check your connection", \
        file=sys.stderr)
test.list_channels()
time.sleep(0.1)
test.enable_channels([0,7])
test.list_channels()
time.sleep(0.1)

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
# print("Put a known mass on the scale.")
# cal = float(input("Mass in kg? "))
# # Calculate the calibration factor
# print("Calculating the calibration factor...")
# scale.calculateCalibrationFactor(cal)
# print("The calibration factor is : {0:0.3f}\n".format(scale.getCalibrationFactor()))
scale.setCalibrationFactor(scale_cal) #20g 12843262.500 30g 12902791.667 20g 12993162.500

#init flags
rec_licks_flag=False
water_flag=False
social_flag=False
wheel_flag=False
rec_wheel_flag=False
food_flag=False
animal_found_flag=False
sense_SEM_flag=False

#define functions
def open_door(d):
    if d==1:
        ser.write(str.encode('a'))
    if d==2:
        ser.write(str.encode('c'))
    if d==3:
        ser.write(str.encode('e'))
    if d==4:
        ser.write(str.encode('g'))
    if d==5:   
        ser.write(str.encode('i'))
    if d==6:
        ser.write(str.encode('k'))
    if d==7:
        ser.write(str.encode('m'))
    if d==8:
        ser.write(str.encode('o'))
    if d==9:
        ser.write(str.encode('q'))
    if d==10:
        ser.write(str.encode('s'))
    if d==11:
        ser.write(str.encode('u'))
    if d==12:
        ser.write(str.encode('w'))
    if d==13:
        ser.write(str.encode('y'))
    if d==14:
        ser.write(str.encode('1'))

def close_door(d):
    if d==1:
        ser.write(str.encode('b'))
    if d==2:
        ser.write(str.encode('d'))
    if d==3:
        ser.write(str.encode('f'))
    if d==4:
        ser.write(str.encode('h'))
    if d==5:
        ser.write(str.encode('j'))
    if d==6:
        ser.write(str.encode('l'))
    if d==7:
        ser.write(str.encode('n'))
    if d==8:
        ser.write(str.encode('p'))
    if d==9:
        ser.write(str.encode('r'))
    if d==10:
        ser.write(str.encode('t'))
    if d==11:
        ser.write(str.encode('v'))
    if d==12:
        ser.write(str.encode('x'))
    if d==13:
        ser.write(str.encode('z'))
    if d==14:
        ser.write(str.encode('2'))
        
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
        #print(df_w)
        animaltag=str(animaltag)
        if not os.path.isfile(savepath + animaltag + "_weight.csv"):
            df_w.to_csv(savepath + animaltag + "_weight.csv", encoding="utf-8-sig", index=False)
            #print("File created sucessfully")
        else:
            df_w.to_csv(savepath + animaltag + "_weight.csv", mode="a+", header=False, encoding="utf-8-sig", index=False)
            #print("File appended sucessfully")
        
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
        if not os.path.isfile(savepath + animaltag + "_events.csv"):
            df_e.to_csv(savepath + animaltag + "_events.csv", encoding="utf-8-sig", index=False)
        else:
            df_e.to_csv(savepath + animaltag + "_events.csv", mode="a+", header=False, encoding="utf-8-sig", index=False)

#initialize
open_door(1)
time.sleep(3)
print("beam check")
for x in range(0, 12):    
    print(x)
    print(GPIO.input(beaml[x]))
GPIO.output(FED_in,True) # give a pellet
GPIO.output(lick_out_port,True) # give a water drop
close_door(1)
close_door(2)
close_door(4)
close_door(6)
close_door(8)
close_door(10)
close_door(12)
close_door(14)
close_door(13)
time.sleep(0.05)
open_door(3)
open_door(5)
open_door(7)
open_door(9)
open_door(11)
open_door(14)
open_door(13)
GPIO.output(lick_out_port,False)
GPIO.output(FED_in,False)
save = SaveData()
for x in range(np.size(subjects)):
    animaltag=subjects[x]
    save.append_event("", "", "initialize", animaltag)
mode=0

# frame_counter=0
# GPIO.output(start_scope_port,True) #start acquisition
#execution loop    
while True:
    #command loop changes door targets, records beams and controls rewards
    millis = int(round(time.time() * 1000))

    if mode==0: #SEM open for entry
        open_door(1)
        close_door(2)
        if not GPIO.input(beaml[0]) and GPIO.input(beaml[1]):
            mode=1
            print("m1")
            w=int(10)
            generic_timer=int(round(time.time() * 1000))
            animal_found_flag=False
            my_RFID.clear_tags()
    if mode==1: #SEM trapped for id        
        close_door(1)
        #id and wscanl
        tag=0
        if millis-generic_timer>500 and not animal_found_flag: #scan RFID every 500ms
            generic_timer=int(round(time.time() * 1000))
            tag = int(my_RFID.get_tag())

        if tag>999999999:
#             animal_found_flag=True
            print("\nfound new animal: ")
            print(tag)
#             animaltag=tag
        if tag==335490249236 or tag==328340226232 or tag==328340178184:
            animal_found_flag=True
            #print("\nfound animal: ")
            #print(tag)
            animaltag=tag
            weight_aqcuisition_timer=int(round(time.time() * 1000))
            m=[] #mass measurement points
            mode=2
            save.append_event("", "", "leave_nest", animaltag)
            #print("m2")
    if mode==2:
#         GPIO.output(start_scope_port,True) #start acquisition      
        while int(round(time.time() * 1000))-weight_aqcuisition_timer<weighing_time:
            n=scale.getWeight() * 1000
            m.append(n)
            #print("Acquired Mass is {0:0.3f} g".format(n))
        w=stats.mean(m)
        #print(w)
        if w<10:
            mode=0
            #print("m0")
        if w>heavy:
            mode=0
            #print("m0")
        if w>10 and w<heavy:
            save.append_weight(w,m,animaltag)                               
            mode=3
            #print("m3")
            w=int(10)
    if mode==3: #SEM open to maze
        open_door(2)
        mode=4
        #print("m4")        
        maze_entry_flag=False #animal must change this flag to exit maze = enter at least one pod
        pod_entry_flag=False  #flag for detecting each beam break only once
        save.append_event("", "", "block_start", animaltag)
        frame_counter=0 #reset frame counter
        GPIO.output(start_scope_port,True) #start acquisition
    if mode==4: #maze operational
        if not maze_entry_flag:
            if not GPIO.input(beaml[2]) or not GPIO.input(beaml[4]) or not GPIO.input(beaml[6]) or not GPIO.input(beaml[8]) or not GPIO.input(beaml[10]) :# or ...: #enter any unit
                maze_entry_flag=True
                #print("in maze")
        if not GPIO.input(beaml[2]) and not pod_entry_flag: #enter unit1
            pod_entry_flag=True
            #print("unit1")
            close_door(3)
            open_door(4)
            save.append_event("", "", "enter_explore", animaltag)
            unit1_timer=int(round(time.time() * 1000))
        if not GPIO.input(beaml[3]) and pod_entry_flag: #exit
            pod_entry_flag=False
            #print("ex1")
            close_door(4)
            open_door(3)
            exploration_consumed = int(round(time.time() * 1000))-unit1_timer
            save.append_event(exploration_consumed, "", "exit_explore", animaltag)
        if not GPIO.input(beaml[4]) and not pod_entry_flag: #enter unit2
            pod_entry_flag=True
            #print("unit2")
            close_door(5)
            open_door(6)
            save.append_event("", "", "enter_run", animaltag)
            unit2_timer=int(round(time.time() * 1000))
            rec_wheel_flag=True
            limit=cycle
            open_door(13) #running wheel 
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
                #print("run start")
                save.append_event("", "", "run", animaltag) 
            if counter >= limit:
                #print(counter)    
                limit=counter+cycle
        if wheel_flag and millis-wheel_timer>wheel_duration:
            close_door(13)
            wheel_flag=False
        if not GPIO.input(beaml[5]) and pod_entry_flag: #exit
            pod_entry_flag=False
            #print("ex2")
            close_door(6)
            open_door(5)
            rec_wheel_flag=False
            wheel_flag=False
            revs=counter/cycle
            save.append_event(revs, latency_to_run, "exit_run", animaltag)
        if not GPIO.input(beaml[6]) and not pod_entry_flag: #enter unit3
            pod_entry_flag=True
            #print("unit3")
            close_door(7)
            open_door(8)
            food_timer=int(round(time.time() * 1000))
            save.append_event("", "", "enter_feed", animaltag)
            food_flag=True
            GPIO.output(FED_in,False)
            pellets=0
            food_delay=[]
        if food_flag and GPIO.input(FED_out): #rec delay to feed
            save.append_event("", "", "retrieve_pellet", animaltag) 
            food_delay=int(round(time.time() * 1000))-food_timer
            #print("food delay was")
            #print(food_delay)
            food_flag=False
            pellets=1
        if not GPIO.input(beaml[7]) and pod_entry_flag: #exit
            pod_entry_flag=False
            #print("ex3")
            close_door(8)
            open_door(7)
            save.append_event(pellets, food_delay, "exit_feed", animaltag)
            GPIO.output(FED_in,True) #prep next pellet
        if not GPIO.input(beaml[9]) and not pod_entry_flag: #enter unit4            
            pod_entry_flag=True
            #print("unit4")
            close_door(9)
            open_door(10)
            open_door(14)#social
            GPIO.output(water_reset_port,True)
            save.append_event("", "", "enter_social", animaltag)
            social_timer=int(round(time.time() * 1000))
            social_flag=True
            GPIO.output(water_reset_port,False)
        if social_flag and millis-social_timer>social_duration:
            close_door(14)#social
            social_flag=False
        if not GPIO.input(beaml[8]) and pod_entry_flag: #exit
            pod_entry_flag=False
            #print("ex4")
            close_door(10)
            open_door(9)
            social_consumed=int(round(time.time() * 1000))-social_timer
            save.append_event(social_consumed, "", "exit_social", animaltag)
            social_flag=False
        if not GPIO.input(beaml[10]) and not pod_entry_flag: #enter unit5
            pod_entry_flag=True
            #print("unit5")
            close_door(11)
            open_door(12)
            save.append_event("", "", "enter_drink", animaltag)
            lick_timer=int(round(time.time() * 1000))
            rec_licks_flag=True
            water_flag=True
            water_stop_dose_flag=False
            licks=0
            drink_delay=[]
        if rec_licks_flag:
            #record licking
            if GPIO.input(lick_in_port):
                licks=licks+1
                if water_flag:
                    drink_delay=int(round(time.time() * 1000))-lick_timer
                    save.append_event("", "", "drink", animaltag) 
                    GPIO.output(lick_out_port,True) # start giving water
                    water_dose_timer=int(round(time.time() * 1000))
                    water_flag=False
                    water_stop_dose_flag=True
            if water_stop_dose_flag and millis-water_dose_timer>water_duration:
                GPIO.output(lick_out_port,False)
                water_stop_dose_flag=False
                #print("drink delay was")
                #print(drink_delay)                   
        if not GPIO.input(beaml[11]) and pod_entry_flag: #exit
            pod_entry_flag=False
            #print("ex5")
            close_door(12)
            open_door(11)
            rec_licks_flag=False
            save.append_event(licks, drink_delay, "exit_drink", animaltag)
        
        if not GPIO.input(beaml[0]) and maze_entry_flag and not sense_SEM_flag: #putative leave maze
            #print("putative return to SEM")
            scale_timer=int(round(time.time() * 1000))
            sense_SEM_flag=True
        if sense_SEM_flag and millis-scale_timer>scale_interval_scan:
            w = scale.getWeight() * 1000
            #print("Mass is {0:0.3f} g".format(w))
            scale_timer=int(round(time.time() * 1000))
            if w>15: #definite leave maze
                close_door(2)
                open_door(1)
                save.append_event("", "", "block_end", animaltag)
                mode=5
                #print("m5")
                another_entered=False
                sense_SEM_flag=False
                exit_safety_timer_flag=True
            if w<3 and GPIO.input(beaml[0]):
                sense_SEM_flag=False

    if mode==5: #wait for exit or entry of other
        if millis-scale_timer>scale_interval_scan:
            w = scale.getWeight() * 1000
            #print("Mass is {0:0.3f} g".format(w))
            scale_timer=int(round(time.time() * 1000))
        if w<3 and GPIO.input(beaml[1]):
            #print("putative exit")
            if exit_safety_timer_flag:
                exit_safety_timer=int(round(time.time() * 1000))
                exit_safety_timer_flag=False
            w = scale.getWeight() * 1000
            if not exit_safety_timer_flag and w<3 and GPIO.input(beaml[1]) and millis-exit_safety_timer>safety_delay:
                close_door(1)
                nest_timer=int(round(time.time() * 1000))
                acquisition_end_timer=int(round(time.time() * 1000))
                mode=6
                #print("m6")
        if w>heavy:
            another_entered=True
            #print("sub")
        if another_entered and w<heavy and w>10 and GPIO.input(beaml[1]):
            mode=1
            #print("m1 sub")
            w=int(10)
            generic_timer=int(round(time.time() * 1000))
            animal_found_flag=False
    if mode==6: #wait for nest choice time out
        if millis-acquisition_end_timer>acquisition_end_timeout:
            GPIO.output(start_scope_port,False) #stop acquisition
        if millis-nest_timer>nest_timeout:
            for x in range(np.size(subjects)):
                animaltag=subjects[x]
                save.append_event("", "", "block_available", animaltag)
            mode=0
            #print("m0")
     
    #Frame rec loop records miniscope frame timestamps in behaviour time
    if GPIO.input(frame_in_port) != LastFrameState: #rising or falling edge
        frame_counter=frame_counter+1
        save.append_event("", frame_counter, "frame", animaltag)
#         print("frame")
#         print(frame_counter)
    LastFrameState=GPIO.input(frame_in_port)
    
    #troubleshoot loop time
#     print(millis)
