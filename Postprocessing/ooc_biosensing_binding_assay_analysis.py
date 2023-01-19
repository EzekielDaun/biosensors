import os
import scipy.io
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.pylab as pylab
import pandas as pd
import seaborn as sns
import datetime
import numpy as np
import fnmatch
import glob
import cv2

# A module to streamline post-processing of retrospective analysis output data, mainly used for Organ-on-Chip Biosensing experiments, functions that extract optical data, consolidate data from fluigent log files, tabulate net shifts, etc. in Python are included.

# Avineet Randhawa | 2023  


def extract_peak_position_profiles_ra_original(path_to_sweep_output_folder):
    '''This function extracts peak position profiles when the original retrospective analysis script is used for analysis with eight sensors.  It scales such that peak shift units are in nanometers and places the output into a dataframe'''
    
    sensor_1 = scipy.io.loadmat(path_to_sweep_output_folder + '/Ch1-2_Analysis/matlab_matrix.mat')['power_1_offset_list'][0]
    sensor_2 = scipy.io.loadmat(path_to_sweep_output_folder + '/Ch1-2_Analysis/matlab_matrix.mat')['power_2_offset_list'][0]
    sensor_3 = scipy.io.loadmat(path_to_sweep_output_folder + '/Ch3-4_Analysis/matlab_matrix.mat')['power_1_offset_list'][0]
    sensor_4 = scipy.io.loadmat(path_to_sweep_output_folder + '/Ch3-4_Analysis/matlab_matrix.mat')['power_2_offset_list'][0]
    sensor_5 = scipy.io.loadmat(path_to_sweep_output_folder + '/Ch5-6_Analysis/matlab_matrix.mat')['power_1_offset_list'][0]
    sensor_6 = scipy.io.loadmat(path_to_sweep_output_folder + '/Ch5-6_Analysis/matlab_matrix.mat')['power_2_offset_list'][0]
    sensor_7 = scipy.io.loadmat(path_to_sweep_output_folder + '/Ch7-8_Analysis/matlab_matrix.mat')['power_1_offset_list'][0]
    sensor_8 = scipy.io.loadmat(path_to_sweep_output_folder + '/Ch7-8_Analysis/matlab_matrix.mat')['power_2_offset_list'][0]
    time = scipy.io.loadmat(path_to_sweep_output_folder + '/Ch5-6_Analysis/matlab_matrix.mat')['t_array'][0]

    sensor_data = pd.DataFrame(columns=['Time', 'Sensor 1', 'Sensor 2', 'Sensor 3', 'Sensor 4', 'Sensor 5', 'Sensor 6', 'Sensor 7', 'Sensor 8'])
    sensor_data['Time'] = time
    sensor_data['Sensor 1'] = sensor_1 * 1e9
    sensor_data['Sensor 2'] = sensor_2 * 1e9
    sensor_data['Sensor 3'] = sensor_3 * 1e9
    sensor_data['Sensor 4'] = sensor_4 * 1e9
    sensor_data['Sensor 5'] = sensor_5 * 1e9
    sensor_data['Sensor 6'] = sensor_6 * 1e9
    sensor_data['Sensor 7'] = sensor_7 * 1e9
    sensor_data['Sensor 8'] = sensor_8 * 1e9

    return sensor_data


# def extract_peak_position_profiles_ra_gui(path_to_sweep_output_folder):
#     '''This function extracts peak position profiles when the updated retrospective analysis script (with a GUI) is used for analysis.  It assumes that results are provided in meters, the power arrays of eight sensors are unlabelled, and that the timesteps array units are in hours; the output is placed into a dataframe'''

#     sensor_1 = scipy.io.loadmat(path_to_sweep_output_folder + '/peak_shifts.mat')['power_1_unknown'][0]
#     sensor_2 = scipy.io.loadmat(path_to_sweep_output_folder + '/peak_shifts.mat')['power_2_unknown'][0]
#     sensor_3 = scipy.io.loadmat(path_to_sweep_output_folder + '/peak_shifts.mat')['power_3_unknown'][0]
#     sensor_4 = scipy.io.loadmat(path_to_sweep_output_folder + '/peak_shifts.mat')['power_4_unknown'][0]
#     sensor_5 = scipy.io.loadmat(path_to_sweep_output_folder + '/peak_shifts.mat')['power_5_unknown'][0]
#     sensor_6 = scipy.io.loadmat(path_to_sweep_output_folder + '/peak_shifts.mat')['power_6_unknown'][0]
#     sensor_7 = scipy.io.loadmat(path_to_sweep_output_folder + '/peak_shifts.mat')['power_7_unknown'][0]
#     sensor_8 = scipy.io.loadmat(path_to_sweep_output_folder + '/peak_shifts.mat')['power_8_unknown'][0]

