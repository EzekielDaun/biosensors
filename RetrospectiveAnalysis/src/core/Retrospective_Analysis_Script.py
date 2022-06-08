import os

from typing import List, Generator, Tuple

from PySide6.QtCore import QRunnable

from matplotlib import animation

# from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import math
import scipy
from scipy import signal
from scipy.io import loadmat
from scipy.io import savemat
from scipy.signal import find_peaks
import numpy as np
from numpy import asarray
from numpy import savetxt
import glob
import csv

from .MultiLorentzianFit import LorentzianFitting

# import pandas as pd
# TODO: Pandas library not installed, would need internet- or maybe can manually install somehow??
# Otherwise replace with a numpy version (pandas only used for one line on interpolation)


class RetrospectiveAnalyzer(QRunnable):
    NUM_PLOTS = 5

    def __init__(
        self,
        folder_path,
        figures: List[Figure],
        canvass: List[FigureCanvas],
    ):
        super().__init__()
        self._folder_path = folder_path
        self._figures = figures
        self._canvass = canvass

    def run(self):
        self._grapher(
            root=self._folder_path,
            p1_index=1,
            p2_index=1,
            sweep_timestep=0.22,
            remove_spikes=False,
            pkProm=6,
            save_animation=0,
        )
        for canvas in self._canvass:
            canvas.draw()

    def _grapher(
        self,
        root,
        p1_index=1,
        p2_index=1,
        sweep_timestep=0.25,
        remove_spikes=True,
        pkProm=4,
        save_animation=0,
    ):
        """
        Generates 3 graphs: (1) a initial point offset vs time graph, showing the offset between power 1 and power 2 peaks relative
                            to their intiial points.
                            (2) an animation fo the power-wavelength plot
                            (3) an animation of the offset-time plot

            :param root: the root folder containing matlab vectors from each sweep
            :param p1_index: the initial index of the power 1 peak for tracking
            :param p2_index: the initial index of the power 2 peak for tracking
            :param sweep_timestep: the time in minutes between each laser sweep
        """

        # Getting all the files currently in the root folder:
        # files_list = []
        # for path, subdirs, files in os.walk(root):
        #     for name in files:
        #         x = os.path.join(path, name)
        #         files_list.append(x)

        files_list = glob.glob(os.path.join(root, "laser*.mat"))
        print(len(files_list))

        # Sorting all these files by their number from lowest to highest
        files_list.sort(key=_file_num)

        # Look at only part of file list
        # files_list = files_list[:int(len(files_list)*.1)]
        # files_list = files_list[401:1330]

        # SG: Set up the default shift direction: 0 for no forcing, -1 for left shift, 1 for right shift
        # Code should not force the shift direction unless the magnitude of the shift (compared to previous position)
        # is FSR/3 or greater
        numFiles = len(files_list)
        force_dir = np.zeros(numFiles)
        # force_dir = np.ones(numFiles)
        # for i in range(len(force_dir)):
        #     force_dir[i] = -force_dir[i]

        # making array to store the offsets and FSRs
        # contains the offsets between power 1 and its initial location
        power_1_offset_list = []
        # contains the offsets between power 2 and its initial location
        power_2_offset_list = []
        power_1_fsr_list = []  # contains the FSRs for each sweep
        power_2_fsr_list = []  # contains the FSRs for each sweep
        power_1_peakWL_list = []
        power_2_peakWL_list = []
        lor_p1_offset = []
        # contains all the time points (min) at which each sweep was conducted.
        t_array = []
        # ch1_spectrogram = [] # 2D array, to be plotted as an image, showing all of the spectra for ch1.
        # ch2_spectrogram = []  # 2D array, to be plotted as an image, showing all of the spectra fpr ch2.

        # Making a array of past peaks indexes:
        past_power_1_peaks = []
        past_power_2_peaks = []
        past_lor_power_1_peaks = []

        # An array containing the sweep data from each sweep
        all_sweeps_array = []

        # If we have the csv file with saved acquisition times, use that instead of the calculated times! (SG)
        # Set up the dictionary
        dTime = dict()
        useDict = False
        csvFileName = os.path.join(root, "timeSteps.csv")
        print(csvFileName)
        if os.path.isfile(csvFileName):
            useDict = True
            with open(csvFileName) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=",")
                for row in csv_reader:
                    # In case we've thrown out any .mat files, look for the filename (second csv column) of interest rather than
                    # relying on the complete dataset to be present.  Convert to minutes prior to storing.
                    if len(row) >= 3:
                        dTime[row[1]] = float(row[2]) / 60

        first_peak_found = 0
        # Looping through all the matlab vectors from each sweep.
        for iteration, filename in enumerate(files_list):
            print(os.path.relpath(filename, root))

            # getting the sweep data from matlab vector
            sweep_data = _get_sweep_data(filename, pkProm)
            all_sweeps_array.append(sweep_data)

            if iteration == 0:
                p1a = sweep_data.get("power1")
                p2a = sweep_data.get("power2")
                p1 = np.array(sweep_data.get("power1"))
                p2 = np.array(sweep_data.get("power2"))
                p1b = p1.astype(float)
                p2b = p2.astype(float)
                # ch1_spectrogram = p1b/np.min(p1b)
                # ch2_spectrogram = p2b/np.min(p2b)
                ch1_spectrogram = np.flip(p1b)
                ch2_spectrogram = np.flip(p2b)

            else:
                p1 = np.array(sweep_data.get("power1"))
                p2 = np.array(sweep_data.get("power2"))
                p1 = p1.astype(np.float)
                p2 = p2.astype(np.float)
                # ch1_spectrogram = np.vstack((ch1_spectrogram, (p1-np.max(p1))/(np.min(p1[10:])-np.max(p1))))
                # ch2_spectrogram = np.vstack((ch2_spectrogram, (p2-np.max(p2))/(np.min(p2[10:])-np.max(p2))))
                ch1_spectrogram = np.vstack((ch1_spectrogram, np.flip(p1)))
                ch2_spectrogram = np.vstack((ch2_spectrogram, np.flip(p2)))

            # Check that we found peaks in this file and proceed if so.  If not, set this element of all of the arrays to NaN.
            if len(sweep_data.get("peaks1")) >= np.max([p1_index + 1, 2]) and len(
                sweep_data.get("peaks2")
            ) >= np.max([p2_index + 1, 2]):

                # If we are just beggining the sweeps, chooses a specific set of datapoints for tracking. (SG change to just the first iteration with peaks)
                if first_peak_found == 0:

                    # Here, we choose to track the first peak on power 1 or power 2 at t=0
                    (
                        offset,
                        power_1_peak,
                        power_2_peak,
                        pk1_hop,
                        pk2_hop,
                        pk1_idx,
                        pk2_idx,
                    ) = _get_offset(
                        sweep_data,
                        [sweep_data.get("peaks1")[p1_index]],
                        [sweep_data.get("peaks2")[p2_index]],
                        0,
                    )
                    init_power1_peak = power_1_peak
                    init_power2_peak = power_2_peak
                    # initialize the variables to correct for hopping between peaks when they enter/exit the frame
                    pkHop1_corr = 0
                    pkHop2_corr = 0
                    # log that we've found the first set of peaks
                    first_peak_found = 1

                # If we are greater than 4 sweeps in, use the previous peak locations for tracking.
                else:
                    # Use only the non-NaN elements of the past power array to understand the historical peak positions
                    past_power_1_peaks_nonan = [
                        item for item in past_power_1_peaks if not math.isnan(item)
                    ]
                    past_power_2_peaks_nonan = [
                        item for item in past_power_2_peaks if not math.isnan(item)
                    ]
                    (
                        offset,
                        power_1_peak,
                        power_2_peak,
                        pk1_hop,
                        pk2_hop,
                        pk1_idx,
                        pk2_idx,
                    ) = _get_offset(
                        sweep_data,
                        past_power_1_peaks_nonan[-3:],
                        past_power_2_peaks_nonan[-3:],
                        force_dir[iteration],
                    )

                # Changing the peaks to their lorentzian form..
                lor_wavelengths = sweep_data.get("wavelength")
                # Power 1 Peaks
                Lorentz1 = LorentzianFitting(
                    sweep_data.get("power1"), lor_wavelengths, pkProm
                )
                adjusted_power1 = Lorentz1.norm_power_array
                adjusted_power1 = Lorentz1.parabolic_overlay()
                lor_power_1_peak = Lorentz1.lorentzian_overlay(
                    adjusted_power1, peak_index=power_1_peak, range_fraction=0.2
                )
                arr1 = np.array([abs(lor_power_1_peak - x) for x in lor_wavelengths])
                power_1_peak = int(np.where(arr1 == np.amin(arr1))[0])

                # Power 2 Peaks
                Lorentz2 = LorentzianFitting(
                    sweep_data.get("power2"), lor_wavelengths, pkProm
                )
                adjusted_power2 = Lorentz2.norm_power_array
                adjusted_power2 = Lorentz2.parabolic_overlay()
                lor_power_2_peak = Lorentz2.lorentzian_overlay(
                    adjusted_power2, peak_index=power_2_peak, range_fraction=0.2
                )
                arr2 = np.array([abs(lor_power_2_peak - x) for x in lor_wavelengths])
                power_2_peak = int(np.where(arr2 == np.amin(arr2))[0])

                if iteration == 0:
                    init_power1_peak = power_1_peak
                    init_power2_peak = power_2_peak
                    init_lor_power_1_peak = lor_power_1_peak
                    init_lor_power_2_peak = lor_power_2_peak

                # Calculating the FSRs
                lor_power_1_peak_list = []
                lor_power_2_peak_list = []
                power_1_peak_list = []
                power_2_peak_list = []
                # Lorentzian fit each peak in the spectrum
                peaks1 = sweep_data.get("peaks1")
                peaks2 = sweep_data.get("peaks2")
                ctr = 0
                for pkIdx in peaks1:
                    lor_power_1_peak_list.append(
                        Lorentz1.lorentzian_overlay(
                            adjusted_power1, peak_index=pkIdx, range_fraction=0.2
                        )
                    )
                    arr1 = np.array(
                        [abs(lor_power_1_peak_list[ctr] - x) for x in lor_wavelengths]
                    )
                    power_1_peak_list.append(int(np.where(arr1 == np.amin(arr1))[0]))
                    ctr += 1

                ctr = 0
                for pkIdx in peaks2:
                    lor_power_2_peak_list.append(
                        Lorentz2.lorentzian_overlay(
                            adjusted_power2, peak_index=pkIdx, range_fraction=0.2
                        )
                    )
                    arr2 = np.array(
                        [abs(lor_power_2_peak_list[ctr] - x) for x in lor_wavelengths]
                    )
                    power_2_peak_list.append(int(np.where(arr2 == np.amin(arr2))[0]))
                    ctr += 1

                # calculate the FSRs from the Lorentzian-fitted peaks
                power_1_fsr_list.append(np.mean(np.diff(lor_power_1_peak_list)))
                power_2_fsr_list.append(np.mean(np.diff(lor_power_2_peak_list)))

                # If we hopped peaks, compute the correction factor (FSR). pkx_hop is -1 if hopped left; 1 if hopped right.
                # pkHopx_corr corrects the absolute wavelength offsets to what they would have been if we had continued tracking
                # the same peak. (want to add an FSR if we hopped left, want to subtract an FSR if we hopped right)
                # also update the previous peaks list to the hopped-to peak so that we don't wind up re-hopping if the original peak comes back into the frame
                if pk1_hop != 0:
                    # fsr_1 = np.mean(np.diff(lor_wavelengths[sweep_data.get('peaks1')]))
                    # compute the difference in peak position between the tracked peaks before and after hopping (FSR)
                    fsr_1 = np.abs(
                        lor_power_1_peak_list[pk1_idx]
                        - lor_power_1_peak_list[pk1_idx - pk1_hop]
                    )
                    pkHop1_corr = pkHop1_corr - pk1_hop * fsr_1
                    print("p1 correction now: ", pkHop1_corr)
                    pkHop1_posCorr = peaks1[pk1_idx] - peaks1[pk1_idx - pk1_hop]
                    past_power_1_peaks[-1] = past_power_1_peaks[-1] + pkHop1_posCorr
                    past_power_1_peaks[-2] = past_power_1_peaks[-2] + pkHop1_posCorr

                if pk2_hop != 0:
                    # fsr_2 = np.mean(np.diff(lor_wavelengths[sweep_data.get('peaks2')]))
                    # compute the difference in peak position between the tracked peaks before and after hopping (FSR)
                    fsr_2 = np.abs(
                        lor_power_2_peak_list[pk2_idx]
                        - lor_power_2_peak_list[pk2_idx - pk2_hop]
                    )
                    pkHop2_corr = pkHop2_corr - pk2_hop * fsr_2
                    print("p2 correction now: ", pkHop2_corr)
                    pkHop2_posCorr = peaks2[pk2_idx] - peaks2[pk2_idx - pk2_hop]
                    past_power_2_peaks[-1] = past_power_2_peaks[-1] + pkHop2_posCorr
                    past_power_2_peaks[-2] = past_power_2_peaks[-2] + pkHop2_posCorr

                # Appending peaks to past_peak_lists.
                # appending past power1 peaks
                past_power_1_peaks.append(power_1_peak)
                # appending past power2 peaks
                past_power_2_peaks.append(power_2_peak)

                # Appending the offsets to the offset and absolute position lists.
                # power_1_offset_list.append((lor_power_1_peak - init_lor_power_1_peak))
                # power_2_offset_list.append((lor_power_2_peak - init_lor_power_2_peak))
                power_1_offset_list.append(
                    (lor_power_1_peak + pkHop1_corr - init_lor_power_1_peak)
                )
                power_2_offset_list.append(
                    (lor_power_2_peak + pkHop2_corr - init_lor_power_2_peak)
                )
                power_1_peakWL_list.append(lor_power_1_peak + pkHop1_corr)
                power_2_peakWL_list.append(lor_power_2_peak + pkHop2_corr)

            else:  # We did not find peaks in this dataset, so set the relevant elements to NaN.
                # Appending the NaNs to the offset lists.
                power_1_offset_list.append(np.nan)
                power_2_offset_list.append(np.nan)
                power_1_fsr_list.append(np.nan)
                power_2_fsr_list.append(np.nan)
                power_1_peakWL_list.append(np.nan)
                power_2_peakWL_list.append(np.nan)
                past_power_1_peaks.append(np.nan)  # appending past power1 peaks
                past_power_2_peaks.append(np.nan)  # appending past power2 peaks

            # If we have the csv file with saved acquisition times, use that instead of the calculated times! (SG)
            if useDict:
                # append the time corresponding to the current filename
                t_array.append(dTime[os.path.relpath(filename, root)])
            # if we don't have the .csv file, manually calculate as we did before (SG)
            else:
                # appending the time, assuming each sweep is .25 min apart.
                t_array.append(sweep_timestep * iteration)

        # Applying a median filter to the offsets. This smooths out bumps
        if remove_spikes:
            power_1_offset_list = signal.medfilt(power_1_offset_list, kernel_size=11)
            # power_1_offset_list = spike_remover(power_1_offset_list)
            power_2_offset_list = signal.medfilt(power_2_offset_list, kernel_size=11)
            # power_2_offset_list = spike_remover(power_2_offset_list)
        else:
            power_1_offset_list = np.array(power_1_offset_list)
            power_2_offset_list = np.array(power_2_offset_list)

        t_array = np.array(t_array)

        # Plotting the spectrograms

        # TODO: Figure 1
        plt = self._figures[0]
        ax: Axes = plt.subplots()

        im = ax.imshow((np.transpose(ch1_spectrogram)), cmap="inferno")
        cbar = plt.colorbar(im, orientation="horizontal")
        ax.set_title("Ch1 Spectrogram")
        # axis labels
        nx = t_array.shape[0]
        no_labels = 7  # how many labels on x axis
        step_x = int(nx / (no_labels - 1))  # step between labels
        x_positions = np.arange(0, nx, step_x)  # pixel count at label position
        # label values (rounded to nearest integer)
        x_labels = np.around(t_array[::step_x], 0)
        ax.set_xticks(x_positions, x_labels)
        ny = np.flip(lor_wavelengths.shape[0])
        no_labels = 7  # how many labels on y axis
        step_y = int(ny / (no_labels - 1))  # step between labels
        y_positions = np.arange(0, ny, step_y)  # pixel count at label position
        # label values (rounded to nearest integer)
        y_labels = np.around(np.flip(lor_wavelengths[::step_y] * 1e9), 2)
        ax.set_yticks(y_positions, y_labels)
        ax.set_xlabel("Time (minutes)")
        ax.set_ylabel("Wavelength (nm)")
        ax.axis("auto")
        # colorbar label
        cbar.set_label("Power (dBm)")

        # # save the spectrogram figure
        # figh.set_size_inches(8, 5)
        # figfilename = os.path.join(root, "ch1_spectrogram.png")
        # figh.savefig(figfilename, bbox_inches="tight")
        # figfilename = os.path.join(root, "ch1_spectrogram.pdf")
        # figh.savefig(figfilename, bbox_inches="tight")

        # plot line plot over it with tracked peak
        ax.plot(
            np.arange(0, nx, 1),
            (ny - past_power_1_peaks),
            "-",
            linewidth=2,
            color="black",
        )
        # figfilename = os.path.join(root, "ch1_spectrogram_overlay.png")
        # figh.savefig(figfilename, bbox_inches="tight")
        # figfilename = os.path.join(root, "ch1_spectrogram_overlay.pdf")
        # figh.savefig(figfilename, bbox_inches="tight")
        # plt.show()

        # TODO: Figure 2
        plt = self._figures[1]
        ax: Axes = plt.subplots()

        im2 = ax.imshow((np.transpose(ch2_spectrogram)), cmap="inferno")
        cbar = plt.colorbar(im2, orientation="horizontal")
        ax.set_title("Ch2 Spectrogram")
        # axis labels
        ax.set_xticks(x_positions, x_labels)
        ax.set_yticks(y_positions, y_labels)
        ax.set_xlabel("Time (minutes)")
        ax.set_ylabel("Wavelength (nm)")
        ax.axis("auto")
        # colorbar label
        cbar.set_label("Power (dBm)")

        # # save the spectrogram figure
        # figh.set_size_inches(8, 5)
        # figfilename = os.path.join(root, "ch2_spectrogram.png")
        # figh.savefig(figfilename, bbox_inches="tight")
        # figfilename = os.path.join(root, "ch2_spectrogram.pdf")
        # figh.savefig(figfilename, bbox_inches="tight")

        # plot line plot over it with tracked peak
        ax.plot(
            np.arange(0, nx, 1),
            (ny - past_power_2_peaks),
            "-",
            linewidth=2,
            color="black",
        )
        # figfilename = os.path.join(root, "ch2_spectrogram_overlay.png")
        # figh.savefig(figfilename, bbox_inches="tight")
        # figfilename = os.path.join(root, "ch2_spectrogram_overlay.pdf")
        # figh.savefig(figfilename, bbox_inches="tight")
        # plt.show()

        # plot_spectrogram_comparison = 0
        # if plot_spectrogram_comparison:
        #     # test code to compare the two spectrograms (for splitter experiment, where we expect them to be ~the same
        #     figh, ax = plt.subplots()
        #     toPlot = np.transpose(np.divide(ch1_spectrogram, ch2_spectrogram))
        #     im = ax.imshow(toPlot, cmap="inferno")
        #     cbar = plt.colorbar(im, orientation="horizontal")
        #     plt.title("Spectrogram Ratios (Ch1/Ch2)")
        #     # axis labels
        #     nx = t_array.shape[0]
        #     no_labels = 7  # how many labels on x axis
        #     step_x = int(nx / (no_labels - 1))  # step between labels
        #     x_positions = np.arange(0, nx, step_x)  # pixel count at label position
        #     # label values (rounded to nearest integer)
        #     x_labels = np.around(t_array[::step_x], 0)
        #     plt.xticks(x_positions, x_labels)
        #     ny = np.flip(lor_wavelengths.shape[0])
        #     no_labels = 7  # how many labels on y axis
        #     step_y = int(ny / (no_labels - 1))  # step between labels
        #     y_positions = np.arange(0, ny, step_y)  # pixel count at label position
        #     # label values (rounded to nearest integer)
        #     y_labels = np.around(np.flip(lor_wavelengths[::step_y] * 1e9), 2)
        #     plt.yticks(y_positions, y_labels)
        #     plt.xlabel("Time (minutes)")
        #     plt.ylabel("Wavelength (nm)")
        #     plt.axis("auto")
        #     # colorbar label
        #     cbar.set_label("Power ratio (ch1/ch2)")
        #     plt.show()
        #     # save the spectrogram figure
        #     figh.set_size_inches(8, 5)
        #     figfilename = os.path.join(root, "ch1_ch2_spectrogram_ratio.png")
        #     figh.savefig(figfilename, bbox_inches="tight")
        #     figfilename = os.path.join(root, "ch1_ch2_spectrogram_ratio.pdf")
        #     figh.savefig(figfilename, bbox_inches="tight")

        # TODO: Figure 3
        # Plotting the offset versus the initial point versus time.
        fig = self._figures[2]
        ax1 = fig.subplots(1, 1)
        ax1.set_title("Offset from initial resonance peak location vs time", size=15)
        ax1.set_ylabel("Offset (pm)", size=15)
        ax1.set_xlabel("Time (min)", size=15)
        ax1.set_xlim(0, int(np.max(t_array)))
        # ax1.plot(t_array, power_1_offset_list*1e12, color='blue', label='Detector Slot 1/Array Channel 1/Top/Power 1')
        lines = ax1.plot(
            t_array,
            power_1_offset_list * 1e12,
            color="blue",
            label="Detector Slot 1/Top",
        )
        # ax1.plot(t_array, lor_p1_offset*1e12,color='orange',label='Lorentzian Fit Power 1')
        # ax1.plot(t_array, power_2_offset_list*1e12, color='r', label='Detector Slot 2/Array Channel 3/Bottom/Power 2')
        lines.append(
            ax1.plot(
                t_array,
                power_2_offset_list * 1e12,
                color="r",
                label="Detector Slot 2/Bottom",
            )
        )
        # ax1.plot(t_array, power_1_offset_list*1e12-power_2_offset_list*1e12, color = 'g', label = 'Power1-Power2')
        ax1.legend(loc="upper left", fontsize="small")
        # plt.draw()

        # save the data to a MATLAB matrix (SG)
        matfilename = os.path.join(root, "matlab_matrix.mat")
        print(matfilename)
        mdic = {
            "t_array": t_array,
            "power_1_offset_list": power_1_offset_list,
            "power_2_offset_list": power_2_offset_list,
            "power_1_fsr_list": power_1_fsr_list,
            "power_2_fsr_list": power_2_fsr_list,
            "power_1_peakWL_list": power_1_peakWL_list,
            "power_2_peakWL_list": power_2_peakWL_list,
        }
        savemat(matfilename, mdic)

        p1_offset_no_nan = power_1_offset_list[~np.isnan(power_1_offset_list)]
        p2_offset_no_nan = power_2_offset_list[~np.isnan(power_2_offset_list)]

        # # save the peak shift figure (SG)
        # fig.set_size_inches(8, 4)
        # figfilename = os.path.join(root, "peakshift.png")
        # plt.savefig(figfilename, bbox_inches="tight")
        # figfilename = os.path.join(root, "peakshift.pdf")
        # plt.savefig(figfilename, bbox_inches="tight")
        # # save only ch1
        ax1.lines.pop(1)
        xmin, xmax, ymin, ymax = ax1.axis()
        yrange = np.max(p1_offset_no_nan * 1e12) - np.min(p1_offset_no_nan * 1e12)
        ymin = np.min(p1_offset_no_nan * 1e12) - 0.05 * yrange
        ymax = np.max(p1_offset_no_nan * 1e12) + 0.05 * yrange
        ax1.axis([xmin, xmax, ymin, ymax])
        # figfilename = os.path.join(root, "ch1_peakshift.png")
        # plt.savefig(figfilename, bbox_inches="tight")
        # figfilename = os.path.join(root, "ch1_peakshift.pdf")
        # plt.savefig(figfilename, bbox_inches="tight")
        # # save only ch2
        lines.append(
            ax1.plot(
                t_array,
                power_2_offset_list * 1e12,
                color="r",
                label="Detector Slot 2/Bottom",
            )
        )
        ax1.lines.pop(0)
        yrange = np.max(p2_offset_no_nan * 1e12) - np.min(p2_offset_no_nan * 1e12)
        ymin = np.min(p2_offset_no_nan * 1e12) - 0.05 * yrange
        ymax = np.max(p2_offset_no_nan * 1e12) + 0.05 * yrange
        ax1.axis([xmin, xmax, ymin, ymax])
        # figfilename = os.path.join(root, "ch2_peakshift.png")
        # plt.savefig(figfilename, bbox_inches="tight")
        # figfilename = os.path.join(root, "ch2_peakshift.pdf")
        # plt.savefig(figfilename, bbox_inches="tight")
        lines.append(
            ax1.plot(
                t_array,
                power_1_offset_list * 1e12,
                color="blue",
                label="Detector Slot 1/Top",
            )
        )
        ax1.axis("auto")

        current_sweep_index = len(all_sweeps_array) - 1
        wavelength_graph = sweep_data.get("wavelength") * 1e9

        # TODO: Figure 4
        fig = self._figures[3]
        axes = fig.subplots(1, 2)
        ax = axes[0]
        ax.set_title("Initial Power- Wavelength Spectrum")
        ax.set_ylabel("Power (dBm)")
        ax.set_xlabel("Wavelength (nm)")
        ax.plot(wavelength_graph, all_sweeps_array[0].get("power1"), label="Power1")
        ax.plot(wavelength_graph, all_sweeps_array[0].get("power2"), label="Power2")

        ax2 = axes[1]
        ax2.set_title("Current Power - Wavelength Spectrum")
        ax2.set_ylabel("Power (dBm)")
        ax2.set_xlabel("Wavelength (nm)")
        ax2.plot(
            wavelength_graph,
            all_sweeps_array[current_sweep_index].get("power1"),
            label="Power1",
        )
        ax2.plot(
            wavelength_graph,
            all_sweeps_array[current_sweep_index].get("power2"),
            label="Power2",
        )

        fig.legend()
        # # plt.draw()

        # # plotting the 3rd graph - an animation of the power-wavlength graph.
        # _generate_animation(
        #     all_sweeps_array,
        #     past_power_1_peaks,
        #     past_power_2_peaks,
        #     power_1_offset_list,
        #     power_2_offset_list,
        #     t_array,
        #     root,
        #     save_animation,
        # )


