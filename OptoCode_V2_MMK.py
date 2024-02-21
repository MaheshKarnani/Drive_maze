#opto code 5th pellet
# laser starts with the 5th pellet and stops when the meal ends (10s without pellet retrieval)
from __future__ import print_function
import time
import pigpio
import os
import pandas as pd
import datetime
import yagmail
import keyboard
import pynput

# Paths and experiment details
note = "stopped previous run to clean" #"nothing unusual in previous session"
experiment = "inh_5" #"hab"
savepath = "/home/raspberry/Documents/Data/"
subject = "animal1" #change animal name here
stop_time = datetime.datetime.now()+datetime.timedelta(hours=1)
stop_time = stop_time.replace(hour=21,minute=5,second=0,microsecond=0) #SET STOP TIME HERE
print('session to stop at')
print(stop_time)

# Constants
pellet_interval = 0.6 #Time between pellet dispensing in seconds, set minimally 0.6s because FEDout TTL is 0.5s long
max_latency = 5 # Meal definition in s

if experiment == "inh_5":
    pellet_laser = 5 # Number of pellets to dispense before triggering the laser
    print('inh5 session')
elif experiment == "inh_1":
    pellet_laser = 1
    print('inh1 session')
elif experiment == "hab":
    print('habituation session')
    pellet_laser = 999

# Flags
MealFlag = False
pellet_wait = True # Flag to prevent read out while new pellet is being dispensed
Day_flag = True # session active flag - unclear name
OptoMealFlag = True #change first meal from opto to ctrl here
ContrMealFlag = False #change first meal from opto to ctrl here
end_flag=True #flag for last print only once.

# Initialize pigpio
pi = pigpio.pi()

# GPIO pin configuration
TTLpin = 17
FED_in = 14
FED_out = 15
pi.set_mode(FED_out, pigpio.INPUT)
pi.set_mode(FED_in, pigpio.OUTPUT)
pi.set_mode(TTLpin, pigpio.OUTPUT)

# Laser control functions
def Laser_on():
    print("Laser on")
    pi.write(TTLpin, 1)

def Laser_off():
    print("Laser off")
    pi.write(TTLpin, 0)

# Pellet dispensing function
def dispense_pellet():
    pi.write(FED_in, 0)
    print("Dispensing next pellet")
    pi.write(FED_in, 1)

# def on_press(key):#pause for cleaning feds
#     if key == keyboard.Key.space:
#         print("Paused. Press space again to resume.")
#         # Loop until space key is pressed again to resume
#         while True:
#             if keyboard.is_pressed(' '):
#                 print("Resuming...")
#                 break
# 
# # Create a listener for keyboard events
# listener = pynput.keyboard.Listener(on_press=on_press)
# listener.start()

# Function to save event data to CSV
def save_event(event_type, tick, experiment, pellet_number, latency, laser):
    event_data = {
        "Date_Time": [datetime.datetime.now()],
        "Type": [event_type],
        "hardware_time": [tick],
        "experiment": [experiment],
        "Pellet_Number": [pellet_number],
        "Latency": [latency],
        "Laser": [laser]
    }

    df_e = pd.DataFrame(event_data)
    filename = savepath + subject + "_events.csv"

    mode = "a+" if os.path.isfile(filename) else "w"
    df_e.to_csv(filename, mode=mode, header=not os.path.isfile(filename), encoding="utf-8-sig", index=False)

# Main loop for pellet retrieval and processing
dispense_pellet() #this sets continuous dispensing -- modify the function def and code below to do something else
Laser_off()
pellet_counter = 0
laser = 0
latency = 0 
last_pellet_time = time.time()-max_latency
tick = pi.get_current_tick()
save_event(note, tick, experiment, pellet_counter, latency, laser)
save_event("Start_session", tick, experiment, pellet_counter, latency, laser)
last_pellet_time = time.time()
                
try:
    while True:
        if Day_flag:
            if not MealFlag and datetime.datetime.now() > stop_time: #stops at user defined time if no meal ongoing, otherwise at next meal end
               Day_flag = False

            if pi.read(FED_out) and pellet_wait:
                #first, get time data
                this_pellet_time=time.time()
                tick = pi.get_current_tick()
                              
                #second, set laser status and log data
                pellet_counter += 1
                latency =  this_pellet_time - last_pellet_time
                if latency <= max_latency:#it's a meal
                    if pellet_counter == pellet_laser:
                        if OptoMealFlag:
                            Laser_on()
                            laser = 1 #marks if laser is on in csv file
                            OptoMealFlag = False
                            ContrMealFlag = True #next meal is a control meal
                        elif ContrMealFlag:
                            ContrMealFlag = False
                            OptoMealFlag = True #next meal is an opto meal
                MealFlag = True #potential meal has started
                #log data
                save_event("Pellet_Retrieved", tick, experiment, pellet_counter, latency, laser)
                
                #last, print data and manage next read
                print(pellet_counter)
                last_pellet_time = this_pellet_time
                pellet_wait = False #don't read again while TTL still up    

            if not pellet_wait and time.time() - last_pellet_time > pellet_interval: #ready for next read
                pellet_wait = True #only now can the next pellet retrieval be registered
                
            if MealFlag and time.time() - last_pellet_time > max_latency: #meal has ended
                #first, get time data
                tick = pi.get_current_tick()
                #second, figure out details, log data, and print
                if pellet_counter < pellet_laser:
                    save_event("Short meal ended", tick, experiment, pellet_counter, "", laser)
                    print("Short meal ended")
                elif laser == 1:
                    Laser_off()
                    laser = 0 #marks if laser is on in csv file
                    save_event("Opto meal ended", tick, experiment, pellet_counter, "", laser)
                    print('Opto meal ended')
                else:
                    save_event("Control meal ended", tick, experiment, pellet_counter, "", laser)
                    print('Ctrl meal ended')
                MealFlag = False
                pellet_counter = 0
                
        if not Day_flag:
            if end_flag:
               tick = pi.get_current_tick()
               save_event("End_session", tick, experiment, pellet_counter, "",laser)
               print("session ended at")
               print(datetime.datetime.now())
               end_flag=False    

# except KeyboardInterrupt:
#     print("Interrupted. Exiting.")#ctrl+c to exit
finally:
    pi.stop()