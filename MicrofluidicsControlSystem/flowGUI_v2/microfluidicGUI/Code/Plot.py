#!/usr/bin/env python
import PySimpleGUI as sg
from random import randint
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, FigureCanvasAgg
from matplotlib.figure import Figure
from com_select import*
import numpy as np
import time
from pySerialTransfer import pySerialTransfer as txfer
import csv
from multiprocessing import Process

csv_name = "Data_Log"
number_of_datapoints = 20

""""
def data_reader(rows_to_read, number_of_rows):
    
    with open("test.csv", "r") as file:
        reader = csv.reader(file, delimiter=" ")

        for row
        #for i, line in enumerate(reader):
"""


def draw_figure(canvas, figure, loc=(0, 0)):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def main():
    #com_windows()
    list_channel_1 = ["Reservoir 1","Reservoir 2", "Reservoir 3", "Reservoir 4", "Reservoir 5",  "Reservoir 6"]

    NUM_DATAPOINTS = 10000
    # define the form layout

    # ------ Menu Definition ------ #
    menu_def = [["Menu", ["Help", "Settings", "Serial Port", "About", "Exit"]]]

    # ------ GUI Definition ------ #

    #------- Channel 1 ------#
    input_layout_1 = [[sg.Text("Pressure PSI"),sg.Input(size=(14,1)),sg.Button('Change', size=(15, 1))],
                      [sg.Text("Reservoir      "),sg.Combo(list_channel_1, key='Favorite Colour'), sg.Button('Change', size=(15, 1))],
                      [sg.Text("Flow uL/min  "),sg.Input(size=(14,1)),sg.Button('Change', size=(15, 1))]]

    channel_1_interface = [[sg.Canvas(size=(600, 850), key='-CANVAS1-'),
                            sg.Frame("Channel 1 Inputs/Outputs", input_layout_1)]]

    #------- Channel 2 ------#
    input_layout_2 = [[sg.Text("Pressure PSI"), sg.Input(size=(14,1)), sg.Button('Change', size=(15, 1))],
                      [sg.Text("Reservoir      "), sg.Combo(list_channel_1, key='Favorite Colour'), sg.Button('Change', size=(15, 1))],
                      [sg.Text("Flow uL/min  "), sg.Input(size=(14,1)), sg.Button('Change', size=(15, 1))]]

    channel_2_interface = [[sg.Canvas(size=(600, 850), key='-CANVAS2-'),
                            sg.Frame("Channel 2 Inputs/Outputs", input_layout_2)]]

    channel_1_and_2 = [[sg.Frame("Channel 1", channel_1_interface)],
                       [sg.Frame("Channel 2", channel_2_interface)]]

    column = sg.Column(channel_1_and_2, scrollable=True, vertical_scroll_only=True, size=(1000,500))

    layout = [[sg.MenubarCustom(menu_def, tearoff=False)],
              [column]]

    # create the form and show it without the plot
    window = sg.Window('Flowgui',
                layout, finalize=True)

    #Making Plot
    canvas_elem_1 = window['-CANVAS1-']
    canvas_elem_2 = window['-CANVAS2-']

    canvas_1 = canvas_elem_1.TKCanvas
    canvas_2 = canvas_elem_2.TKCanvas

    # draw the initial plot in the window
    #Channel 1
    fig_1 = Figure()
    ax_1 = fig_1.add_subplot(111)
    ax2_1 = ax_1.twinx()

    #Channel 2
    fig_2 = Figure()
    ax_2 = fig_2.add_subplot(111)
    ax2_2 = ax_2.twinx()


    # Add axis
    #Channel 1
    ax_1.set_xlabel("Time (s)")
    ax_1.set_ylabel("Flow (uL/Min)")
    ax2_1.set_ylabel("Pressure (PSI)", labelpad=-5)

    #Channel 2
    ax_2.set_xlabel("Time (s)")
    ax_2.set_ylabel("Flow (uL/Min)")
    ax2_2.set_ylabel("Pressure (PSI)", labelpad=-5)


    ax_1.grid()
    ax_2.grid()
    fig_agg_1 = draw_figure(canvas_1, fig_1)
    fig_agg2 = draw_figure(canvas_2, fig_2)

    # make a bunch of random data points
    dpts = [0 for x in range(NUM_DATAPOINTS)]
    rdd = [0 for x in range(NUM_DATAPOINTS)]


    for i in range(len(dpts)):

        event, values = window.read(timeout=10)
        if event in ('Exit', None):
            exit(69)

        if event == "Serial Port":
            com_windows()

        """
        file = open(csv_name+'.csv', 'w', encoding='UTF8', newline='')
        row_count = sum(1 for row in file)

        if number_of_datapoints>row_count:
            data = data_reader(row_count,row_count)

        else :
            data = data_reader(number_of_datapoints,row_count)

        """

        # clear the subplot
        ax_1.cla()
        ax2_1.cla()

        ax_2.cla()
        ax2_2.cla()


        # Add axis
        ax_1.set_xlabel("Time (s)")
        ax_1.set_ylabel("Flow (uL/Min)")
        ax2_1.set_ylabel("Pressure (PSI)", labelpad=-5)

        ax_2.set_xlabel("Time (s)")
        ax_2.set_ylabel("Flow (uL/Min)")
        ax2_2.set_ylabel("Pressure (PSI)", labelpad=-5)


        ax_1.grid()                   # draw the grid
        data_points = 100 # draw this many data points (on next line)
        ax_1.plot(range(data_points), dpts[i:i+data_points],  color='purple')
        ax2_1.plot(range(data_points), rdd[i:i+data_points],  color='yellow')
        fig_agg_1.draw()

        ax_2.grid()  # draw the grid
        data_points = 100  # draw this many data points (on next line)
        ax_2.plot(range(data_points), dpts[i:i + data_points], color='purple')
        ax2_2.plot(range(data_points), rdd[i:i + data_points], color='yellow')
        fig_agg2.draw()



    window.close()

if __name__ == '__main__':
    main()