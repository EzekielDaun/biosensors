"""
PROGRAM NAME - Map_PvsF

PROGRAMMER - Spencer Witt, 2022-10-17

USAGE - Maps the pressure vs the flow

SYSTEM - Python 3.10.7 on a MAC II running A/UX V12.6

DATE - Started 2022-10-14
       Phase I completed 2022-10-17

BUGS -

DESCRIPTION -
*******************************************************)

"""
import numpy as np
import math
import csv

#creates csv files

def generate_csv(csv_name, headings, values):

    file = open(csv_name, 'w', encoding='UTF8', newline='')
    writer = csv.writer(file)

    # write the header
    writer.writerow(headings)

    for row in range(30):
         current_row = []
         for column in range(2):
             current_row.append(values[row, column])
         writer.writerow(current_row)
"""
#For testing purposes
""" 
def get_flow(pressure):
    return 2*(pressure) #For testing purposes


reservoir= "reservoir 1"
headings=["Pressure (bars)", "Flow (uL/min)"]

#pressure given in bar
max_pressure= 1

increments=5
step = max_pressure/increments

pressure = np.arange(0.0, max_pressure+step, step, dtype=np.float32) #pressure
#print(pressure) #Test to see if woprking

#flow in uL/min
flow = np.zeros((1,increments+1),  dtype=np.float32) #flow

for i in range(len(pressure)):
    flow = pressure #get_flow(pressure)
    print(flow[i]) #test if flow function working

csv_name=reservoir+"PvsF map"

#print("Done") #Test for loop
#generate_csv(csv_name, headings, pressure)





