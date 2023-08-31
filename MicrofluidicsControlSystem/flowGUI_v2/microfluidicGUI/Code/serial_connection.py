import PySimpleGUI as sg
#import uProcess_x64
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, FigureCanvasAgg
from matplotlib.figure import Figure
import numpy as np
from pathlib import Path  # core python module
import time
from pySerialTransfer import pySerialTransfer as txfer
import csv
from datetime import datetime
from multiprocessing import Process

headings = ['Time', 'Pressure1', 'Pressure2', 'Flow1', 'Flow2']
csv_name = "Data_Log"

link = 0

# sets link for arduino up
def link_arduino():
    SETTINGS_PATH = Path.cwd()

    settings = sg.UserSettings(
        path=SETTINGS_PATH, filename="settings.ini", use_config_file=True, convert_bools_and_none=True
    )

    arduino_com = settings["COM"]["arduino_com"]

    global link
    link = txfer.SerialTransfer('COM' + str(arduino_com))

    """
    Test to tell if valid
    if link is None:
        sg.popup_error('Invalid COM port for Arduino', title='Unable to connect to Arduino', button_color='tomato')
        return False
    """

    link.open()

    time.sleep(2)  # allow some time for the Arduino to completely reset
    return True

#creates csv files
def generate_csv():

    file = open(csv_name+'.csv', 'w', encoding='UTF8', newline='')
    writer = csv.writer(file)

    # write the header
    writer.writerow(headings)

    file.close()

def append_csv(list):
    with open(csv_name+".csv", 'a') as f_object:
        # Pass this file object to csv.writer()
        # and get a writer object
        writer_object = csv.writer(f_object)

        # Pass the list as an argument into
        # the writerow()
        writer_object.writerow(List)

        # Close the file object
        f_object.close()


def change_pressure(pressure):
    slope = (2 ** 12 - 1) / 15  # slope for converting pressure [psi] to 12bit DAC code

    code1 = max(min(2 ** 12 - 1, int(slope * (pressure[0]))), 0)
    code2 = max(min(2 ** 12 - 1, int(slope * (pressure[1]))), 0)

    sendSize = 0
    sendSize = link.tx_obj(code1, start_pos=sendSize)
    sendSize = link.tx_obj(code2, start_pos=sendSize)

    link.send(sendSize)

    while not link.available():
        if link.status < 0:
            if link.status == txfer.CRC_ERROR:
                sg.popup_error('ERROR: CRC_ERROR', button_color='tomato')
                print('ERROR: CRC_ERROR')

            elif link.status == txfer.PAYLOAD_ERROR:
                sg.popup_error('ERROR: PAYLOAD_ERROR', button_color='tomato')
                print('ERROR: PAYLOAD_ERROR')
            elif link.status == txfer.STOP_BYTE_ERROR:
                sg.popup_error('ERROR: STOP_BYTE_ERROR', button_color='tomato')
                print('ERROR: STOP_BYTE_ERROR')
            else:
                sg.popup_error('ERROR: {}'.format(link.status), button_color='tomato')
                print('ERROR: {}'.format(link.status))


    list = 0
    list.append = datetime.now()
    name = csv_name + ".csv"

    # add pressure since no feeback only change if changed by user
    list.extend(pressure)

    # add flow
    list.extend(read_flow())

    # add to csv
    append_csv(list)

def read_flow():
    recSize = 0
    flow = [0, 0]

    flow[0] = link.rx_obj(obj_type='f', start_pos=recSize)
    recSize += txfer.STRUCT_FORMAT_LENGTHS['f']

    flow[1] = link.rx_obj(obj_type='f', start_pos=recSize)
    recSize += txfer.STRUCT_FORMAT_LENGTHS['f']

    return flow

def read_data():
    list = 0
    list.append = datetime.now()
    name = csv_name+".csv"
    with open(name, 'r') as file:
        data = file.readlines()
    lastRow = data[-1]

    #add pressure since no feeback only change if changed by user
    list.extend(lastRow[1],lastRow[2])

    #add flow
    list.extend(read_flow())

    #add to csv
    append_csv(list)

    return


