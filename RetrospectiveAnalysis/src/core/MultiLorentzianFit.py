import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
import copy
import time

import argparse


class LorentzianFitting:
    def __init__(self, power, wavelength, pkProm):
        self.raw_power_array, self.nm_wavelength = self.return_sweep_data(
            power, wavelength
        )
        # Normalizing the power array:
        self.min = min(self.raw_power_array)
        self.max = max(self.raw_power_array)
        self.norm_power_array = np.array(
            (self.raw_power_array - self.min) / (self.max - self.min)
        )

        # Finding the peak prominence for the normalized array:
        self.prom = pkProm / (self.max - self.min)
        self.peaks, _ = find_peaks((-1) * self.norm_power_array, prominence=self.prom)
        self.dist_bt_peaks = self.get_dist_bt_peaks(self.peaks)
        # self.parabolic_params = np.load('Normalized Grating Coupler Curves/params.npy')

    def parabola_fit(self, x, a, b, c):
        return a * x**3 + b * x**2 + c

    def return_sweep_data(self, raw_power, wavelength):
        # matlab_vector = loadmat('wave_power_vectors/laser_sweep_852.mat')  # loading the matlab vector
        #
        # raw_power, wavelength = matlab_vector['power1'][0], matlab_vector['wavelength'][0]
        raw_power = np.array(raw_power * 1)
        wavelength = np.array(wavelength)
        # Making both of these float types:
        raw_power = raw_power.astype("float")
        wavelength = wavelength.astype("float")
        wavelength = [x * 1e12 for x in wavelength]
        # retrieving the values for the power1 channel. (dBm)
        return raw_power, wavelength

    def get_dist_bt_peaks(self, peaks):
        if len(peaks) == 1 and peaks[0] == 1613:
            plt.plot(self.nm_wavelength, self.raw_power_array)
            plt.show()
            print("------------------------")
        avg_dist_bt_peaks = np.mean(
            [peaks[x + 1] - peaks[x] for x in list(range(0, len(peaks) - 1))]
        )
        return int(avg_dist_bt_peaks)

    def remove_peaks(self, p_array, range_fraction=0.1):
        power_array = np.array(copy.deepcopy(p_array))
        wavelength = np.array(copy.deepcopy(self.nm_wavelength))

        # Tagging peak areas as NaN
        for peak in self.peaks:
            st = int(peak - self.dist_bt_peaks * range_fraction)
            end = int(peak + self.dist_bt_peaks * range_fraction)
            if st < 0:
                st = 0
            if end >= len(p_array):
                end = len(p_array) - 1
            power_array[st:end] = np.nan
            wavelength[st:end] = np.nan

        # Removing NaN from arrays:
        power_array = power_array[~np.isnan(power_array)]
        wavelength = wavelength[~np.isnan(wavelength)]

        # Removing the ends:
        amt_to_rem = int(0.02 * len(power_array))
        power_array = power_array[amt_to_rem : (len(power_array) - amt_to_rem)]
        wavelength = wavelength[amt_to_rem : (len(wavelength) - amt_to_rem)]

        return np.array(power_array), np.array(wavelength)

    def lorentzian_overlay(self, power, peak_index, range_fraction=0.5, graph=False):
        def lorentzian(x, x0, I, gam, Yo):
            return I * gam**2 / (gam**2 + (x - x0) ** 2) + Yo

        # Prepping a slice for adding lorentzian on a single peak
        slice_start = int(peak_index - self.dist_bt_peaks * range_fraction)
        if slice_start < 0:
            slice_start = 0
        slice_end = int(peak_index + self.dist_bt_peaks * range_fraction)
        if slice_end >= len(power):
            slice_end = len(power) - 1

        # print("Slice", self.nm_wavelength[slice_start], self.nm_wavelength[slice_end])
        # Creating that slice
        power_slice = power[slice_start:slice_end]
        wavelength_slice = np.array(self.nm_wavelength[slice_start:slice_end])

        # Fitting the lorentzian paratmeters
        st_pk = self.nm_wavelength[peak_index]
        bnds = ([st_pk - 1000, -0.9, -1000, -0.4], [st_pk + 1000, -0.1, -10, 0])
        p0 = [self.nm_wavelength[peak_index], -0.7, -80, 0]
        power_fitted = curve_fit(
            lorentzian, wavelength_slice, power_slice, p0=p0, bounds=bnds
        )

        # Generating new fitted power array using lorentzian parameters and function
        x0, I, gam, Yo = power_fitted[0]

        if graph == False:
            return x0 * 1e-12
        # Generating high res arrays:
        high_res_wave_slice = np.arange(
            np.min(wavelength_slice), np.max(wavelength_slice), 0.1
        )
        high_res_grating_curve = np.array(
            [
                self.parabola_fit(
                    x,
                    self.parabolic_params[0],
                    self.parabolic_params[1],
                    self.parabolic_params[2],
                )
                for x in high_res_wave_slice
            ]
        )

        fitted_power_slice = np.array(
            [lorentzian(x, x0, I, gam, Yo) for x in high_res_wave_slice]
        )
        # print("Lorentzian Peak (nm) = ", x0/1000, "Raw Peak (nm) = ", self.nm_wavelength[peak_index]/1000)
        #
        # Printing the idfferenct between actual and theoretical:
        # print("Theoretical Lorentzian Parameters", power_fitted[0])
        # print("Theoretical Lorentzian Peak=", x0)
        # print("Raw Peak", self.nm_wavelength[peak_index])

        # # Showing raw data and lorentzian peak overlayed on a graph after re-scaling back to original values:
        # fig,ax = plt.subplots()
        # plt.title("Lorenztian Curve Fit - Grating coupler response")
        # ax.plot(self.nm_wavelength,power*(self.max-self.min)+self.max, color= 'blue', label= 'raw')
        # ax.plot(high_res_wave_slice,fitted_power_slice*(self.max-self.min)+self.max, color= 'orange', label = 'Lorentzian')
        # plt.ylabel('Power(dbm)')
        # plt.xlabel('Wavelength (picometers)')
        # ax.text(0.05, 0.2, 'Lorentzian Peak Location: \n %.3f' % (x0/1000) + 'nm', transform=ax.transAxes, fontsize=8,
        #         verticalalignment='bottom')
        # ax.text(0.05, 0.1, 'Raw Peak Location: \n %.3f' % (self.nm_wavelength[peak_index]/1000) + 'nm', transform=ax.transAxes, fontsize=8,
        #         verticalalignment='bottom')
        #
        # plt.legend(loc = 'lower right')
        # plt.show()
        # returning the theoretical lorentzian peak location
        return (
            x0 * 1e-12,
            high_res_wave_slice * 1e-12,
            (fitted_power_slice + high_res_grating_curve) * (self.max - self.min)
            + self.min,
        )

    def parabolic_overlay(self):
        downsample_factor = 10  # start with a downsample factor of 10 to reduce processing time -- we don't need so many points for the rough parabola fit
        rem_power, rem_wave = self.remove_peaks(self.norm_power_array)
        # downsample the power and wavelength by the downsample factor to reduce processing time
        rem_power = rem_power[::downsample_factor]
        rem_wave = rem_wave[::downsample_factor]
        # fit the curve
        rem_power_fit_params = curve_fit(self.parabola_fit, rem_wave, rem_power)
        a, b, c = rem_power_fit_params[0]

        self.grating_curve = np.array(
            [self.parabola_fit(x, a, b, c) for x in self.nm_wavelength]
        )
        self.parabolic_params = (a, b, c)
        # np.save('Normalized Grating Coupler Curves/params.npy',np.array([a,b,c]))
        adjusted_power = np.subtract(self.norm_power_array, self.grating_curve)

        # plt.figure()
        # plt.title('Normalization and removal of grating coupler response')
        # plt.plot(self.nm_wavelength,self.norm_power_array,color='blue',label = 'Normalized data')
        # plt.plot(self.nm_wavelength,grating_curve,color='red',label = 'Grating coupler response- 3rd order parabola')
        # plt.plot(self.nm_wavelength,adjusted_power,color = 'green', label = 'Normalized - grating coupler response')
        # plt.ylabel('Normalized Power')
        # plt.xlabel('Wavelength (pm)')
        # plt.legend()
        # plt.draw()
        return adjusted_power


