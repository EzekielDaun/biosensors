import numpy as np
import math
import csv
import time
import PySimpleGUI as sg

def read_csv(csv_name):


    with open(csv_name, "r") as infile:
        reader = csv.reader(infile)

        header_list = next(reader)
        try:
            data = list(reader)  # read everything else into a list of rows

        except:
            sg.popup_error('Error reading file')
            #return


    column1=[row[0] for row in data]
    column2=[row[1] for row in data]

    #print(column1)
    #print(column2)


csv_name = "test.csv"
current_pressure = 0.0
current_flow = 0.0
min = 0
max = 0

for i in range(length(flow)):
    if flow[i]==set:
        min=i
        max=i
        slope = (flow[i]-flow[i-1])/(pressure[i]-pressure[i-1])
        current_pressure = pressure[i]

    if flow[i]<set:
        min=i

    if flow[i]>set:
        max=i
        slope = (flow[max] - flow[min]) / (pressure[max] - pressure[min])
        y_intercept = flow[min] - slope * pressure[min]
        current_pressure = (flow[min] - y_intercept) / slope
        break


change_pressure(channel, set_pressure)
time.sleep(0.001)
current_flow = get_flow(channel)

for i in range(30):
    difference = flow-set


    if difference == 0:
         #done
        break

    if difference > 0:
        #flow is higher then set
        #adjust pressure accordingly using slope incase decreasing pressure increase flow
        slope = (current_flow - flow[min]) / (current_pressure - pressure[min])
        y_intercept = flow[min] - slope * pressure[min]
        #max will be replaced by current value

    else: #difference < 0:
        #flow is lower then set
        slope = (flow[max] - current_flow) / (pressure[max] - current_pressure)
        y_intercept = flow[min] - slope * pressure[min]
        min += 1 #start from current pressure
        max += 1 #max is shifted from by 1

    current_pressure = (set - y_intercept) / slope
    change_pressure(channel, current_pressure)
    time.sleep(0.001)
    current_flow = get_flow(channel)

    pressure.insert(min)


#add new data to csv file

