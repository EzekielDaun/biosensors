import PySimpleGUI as sg
import time
import uProcess_x64

eib_com = 6
arduino_com = 4
fourVM_addr = 10

def com_windows():
    eib = uProcess_x64.CEIB()
    time.sleep(2)
    output = []
    layout = [
        [sg.Text('Valve Control', size=(40, 1),
                 justification='center', font='Helvetica 20')],
        [sg.Text('EIB200 COM port', size=(15, 1), font='Helvetica 12'), sg.InputText('6')],
        [sg.Text('Arduino1 COM port', size=(15, 1), font='Helvetica 12'), sg.InputText('4')],
        [sg.Text('4VM Adress', size=(15, 1), font='Helvetica 12'), sg.InputText('10')],

        [sg.Canvas(key='controls_cv')],
        [sg.Canvas(size=(650, 30), key='-CANVAS-')],

        [sg.Button('Submit', size=(10, 1), pad=((280, 0), 3), font='Helvetica 14')]
    ]

    # create the form and show it without the plot
    window = sg.Window('Start Screen',
                       layout, finalize=True)

    canvas_elem = window['-CANVAS-']
    canvas = canvas_elem.TKCanvas

    while True:
        event, values = window.read()

        if event in ('Submit', None):
            global eib_com
            global arduino_com
            global fourVM_addr

            eib_com = int(values[0])
            arduino_com = int(values[1])
            fourVM_addr = int(values[2])


            #output.append(eib_com)
            #output.append(arduino_com)
            #output.append(fourVM_addr)


            #print(output) #Test output

            eib.InitConnection(eib_com)  # COM port we just chose


            #break # for testing if reads input into main function

            if eib.New4VM(fourVM_addr) is None:
                print('Invalid COM or Address')
                continue
            else:
                break

    eib.CloseConnection()  # This connection will be re-made inside the fluidic_control process
    window.close()