def _spike_remover(offset_data, std_multiplier=1):
    # Creating a median smoothed array to find std:
    median_smoothed = signal.medfilt(offset_data, kernel_size=15)
    med_smooth_std = np.std(median_smoothed)
    upper_bound = np.array(
        [x + med_smooth_std * std_multiplier for x in median_smoothed]
    )
    lower_bound = np.array(
        [x - med_smooth_std * std_multiplier for x in median_smoothed]
    )

    # Replacing data outside of bounds with NaN:
    for i, x in enumerate(offset_data):
        if x > upper_bound[i]:
            offset_data[i] = np.nan
        elif x < lower_bound[i]:
            offset_data[i] = np.nan

    # Filling NaN zones via linear interpolation:
    df = pd.Series(offset_data)
    interpolated_data = df.interpolate(method="linear")

    return interpolated_data


def _get_sweep_data(filename, pkProm):
    """
    This function converts the sweep data from a MATLAB vector in to a dictionary datatype that is
    easier for python to read.

    :param filename: the name of the MATLAB vector representing a single sweep
    :return: a dictionary containing:
            array of wavelengths (m)
            array of power 1 (I believe units are dBm)
            array of power 2 (I believe units are dBm)
            array of peaks in power 1 (where the peaks are the array index values where peaks occur in power 1 array)
            array of peaks in power 2 (where the peaks are the array index values where peaks occur in power 2 array)
    """
    matlab_vector = loadmat(filename)  # loading the matlab vector
    # retrieving the wavelengths used during the sweep (nm)
    wavelength = matlab_vector["wavelength"][0]
    # retrieving the values for the power1 channel. (dBm)
    power1 = matlab_vector["power1"][0]
    # retrieving the values for the power2 channel. (dBm)
    power2 = matlab_vector["power2"][0]

    # Using the scipy find_peaks algorithm to find peaks in the power & power 2 channels. Operating on the raw data here.
    # key parameter: peak prominence, which is the vertical distance between a peak and its lowest contour line.
    # There a lots of other parameters you could use here- i.e horizontal distances, min heights..
    # refer to scipy find_peaks docs to view additional parameters.
    # set the minimum distance between peaks to 20 datapoints (200 pm)
    minPkSpacing = 20
    peaks1 = find_peaks((-1) * power1, prominence=pkProm, distance=minPkSpacing)[0]
    peaks2 = find_peaks((-1) * power2, prominence=pkProm, distance=minPkSpacing)[0]

    if "852" in filename:
        print("852 sweep peak", peaks1)
    return {
        "wavelength": wavelength,
        "power1": power1,
        "peaks1": peaks1,
        "power2": power2,
        "peaks2": peaks2,
    }


