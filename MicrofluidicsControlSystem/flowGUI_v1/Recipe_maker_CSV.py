import os.path
import PySimpleGUI as sg
import csv
from datetime import datetime

#creates csv files
def generate_csv(csv_name, headings, values):

    file = open(csv_name, 'w', encoding='UTF8', newline='')
    writer = csv.writer(file)

    # write the header
    writer.writerow(headings)

    for row in range(30):
        current_row = []
        for column in range(8):
            current_row.append(values[row, column])
        writer.writerow(current_row)

    file.close()

#Clear table and renumbers lines
def clear_all(window):
    line = 0

    for row in range(20):
        line = line + 1

        for column in range(8):
            if column==0:
                window[(row, column)].update(line)

            else:
                window[(row, column)].update('')

def file_already_exists(csv_name):
    data = []
    header_list = []
    title = (csv_name + " already exists")
    flag = 0

    layout_error = [
            [sg.T(csv_name + " already exists")],
            [sg.B('Error', button_color="tomato"),
             sg.B("Replace"),
             sg.B("View")]]

    error_window = sg.Window(title, layout_error, modal=True)

    while True:
        event, values = error_window.read()
        if event in (sg.WIN_CLOSED, 'Error'):
            break
        elif event == "Replace":
            flag = True
            break

        elif event == "View":
            with open(csv_name, "r") as infile:
                reader = csv.reader(infile)

                header_list = next(reader)
                try:
                    data = list(reader)  # read everything else into a list of rows

                except:
                    sg.popup_error('Error reading file')
                    return
        sg.set_options(element_padding=(0, 0))

        error_window.close()
        layout = [[sg.Table(values=data, headings=headings, max_col_width=25,
                        auto_size_columns=True,
                        # display_row_numbers=True,
                        justification='right',
                        num_rows=20,
                        alternating_row_color=sg.theme_button_color()[1],
                        expand_x=True,
                        expand_y=True,
                        )],
                            [sg.B('Error', button_color="tomato"),
                            sg.B("Replace")]]

        window = sg.Window('Table', layout, grab_anywhere=False)
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Error'):
            window.close()

        elif event == "Replace":
            flag = True
            window.close()


        window.close()

    error_window.close()
    return flag

csv_name = ''
now = datetime.now()
today = now.strftime("%Y-%m-%d")

# ------ Menu Definition ------ #
menu_def = [["Menu",["Help", "About", "Settings", "Exit"]]]

# ------ GUI Definition ------ #
headings = ['Line', 'Channel', 'Operation', 'Time', 'Flow Rate (uL/min)', 'Kp','Ki','Kd']
header = [[sg.MenubarCustom(menu_def, tearoff=False)],
        [sg.T('File Name:')],[sg.I('Recipe Name', s=15, key="-Name-", pad=(0,5)),sg.T("_",pad=(0,0)),
        sg.I('Your_name_here', s=15, key="-Author-", pad=(0,0)),sg.T("_", pad=(0,0)),
        sg.I(today+' ',s=11, key="-Date-", pad=(0,0)),sg.T(".csv", pad=(0,0))],

        sg.T('Line', pad=(0, 0), size=(15,1), justification='c'),
        sg.T('Channel', pad=(0, 0), size=(15,1), justification='c'),
        sg.T('Operation', pad=(0, 0), size=(15,1), justification='c'),
        sg.T('Time', pad=(0, 0), size=(15,1), justification='c'),
        sg.T('Flow Rate (uL/min)', pad=(0, 0), size=(30,1), justification='c'),
        sg.T('Kp', pad=(0, 0), size=(5,1), justification='c'),
        sg.T('Ki', pad=(0, 0), size=(5,1), justification='c'),
        sg.T('Kd', pad=(0, 0), size=(5,1), justification='c'),

    ]

layout = [header]

line = 0

for row in range(0,30):
    line = line + 1
    layout.append([
        sg.I(line,size=(15, 1), pad=(0, 0), key=(row, 0)),
        sg.I(size=(15,1), pad=(0, 0), key=(row, 1)),
        sg.I(size=(15,1), pad=(0, 0), key=(row, 2)),
        sg.I(size=(15,1), pad=(0, 0), key=(row, 3)),
        sg.I(size=(30, 1), pad=(0, 0), key=(row, 4)),
        sg.I(size=(5, 1), pad=(0, 0), key=(row, 5)),
        sg.I(size=(5, 1), pad=(0, 0), key=(row, 6)),
        sg.I(size=(5, 1), pad=(0, 0), key=(row, 7))
    ])

layout.append([sg.B('Exit',button_color="tomato"),sg.B("Generate CSV"), sg.B("Clear")])

window = sg.Window('Recipe Maker', layout, font='Courier 12', use_custom_titlebar=True, size=(775,675))


while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break

    elif event == 'Generate CSV':
        #if statements determine if all request information has been filled out
        if not values['-Name-']:
            sg.Popup("Sorry can't save recipe without a name")

        if not values['-Author-']:
            sg.Popup("Sorry can't save recipe without an Author")

        if not values['-Date-']:
            sg.Popup("Sorry can't save recipe without an Author")

        #Create name for csv file
        if values['-Name-'] and values['-Author-'] and values['-Date-']:
            csv_name = values['-Name-']+"_"+values['-Author-']+"_"+values['-Date-']+".csv"

            if os.path.isfile(csv_name):
                    if file_already_exists(csv_name):
                        generate_csv(csv_name, headings, values)

                #Test if statement
                #sg.popup_error(csv_name+" already exists")

            else:
                generate_csv(csv_name, headings, values)


    elif event == 'Clear':
        values = []
        clear_all(window)

window.close()