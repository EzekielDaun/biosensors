import datetime
import random
import sys
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import Signal, QObject, QRunnable, QThreadPool, Slot
import json
import logging
from MultiSweep.parameterTab import ParamTableWindow
from MultiSweep.multi_sweep_v2 import MultiSweep
import sys
import traceback
import pprint
from fineAlign_wN77 import fineAlign
import time
import os
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from MultiSweep.ui.multi_run import Ui_GroupBox
from scipy.io import loadmat
import pyqtgraph as pg
import numpy as np
from numpy.typing import NDArray
from itertools import cycle

class RunWindow(QtWidgets.QGroupBox, Ui_GroupBox):
    def __init__(self, multisweep):
        super(RunWindow, self).__init__()
        self.setupUi(self)

        self.multisweep = multisweep
        self.graphs = MplCanvas()
        self.toolbar = NavigationToolbar(self.graphs, self)

        self.add_graph(self.toolbar)
        self.add_graph(self.graphs)

        self.fa_data = None
        self.temp_data = []
        self.temp_x_data = []
        self.fa_lines = []
        self.sweep_lines = []

    def add_graph(self, graph):
        self.graphLayout.addWidget(graph)

    def fa_warning(self, sweep, res):
        self.fineAlignLog.moveCursor(QtGui.QTextCursor.End)
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        if res == 0:
            res = 'FineAlign Succeeded'
        else:
            res = 'FineAlign Failed'

        self.fineAlignLog.insertPlainText('{} Sweep #{} {}\n'.format(current_time, sweep, res))
        self.fineAlignLog.moveCursor(QtGui.QTextCursor.End)

    def update_graphs(self, res, fa_power, wavelength, power, temp, abs_sweep, fa=True):

        if self.multisweep.tec1 is not None:
            self.update_temp_graph(temp, abs_sweep)

        self.update_sweep_graph(abs_sweep, power, wavelength)

        if fa:
            self.fa_warning(abs_sweep, res)
            self.update_fa_graph(fa_power)

        self.graphs.fig.canvas.draw()

    def update_sweep_graph(self, abs_sweep, power, wavelength):
        power = np.array(power).transpose()

        if abs_sweep == 1:
            self.sweep_lines = []
            for i in range(len(power)):
                sweep_line, = self.graphs.axSweep.plot([],[], label='Power{}'.format(i+1), color=self.graphs.color_map[i])
                self.sweep_lines.append(sweep_line)

        self.graphs.axSweep.legend(loc='upper left')
        self.graphs.axSweep.relim()
        self.graphs.axSweep.autoscale_view(True,True,True)

        wavelength = np.array(wavelength)

        for index, i in enumerate(self.graphs.axSweep.get_lines()):
            i.set_data(wavelength * 1e9, power[index])

    def update_fa_graph(self, log_power):

        if self.fa_data is None:
            self.fa_data = [list() for i in range(len(list(log_power.values())))]

            self.fa_lines = []

            for det, power in log_power.items():
                if 'N77' in det:
                    power_num = power.split('_')[1] + len(self.mulitsweep.laser.getSlotInfo())
                else:
                    power_num = int(det)

                self.fa_line, = self.graphs.axFA.plot([], [], label='Power{}'.format(int(det)), color=self.graphs.color_map[power_num-1])
                self.fa_lines.append(self.fa_line)

        if len(self.fa_data) != 0:
            self.graphs.axFA.legend(loc='upper left')
            self.x_data = [i for i in range(len(self.fa_data[0])+1)]
            self.graphs.axFA.relim()
            self.graphs.axFA.autoscale_view(True,True,True)

            for i, val in enumerate(self.fa_data):
                val.append(list(log_power.values())[i])
                line = self.fa_lines[i]
                line.set_data(self.x_data, val)

    def update_temp_graph(self, temp, scan):
        self.temp_data.append(temp)
        self.temp_x_data.append(scan)

        self.graphs.axTemp.relim()
        self.graphs.axTemp.autoscale_view(True,True,True)
        self.graphs.temp_plot.set_data(self.temp_x_data, self.temp_data)

    def restart_graph(self):
        self.fa_data = None
        self.temp_data = []
        self.temp_x_data = []

        self.graphs.restart_graph(self.fa_lines, self.sweep_lines)

    def read_mat(self, file_path=r"C:/Users/piram/Downloads/2022-08-18_OOC_Trial3/2022-08-18_OOC_Trial3/bulkRI/laser_sweep_2.mat"):

        mat = loadmat(file_path)
        power = np.array(mat["power"]).transpose()
        wavelengths = np.array(mat["wavelength"][0])
        if power.shape[1] != wavelengths.shape[0]:
            raise RuntimeError("Number of wavelengths and powers do not match")

        return (power, wavelengths)


class MplCanvas(FigureCanvas):
    color_map = ['royalblue', 'green', 'red', 'c', 'm', 'y', 'k', 'orange', 'blue', 'green']

    def __init__(self, parent=None, width=5, height=4, dpi=100, title='None', yaxis=None, xaxis=None):
        self.fig = plt.figure()

        self.axTemp = self.fig.add_subplot(221, title='Temperature')
        self.axFA = self.fig.add_subplot(223, title='FineAlignment Power')
        self.axSweep = self.fig.add_subplot(1,2,2, title='Latest Sweep')

        self.axTemp.set_xlabel('Sweep Number')
        self.axTemp.set_ylabel('Temperature [C]')

        self.axFA.set_xlabel('Sweep Number')
        self.axFA.set_ylabel('Power (dBm)')

        self.axSweep.set_xlabel('Wavelength (nm)')
        self.axSweep.set_ylabel('Power (dBm)')

        self.temp_plot, = self.axTemp.plot([], [])
        self.fa_plot, = self.axFA.plot([], [])
        self.sweep_plot,= self.axSweep.plot([],[])

        plt.tight_layout()
        plt.subplots_adjust(top=0.921,
                            bottom=0.123,
                            left=0.076,
                            right=0.987,
                            hspace=0.543,
                            wspace=0.182)

        plt.close()
        super(MplCanvas, self).__init__(self.fig)

    def restart_graph(self, fa_lines, sweep_lines):
        for line in self.axSweep.get_lines():
            line.remove()

        for line in self.axFA.get_lines():
            line.remove()

        self.temp_plot.set_data([],[])

        self.fig.canvas.draw()