def _get_offset(sweep_data, past_power_1_peaks, past_power_2_peaks, force_dir=0):
    """
    Finds the offset between two given peaks.

    :param sweep_data: a dictionary containing data from a single sweep
    :param past_power_1_peaks: index of the previous peak in power 1
    :param past_power_2_peaks: index of the previous peak in power 2
    :param force_dir: forces the direction of the shift, in the case of large shifts on the order of the FSR (FSR/3).
    Set to -1 for expected negative peak shift, +1 for expected positive peak shift, 0 to not force.
    :return: offset = Power 1 peak - power 2 peak
            power_1_peak = the index in the power array of the peak for power 1 as defined by peak tracker (closest peak to previous peak location)
            power_2_peak = the index in the power array of the peak for power 2 defined by peak tracker (closest peak to previous peak location)
            pk1_idx = the peak number that we are tracking in power 1 (e.g., 1 for the lowest-wavelength peak in the spectrum
            pk2_idx = the peak number that we are tracking in power 2 (e.g., 1 for the lowest-wavelength peak in the spectrum
    """
    wavelength = sweep_data.get("wavelength")

    # If the previous peak position was in the 20% of the wavelength range nearest either edge, hop to the next peak (SG)
    # set the edge tolerance here to 20% for now
    p1_hop = 0
    p2_hop = 0
    edge_tolerance = 0.15
    low_thresh = edge_tolerance * (np.max(wavelength) - np.amin(wavelength)) + np.amin(
        wavelength
    )
    high_thresh = np.max(wavelength) - edge_tolerance * (
        np.max(wavelength) - np.amin(wavelength)
    )

    # compute the rough FSRs (in indices, not WL) from the peak positions
    print("peaks1 ", sweep_data.get("peaks1"))
    print("peaks2 ", sweep_data.get("peaks2"))
    if np.isnan(sweep_data.get("peaks1")).any() or len(sweep_data.get("peaks1")) < 2:
        fsr_1 = np.nan
    else:
        fsr_1 = round(np.mean(np.diff(sweep_data.get("peaks1"))))

    if np.isnan(sweep_data.get("peaks2")).any() or len(sweep_data.get("peaks2")) < 2:
        fsr_2 = np.nan
    else:
        fsr_2 = round(np.mean(np.diff(sweep_data.get("peaks2"))))

    # check whether each peak was near either edge of the frame, and set the appropriate flag if so
    # (to 1 if we hopped to the peak to the right; to -1 if we hopped to the peak to the left)
    print("previous power1 ", past_power_1_peaks[-1])
    print("previous power2 ", past_power_2_peaks[-1])

    if not (np.isnan(past_power_1_peaks[-1])):
        if wavelength[past_power_1_peaks[-1]] < low_thresh:
            for index, peak in enumerate(past_power_1_peaks):
                past_power_1_peaks[index] += fsr_1

            p1_hop = 1

        if wavelength[past_power_1_peaks[-1]] > high_thresh:
            for index, peak in enumerate(past_power_1_peaks):
                past_power_1_peaks[index] -= fsr_1

            p1_hop = -1

    if not (np.isnan(past_power_2_peaks[-1])):
        if wavelength[past_power_2_peaks[-1]] < low_thresh:
            for index, peak in enumerate(past_power_2_peaks):
                past_power_2_peaks[index] += fsr_2

            p2_hop = 1

        if wavelength[past_power_2_peaks[-1]] > high_thresh:
            for index, peak in enumerate(past_power_2_peaks):
                past_power_2_peaks[index] -= fsr_2

            p2_hop = -1

    # Now, peak_tracker should look for the peak further from the edge of the frame, and the px_hop variable has
    # recorded whether we hopped peaks.

    power_1_peak = _peak_tracker_test(
        sweep_data.get("peaks1"), past_power_1_peaks, force_dir
    )
    power_2_peak = _peak_tracker_test(
        sweep_data.get("peaks2"), past_power_2_peaks, force_dir
    )
    offset = wavelength[power_1_peak] - wavelength[power_2_peak]
    power_1_peak_idx = (np.abs(sweep_data.get("peaks1") - power_1_peak)).argmin()
    power_2_peak_idx = (np.abs(sweep_data.get("peaks2") - power_2_peak)).argmin()
    return [
        offset,
        power_1_peak,
        power_2_peak,
        p1_hop,
        p2_hop,
        power_1_peak_idx,
        power_2_peak_idx,
    ]


