import PySimpleGUI as sg
import uProcess_x64
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, FigureCanvasAgg
from matplotlib.figure import Figure
import numpy as np
import time
from pySerialTransfer import pySerialTransfer as txfer
from Data import*
import csv
from multiprocessing import Process

link = txfer.SerialTransfer('COM' + str(arduino_com))
link.open()
time.sleep(2)  # allow some time for the Arduino to completely reset

def change_pressure(pressure):
    slope = (2 ** 12 - 1) / 15  # slope for converting pressure [psi] to 12bit DAC code

    code1 = max(min(2 ** 12 - 1, int(slope * (pressure.chan1))), 0)
    code2 = max(min(2 ** 12 - 1, int(slope * (pressure.chan2))), 0)

    sendSize = 0
    sendSize = link.tx_obj(code1, start_pos=sendSize)
    sendSize = link.tx_obj(code2, start_pos=sendSize)

    link.send(sendSize)

    while not link.available():
        if link.status < 0:
            if link.status == txfer.CRC_ERROR:
                print('ERROR: CRC_ERROR')
            elif link.status == txfer.PAYLOAD_ERROR:
                print('ERROR: PAYLOAD_ERROR')
            elif link.status == txfer.STOP_BYTE_ERROR:
                print('ERROR: STOP_BYTE_ERROR')
            else:
                print('ERROR: {}'.format(link.status))

def read_flow():
    recSize = 0
    flow = [0, 0]

    flow[0] = link.rx_obj(obj_type='f', start_pos=recSize)
    recSize += txfer.STRUCT_FORMAT_LENGTHS['f']

    flow[1] = link.rx_obj(obj_type='f', start_pos=recSize)
    recSize += txfer.STRUCT_FORMAT_LENGTHS['f']

    return flow