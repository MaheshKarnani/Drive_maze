#drivemaze v11, pigpio, new layout, run beams_startup and sudo pigpiod before
#with email alarm
#2023 Feb
#15th
from __future__ import print_function
import serial
# import keyboard
import time
import pigpio
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
import yagmail
experiment = "baseline"#"FEDoff"#"baseline"#"FED removed"
FEDonFLAG = True #change for turning FED on or off
pi = pigpio.pi() 


savepath="/home/drivemazepi/Documents/Data/"
#Choose "Animal" or "Test" below
# trial_type = "Test"
trial_type = "Animal"
print(trial_type)
if trial_type == "Test":
    subjects = ["335490249236"]
if trial_type == "Animal":  
    #subjects = ["328340226232" ,"3354904556", "y"] #out of study,  ""
    #subjects = ["328340226232" ,"3354903011", "335490167178", "8501114126"]
    subjects = ["8500188177" ,"3354909574", "3354916686"]#L,nm, R

#general variables
heavy=40 #heavy limit for weight based sensing
scale_cal= 13959025.000#13011825.000 #use a calibration code and 20g weight to find out
nest_timeout=60000 #nest choice timeout in ms
acquisition_end_timeout=20000 #scope timeout after return to nest
scale_interval_scan=500 #scan interval in ms when sensing
weighing_time=1000 #duration of weight aqcuisition in ms
safety_delay=4000 #ms delay to confirm putative maze exit
exit_delay =2000 #ms delay to close door 2 after entry into sem
alarm_email = 1500000 #25min#2700000 #ms 45 min
exit_timer_flag= True



#timestamp miniscope frames
frame_in_port=5#10 
pi.set_mode(frame_in_port, pigpio.INPUT)
fc=pi.callback(frame_in_port,pigpio.EITHER_EDGE)
fc.reset_tally()
print(fc.tally())
frame_counter=fc.tally()
tick = pi.get_current_tick()
print(tick)

#trigger miniscope
start_scope_port=9
pi.set_mode(start_scope_port, pigpio.OUTPUT)
pi.write(start_scope_port,0)

#drink module
water_reset_port=12
pi.set_mode(water_reset_port, pigpio.OUTPUT)
pi.write(water_reset_port,1)
lick_in_port=4
lick_out_port=17
pi.set_mode(lick_in_port, pigpio.INPUT)
pi.set_mode(lick_out_port, pigpio.OUTPUT)
water_duration=100 # in ms 50ms=10ul
water_flag=False
water_stop_dose_flag=False

#run module
wheel_in_port=18
pi.set_mode(wheel_in_port, pigpio.INPUT)
clkLastState=pi.read(wheel_in_port)
cycle=1200 #cycle on running wheel gives approx this many counts 1200 600b 90 copal;
run_clk_start = 0
wheel_duration=120000

#food module
FED_in=14#14 #input to FED3 - dispense
FED_out=15#6#14#15#output from FED3 - pellet retrieved
pi.set_mode(FED_out, pigpio.INPUT)
pi.set_mode(FED_in, pigpio.OUTPUT)

#social module
social_duration=15000

#beams
#SEM
b0=20
b1=16#6
#unit1 
b2=7#11 
b3=27 
#unit2
b4=23
b5=24
#unit3
b6=25
b7=19 
#unit4
b8=21
b9=26
#unit5
b10=10
b11=13
beaml=(b0,b1,b2,b3,b4,b5,b6,b7,b8,b9,b10,b11)

#set up gpio
for x in range(0, 12):
    pi.set_mode(beaml[x], pigpio.INPUT)
# for x in [7]:
#     pi.set_mode(beaml[x], pigpio.PUD_DOWN) # Set an input pin and initial value to be pulled low (off)
#for x in [1]:
#   pi.set_mode(beaml[x], pigpio.INPUT) 
#   pi.set_mode(beaml[x], pigpio.PUD_DOWN)
for x in [1,2,3,5,7,8,10,11]:
    pi.set_mode(beaml[x], pigpio.INPUT)