def _peak_tracker(peaks, previous_peaks):
    """

    This function finds the new peak based off the location of previous peaks.
    This allows us to effectively "track" peaks, ensuring we are analysing the same peak each time.

    :param peaks: contains the indexes of all the peak of for a given channel.
    :param previous_peaks: contains the previous 3 peaks of a given channel.
    Unless we are analyzing the first 3 peaks- in this case, will contain a single peak
    :param wavelength: an array containing the wavelengths
    :return: the index of the selected peak in the wavelength array
    """
    # making sure there are actually peaks in the dataset :
    if len(peaks) == 0:
        print("No peaks found")
        raise ValueError

    # Getting the average of the previous peaks.
    prev_avg = np.mean(previous_peaks)

    # finging the new intervention peak:
    min_diff = abs(peaks[0] - prev_avg)  # placeholder value for min_diff
    selected_peak = peaks[0]  # placeholder value for the selected peak.
    for peak in peaks:
        difference = abs(peak - prev_avg)
        if difference < min_diff:
            min_diff = difference
            selected_peak = peak
    return selected_peak


def _peak_tracker_test(peaks, previous_peaks, force_dir=0):
    """

    This function finds the new peak based off the location of previous peaks.
    This allows us to effectively "track" peaks, ensuring we are analysing the same peak each time.
    2021-03-30 test (SMG) -- this version of the function is intended to fix bugs that are generated when:
    (1) peaks shift too quickly, making the script hop to the next peak instead of tracking the intended peak
    (2) the tracked peak shifts off of the swept wavelength range

    :param peaks: contains the indexes of all the peak of for a given channel.
    :param previous_peaks: contains the previous 3 peaks of a given channel.
    Unless we are analyzing the first 3 peaks- in this case, will contain a single peak
    :param force_dir: forces the direction of the shift, in the case of large shifts on the order of the FSR (FSR/3).
    Set to -1 for expected negative peak shift, +1 for expected positive peak shift, 0 to not force.
    :param wavelength: an array containing the wavelengths
    :return: the index of the selected peak in the wavelength array
    """
    # making sure there are actually peaks in the dataset :
    if len(peaks) == 0:
        print("No peaks found")
        raise ValueError

    # Getting the average of the previous peaks.
    prev_avg = np.mean(previous_peaks)

    # choose to compare against the most recent peak position only.
    # prev_avg = previous_peaks[-1]

    # find the fsr
    if np.isnan(peaks).any() or len(peaks) < 2:
        fsr = np.nan
    else:
        fsr = round(np.mean(np.diff(peaks)))

    # finding the new intervention peak:
    min_diff = min(abs(peaks - prev_avg))
    selected_index = np.argmin(abs(peaks - prev_avg))
    selected_peak = peaks[selected_index]

    """
    min_diff = abs(peaks[0]-prev_avg)  ## placeholder value for min_diff
    selected_peak = peaks[0]   ## placeholder value for the selected peak.
    selected_index = 0  ## placeholder value for the index
    for index, peak in enumerate(peaks):
        difference = abs(peak - prev_avg)
        if difference<min_diff:
            min_diff = difference
            selected_peak = peak
            selected_index = index
    """

    # SG force correction in case of large shifts (here choose 1/3 FSR)
    if min_diff > fsr / 3:
        if force_dir != 0:
            if (selected_peak - prev_avg) / force_dir < 0:
                # the peak shift direction does not match the 'forced' large shift direction
                if force_dir < 0:
                    if selected_index > 0:
                        # we should be moving left --> hop one peak to the left if we can
                        selected_peak = peaks[selected_index - 1]
                if force_dir > 0:
                    if selected_index < len(peaks):
                        # we should be moving right --> hop one peak to the right if we can
                        selected_peak = peaks[selected_index + 1]

    return selected_peak


