
import PySimpleGUI as sg
from uProcess_x64 import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, FigureCanvasAgg
from matplotlib.figure import Figure
import numpy as np
import time
from pySerialTransfer import pySerialTransfer as txfer
import csv
from multiprocessing import Process

def draw_figure(canvas, figure, loc=(0, 0)):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def com_windows():
    layout = [
        [sg.Text('Valve Control', size=(40, 1),
                 justification='center', font='Helvetica 20')],
        [sg.Text('EIB200 COM port', size=(15, 1), font='Helvetica 12'), sg.InputText('6')],
        [sg.Text('Arduino1 COM port', size=(15, 1), font='Helvetica 12'), sg.InputText('4')],
        [sg.Text('4VM Adress', size=(15, 1), font='Helvetica 12'), sg.InputText('10')],
        [sg.Text('Arduino2 COM port', size=(15, 1), font='Helvetica 12'), sg.InputText('4')],

        [sg.Canvas(key='controls_cv')],
        [sg.Canvas(size=(650, 30), key='-CANVAS-')],

        [sg.Button('Submit', size=(10, 1), pad=((280, 0), 3), font='Helvetica 14')]
    ]

    # create the form and show it without the plot
    window = sg.Window('Start Screen',
                       layout, finalize=True)

    canvas_elem = window['-CANVAS-']
    canvas = canvas_elem.TKCanvas

    return window

def write_read(pressure):
    link = txfer.SerialTransfer('COM ' + str(arduino_com))
    link.open()
    time.sleep(2)  # allow some time for the Arduino to completely reset

    # create the data packets that will be transferred to/from Arduino
    pressure = packet()
    flow = packet()

    # Initialize system with known pressure to get starting value resistance value
    pressure.chan1, pressure.chan2 = 0, 0  # Initial pressure [psi]
    slope = ( 2**12 - 1 ) /15 # slope for converting pressure [psi] to 12bit DAC code

    code1 = max(min( 2**12 - 1, int(slope *(pressure.chan1))), 0)
    code2 = max(min( 2**12 - 1, int(slope *(pressure.chan2))), 0)

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

    recSize = 0
    flow = [0 ,0]

    flow[0] = link.rx_obj(obj_type='f', start_pos=recSize)
    recSize += txfer.STRUCT_FORMAT_LENGTHS['f']

    flow[1] = link.rx_obj(obj_type='f', start_pos=recSize)
    recSize += txfer.STRUCT_FORMAT_LENGTHS['f']

    return flow




# boiler plate code for GUI and animation
def create_windows():
    layout = [
        [sg.Text('Flow Rate', size=(40, 1),
                 justification='center', font='Helvetica 20')],

        [sg.Text('Enter PID values')],
        [sg.Text('P', size=(15, 1), font='Helvetica 12'), sg.InputText('1')],
        [sg.Text('I', size=(15, 1), font='Helvetica 12'), sg.InputText('0')],
        [sg.Text('D', size=(15, 1), font='Helvetica 12'), sg.InputText('0')],
        [sg.Text('Flow Rate [uL/min]', size=(15, 1), font='Helvetica 12'), sg.InputText('1')],
        [sg.Button('Update PID', size=(10, 1), pad=((280, 0), 3), font='Helvetica 14')],

        [sg.Button('Channel 1', size=(8 ,1), button_color=('white', 'green'), key='1'),
         sg.Button('Channel 2', size=(8 ,1), button_color=('white', 'green'), key='2'),
         sg.Button('Channel 3', size=(8 ,1), button_color=('white', 'green'), key='3'),
         sg.Button('Channel 4', size=(8 ,1), button_color=('white', 'green'), key='4'),
         sg.Button('Channel 5', size=(8 ,1), button_color=('white', 'green'), key='5'),
         sg.Button('Channel 6', size=(8 ,1), button_color=('white', 'green'), key='6'),
         sg.Button('Channel 7', size=(8 ,1), button_color=('white', 'green'), key='7'),
         sg.Button('Channel 8', size=(8 ,1), button_color=('white', 'green'), key='8')],

        [sg.Button('Start Control', size=(10 ,1), pad=((280, 0), 3), font='Helvetica 14')],

        [sg.Canvas(key='controls_cv')],
        [sg.Canvas(size=(640, 480), key='-CANVAS-')],
        [sg.Text('Number of data points to display on screen')],
        [sg.Slider(range=(10, 100), default_value=40, size=(40, 10),
                   orientation='h', key='-SLIDER-DATAPOINTS-')],
        [sg.Button('Exit', size=(10, 1), pad=((280, 0), 3), font='Helvetica 14')]
    ]

    # create the form and show it without the plot
    window = sg.Window('Start Screen',
                       layout, finalize=True)

    canvas_elem = window['-CANVAS-']
    canvas = canvas_elem.TKCanvas

    # draw the initial plot in the window
    fig = Figure()
    ax = fig.add_subplot(111)
    fig_agg = draw_figure(canvas, fig)

    return window, ax, fig_agg



