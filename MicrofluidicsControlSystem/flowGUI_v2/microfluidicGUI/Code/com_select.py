import PySimpleGUI as sg #Install PysimpleGUI
from pathlib import Path  # core python module
from serial_connection import*
import time #Install time
#import uProcess_x64
import serial.tools.list_ports


def com_windows():
    SETTINGS_PATH = Path.cwd()

    settings = sg.UserSettings(
        path=SETTINGS_PATH, filename="settings.ini", use_config_file=True, convert_bools_and_none=True
    )

    eib_com = settings["COM"]["eib_com"]
    arduino_com = settings["COM"]["arduino_com"]
    fourVM_addr = settings["COM"]["fourVM_addr"]

    layout = [
        [sg.Text('Valve Control', size=(40, 1),
                 justification='center', font='Helvetica 20')],
        [sg.Text('EIB200 COM port', size=(15, 1), font='Helvetica 12'), sg.InputText(eib_com)],
        [sg.Text('Arduino1 COM port', size=(15, 1), font='Helvetica 12'), sg.InputText(arduino_com)],
        [sg.Text('4VM Address', size=(15, 1), font='Helvetica 12'), sg.InputText(fourVM_addr)],

        [sg.Canvas(key='controls_cv')],
        [sg.Canvas(size=(650, 30), key='-CANVAS-')],

        [sg.Button('Submit', size=(10, 1), font='Helvetica 14'),
         sg.Button('List Ports', size=(10, 1), font='Helvetica 14')]

    ]

    # create the form and show it without the plot
    window = sg.Window('COM Select',
                       layout, finalize=True, size=(480,200))

    canvas_elem = window['-CANVAS-']
    canvas = canvas_elem.TKCanvas

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, "Exit"):
            break

        elif event in "List Ports":
            myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
            sg.Popup("COM Port list", myports)

        elif event in ('Submit', None):
            #eib = uProcess_x64.CEIB()
            #time.sleep(2)

            settings["COM"]["eib_com"] = int(values[0])
            settings["COM"]["arduino_com"] = int(values[1])
            settings["COM"]["fourVM_addr"] = int(values[2])

            #print(output) #Test output

            #eib.InitConnection(eib_com)  # COM port we just chose



            """Check arduino correct
            if link_arduino() is False:
                continue
            """

            break  # for testing if reads input into main function

            """
            if eib.New4VM(fourVM_addr) is None:
            
                sg.popup_error('Invalid COM or Address for Labsmith',title='Invalid COM or Address', button_color='tomato')
                print('Invalid COM or Address')
                continue
            else:
                break
            """

    generate_csv() #generate csv
    #eib.CloseConnection()
    window.close()

