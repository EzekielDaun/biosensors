import PySimpleGUI as sg
import uProcess_x64 as uProcess
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, FigureCanvasAgg
from matplotlib.figure import Figure
import numpy as np
from math import factorial
import time
from datetime import datetime
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
             [sg.Text('Valve Control', size=(40, 1), justification='center', font='Helvetica 20')],
             [sg.Text('EIB200 COM port', size=(15, 1), font='Helvetica 12'), sg.InputText('12')],
             [sg.Text('Nano 33 COM port', size=(15, 1), font='Helvetica 12'), sg.InputText('14')],
             [sg.Text('4VM02 Address', size=(15, 1), font='Helvetica 12'), sg.InputText('10')],
             [sg.Text('Log Filename', size=(15, 1), font='Helvetica 12'), sg.InputText('run1')],

             [sg.Canvas(key='controls_cv')],
             [sg.Canvas(size=(650, 30), key='-CANVAS-')],

             [sg.Button('Submit', size=(10, 1), pad=((280, 0), 3), font='Helvetica 14')]
             ]

    # create the form and show it without the plot
    window = sg.Window('Start Screen', layout, finalize=True)

    canvas_elem = window['-CANVAS-']
    canvas = canvas_elem.TKCanvas
    
    return window

def create_windows():
    layout = [
        [sg.Text('Microfluidic Controller', size=(50, 1),justification='center', font='Helvetica 15')],
        [sg.Text('Set Flow [uL/min]', size=(15, 1), font='Helvetica 12'), sg.InputText('10')],
        [sg.Text('Enter PID values')],
        [sg.Text('P', size=(15, 1), font='Helvetica 12'), sg.InputText('0.01')],
        [sg.Text('I', size=(15, 1), font='Helvetica 12'), sg.InputText('0.005')],
        [sg.Text('D', size=(15, 1), font='Helvetica 12'), sg.InputText('0.3')],
        [sg.Button('Update PID', size=(10, 1), pad=((280, 0), 3), font='Helvetica 12')],

         [sg.Button('Channel 1', size=(8,1), button_color=('white', 'green'), key='1'),
         sg.Button('Channel 2', size=(8,1), button_color=('white', 'green'), key='2'),
         sg.Button('Channel 3', size=(8,1), button_color=('white', 'green'), key='3'),
         sg.Button('Channel 4', size=(8,1), button_color=('white', 'green'), key='4'),
         sg.Button('Channel 5', size=(8,1), button_color=('white', 'green'), key='5'),
         sg.Button('Channel 6', size=(8,1), button_color=('white', 'green'), key='6'),
         sg.Button('Channel 7', size=(8,1), button_color=('white', 'green'), key='7'),
         sg.Button('Channel 8', size=(8,1), button_color=('white', 'green'), key='8')],

        [sg.Button('Start Control', size=(10,1), pad=((280, 0), 3), font='Helvetica 12')],
        [sg.Button('Exit', size=(10, 1), pad=((280, 0), 3), font='Helvetica 12')],
        [sg.Canvas(key='controls_cv')],
        [sg.Canvas(size=(640, 480), key='-CANVAS-')]
        #[sg.Text('Number of data points to display on screen')],
        #[sg.Slider(range=(10, 100), default_value=40, size=(40, 10), orientation='h', key='-SLIDER-DATAPOINTS-')],

        ]

    # create the form and show it without the plot
    window = sg.Window('Microfluidic Controller', layout, finalize=True)

    canvas_elem = window['-CANVAS-']
    canvas = canvas_elem.TKCanvas

    # draw the initial plot in the window
    fig = Figure()
    ax = fig.add_subplot(111)
    fig_agg = draw_figure(canvas, fig)
    
    return window, ax, fig_agg

class pressureCodes(object):
    pressureCode1 = 0
    pressureCode2 = 0

class sensors(object):
    flowchan1 = 0
    flowchan2 = 0
    pressuresensor1 = 0
    pressuresensor2 = 0