class packet:
    chan1 = 1.0
    chan2 = 4.5


# function for controlling fluidic delivery.
def fluidic_control(eib_com, fourVM_addr, arduino_com):
    # write pressure to arduino, and read flow rate back


    eib = uProcess.CEIB()
    eib.InitConnection(eib_com)
    a = eib.New4VM(fourVM_addr)

    link = txfer.SerialTransfer('COM ' +str(arduino_com))
    link.open()
    time.sleep(2) # allow some time for the Arduino to completely reset

    # create the data packets that will be transferred to/from Arduino
    pressure = packet()
    flow = packet()

    # Initialize system with known pressure to get starting value resistance value
    pressure.chan1, pressure.chan2 = 0 ,0  # Initial pressure [psi]
    flow.chan1, flow.chan2 = write_read(pressure)    # write to DAC and read from flow sensor

    R = pressure.chan1 /flow.chan1 # initial resistance []

    Kp, Kd, Ki = 1, 0, 0
    err = np.zeros(100)
    N = 50 # How many samples are used for PID control (History depth)

    window, ax, fig_agg = create_windows()

    channels = ('1' ,'2' ,'3' ,'4' ,'5' ,'6' ,'7' ,'8')

    log = open('flowrate.csv', mode='w', newline = '')
    writer = csv.writer(log, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow([ 'Time [s]', 'Flow Rate [uL/min]', 'Pressure [bar]'])

    # wait to start
    pid, chan_sel = False, False
    while True:
        event, values = window.read()
        if event in ('Update PID'):
            Kp, Ki, Kd = float(values[0]), float(values[1]), float(values[2])
            flow_setpoint = float(values[3])
            pid = True
        elif event in channels:

            a.CmdSelect (1, int(event)) # Move channel 1 into position
            time.sleep(2.5)             # wait until valve is in position (2.5s max actuation time)

            for e in channels:
                if e == event:
                    window.Element(e).Update(button_color=(('white', 'green')))
                else:
                    window.Element(e).Update(button_color=(('white', 'red')))
            chan_sel = True
        if event in ('Start Control') and (pid and chan_sel):
            break

    start = time.time()  # Time at the beginning of control
    last = start
    while True:
        event, values = window.read(timeout=10)

        if event in ('Update PID'):
            Kp, Ki, Kd = float(values[0]), float(values[1]), float(values[2])
            flow_setpoint = float(values[3])

        elif event in channels:

            a.CmdSelect (1, int(event)) # Move channel 1 into position
            time.sleep(2.5)

            for e in channels:
                if e == event:
                    window.Element(e).Update(button_color=(('white', 'green')))
                else:
                    window.Element(e).Update(button_color=(('white', 'red')))

        elif event in ('Exit', None):
            break

        err = np.roll(err ,1) # Update error history
        err[0] = flow_setpoint - flow.chan1
        pressure.chan1 += float \
            (( Kp *err[0] + K d *(err[0] - np.mean(err[1:N])) + K i *np.sum(err[1:N]) )* R)  # Update pressure [psi]

        flow.chan1, flow.chan2 = write_read(pressure)  # write to DAC and read from flow sensor

        R = pressure.chan1 / flow.chan1

        ax.cla()  # clear the subplot
        ax.grid()  # draw the grid
        data_points = int(values['-SLIDER-DATAPOINTS-'])  # draw this many data points (on next line)
        ax.plot(range(data_points), err[:data_points], color='purple')
        ax.set_xlabel('Readings')
        ax.set_ylabel('Error')
        fig_agg.draw()

        # print(1/(time.time()-last)) #print frequency
        last = time.time()
        writer.writerow([time.time() - start, flow.chan1, pressure.chan1])

    window.close()
    log.close()


def main():
    eib = uProcess.CEIB()
    time.sleep(2)

    COM_select = com_windows()
    while True:
        event, values = COM_select.read(timeout=10)

        if event in ('Submit', None):
            eib_com = int(values[0])
            arduino_com = int(values[1])
            fourVM_addr = int(values[2])
            arduino = int(values[3])  # for photonic readout

            eib.InitConnection(eib_com)  # COM port we just chose

            if eib.New4VM(fourVM_addr) is None:
                print('Invalid COM or Address')
                continue
            else:
                break

    COM_select.close()

    eib.CloseConnection()  # This connection will be re-made inside the fluidic_control process

    # fluidic_control(eib, fourVM_addr, arduino_com)

    fluidic = Process(target=fluidic_control, args=(eib_com, fourVM_addr, arduino_com))
    # readout = Process(target = photonic_readout, args = (arduino,))
    fluidic.start()
    # readout.start()

    fluidic.join()


if __name__ == '__main__':
    main()