#     sensor_1 -= sensor_1[0]
#     sensor_2 -= sensor_2[0]
#     sensor_3 -= sensor_3[0]
#     sensor_4 -= sensor_4[0]
#     sensor_5 -= sensor_5[0]
#     sensor_6 -= sensor_6[0]
#     sensor_7 -= sensor_7[0]
#     sensor_8 -= sensor_8[0]

#     time = pd.read_csv(path_to_sweep_output_folder+'/Bioassay/timeSteps.csv', header=None).iloc[:-1, 2].to_numpy()/60

#     sensor_data = pd.DataFrame(columns=['Time', 'Sensor 1', 'Sensor 2', 'Sensor 3', 'Sensor 4', 'Sensor 5', 'Sensor 6', 'Sensor 7', 'Sensor 8'])
#     sensor_data['Time'] = time
#     sensor_data['Sensor 1'] = sensor_1 * 1e9
#     sensor_data['Sensor 2'] = sensor_2 * 1e9
#     sensor_data['Sensor 3'] = sensor_3 * 1e9
#     sensor_data['Sensor 4'] = sensor_4 * 1e9
#     sensor_data['Sensor 5'] = sensor_5 * 1e9
#     sensor_data['Sensor 6'] = sensor_6 * 1e9
#     sensor_data['Sensor 7'] = sensor_7 * 1e9
#     sensor_data['Sensor 8'] = sensor_8 * 1e9

#     return sensor_data


def extract_peak_positions_ra_gui(path_to_sweep_output_folder):
    '''This function extracts peak position profiles when the updated retrospective analysis script (with a GUI) is used for analysis.  It assumes that results are provided in nanometers, the power arrays of each sensor contains the word power (case sensitive) and are arranged in ascending order (i.e. power_1_array, power_2_array, etc.), and that the timesteps array units are in minutes; the output is placed into a dataframe'''

    sensor_matrix = scipy.io.loadmat(path_to_sweep_output_folder + '/peak_shifts.mat')
    sensor_data = pd.DataFrame()

    i = 1

    for key in sensor_matrix:
        if "power" in key:
            sensor_data.insert(loc = i-1, column = f'Sensor {i}', value = sensor_matrix[f'{key}'][0])
            i += 1
        if "t_" in key:
            sensor_data.insert(loc = i-1, column = f'Time', value = sensor_matrix[f'{key}'][0])

    for column in sensor_data:
        if 'Sensor' in column:
            sensor_data[column] -= sensor_data[column].iloc[0]

    return sensor_data


def consolidate_fluigent_data(sensor_dataframe, path_to_fluigent, save_path):
    '''This function takes the power sensor dataframe and adds columns corresponding to data from the fluigent log file.  The fluigent logging frequency will likely not match the sweep frequency, and so this function assigns the fluigent log datapoint immediately before a given sweep to that entry in the resulting dataframe, thereby providing a consolidated dataframe with corresponding optical and fluidic information.'''

    # Load the log files of interest based on keywords in the filename (based on the name assigned to the fluigent protocol running)
    fluigent_part_1 = pd.read_csv(glob.glob(path_to_fluigent + "/*Part-1*.csv")[0])
    fluigent_part_2 = pd.read_csv(glob.glob(path_to_fluigent + "/*Part-2*.csv")[0])

    # Convert the fluigent timestamps to timestamps recognized by the pandas library for downstream processing
    fluigent_part_1['Time'] = pd.to_datetime(fluigent_part_1['Time'])
    fluigent_part_2['Time'] = pd.to_datetime(fluigent_part_2['Time'])

    # Convert fluigent timestamps from absolute to relative time for compatibility with sweep timesteps
    start_datetime = fluigent_part_1['Time'][0]
    fluigent_part_1['Time'] = fluigent_part_1['Time'] - start_datetime
    fluigent_part_2['Time'] = fluigent_part_2['Time'] - start_datetime

    # Convert relative timestamps to minutes
    fluigent_part_1['Time'] = fluigent_part_1['Time'].dt.total_seconds()
    fluigent_part_1['Time'] = fluigent_part_1['Time']/60

    fluigent_part_2['Time'] = fluigent_part_2['Time'].dt.total_seconds()
    fluigent_part_2['Time'] = fluigent_part_2['Time']/60

    # Consolidate timesteps across two consecutive fluigent protocols into new dataframe
    fluigent = pd.concat([fluigent_part_1, fluigent_part_2], ignore_index=True, sort=False)

    # Loop through sweep timesteps and extract the fluigent entry nearest in time (but prior) to each sweep timestep
    union_indices = [0]
    for sensor_time in sensor_dataframe['Time'][1:]:
        lower_index = fluigent[fluigent['Time'] < sensor_time]['Time'].idxmax()
        union_indices.append(lower_index)

    # Filter consolidated fluigent log file for those entries identified just above
    fluigent_data = fluigent.loc[union_indices]

    # Consolidate the relevent columns of the filtered fluigent log file (renaming said column names more intuitively) with peak positions dataframe
    all_data = sensor_dataframe.copy()
    all_data['Valve Position (Channel 1)'] = fluigent_data['M-Switch #1 [Switch EZ #3 (10535)]'].to_numpy()
    all_data['Valve Position (Channel 2)'] = fluigent_data['M-Switch #4 [Switch EZ #3 (10535)]'].to_numpy()
    all_data['Flowrate (Channel 1)'] = fluigent_data['Flow EZ #1 (13109) Q'].to_numpy()
    all_data['Flowrate (Channel 2)'] = fluigent_data['Flow EZ #2 (13110) Q'].to_numpy()
    all_data['Pressure (Channel 1)'] = fluigent_data['Flow EZ #1 (13109)'].to_numpy()
    all_data['Pressure (Channel 2)'] = fluigent_data['Flow EZ #2 (13110)'].to_numpy()

    all_data.to_csv(save_path+'/Tabulated Data.csv')

    return all_data