# for x in [0]:
#     pi.set_mode(beaml[x], pigpio.PUD_UP)
# for x in [10]:
#     pi.set_mode(beaml[x], pigpio.INPUT)
#     pi.set_mode(beaml[x], pigpio.PUD_UP)    

#serial to ard mega servos
ser = serial.Serial('/dev/ttyACM0', 9600)
time.sleep(5)
# input("turn servo power on and press enter")
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
        
    def append_event(self,amount_consumed,latency_to_consumption,event_type,animaltag,frame,hardware_time,experiment):
        """
        Function used to save event parameters to a .csv file
        example use save.append_event("", "", "initialize", animaltag,frame_counter,tick, experiment)
        """
        global event_list

        event_list = {
            "Date_Time": [],
            "amount_consumed": [],
            "latency_to_consumption": [],
            "Type" : [],   
            "frame": [],
            "hardware_time" : [],
            "experiment" : [],
        }
        amount_consumed=str(amount_consumed)
        latency_to_consumption=str(latency_to_consumption)
        
        event_list.update({'amount_consumed': [amount_consumed]})
        event_list.update({'latency_to_consumption': [latency_to_consumption]})
        event_list.update({'Type': [event_type]})
        event_list.update({'Date_Time': [datetime.now()]})
        event_list.update({'frame': [frame]})
        event_list.update({'hardware_time': [hardware_time]})
        event_list.update({'experiment': [experiment]})

        df_e = pd.DataFrame(event_list)
        animaltag=str(animaltag)
        if not os.path.isfile(savepath + animaltag + "_events.csv"):
            df_e.to_csv(savepath + animaltag + "_events.csv", encoding="utf-8-sig", index=False)
        else:
            df_e.to_csv(savepath + animaltag + "_events.csv", mode="a+", header=False, encoding="utf-8-sig", index=False)

#initialize
#open_door(1)
time.sleep(3)
#for x in range (1,15): #python... stops at 15
#    close_door(x)
#    time.sleep(0.5)
for x in [3,5,7,9,11,14,1]:
    open_door(x)
    time.sleep(1)
#close_door(14)
#time.sleep(1)
#open_door(14)
pi.write(water_reset_port,0)
print("beam check")
for x in range(0, 12):    
    print(x)
    print(pi.read(beaml[x]))
if FEDonFLAG:    
    pi.write(FED_in,1) # give a pellet
pi.write(lick_out_port,1) # give a water drop
time.sleep(0.05)
pi.write(lick_out_port,0)


pi.write(FED_in,0)
pi.write(water_reset_port,1)
save = SaveData()
for x in range(np.size(subjects)):
    animaltag=subjects[x]
    save.append_event("", "", "initialize", animaltag,"","","")
mode=0
#fc.reset_tally
# pi.write(start_scope_port,1) #start acquisition
#execution loop    
while True:
    #command loop changes door targets, records beams and controls rewards
    millis = int(round(time.time() * 1000))

    if mode==0: #SEM open for entry
        open_door(1)
        close_door(2)
        if not pi.read(beaml[1]) and pi.read(beaml[0]):#changed from 0,1
            mode=1
            print("m1")
            w=int(10)
            generic_timer=int(round(time.time() * 1000))
            animal_found_flag=False
            my_RFID.clear_tags()
    if mode==1: #SEM trapped for id        
        ################close_door(1)
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
        if tag==335490249236 or tag==8500188177 or tag==3354909574 or tag==3354916686:
            animal_found_flag=True 
            #print("\nfound animal: ")
            #print(tag)
            animaltag=tag
            weight_aqcuisition_timer=int(round(time.time() * 1000))
            m=[] #mass measurement points
            mode=2
            fc.reset_tally()
            frame_counter=fc.tally()
            tick = pi.get_current_tick()
            save.append_event("", "", "leave_nest", animaltag,frame_counter,tick,experiment)
            #print("m2")
    if mode==2:
#        pi.write(start_scope_port,1) #start acquisition      
        while int(round(time.time() * 1000))-weight_aqcuisition_timer<weighing_time:
            n=scale.getWeight() * 1000
            m.append(n)
            #print("Acquired Mass is {0:0.3f} g".format(n))
        w=stats.mean(m)
        #print(w)
        if w<5:
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
        close_door(1)
        mode=4
        #print("m4")        
        maze_entry_flag=False #animal must change this flag to exit maze = enter at least one pod
        pod_entry_flag=False  #flag for detecting each beam break only once
        fc.reset_tally()
        pi.write(start_scope_port,1) #start acquisition
        stop_imaging_flag=False
        frame_counter=fc.tally()
        tick = pi.get_current_tick()
        save.append_event("", "", "block_start", animaltag,frame_counter,tick,experiment)
        frame_counter=fc.tally()
        tick = pi.get_current_tick()
        save.append_event("", "", "imaging_start", animaltag,frame_counter,tick,experiment)
        email_timer = int(round(time.time() * 1000))
    if mode==4: #maze operational
        if not maze_entry_flag:
            if not pi.read(beaml[2]) or not pi.read(beaml[4]) or not pi.read(beaml[6]) or not pi.read(beaml[8]) or not pi.read(beaml[10]) :# or ...: #enter any unit
                maze_entry_flag=True
                #print("in maze")
                                 
        if int(round(time.time() * 1000)) - email_timer>alarm_email:
            print("no movement")
            try:
                 # initializing the server connection
                 yag = yagmail.SMTP(
                     user="switchmazebot2000@gmail.com", oauth2_file="~/oauth2_creds.json"
                  )
                 # sending the email
                 yag.send(
                     to="cse.hartmann@gmail.com",
                     subject="Drivemaze rescue",
                     contents="""
                     Drivemaze rescue needed.
                     """,
                 )
                 print("Email sent successfully")
                 pi.write(start_scope_port,0) #stop acquisition
                 frame_counter=fc.tally()
                 tick = pi.get_current_tick()
                 save.append_event("", "", "imaging_stop", animaltag,frame_counter,tick,experiment)
                 mode=2# stop maze
            except:
                 print("Error, email was not sent")


        if not pi.read(beaml[2]) and not pod_entry_flag: #enter unit1 FOOD
            email_timer = int(round(time.time() * 1000))
            frame_counter=fc.tally()
            tick = pi.get_current_tick()
            save.append_event("", "", "enter_feed", animaltag,frame_counter,tick,experiment)
            pod_entry_flag=True
            print("unit1")
            close_door(3)
            open_door(4)
            food_timer=int(round(time.time() * 1000))
            food_flag=True
            pi.write(FED_in,0)
            pellets=0
            food_delay=[]
        if food_flag and pi.read(FED_out): #rec delay to feed
            email_timer = int(round(time.time() * 1000))
            print("retrieved")
            frame_counter=fc.tally()
            tick = pi.get_current_tick()
            save.append_event("", "", "retrieve_pellet", animaltag,frame_counter,tick,experiment) 
            food_delay=int(round(time.time() * 1000))-food_timer
            #print("food delay was")
            #print(food_delay)
            food_flag=False
            pellets=1
        if not pi.read(beaml[3]) and pod_entry_flag: #exit
            email_timer = int(round(time.time() * 1000))
            frame_counter=fc.tally()
            tick = pi.get_current_tick()
            save.append_event(pellets, food_delay, "exit_feed", animaltag,frame_counter,tick,experiment)
            pod_entry_flag=False
            #print("ex1")
            close_door(4)
            open_door(3)
            if FEDonFLAG:
                #print("prep next")
                pi.write(FED_in,1) #prep next pellet
        if not pi.read(beaml[4]) and not pod_entry_flag: #enter unit2
            email_timer = int(round(time.time() * 1000))
            frame_counter=fc.tally()
            tick = pi.get_current_tick()
            save.append_event("", "", "enter_run", animaltag,frame_counter,tick,experiment)
            pod_entry_flag=True
            #print("unit2")
            close_door(5)
            open_door(6)
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
            email_timer = int(round(time.time() * 1000))
            #record running wheel 
            clkState=pi.read(wheel_in_port)
            if clkState != clkLastState:
                counter += 1  
                clkLastState = clkState
            if save_flag and counter>limit/4: #detect latency to run start at first quarter revolution
                frame_counter=fc.tally()
                tick = pi.get_current_tick()
                save.append_event("", "", "run", animaltag,frame_counter,tick,experiment) 
                latency_to_run = int(round(time.time() * 1000))-unit2_timer
                save_flag=False
                #print("run start")
            if counter >= limit:
                #print(counter)    
                limit=counter+cycle
        if wheel_flag and millis-wheel_timer>wheel_duration:
            close_door(13)
            wheel_flag=False
        if not pi.read(beaml[5]) and pod_entry_flag: #exit
            email_timer = int(round(time.time() * 1000))
            frame_counter=fc.tally()
            tick = pi.get_current_tick()
            revs=counter/cycle
            save.append_event(revs, latency_to_run, "exit_run", animaltag,frame_counter,tick,experiment)
            pod_entry_flag=False
            #print("ex2")
            close_door(6)
            open_door(5)
            rec_wheel_flag=False
            wheel_flag=False
        if not pi.read(beaml[6]) and not pod_entry_flag: #enter unit3 EXPLORE
            email_timer = int(round(time.time() * 1000))
            frame_counter=fc.tally()
            tick = pi.get_current_tick()
            save.append_event("", "", "enter_explore", animaltag,frame_counter,tick,experiment)
            pod_entry_flag=True
            #print("unit3")
            close_door(7)
            open_door(8)
            unit1_timer=int(round(time.time() * 1000))
        if not pi.read(beaml[7]) and pod_entry_flag: #exit
            email_timer = int(round(time.time() * 1000))
            frame_counter=fc.tally()
            tick = pi.get_current_tick()
            exploration_consumed = int(round(time.time() * 1000))-unit1_timer
            save.append_event(exploration_consumed, "", "exit_explore", animaltag,frame_counter,tick,experiment)
            pod_entry_flag=False
            #print("ex3")
            close_door(8)
            open_door(7)
        if not pi.read(beaml[8]) and not pod_entry_flag: #enter unit4  SOCIAL 
            email_timer = int(round(time.time() * 1000))         
            frame_counter=fc.tally()
            tick = pi.get_current_tick()
            save.append_event("", "", "enter_social", animaltag,frame_counter,tick,experiment)
            pod_entry_flag=True
            #print("unit4")
            close_door(9)
            open_door(10)
            #open_door(14)#social
            pi.write(water_reset_port,0)
            social_timer=int(round(time.time() * 1000))
            social_flag=True
            pi.write(water_reset_port,1)
            #print("before")
        if social_flag and millis-social_timer>social_duration:
            close_door(14)#social, saftey to prevet getting stuck
            social_flag=False
            #print("here")
        if not pi.read(beaml[9]) and pod_entry_flag: #exit
            email_timer = int(round(time.time() * 1000))
            frame_counter=fc.tally()
            tick = pi.get_current_tick()
            social_consumed=int(round(time.time() * 1000))-social_timer
            save.append_event(social_consumed, "", "exit_social", animaltag,frame_counter,tick,experiment)
            pod_entry_flag=False
            #print("ex4")
            close_door(10)
            open_door(9)
            open_door(14)#open social door
            social_flag=False
        if not pi.read(beaml[10]) and not pod_entry_flag: #enter unit5
            email_timer = int(round(time.time() * 1000))
            frame_counter=fc.tally()
            tick = pi.get_current_tick()
            save.append_event("", "", "enter_drink", animaltag,frame_counter,tick,experiment)
            pod_entry_flag=True
            #print("unit5")
            close_door(11)
            open_door(12)
            lick_timer=int(round(time.time() * 1000))
            rec_licks_flag=True
            water_flag=True
            water_stop_dose_flag=False
            licks=0
            drink_delay=[]
        if rec_licks_flag:
            #record licking
            if pi.read(lick_in_port):
                licks=licks+1
                if water_flag:
                    frame_counter=fc.tally()
                    tick = pi.get_current_tick()
                    save.append_event("", "", "drink", animaltag,frame_counter,tick,experiment) 
                    drink_delay=int(round(time.time() * 1000))-lick_timer
                    pi.write(lick_out_port,1) # start giving water
                    water_dose_timer=int(round(time.time() * 1000))
                    water_flag=False
                    water_stop_dose_flag=True
            if water_stop_dose_flag and millis-water_dose_timer>water_duration:
                pi.write(lick_out_port,0)
                water_stop_dose_flag=False
                #print("drink delay was")
                #print(drink_delay)                   
        if not pi.read(beaml[11]) and pod_entry_flag: #exit
            email_timer = int(round(time.time() * 1000))
            frame_counter=fc.tally()
            tick = pi.get_current_tick()
            save.append_event(licks, drink_delay, "exit_drink", animaltag,frame_counter,tick,experiment)
            pod_entry_flag=False
            #print("ex5")
            close_door(12)
            open_door(11)
            rec_licks_flag=False
        
        if not pi.read(beaml[1]) and maze_entry_flag and not sense_SEM_flag and not pod_entry_flag: #putative leave maze
            email_timer = int(round(time.time() * 1000))
            #print("putative return to SEM")
            scale_timer=int(round(time.time() * 1000))
            sense_SEM_flag=True
            exit_timer_flag= True
        if sense_SEM_flag and millis-scale_timer>scale_interval_scan:
            w = scale.getWeight() * 1000
            #print("Mass is {0:0.3f} g".format(w))
            scale_timer=int(round(time.time() * 1000))
            if w>15: #definite leave maze
                frame_counter=fc.tally()
                tick = pi.get_current_tick()
                save.append_event("", "", "block_end", animaltag,frame_counter,tick,experiment)
                #close_door(2)
                open_door(1)
                if exit_timer_flag:
                    exit_timer = int(round(time.time() * 1000))
                    exit_timer_flag = False
                if int(round(time.time() * 1000))- exit_timer>exit_delay: #2s wait to close door
                    #time.sleep(2.0)
                    close_door(2)
                    mode=5
                    #print("m5")
                    another_entered=False
                    sense_SEM_flag=False
                    exit_safety_timer_flag=True
            if w<3 and pi.read(beaml[0]):
                sense_SEM_flag=False

    if mode==5: #wait for exit or entry of other
        if millis-scale_timer>scale_interval_scan:
            w = scale.getWeight() * 1000
            #print("Mass is {0:0.3f} g".format(w))
            scale_timer=int(round(time.time() * 1000))
        if w<3 and pi.read(beaml[1]):
            #print("putative exit")
            if exit_safety_timer_flag:
                exit_safety_timer=int(round(time.time() * 1000))
                exit_safety_timer_flag=False
                w = scale.getWeight() * 1000
            if not exit_safety_timer_flag and w<3 and pi.read(beaml[0]) and int(round(time.time() * 1000))-exit_safety_timer>safety_delay:
                close_door(1)
                nest_timer=int(round(time.time() * 1000))
                acquisition_end_timer=int(round(time.time() * 1000))
                mode=6
                #print("m6")
        if w>heavy:
            another_entered=True
            #print("sub")
        if another_entered and w<heavy and w>10 and pi.read(beaml[1]):
            mode=1
            #print("m1 sub")
            w=int(10)
            generic_timer=int(round(time.time() * 1000))
            animal_found_flag=False
    if mode==6: #wait for nest choice time out
        if millis-acquisition_end_timer>acquisition_end_timeout and not stop_imaging_flag:
            pi.write(start_scope_port,0) #stop acquisition
            frame_counter=fc.tally()
            tick = pi.get_current_tick()
            save.append_event("", "", "imaging_stop", animaltag,frame_counter,tick,experiment)
            print("Imaging stopped. Frames captured:")
            print(frame_counter)
            stop_imaging_flag=True
        if millis-nest_timer>nest_timeout:
            frame_counter=0
            for x in range(np.size(subjects)):
                animaltag=subjects[x]
                save.append_event("", "", "block_available", animaltag,frame_counter,tick,experiment)
            mode=0
            #print("m0") 
    
    #troubleshoot loop time
#     print(millis)l 