## This was originally written by Michael Caverley in 2015
## Code has been modified by Eric Lyall in December 2020 ericlyall1428@gmail.com
## It was modified for the 8164A laser set-up at the Life Sciences Institute at UBC. The laser has 2 active detectors.
## An option for a periodic fine align is/has been added
## 2021-03-31 S. Grist added saving the timestamp associated with each sweep to a CSV.
import logging
import random
from typing import Optional, Union
from PySide6 import QtWidgets, QtGui
import os
import time
import csv
import toml
from shutil import copyfile
import psutil
import pyvisa as visa
import numpy as np
from matplotlib import pyplot as plt
import matplotlib
from scipy.io import savemat
import json
from SRS_LDC501_instr import SRS_LDC501
from hp816x_instr import hp816x
from hp816x_N77Det_instr import hp816x_N77Det
from fineAlign_wN77 import fineAlign
from CorvusEco import CorvusEcoClass
from scipy.io import loadmat

import numpy as np
from numpy.typing import NDArray

import logging

logger = logging.getLogger(__name__)


class MultiSweep:
    speed_map = dict(
        [
            ("0.5", "0.5nm"),
            ("5", "5nm"),
            ("10", "10nm"),
            ("20", "20nm"),
            ("40", "40nm"),
            ("80", "80nm"),
            ("auto", "auto"),
        ]
    )

    speedMap_rev = dict((v, k) for k, v in speed_map.items())

    def __init__(self):
        self.f = open("MultiSweep/multisweep.json")
        self.config = json.load(self.f)

        self.fineAlign = None
        self.laser = None
        self.stage = None
        self.tec1 = None
        self.active_instr = []
        self.confirm_instr = []
        self.segment_num = None
        self.is_N77 = None
        self.is_OBand = None
        self.is_time = None

        # file names
        self.current_dir = os.getcwd()
        self.timeSteps_csv = "timeSteps.tmp"
        self.timeSteps_copy = "timeSteps.csv"
        self.fineAlignment_csv = "fineAlignment.tmp"
        self.fineAlignment_copy = "fineAlignment.csv"

    def calc_slice_indices(self, wavelength, guess_wavelength, range):
        st_index = int(
            (guess_wavelength - range - wavelength[0])
            / (wavelength[len(wavelength) - 1] - wavelength[0])
            * len(wavelength)
        )
        end_index = int(
            (guess_wavelength + range - wavelength[0])
            / (wavelength[len(wavelength) - 1] - wavelength[0])
            * len(wavelength)
        )
        return st_index, end_index

    def find_optimum_wavelength(self, matdict, guess_wavelength=1560e-9, range=2e-9):
        """
        Find a good wavelength to fine align to by searching for the highest combined power readings within +- range
        :param matdict: matdict to read power readings from
        :param guess_wavelength: wavelength to center the range around
        :param range: range to search for highest combined readings
        :return: optimal wavelength
        """

        wavelength = np.array(
            matdict["wavelength"]
        )  # retrieving the wavelengths used during the sweep (nm)
        power1 = np.array(
            matdict["power1"]
        )  # retrieving the values for the power1 channel. (dBm)
        power2 = np.array(
            matdict["power2"]
        )  # retrieving the values for the power2 channel. (dBm)
        # Finding the range (by array index) to look for max combined power
        st_index, end_index = self.calc_slice_indices(
            wavelength, guess_wavelength, range
        )
        # Creating an array with added power, tha only looks at the previously specified range.
        combo_power = np.add(power1, power2)[st_index:end_index]

        max_index = (
            combo_power.argmax() + st_index
        )  # returns the first incidence of the maximum value.

        optimum_wavelength = wavelength[max_index]

        return optimum_wavelength

    def run_fine_align(self, laser, stage, optimum_wavelength=1560e-9):
        """
        Runs a fine align, moving the stage around to optimize power readings
        :param laser: A connected laser
        :param stage: A connected stage
        :param optimum_wavelength: The wavelength you would like to do the fine align around. This doesn't actually do
        anything yet, as teh fineAlign wavelength gets re-defined in the fineAlign code.
        :return:
        """
        laser.setAutorangeAll()

        if self.is_N77:
            laser.N77setAutorangeAll()
        laser.setTLSWavelength(
            optimum_wavelength
        )  # Setting the laser to optimum wavelength before alignment
        print("Did the wavelength change to: ", optimum_wavelength * 1e9)

        self.fineAlign.wavelength = optimum_wavelength

        power_before = {}
        power_after = {}

        detectorLog = self.config["logging"]["HP816x"]
        N77log = self.config["logging"]["N77"]

        print("Detectors being logged: {}".format(detectorLog))

        for det in detectorLog:
            if det > len(self.fineAlign.laser.pwmSlotMap):
                print("Detector {} out of range".format(det))
            else:
                detSlot = self.fineAlign.laser.pwmSlotMap[det - 1][0]
                detChan = self.fineAlign.laser.pwmSlotMap[det - 1][1]
                power = self.fineAlign.laser.readPWM(detSlot, detChan)
                power_before[str(det)] = power
                print("Detector", det, "Before fine align Power = ", power, " dBm")

        if self.is_N77:
            for det in N77log:
                if det > len(self.fineAlign.laser.N77pwmSlotMap):
                    print("Detector {} out of range".format(det))
                else:
                    detSlot = self.fineAlign.laser.N77pwmSlotMap[det - 1][0]
                    detChan = self.fineAlign.laser.N77pwmSlotMap[det - 1][1]
                    power = self.fineAlign.laser.N77readPWM(detSlot, detChan)
                    power_before["N77_" + str(det)] = power
                    print(
                        "N77 Detector",
                        self.laser.N77pwmSlotIndex[det - 1],
                        "Before fine align Power = ",
                        power,
                        " dBm",
                    )

        print("Starting fine align...")
        print("FineAligning to detectors: {}".format(self.fineAlign.detectorPriority))

        res = (
            self.fineAlign.doFineAlign()
        )  # Doing the actual fine Align - this is currently automatically set to 1550

        # Getting power after fine alignment
        for det in detectorLog:
            if det > len(self.fineAlign.laser.pwmSlotMap):
                print("Detector {} out of range".format(det))
            else:
                detSlot = self.fineAlign.laser.pwmSlotMap[det - 1][0]
                detChan = self.fineAlign.laser.pwmSlotMap[det - 1][1]
                power = self.fineAlign.laser.readPWM(detSlot, detChan)
                power_after[str(det)] = power
                print("Detector", det, "After fine align Power = ", power)

        if self.is_N77:
            for det in N77log:
                if det > len(self.fineAlign.laser.N77pwmSlotMap):
                    print("Detector {} out of range".format(det))
                else:
                    detSlot = self.fineAlign.laser.N77pwmSlotMap[det - 1][0]
                    detChan = self.fineAlign.laser.N77pwmSlotMap[det - 1][1]
                    power = self.fineAlign.laser.N77readPWM(detSlot, detChan)
                    power_after["N77_" + str(det)] = power
                    print("N77 Detector", det, "After fine align Power = ", power)

        return power_before, power_after, res

    def run_fine_align_test(self):
        power_before = {}
        power_after = {}

        detectorLog = self.config["logging"]["HP816x"]
        N77log = self.config["logging"]["N77"]

        for det in detectorLog:
            power = random.uniform(-30, -60)
            power_before[str(det)] = power
            print("Detector", det, "Before fine align Power = ", power)

        if self.is_N77:
            power = random.uniform(-30, -60)
            power_before["N77_" + str(det)] = power
            print(
                "N77 Detector",
                self.laser.N77pwmSlotIndex[det - 1],
                "Before fine align Power = ",
                power,
            )

        print("Starting fine align...")

        res = 0

        # Getting power after fine alignment
        for det in detectorLog:
            power = random.uniform(-30, -60)
            power_after[str(det)] = power
            print("Detector", det, "After fine align Power = ", power)

        if self.is_N77:
            power = random.uniform(-30, -60)
            power_after["N77_" + str(det)] = power
            print("N77 Detector", det, "After fine align Power = ", power)

        return power_before, power_after, res

    def turnon_laser(self):
        start_wl = self.config["default"]["startWavelength"]
        stop_wl = self.config["default"]["endWavelength"]

        # Setting up part 1 of sweep parameters
        central_wavelength = (start_wl + stop_wl) / 2
        central_wavelength = central_wavelength * 1e-9
        sweep_range = ((stop_wl - start_wl) / 2) * 1e-9

        time.sleep(6.0)  # gives the laser some time to connect
        self.laser.setTLSState("on")

        # turn on laser
        self.laser.setAutorangeAll()
        if self.is_N77:
            self.laser.N77setAutorangeAll()
        self.laser.setTLSWavelength(central_wavelength)
        self.laser.setPWMPowerUnit(1, 0, "dBm")

        self.laser.sweepStartWvl = (
            central_wavelength - sweep_range
        )  # set starting wavelength
        self.laser.sweepStopWvl = (
            central_wavelength + sweep_range
        )  # set stopping wavelength
        self.laser.sweepStepWvl = 0.008 * 1e-9  # step size
        self.laser.sweepNumScans = 1  # the laser can average out over 1, 2 or 3 scans.
        self.laser.sweepSpeed = "5nm"  # '5nm' is the only sweep speed that currently works. The laser is capable of '40nm' and '.5nm',
        # but this software is not
        self.laser.sweepLaserOutput = "highpower"
        self.laser.sweepPower = 0
        self.laser.sweepInitialRange = -20

        return True

    def turnon_TEC(self):
        self.tec1.tecON()
        self.tec1.setTemperature(int(self.config["default"]["tec1Temp"]))

    def turnon_LDC(self):
        self.tec1.setLDcurrent()
        self.tec1.LDturnON()

    def disconnect_instr(self, disconnect=False):
        for instr in self.active_instr:
            if instr.isTEC:
                instr.setTemperature(int(self.config["default"]["tec1Temp"]))
            if instr.isLaser:
                instr.setTLSState("off")

            if disconnect:
                instr.disconnect()

    def set_configurations(self, i=None):
        """
        Set Configurations for each segment of the experiment
        @param i: Segment Number
        """

        # Setting up part 1 of sweep parameters
        central_wavelength = ((self.start_wl[i] + self.end_wl[i]) / 2) * 1e-9
        sweep_range = ((self.end_wl[i] - self.start_wl[i]) / 2) * 1e-9
        sweep_power = self.config["segment"]["laserIntensity"][i]

        self.laser.sweepStartWvl = (
            central_wavelength - sweep_range
        )  # starting wavelength
        self.laser.sweepStopWvl = (
            central_wavelength + sweep_range
        )  # stopping wavelength
        self.laser.sweepStepWvl = (
            self.config["segment"]["sweepStep"][i] * 1e-9
        )  # step size
        self.laser.sweepNumScans = (
            1  # The laser can average out over 1, 2 or 3 scans - UNSURE
        )
        self.laser.sweepSpeed = self.speed_map[self.sweep_speed[i]]

        self.laser.sweepLaserOutput = "highpower"
        self.laser.sweepPower = sweep_power  # Always set this to 0
        self.laser.sweepInitialRange = -20

        # TEC parameters
        if self.tec1:
            self.tec1.setTemperature(self.tec1_temp[i])
            print("Successfully set TEC1 temperature")

    def initial_sweep(self, param_dict=None):
        """
        Run initial sweep of the laser
        """

        try:
            if param_dict is False:
                self.laser.sweepStartWvl = self.start_wl[0] * 1e-9
                self.laser.sweepStopWvl = self.end_wl[0] * 1e-9
                self.laser.sweepStepWvl = self.config["segment"]["sweepStep"][0] * 1e-9
                self.laser.sweepSpeed = self.speed_map[
                    self.config["segment"]["sweepSpeed"][0]
                ]

            start_time = time.time()

            (wavelength, power) = self.laser.sweep()
            print("Sweep time = ", (time.time() - start_time), "seconds")

        except Exception as e:
            logging.error(e)
            raise

        # Change power units to dBm after sweep
        self.laser.setAutorangeAll()
        if self.is_N77:
            self.laser.N77setAutorangeAll()

        # Getting the power channels from the sweep output
        power_chan1 = power[:, 0]
        power_chan2 = power[:, 1]
        if self.is_N77:
            power_chan3 = power[
                :, 2
            ]  # Seems like we could have multiple channels, this could be useful for future layouts.
            power_chan4 = power[:, 3]
            power_chan5 = power[:, 4]
            power_chan6 = power[:, 5]
            power_chan7 = power[:, 6]
            power_chan8 = power[:, 7]
            if self.is_OBand:
                power_chan9 = power[:, 8]
                power_chan10 = power[:, 9]

        print("Plotting first sweep")

        return power, wavelength

        # Plot the initial sweep:
        plt.figure()
        plt.plot(wavelength * 1e9, power_chan1, "r", label="Power1")
        plt.plot(wavelength * 1e9, power_chan2, "g", label="Power2")
        if self.is_N77:
            plt.plot(wavelength * 1e9, power_chan3, "b", label="Power3")
            plt.plot(wavelength * 1e9, power_chan4, "c", label="Power4")
            plt.plot(wavelength * 1e9, power_chan5, "m", label="Power5")
            plt.plot(wavelength * 1e9, power_chan6, "y", label="Power6")
            plt.plot(wavelength * 1e9, power_chan7, "k", label="Power7")
            plt.plot(wavelength * 1e9, power_chan8, "r", label="Power8")
            if self.is_OBand:
                plt.plot(wavelength * 1e9, power_chan9, "g", label="Power9")
                plt.plot(wavelength * 1e9, power_chan10, "b", label="Power10")

        plt.xlabel("Wavelength (nm)")
        plt.ylabel("Power (dBm)")
        plt.legend()
        plt.show()
        logging.info(
            "Finish initial sweep. Click resume to continue the experiment. Else, stop the experiment and start again"
        )

    def multiple_sweeps(self, i, j, abs_sweep, total_time, abs_time):
        """
        Perform one laser sweep and fineAlign for specified intervals. save scans into specified files
        @param i: Segment number
        @param j: Sweep/Scan Number
        @param seg_time: Start time of the segment or the experiment
        @param total_time: Total time of the experiments
        @return:
        """

        res, fa_power, temperature_log = None, {}, None
        print("Starting Sweep Number: {}. Total Sweeps: {}".format(j, abs_sweep))

        # get elapsed time
        t1 = time.time()
        total_time = t1 - total_time
        abs_time = t1 - abs_time

        matFilename = "laser_sweep_%d.mat" % j

        if self.tec1:
            temperature_log = self.tec1.getTemperature()

        try:
            # sweep laser
            (wavelength, power) = self.laser.sweep()

        except Exception as e:
            logging.error(str(e))

        sweep_time = time.time() - t1

        with open(os.path.join(self.path[i], self.timeSteps_csv), "a", newline="") as f:
            writer = csv.writer(f)
            if self.tec1:
                writer.writerow(
                    [i + 1]
                    + [j]
                    + [total_time]
                    + [matFilename]
                    + [sweep_time]
                    + [temperature_log]
                )
            else:
                writer.writerow(
                    [i + 1] + [j] + [total_time] + [matFilename] + [sweep_time]
                )

        try:  # Copy file to EXCEL for reading
            copyfile(
                os.path.join(self.path[i], self.timeSteps_csv),
                os.path.join(self.path[i], self.timeSteps_copy),
            )
        except:
            print(
                "Read file opened. Please close the file to update fineAlignment.csv data"
            )

        power_chan1 = power[:, 0]
        power_chan2 = power[:, 1]

        if self.is_N77:
            power_chan3 = power[:, 2]
            power_chan4 = power[:, 3]
            power_chan5 = power[:, 4]
            power_chan6 = power[:, 5]
            power_chan7 = power[:, 6]
            power_chan8 = power[:, 7]
            if self.is_OBand:
                power_chan9 = power[:, 8]
                power_chan10 = power[:, 9]

        matDict = dict()

        matDict["wavelength"] = wavelength
        matDict["power"] = power
        matDict["power1"] = power_chan1
        matDict["power2"] = power_chan2

        if self.is_N77:
            matDict["power3"] = power_chan3
            matDict["power4"] = power_chan4
            matDict["power5"] = power_chan5
            matDict["power6"] = power_chan6
            matDict["power7"] = power_chan7
            matDict["power8"] = power_chan8
            if self.is_OBand:
                matDict["power9"] = power_chan9
                matDict["power10"] = power_chan10

        savemat(os.path.join(self.path[i], matFilename), matDict)
        rangeWL = ((self.end_wl[i] - self.start_wl[i]) / 20) * 1e-9

        # Every n number of sweeps, do a fine align:
        if j % self.config["fineAlign"]["interval"] == 0 or j == 1:
            logging.info("Sweep Number: {}. Total Sweeps: {}".format(j, abs_sweep))
            if self.config["fineAlign"]["optimizeWL"]:
                self.fine_align_wavelength = self.find_optimum_wavelength(
                    matDict,
                    guess_wavelength=(self.guess_wavelength[i] * 1e-9),
                    range=rangeWL,
                )
            else:
                self.fine_align_wavelength = self.guess_wavelength[i] * 1e-9

            power_before, fa_power, res = self.run_fine_align(
                self.laser, self.stage, optimum_wavelength=self.fine_align_wavelength
            )

            log_power = []
            for bef, aft in zip(power_before.values(), fa_power.values()):
                log_power.append(bef)
                log_power.append(aft)

            with open(
                os.path.join(self.path[i], self.fineAlignment_csv), "a", newline=""
            ) as f:
                writer = csv.writer(f)
                writer.writerow(
                    [i + 1]
                    + [j]
                    + [abs_time]
                    + [self.fine_align_wavelength]
                    + log_power
                )

            try:
                copyfile(
                    os.path.join(self.path[i], self.fineAlignment_csv),
                    os.path.join(self.path[i], self.fineAlignment_copy),
                )
            except:
                print(
                    "Read file is open - canonot update data. Close .csv and wait for the next sweep"
                )

        return temperature_log, res, fa_power, wavelength, power

    def update_config(self):
        self.segment_num = len(self.config["segment"]["outputPath"])
        self.is_time = self.config["segment"]["isTime"]
        self.path = self.config["segment"]["outputPath"]
        if self.tec1:
            self.tec1_temp = self.config["segment"]["tec1Temp"]
        self.start_time = self.config["segment"]["time"]
        self.start_wl = self.config["segment"]["startWavelength"]
        self.end_wl = self.config["segment"]["endWavelength"]
        self.guess_wavelength = self.config["segment"]["fineAlignWavelength"]
        self.sweep_time = self.config["segment"]["sweep"]
        self.sweep_speed = self.config["segment"]["sweepSpeed"]
        self.log_vals = []

        for i in self.config["logging"]["HP816x"]:
            if self.laser:
                if i <= len(self.laser.pwmSlotIndex):
                    self.log_vals.append("HP816x{}_before".format(i))
                    self.log_vals.append("HP816x{}_after".format(i))
            else:
                self.log_vals.append("HP816x{}_before".format(i))
                self.log_vals.append("HP816x{}_after".format(i))

        if self.is_N77:
            if self.laser:
                for i in self.config["logging"]["N77"]:
                    self.log_vals.append("N77_{}_before".format(i))
                    self.log_vals.append("N77_{}_after".format(i))
            else:
                self.log_vals.append("N77_{}_before".format(i))
                self.log_vals.append("N77_{}_after".format(i))

    def turnon_instruments(self):
        self.turnon_laser()

        if self.tec1:
            self.turnon_TEC()
            print("TEC1 successfully turned on")

    def start_segment(self, i):
        # timeCSV and finealignment header here
        with open(os.path.join(self.path[i], self.timeSteps_csv), "a", newline="") as f:
            writer = csv.writer(f)
            if self.tec1:
                writer.writerow(
                    [
                        "Segment",
                        "Index",
                        "Time Elapse",
                        ".mat File Name",
                        "Sweep Time",
                        "TEC1 Temp",
                    ]
                )
            else:
                writer.writerow(
                    ["Segment", "Index", "Time Elapse", ".mat File Name", "Sweep Time"]
                )

        with open(
            os.path.join(self.path[i], self.fineAlignment_csv), "a", newline=""
        ) as f:
            writer = csv.writer(f)
            writer.writerow(
                ["Segment Number"]
                + ["Scan Number"]
                + ["Elapse Time"]
                + ["FineAlign Wavelength"]
                + self.log_vals
            )

    def validate_input(self):
        self.validPath = []
        for i in range(self.segment_num):
            self.validate_speed(
                i, self.sweep_speed[i], self.config["segment"]["sweepStep"][i]
            )
            self.validate_wavelength(
                i, self.start_wl[i], self.end_wl[i], self.guess_wavelength[i]
            )
            self.validate_data_points(
                i,
                self.start_wl[i],
                self.end_wl[i],
                self.config["segment"]["sweepStep"][i],
            )
            self.validate_path(i, self.path[i])

            if self.tec1:
                self.validate_temperature(self.tec1, i, self.tec1_temp[i])

    def validate_speed(self, i, speed, step_size):
        c_band = ["5"]

        # Check Averaging Time
        if speed not in list(self.speed_map.keys()):
            raise ValueError(
                "Sweep Speed provided in row {} is invalid. Must be one of the following: {}".format(
                    i + 1, list(self.speed_map.keys())
                )
            )

        if speed != "auto":
            if float(step_size / float(speed)) < 0.0001:
                raise ValueError(
                    "Sweep speed in segment {} exceeds limit. Please input a different value and try again".format(
                        i + 1
                    )
                )

        # Check CBand Speed Compatability
        if self.is_OBand is False and speed not in c_band:
            raise ValueError(
                "Sweep Speed in segment {} is invalid. Must be one of the following: {}".format(
                    i + 1, c_band
                )
            )

    def validate_wavelength(self, i, start, end, fa_wavelength):
        if self.is_OBand:
            min, max = 1265, 1375
        else:
            min, max = 1460, 1560

        if not min <= start <= max or not min <= end <= max:
            raise TypeError(
                "Wavelength in segment {} is not within range. Must be within {} - {}".format(
                    i, min, max
                )
            )

        if end < start:
            raise TypeError(
                "Wavelength in segment {} is not within range. Must be within {} - {}".format(
                    i, min, max
                )
            )

        if fa_wavelength < start or fa_wavelength > end:
            raise TypeError(
                "FineAlign Wavelength {} in segment {} is not within range. Must be within {} - {}".format(
                    i, fa_wavelength, start, end
                )
            )

    def validate_data_points(self, i, start, end, step_size):
        if step_size < 0.00005:
            raise ValueError(
                "Step size in segment {} is too small. Must be above 0.00005".format(i)
            )
        if (end - start) / step_size > 20000:
            raise ValueError(
                "Datapoints in segment {} exceeds maximum of 20,000.".format(i)
            )

    def validate_temperature(self, tec, i, tec_temp):
        min, max = tec.getTemplimit()
        if not min <= tec_temp <= max:
            raise TypeError("Invalid Input: Value of TEC1 exceed instrument limit.")

    def validate_path(self, i, path):
        try:
            if len(os.listdir(path)) > 0 and path not in self.validPath:
                msgBox = QtWidgets.QMessageBox()
                msgBox.setText(
                    "Output Path in Segment {} already contain files including: {}. Continue?".format(
                        i + 1, os.listdir(path)[:5]
                    )
                )
                msgBox.setStandardButtons(
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel
                )
                returnValue = msgBox.exec()

                if returnValue == QtWidgets.QMessageBox.Cancel:
                    raise TypeError()

                if returnValue == QtWidgets.QMessageBox.Yes:
                    self.validPath.append(path)

        except OSError as e:
            val = str(e).split("]")  # Remove [Win Error] from printing out
            raise OSError("Invalid Output Path in Segment {}. {}".format(i + 1, val[1]))

    def get_test_config(self, speed_map):
        self.is_OBand = random.choice([True, False])
        for i in self.config["segment"].keys():
            self.config["segment"][i] = []

        if self.is_OBand:
            min, max = 1265, 1375
        else:
            min, max = 1460, 1560

        self.config["segment"]["startWavelength"].append(random.uniform(min, max))
        self.config["segment"]["endWavelength"].append(random.uniform(min, max))
        self.config["segment"]["sweepSpeed"].append(
            random.choice(list(speed_map.keys()))
        )
        self.config["segment"]["sweepStep"].append(random.uniform(0, 0.01))

    def initial_sweep_test(self):
        """
        Run initial sweep of the laser
        """
        power, wavelength = self.read_mat()
        return power, wavelength

    def multiple_sweeps_test(self, i, j, abs_sweep, total_time, abs_time):
        """
        Perform one laser sweep and fineAlign for specified intervals. save scans into specified files
        @param i: Segment number
        @param j: Sweep/Scan Number
        @param seg_time: Start time of the segment or the experiment
        @param total_time: Total time of the experiments
        @return:
        """

        res, fa_power = None, {}
        logging.info("Starting Sweep Number {}. Total Sweeps {}".format(j, abs_sweep))

        # get elapsed time
        t1 = time.time()
        total_time = t1 - total_time
        abs_time = t1 - abs_time

        matFilename = "laser_sweep_%d.mat" % j
        temperature_log = random.uniform(25, 30)

        try:
            # sweep laser
            (power, wavelength) = self.read_mat()

        except Exception as e:
            logging.error(str(e))

        sweep_time = time.time() - t1

        with open(os.path.join(self.path[i], self.timeSteps_csv), "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [i + 1]
                + [j]
                + [total_time]
                + [matFilename]
                + [sweep_time]
                + [temperature_log]
            )

        try:  # Copy file to EXCEL for reading
            copyfile(
                os.path.join(self.path[i], self.timeSteps_csv),
                os.path.join(self.path[i], self.timeSteps_copy),
            )
        except:
            print(
                "Read file opened. Please close the file to update fineAlignment.csv data"
            )

        rangeWL = ((self.end_wl[i] - self.start_wl[i]) / 20) * 1e-9
        time.sleep(5)

        # Every n number of sweeps, do a fine align:
        if j % self.config["fineAlign"]["interval"] == 0 or j == 1:
            power_before, fa_power, res = self.run_fine_align_test()

            log_power = []
            for bef, aft in zip(power_before.values(), fa_power.values()):
                log_power.append(bef)
                log_power.append(aft)

            with open(
                os.path.join(self.path[i], self.fineAlignment_csv), "a", newline=""
            ) as f:
                writer = csv.writer(f)
                writer.writerow([i + 1] + [j] + [abs_time] + log_power)

            try:
                copyfile(
                    os.path.join(self.path[i], self.fineAlignment_csv),
                    os.path.join(self.path[i], self.fineAlignment_copy),
                )
                copyfile(
                    os.path.join(self.path[i], self.timeSteps_csv),
                    os.path.join(self.path[i], self.timeSteps_copy),
                )
            except:
                print(
                    "Read file is open - canonot update data. Close .csv and wait for the next sweep"
                )

        return temperature_log, res, fa_power, wavelength, power

    def read_mat(
        self,
        file_path=r"C:/Users/piram/Downloads/2022-08-18_OOC_Trial3/2022-08-18_OOC_Trial3/bulkRI/laser_sweep_2.mat",
    ):
        mat = loadmat(file_path)
        power = np.array(mat["power"])
        wavelengths = np.array(mat["wavelength"][0])
        if power.shape[0] != wavelengths.shape[0]:
            raise RuntimeError("Number of wavelengths and powers do not match")

        return (power, wavelengths)


if __name__ == "__main__":
    pass