def tabulate_net_peak_shifts(experiment_data, sweep_coordinates, list_of_assay_stages, conditions, save_path, sweeps_average=5):
    '''This function calculates the mean peak position across a series consecutive sweeps (the first sweep in each series is defined by the list of sweep_coordinates and the last is defined by the sweeps_average optional parameter, default set to the five sweeps following the first) and tabulates them into a dataframe.  The number of coordinates supplied should match the number of strings in the list_of_assay_stages parameter (e.g. Baseline PBS, antibody, antigen, etc.).  The resulting dataframe includes a condition column, which is defined by a list of strings (user defined, such as positive and negative control).  This dataframe is saved as a csv to the save path (default save_path).  A second dataframe is generated that contains a 'Peak Shift' column, generated using the Pandas .diff method, replacing the 'Mean Peak Position' entry with the difference between each subsequent stage (i.e. the net shift corresponding to each stage), with the first assay stage removed (assumed to be a reference point for later bulk RI or binding shifts).  The second dataframe is saved to the same save path.'''
    
    quantified_peak_pos_data = pd.DataFrame(columns=['Condition', 'Sensor' ,'Stage', 'Mean Peak Position Over 5 Sweeps (nm)'])
    
    for i, column in enumerate(experiment_data):
        if 'Sensor' in column:
            sensor_num = i+1
            if conditions[0] in column:
                condition = conditions[0]
            if conditions[1] in column: 
                condition = conditions[1]
            for j, sweep in enumerate(sweep_coordinates):
                mean_peak_pos = experiment_data[column].iloc[sweep:sweep+sweeps_average].mean()
                stage = list_of_assay_stages[j]
                count = i*6 + j
                quantified_peak_pos_data.loc[count] = [condition, sensor_num, stage, mean_peak_pos]
        
    quantified_peak_pos_data.to_csv(save_path + '/Processed Peak Position Data.csv')
    
    drop_indexes = quantified_peak_pos_data.index[quantified_peak_pos_data['Stage'] == list_of_assay_stages[0]].tolist()
    shift_data = quantified_peak_pos_data.copy()
    shift_data["Peak Shift"] = shift_data['Mean Peak Position Over 5 Sweeps (nm)'].diff()
    shift_data.drop(drop_indexes, inplace=True)
    shift_data.drop(['Mean Peak Position Over 5 Sweeps (nm)'], axis = 1, inplace=True)
    shift_data.to_csv(save_path + '/Processed Shift Data.csv')
    
    return shift_data


def stich_video_from_timelapse_captures(image_format, video_framerate, image_folder, video_name, save_path):
    '''This funciton uses openCV's VideoWriter to stich a video from a series of images (intended to be timelapse captures from the overhead microscope for observation of potential bubbles).  The image format variable should be in the following format: '.format', (e.g. '.jpg').  The video name should include the format (mp4), i.e. 'video_name.mp4'.'''

    images = [img for img in os.listdir(image_folder) if img.endswith(image_format)]
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(save_path + '/' + video_name, fourcc, video_framerate, (width,height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    cv2.destroyAllWindows()
    video.release()