def _file_num(filename):
    """

    Find the sweep number based on the filename.
    For example, "laser_sweep_12" would be sweep number 12.

    :param filename: the name of the matlab vector. Must be in the format "laser_sweep_1.mat"
    :return: the filenumber ( the sweep iteration - for example, laser_sweep_1.mat is the first sweep
            laser_sweep_12 is the 12th sweep
    """
    start_index = int(str.index(filename, "sweep_") + 6)
    end_index = int(str.index(filename, ".mat"))
    filenumber = int(filename[start_index:end_index])
    return filenumber


def _generate_animation(
    all_sweep_data,
    p1peaks,
    p2peaks,
    p1_offset_list,
    p2_offset_list,
    time_array,
    root,
    save_animation,
):
    """
    Makes a replay of the power-wavlength graph.

        :param all_sweep_data: and array containing sweep data dictionaries.
        :param p1peaks: The past power 1 peaks at every sweep
        :param p2peaks: The past power 2 peaks at every sweep.
        :return:
    """
    x_wavelengths = all_sweep_data[0].get("wavelength")

    fig = plt.figure()
    fig.set_size_inches(15, 8)
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)

    # Setting up skeleton of power-wavelength graph
    ax1.set_title("Power vs wavelength replay")
    ax1.set_ylabel("Power (dBm)")
    ax1.set_xlabel("Wavelength (nm)")
    ax1.axvline(
        x=all_sweep_data[0].get("wavelength")[p1peaks[0]],
        color=(0.8, 0.8, 0.99),
        label="power1 initial",
    )
    ax1.axvline(
        x=all_sweep_data[0].get("wavelength")[p2peaks[0]],
        color=(0.99, 0.8, 0.8),
        label="power2 initial",
    )

    # Setting up skeleton of initial point offset vs time graph:
    ax2.set_title("Offset from initial resonance peak location vs time")
    ax2.set_ylabel("Offset (m)")
    ax2.set_xlabel("Time (min)")
    ax2.set_xlim(0, int(np.max(time_array)))

    def update(
        num,
        x_wavelengths,
        all_sweep_data,
        p1peaks,
        p2peaks,
        p1_offset_list,
        p2_offset_list,
        time_array,
    ):

        # Updating power-wavelength graph:
        (power_1_line,) = ax1.plot(
            x_wavelengths,
            all_sweep_data[num].get("power1"),
            color="blue",
            label="P1 Wave",
        )
        (power_2_line,) = ax1.plot(
            x_wavelengths,
            all_sweep_data[num].get("power2"),
            color="red",
            label="P2 Wave",
        )

        (p1_pt,) = ax1.plot(
            x_wavelengths[p1peaks[num]],
            all_sweep_data[num].get("power1")[p1peaks[num]],
            marker="*",
            color="black",
            label="Comparison point",
        )
        (p2_pt,) = ax1.plot(
            x_wavelengths[p2peaks[num]],
            all_sweep_data[num].get("power2")[p2peaks[num]],
            marker="X",
            color="black",
            label="Reference point",
        )

        # Updating initial point offset vs time graph:
        (p1_offset_line,) = ax2.plot(
            time_array[:num], p1_offset_list[:num], color="blue", label="Power 1"
        )
        (p2_offset_line,) = ax2.plot(
            time_array[:num],
            p2_offset_list[:num],
            color="red",
            label="Power 2",
            linestyle="dashed",
        )

        print("updating video plot: ", num)

        return (
            power_1_line,
            power_2_line,
            p1_pt,
            p2_pt,
            p1_offset_line,
            p2_offset_line,
        )

    # Running the animation. Here, interval is the tim (ms) between frames.
    # The interval is the speed of the aminiation (how often it updates im ms)

    # Set up movie writer
    Writer = animation.writers["ffmpeg"]
    writer = Writer(fps=20, metadata=dict(artist="Me"), bitrate=1800)

    ani = animation.FuncAnimation(
        fig,
        update,
        len(all_sweep_data),
        fargs=[
            x_wavelengths,
            all_sweep_data,
            p1peaks,
            p2peaks,
            p1_offset_list,
            p2_offset_list,
            time_array,
        ],
        blit=True,
        repeat=False,
        interval=200,
    )

    # plt.show()
    if save_animation:
        anifilename = os.path.join(root, "animation.mp4")
        ani.save(anifilename, writer=writer)


