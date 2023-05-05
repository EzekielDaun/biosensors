import re
import os
from functools import lru_cache


import logging

import numpy as np
from numpy.typing import NDArray

from scipy.signal import find_peaks, lsim, sawtooth
from scipy.ndimage import gaussian_filter1d

logger = logging.getLogger(__name__)


class RampUpSweepCSVReader(object):
    def __init__(
        self,
        base_folder: str,
        pattern: re.Pattern,
        freq: float,
        timestamp_file="timeSteps.csv",
    ):
        self.__filepaths = [
            os.path.join(base_folder, f)
            for f in sorted(
                list(filter(lambda x: pattern.match(x), iter(os.listdir(base_folder)))),
                key=lambda x: int(pattern.match(x).group(1)),  # type: ignore
            )
        ]
        self.__freq = freq
        timestamp_csv = np.loadtxt(
            os.path.join(base_folder, timestamp_file), delimiter=",", dtype="object"
        ).T
        self.__timestamps: dict[str, float] = {
            k: v for k, v in zip(timestamp_csv[3], timestamp_csv[1])
        }

    def __iter__(self):
        for filepath in self.__filepaths:
            print(f"Reading \042{os.path.basename(filepath)}\042")

            data = np.loadtxt(filepath, delimiter=",")[:].T
            power, reference = data[0], data[1]

            maxima, _ = find_peaks(
                gaussian_filter1d(reference, 1),
                prominence=(np.max(reference) - np.min(reference)) * 0.9,
            )

            minima, _ = find_peaks(
                gaussian_filter1d(-reference, 1),
                prominence=(np.max(reference) - np.min(reference)) * 0.9,
            )

            if minima[0] > maxima[0]:
                maxima = maxima[1:]
            if minima[-1] > maxima[-1]:
                minima = minima[:-1]

            if len(minima) != len(maxima):
                raise ValueError(
                    "number of minima and maxima mismatch in reference signal"
                )

            for i, (start, stop) in enumerate(zip(minima, maxima)):
                p = power[start:stop]
                t = (
                    float(self.__timestamps[os.path.basename(filepath)])
                    + i / self.__freq
                )
                yield p, t
            print(f"end of  \042{os.path.basename(filepath)}\042")


@lru_cache()
def thermal_simulation(sweep_freq: float, t_final: int, len_period: int, tau: float):
    pole = 1 / tau
    t = np.arange(0, t_final, 1 / sweep_freq / len_period)

    v = sawtooth(2 * np.pi * sweep_freq * t)
    v -= min(v)
    v *= 0.5  # scale to 0-1
    u = v**2

    system = ([1.0], [1.0, pole])  # transfer function 1/(s+p)
    t, y, x = lsim(system, u, t)
    y = y[-len_period:]
    return y


def generate_wavelength(
    power: NDArray[np.float64],
    reference_temp_sweep: NDArray[np.float64],
    wavelength_range=(1309, 1310),
    **kwargs,
):
    reference_temp_sweep = np.interp(  # interpolate to the same length as power
        np.linspace(0, 1, len(power)),
        np.linspace(0, 1, len(reference_temp_sweep)),
        reference_temp_sweep,
    )
    index = np.argmin(reference_temp_sweep)
    temp = reference_temp_sweep[index:]
    temp = -temp
    temp -= temp.min()
    temp /= temp.max()
    wavelength = (  # scale to wavelength range
        wavelength_range[0] + (wavelength_range[1] - wavelength_range[0]) * temp
    )
    power = power[index:]

    indices = np.argsort(wavelength)
    wavelength = wavelength[indices]
    power = power[indices]
    return wavelength, power
