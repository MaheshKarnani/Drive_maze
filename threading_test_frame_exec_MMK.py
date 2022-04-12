import time
import os
import pandas as pd
import statistics as stats
import sys
import datetime
import numpy as np
import threading

water_time = 0.1 # seconds water dispensed when animal licks spout 0.1=20ul standard
run_time = 120
wheel_position = "Left"
FED_position = "Right"

os.chdir("C:\Data\MMK")
class SaveData: 
    def append_event(self,rotation,food_time,event_type,animaltag,
                    wheel_position,FED_position):
        """
        Function used to save event parameters to a .csv file
        """
        global event_list
        event_list = {
            "Date_Time": [],
            "Rotation": [],
            "Pellet_Retrieval": [],
            "Type": [],
            "Wheel_Position": [],
            "FED_Position": []    
        }
        event_list.update({'Rotation': [rotation]})
        event_list.update({'Pellet_Retrieval': [food_time]})
        event_list.update({'Type': [event_type]})
        event_list.update({'Date_Time': [datetime.datetime.now()]})
        event_list.update({'Wheel_Position': [wheel_position]})
        event_list.update({'FED_Position': [FED_position]})
        df_e = pd.DataFrame(event_list)
        if not os.path.isfile(animaltag + "_events.csv"):
            df_e.to_csv(animaltag + "_events.csv", encoding="utf-8-sig", index=False)
        else:
            df_e.to_csv(animaltag + "_events.csv", mode="a+", header=False, encoding="utf-8-sig", index=False)

save = SaveData()
animaltag="31"
def frame_loop():  
    print("frame loop active")
    for i in range(100):
        save.append_event(run_time, water_time, "frame", animaltag, wheel_position, FED_position)
def execution_loop():
    for j in range(100):
        save.append_event(run_time, water_time, "exec", animaltag, wheel_position, FED_position)

x=threading.Thread(target=frame_loop)
x2=threading.Thread(target=execution_loop)
x.start()
x2.start()
print("done")