class PIDobject(object):
    setPoint = 0
    kP = 0
    kI = 0
    kD = 0

port_4vm = 3

def write_read(link, TX, RX):
    sendSize, recSize = 0, 0
    sendSize = link.tx_obj(TX.pressureCode1, sendSize)
    link.send(sendSize)  # send value to Arduino

    while not link.available():  # wait until we get a value from Arduino
        if link.status < 0:
            if link.status == txfer.CRC_ERROR:
                print('ERROR: CRC_ERROR')
            elif link.status == txfer.PAYLOAD_ERROR:
                print('ERROR: PAYLOAD_ERROR')
            elif link.status == txfer.STOP_BYTE_ERROR:
                print('ERROR: STOP_BYTE_ERROR')
            else:
                print('ERROR: {}'.format(link.status))

    RX.flowchan1 = link.rx_obj(obj_type=float, start_pos=recSize)  # read response from Arduino
    recSize += txfer.STRUCT_FORMAT_LENGTHS['f']
    RX.pressuresensor1 = link.rx_obj(obj_type=int, start_pos=recSize)


def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    try:
        window_size = np.abs(int(window_size))
        order = np.abs(int(order))
    except ValueError:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order + 1)
    half_window = (window_size - 1) // 2
    # precompute coefficients
    b = np.mat([[k ** i for i in order_range] for k in range(-half_window, half_window + 1)])
    m = np.linalg.pinv(b).A[deriv] * rate ** deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs(y[1:half_window + 1][::-1] - y[0])
    lastvals = y[-1] + np.abs(y[-half_window - 1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve(m[::-1], y, mode='valid')

def fluidic_controller(eib_com, fourVM_addr, arduino_com, filename):
    eib = uProcess.CEIB()
    eib.InitConnection(eib_com)
    a = eib.New4VM(fourVM_addr)

    TX = pressureCodes
    RX = sensors
    link = txfer.SerialTransfer('COM'+str(arduino_com))
    link.open()
    time.sleep(2) # allow some time for the Arduino to completely reset
    print('Connected to device')

    # Initialize system with known pressure to get starting value resistance value
    pressureCode = 10
    # TX.pressureCode1 = 100 #Initial pressure [psi]
    # write_read(link, TX, RX)  #Update initial flow rate [ml/min]
    # try:
    #     R = TX.pressureCode1 / RX.flowchan1
    # except ZeroDivisionError:
    #     R = TX.pressureCode1

    control = PIDobject
    channels = ('1', '2', '3', '4', '5', '6', '7', '8')

    err = np.zeros(100)
    flow = np.zeros(100)
    pressure = np.zeros(100)
    pressureC = np.zeros(100)
    N = 2 # How many samples are used for PID control (History depth)

    window, ax, fig_agg = create_windows()

    log = open(str(filename)+'.csv', mode='w', newline = '')
    writer = csv.writer(log, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['Date', 'Time [s]', 'Flow Rate [uL/min]', 'Pressure [mbar]'])

    # wait to start
    pid_flag, chan_sel = False, False
    while True:
        event, values = window.read()
        if event in ('Update PID'):  #Button Press
            control.setPoint = int(values[0])
            control.kP, control.kI, control.kD = float(values[1]), float(values[2]), float(values[3])
            pid_flag = True
            print('kP:{} | kI:{} | kD:{}'.format(control.kP, control.kI, control.kD))
        elif event in channels:  #Button Press
            a.CmdSelect(port_4vm, int(event))  # Move channel 3 into position
            print('channel: {}'.format(int(event)))
            time.sleep(2.5)                    # wait until valve is in position (2.5s max actuation time)
            for e in channels:
                if e == event:
                    window.Element(e).Update(button_color=(('white', 'green')))
                else:
                    window.Element(e).Update(button_color=(('white', 'red'))) 
            chan_sel = True
        if event in ('Start Control') and (pid_flag or chan_sel):  #Button Press
            break 

    start = time.time() #Time at the beginning of control
    last_time = start
    current_time = datetime.now()
    while True:
        event, values = window.read(timeout=10)
        if event in ('Update PID'):
            control.setPoint = int(values[0])
            control.kP, control.kI, control.kD = float(values[1]), float(values[2]), float(values[3])
            print('kP:{} | kI:{} | kD:{}'.format(control.kP, control.kI, control.kD))
        elif event in channels:
            a.CmdSelect(port_4vm, int(event))
            print('channel: {}'.format(int(event)))
            time.sleep(2.5)
            for e in channels:
                if e == event:
                    window.Element(e).Update(button_color=(('white', 'green')))
                else:
                    window.Element(e).Update(button_color=(('white', 'red')))
        elif event in ('Exit', None):
            break

        curr_time = time.time()
        dt = curr_time - last_time

        err = np.roll(err,1) # Update error history
        flow = np.roll(flow, 1)  # Update flow history
        pressure = np.roll(pressure, 1)  # Update flow history
        pressureC = np.roll(pressureC, 1)  # Update flow history

        err[0] = control.setPoint - RX.flowchan1
        flow[0] = RX.flowchan1
        pressure[0] = RX.pressuresensor1

        pressureCode += float((control.kP*err[0] + control.kD*(err[0] - np.mean(err[1:N])) + control.kI*np.sum(err[1:N]))) # Update pressure [psi]
        TX.pressureCode1 = max(min(int(pressureCode), 1000), 0)
        #TX.pressureCode1 = control.setPoint

        pressureC[0] = TX.pressureCode1
        write_read(link, TX, RX)  # Write to DAC and read from flow sensor

        ax.cla()                    # clear the subplot
        ax.grid()                   # draw the grid
        #data_points = int(values['-SLIDER-DATAPOINTS-']) # draw this many data points (on next line)
        data_points = 50
        y = (pressure[:data_points])[::-1]
        yhat = savitzky_golay(y, 49, 4)
        ax.plot(range(data_points), (err[:data_points])[::-1],  color='purple', label="error")
        ax.plot(range(data_points), (flow[:data_points])[::-1], color='blue', label="flow sensor")
        ax.plot(range(data_points), yhat, color='red', label="pressure sensor")
        ax.plot(range(data_points), (pressureC[:data_points])[::-1], color='green', label="pressure code")
        # ax = subplot(1, 1, 1)
        # p1, = ax.plot([1, 2, 3], label="line 1")
        # p2, = ax.plot([3, 2, 1], label="line 2")
        # p3, = ax.plot([2, 3, 1], label="line 3")
        ax.set_xlabel('Readings')
        ax.set_ylabel('Values')
        handles, labels = ax.get_legend_handles_labels()
        # reverse the order
        ax.legend(handles, labels)
        fig_agg.draw()

        #print(1/(time.time()-last)) #print frequency
        #print(flow)
        time_stamp = current_time.timestamp()
        date_time = datetime.fromtimestamp(time_stamp)
        writer.writerow([date_time, time.time() - start, RX.flowchan1, RX.pressuresensor1])
        #print('sent: {} | received: f:{} p:{}'.format(TX.pressureCode1, RX.flowchan1, RX.pressuresensor1))

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
            filename = str(values[3])

            eib.InitConnection(eib_com) # COM port we just chose

            if eib.New4VM(fourVM_addr) is None:
                #print('Invalid COM or Address')
                break #continue
            else:
                break
    COM_select.close()
    eib.CloseConnection() #This connection will be re-made inside the fluidic_control process

    #controller = fluidic_controller(eib_com, fourVM_addr, arduino_com, filename)

    fluidic = Process(target = fluidic_controller, args = (eib_com, fourVM_addr, arduino_com, filename))
    fluidic.start()
    fluidic.join()
    print('joined')
    
if __name__ == '__main__':    
    main()