# if __name__ == "__main__":
#     # Loading in the matlab vector
#     start_time = time.time()

#     matlab_vector = loadmat("../../../Documents/wave_power_vectors/laser_sweep_200.mat")
#     raw_power, wavelength = matlab_vector["power1"][0], matlab_vector["wavelength"][0]

#     SweepFit = LorentzianFitting(raw_power, wavelength)

#     import_time = time.time()
#     print("Import time =", import_time - start_time)

#     adjusted_power = SweepFit.parabolic_overlay()

#     parabolic_time = time.time()
#     print("parabolic time = ", parabolic_time - import_time)

#     peak_loc = SweepFit.lorentzian_overlay(
#         adjusted_power, peak_index=616, range_fraction=0.1
#     )

#     lorentz_time = time.time()
#     print("Lorentzian Time = ", lorentz_time - parabolic_time)
#     print("Total Time = ", time.time() - start_time)

#     plt.figure()
#     plt.plot(SweepFit.nm_wavelength, SweepFit.raw_power_array)
#     plt.title("Raw Data")
#     plt.draw()

#     plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="MultiLorentzianFit with CLI parameters"
    )
    parser.add_argument(
        "file",
        type=str,
        help="the absolute path to laser*.mat file",
    )
    args = parser.parse_args()

    # Loading in the matlab vector
    start_time = time.time()

    matlab_vector = loadmat(args.file, appendmat=False)
    raw_power, wavelength = matlab_vector["power1"][0], matlab_vector["wavelength"][0]

    SweepFit = LorentzianFitting(raw_power, wavelength, 1)

    import_time = time.time()
    print("Import time =", import_time - start_time)

    adjusted_power = SweepFit.parabolic_overlay()

    parabolic_time = time.time()
    print("parabolic time = ", parabolic_time - import_time)

    peak_loc = SweepFit.lorentzian_overlay(
        adjusted_power, peak_index=616, range_fraction=0.1
    )

    lorentz_time = time.time()
    print("Lorentzian Time = ", lorentz_time - parabolic_time)
    print("Total Time = ", time.time() - start_time)

    plt.figure()
    plt.plot(SweepFit.nm_wavelength, SweepFit.raw_power_array)
    plt.title("Raw Data")
    plt.draw()

    plt.show()
