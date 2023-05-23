# This script is used to connect to the N77 module, and stream in data.
# Author: Al-Qadasi

# import python modules
import visa
import time
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
from scipy import io
from scipy.io import savemat
from scipy.io import loadmat
import csv
plt.rcParams.update({'font.size': 24})
import os
rm = visa.ResourceManager()
#import fineAlign_DFB_laser

stage_temp = False;

measurement_time = datetime.now().strftime('%Y')+"-"+datetime.now().strftime('%m')+"-"+datetime.now().strftime('%d')+"_"+datetime.now().strftime('%H')+"_"+datetime.now().strftime('%M')+"_"+datetime.now().strftime('%S')+"_"

#baseFolder = 'C:/Users/MapleLeafStage/Al-Qadasi/LSI/AIM_chip_active_measurement/'
#simulationFolderName_MatlabDrive='../../MATLAB/Active_AIM_chip/'+simulationFolderName_local

baseFolder = 'C:/Users/MapleLeafStage/Documents/Al-Qadasi/AIM chip testing/DP_2020_07/'

simulationFolderName_local=measurement_time+'ChipG_10HzRampUp0to3V_StageTemp20C_LaserTemp12C/'
r_freq = 10
simulationFolderName_MatlabDrive= simulationFolderName_local

simulation_name= 'SARS-CoV-2_Spike_Bioassay'

print(baseFolder+simulationFolderName_MatlabDrive)
try:
    os.stat(baseFolder+simulationFolderName_local)
except:
    os.mkdir(baseFolder+simulationFolderName_local)

try:
    os.stat(baseFolder+simulationFolderName_MatlabDrive)
except:
    os.mkdir(baseFolder+simulationFolderName_MatlabDrive)

# Connect to Stage motors
import CorvusEco
# reload(CorvusEco)
motors=CorvusEco.CorvusEcoClass()
motors.connect('ASRL4::INSTR',rm,1,0,3)

'''#Connecting to the laser
import hp816x_instr
reload(hp816x_instr)
laser = hp816x_instr.hp816x();
laser.connect('GPIB0::20::INSTR', reset=0, forceTrans=1)
'''


##################################################
################### STAGE TEC ####################
##################################################
if(stage_temp):
    # Stage TEC
    import SRS_LDC501_instr as SRS_LDC501
    # reload(SRS_LDC501)
    LDC_stage = SRS_LDC501.SRS_LDC501()
    LDC_stage.connect('GPIB0::4::INSTR')#, reset=0, forceTrans=1)
    Vlimit=1.2
    Ilimit=40
    #Stage_temp=15

    # Setting sTAGE temperature range and steps for sweep
    Stage_min_temp    = 20 #21.4
    Stage_max_temp    = 30#21.7
    Stage_steps_temp  = 11# Stage_max_temp-Stage_min_temp+1
    #Stage_temp_axis   = np.linspace(Stage_min_temp,Stage_max_temp, Stage_steps_temp)
    Stage_temp_axis_increment   = np.linspace(Stage_min_temp, Stage_max_temp, Stage_steps_temp)
    Stage_temp_axis_decrement   = np.linspace(Stage_max_temp, Stage_min_temp, Stage_steps_temp)
    Stage_temp_axis    = np.concatenate([Stage_temp_axis_increment, Stage_temp_axis_decrement])

    #sinusoidal_increments    = 5*np.sin(np.linspace(0, 2*3.1415926535897932384626433, Stage_steps_temp))
    #Stage_temp_axis          = Stage_min_temp + sinusoidal_increments

    Stage_TEC_wait_time= 0
    LDC_stage.setTemperature(Stage_temp_axis[0])
    LDC_stage.tecON()
    LDC_stage.getTemperature()

# Open Connection
import N774xA
# reload(N774xA)
N77instr = N774xA.N774xA();
N77instr.connect('TCPIP0::100.65.11.185::inst0::INSTR')
print ("Connected to N7744 detector")

set_chan = [1, 2, 3, 4]
meas_chan = [1, 2]
PD_Ch_number = 1
ramp_freq = r_freq
Samples_per_ramp = 1000 # fs = ramp_freq*Samples_per_ramp
Sampling_time_ms = 1000.0/(ramp_freq*Samples_per_ramp) # 0.1
Number_of_ramps  = 1000 # 10Hz:1000,
N77_measurement_loops = 1
measurement_iterations = 2000 #2*Stage_steps_temp-1 # 10

Number_of_readings = Number_of_ramps* int(1/(ramp_freq*Sampling_time_ms*1e-3)) #200