if __name__ == "__main__":

    from datetime import datetime

    startTime = datetime.now()

    # Sweep times: How many minutes each sweep is apart from the next:
    sweep_timestep = 0.22  # minutes

    # Enter the name of the folder that contians the matlab vectors of different sweeps.
    # root_folder = r'C:\Users\eric1\Google Drive\UBC\CBR\Vinny COVID Project\Dec9Trial'
    root_folder = os.path.expanduser(
        r"D:\\Liu Yifei\\UBC\\COOP\\UBC Biophotonics\\Sample Data\\2022-03-10_Spike_Validation_Phase_0_Trial_1\\Bulk"
    )
    # import argparse
    # parser = argparse.ArgumentParser(
    #     description="MultiLorentzianFit with CLI parameters"
    # )
    # parser.add_argument(
    #     "folder",
    #     type=str,
    #     help="the absolute path to the folder containing laser*.mat file",
    # )
    # args = parser.parse_args()
    # root_folder=args.folder
    # print("Root folder is: "+root_folder)

    # r'C:\Users\MapleLeafStage\Documents\Dec23Trial'

    # root_folder = 'wave_power_vectors'

    # Enter the index of the power 1 peak that you would like to track (0, 1 or 2)
    track_p1_peak = 1

    # Enter the index of the power 2 peak that you would like to track (0,1 or 2)
    track_p2_peak = 1

    # Graphing the offset versus time.
    _grapher(
        root=root_folder,
        p1_index=track_p1_peak,
        p2_index=track_p2_peak,
        sweep_timestep=sweep_timestep,
        remove_spikes=False,
        pkProm=6,
        save_animation=0,
    )

    print("Program Time=", datetime.now() - startTime)
    plt.show()