# Stop logging for all Channels
for i in set_chan:
    N77instr.stopLogging(i)
# Setup Channels
for i in set_chan:
    N77instr.setLoopRangeGainTriggerPWR(i, 0, Number_of_readings, Sampling_time_ms)
# Start Logging (Prepare all channels to take measurements upon receiving the trigger)
for i in set_chan:
    N77instr.startLogging(i)

Measurement_time = Number_of_ramps*Samples_per_ramp*Sampling_time_ms/1000.0*N77_measurement_loops*measurement_iterations/60.0
print("Data Acquisition Time = %.3f mins" % (Measurement_time))
print("Total number of a single N77 measurement readings = %d . <- [Values greater than 1,000,000 result in wrong number of samples]" % (Number_of_readings))
print("Total number of N77 ramps = %d " % (N77_measurement_loops*Number_of_readings))
print("Total number of ramps = %d " % (measurement_iterations*N77_measurement_loops*Number_of_readings))

# Start Measurement
N77instr.trigger(1)

i_stage_temp = 0;
LDC_stage_measured_temp = np.zeros(measurement_iterations)

plt.figure(1)
plt.axes(ylim=(-34,-24))

# get the initial time
t0 = time.time()
csvFilename = 'timeSteps.csv'
with open(baseFolder + simulationFolderName_MatlabDrive + csvFilename, 'a') as f:
    writer = csv.writer(f)
    writer.writerow([0,0,t0, simulation_name+'measurementXYZ.csv'])

## Loop to get x Continuous results
for i in range(measurement_iterations):
    #do_fine_align(laser, motors)  # Running  Fine Alignment
    for chan in meas_chan:
        N77instr.stopLogging(chan)
        N77instr.startLogging(chan)
    N77instr.trigger(1)
    array = N77instr.measure(meas_chan, N77_measurement_loops)
    for chan in meas_chan:
        N77instr.stopLogging(chan)
    ###np.savetxt(baseFolder+simulationFolderName+simulation_name+'_measurement'+str(i) + '.csv', array.T, delimiter=',')
    np.savetxt(baseFolder+simulationFolderName_MatlabDrive+simulation_name+'measurement'+str(i).zfill(4) + '.csv', array.T, delimiter=',')

    # get elapsed time
    t1 = time.time()
    t_elapse = t1 - t0
    # save elapsed time to CSV
    with open(baseFolder + simulationFolderName_MatlabDrive + csvFilename, 'a') as f:
        writer = csv.writer(f)
        writer.writerow([i,t_elapse,t1, simulation_name+'measurement'+str(i).zfill(4) + '.csv'])

    print("Loop# %d" % i)
    if (stage_temp):
        if(i%2==0):# and i<44): # Change the stage temperature every 1 loop iterations
            i_stage_temp = i_stage_temp+1
        #    LDC_stage.setTemperature(Stage_temp_axis[i_stage_temp])
        LDC_stage_measured_temp[i] = LDC_stage.getTemperature()
        #if(i==44):
        #    LDC_stage.setTemperature(Stage_min_temp)
        #    time.sleep(2)
        #    LDC_stage.tecON()
        #time.sleep(1)

    if(False):
        plt.clf()
        plt.plot(array[0,:], linewidth=3)
        plt.plot(array[1,:])
        #plt.title("F_ramp="+str(ramp_freq)+"Hz")#i
        #plt.axes(ylim=(-34, -24))
        #plt.savefig('C:/Users/MapleLeafStage/Al-Qadasi/LSI/AIM_chip_active_measurement/trial_continuous_logging_channel' + str(meas_chan)+'_measurement'+str(i).zfill(4)+str(time.time()) + '.png', bbox_inches='tight')
        #plt.savefig(baseFolder+simulationFolderName_MatlabDrive+simulation_name+'_measurement'+str(i).zfill(4)+'.jpg', bbox_inches='tight')
        plt.pause(0.0000001)

if(stage_temp):
    plt.figure(1)
    plt.plot(LDC_stage_measured_temp)
    plt.savefig(baseFolder+simulationFolderName_MatlabDrive+simulation_name+ str(meas_chan) + '.png', bbox_inches='tight')
    plt.pause(1)
    matDict_Stage_temp           = dict()
    matDict_Stage_temp['LDC_stage_measured_temp'] = LDC_stage_measured_temp
    savemat(baseFolder+simulationFolderName_MatlabDrive+simulation_name + '.mat', matDict_Stage_temp)#'Stage_temperatures'+

# Stop logging for all Channels
for i in set_chan:
    N77instr.stopLogging(i)

