import csv
import logging
import multiprocessing as mp
import os
import re
from functools import reduce
from itertools import repeat, starmap
from typing import Optional

import numpy as np
from numpy.typing import NDArray
from scipy.io import loadmat

from .lib import get_lorentzian_peaks, peaks_to_traces

logger = logging.getLogger(__name__)


class PassiveAnalyzer(object):
    def __init__(
        self,
        folder_path: str,
        timestamp: str | float,
        pattern: str = r".*sweep_(\d+)\.mat",
        wavelength_multiplier: float = 1e9,
        timestamp_multiplier: float = 1 / 60,
    ):
        self.__folder_path = folder_path

        pat = re.compile(pattern)
        self.__filenames = sorted(
            list(filter(lambda x: pat.match(x), iter(os.listdir(folder_path)))),
            key=lambda x: int(pat.match(x).group(1)),  # type: ignore
        )

        self.__timestamps: NDArray[np.float64] = np.array([])
        if type(timestamp) is str:
            with open(os.path.join(self.__folder_path, timestamp), "r") as csv_file:
                time_dict: dict[int, float] = {
                    int(row[0]): float(row[2])
                    for row in csv.reader(csv_file, delimiter=",")
                    if len(row) >= 3 and row[2] != ""
                }
                self.__timestamps = (
                    np.array(
                        [
                            time_dict[int(pat.match(s).group(1))] for s in self.__filenames  # type: ignore
                        ]
                    )
                    * timestamp_multiplier
                )
        elif type(timestamp) is float:
            self.__timestamps = np.array(list(range(len(self.__filenames)))) * timestamp
        else:
            raise RuntimeError(
                "Timestamp must be a filename string or a time interval float"
            )

        # check the first file for wavelengths, assume all files have the same wavelengths
        self.__wavelengths = (
            read_mat(os.path.join(self.__folder_path, self.__filenames[0]))[1]
            * wavelength_multiplier
        )
        self.__wavelength_multiplier = wavelength_multiplier

    @property
    def timestamps(self):
        return self.__timestamps

    @property
    def wavelengths(self):
        return self.__wavelengths

    def info(self) -> tuple[int, int]:
        """Get the number of files in the folder and the number of powers in the first file.

        Returns:
            Tuple[number_of_files, number_of_powers]
        """
        return len(self.__filenames), len(
            read_mat(os.path.join(self.__folder_path, self.__filenames[0]))[0]
        )

    def get_spectrograms(
        self,
        channels: set[int],
        step: int = 1,
        start_index: int = 0,
        stop_index: int | None = None,
    ) -> dict[int, NDArray[np.float64]]:
        """Get spectrums at a given sample rate for the given channels.

        Args:
            `channels` (List[int]): the channel indexes e.g. [0,2,4] for channel 1,3,5
            `step` (int, optional): the down sample rate. Read one for each `step` files. Defaults to 1 (no down sample).

        Returns:
            `data`: Dict[K:`index`, V:`spectrogram`], where `spectrogram` is ready to be plotted with matplotlib.imshow()
        """
        data: dict[int, NDArray[np.float64]] = {}
        for f in self.__filenames[start_index:stop_index:step]:
            matrix, _ = read_mat(os.path.join(self.__folder_path, f))
            for key in channels:
                vector = np.flip(np.array([matrix[key]])).transpose()
                data[key] = np.hstack((data[key], vector)) if key in data else vector
        return data

    def analyze(
        self,
        channels: set[int],
        start_stop_step: tuple[int, Optional[int], int],
        r2_threshold: float,
        max_n100dBm_points: int,
        enable_multi_processing: bool = True,
    ) -> tuple[
        dict[int, tuple[list[list[float]], float]], dict[int, list[NDArray[np.float64]]]
    ]:
        """analyze

        Args:

            - channels (list[int]): the channel indexes e.g. [0,2,4] for channel 1,3,5
            - prominence (float): prominence for the peak detection
            - enable_multi_processing (bool, optional): Defaults to True. Set to false for debugging.

        Returns:

            - tuple[dict[int, tuple[list[list[float]], float]], dict[int, list[NDArray[np.float64]]] ]: traces dictionary and peaks dictionary, where keys are channel indexes and values are:

                - traces: (list of list of floats, FSR), the traces start at an actual peak wavelength in spectrogram.
                - peaks: list of sweep matrix, indexes are sweep number and values are rows of sweep vectors.
        """

        def __starmap(*args, **kwargs):
            if enable_multi_processing:
                process_num: int = 1 if os.cpu_count() is None else os.cpu_count()  # type: ignore
                return mp.Pool(processes=max(1, process_num - 2)).starmap(
                    *args, **kwargs
                )  # reserve one for GUI and one for other programs
            else:
                return starmap(*args, **kwargs)

        start, stop, step = start_stop_step[0], start_stop_step[1], start_stop_step[2]

        peaks: dict[int, list[NDArray[np.float64]]] = reduce(
            lambda acc, b: {
                x: acc.get(x, []) + b.get(x, []) for x in set(acc).union(b)  # type: ignore
            },
            __starmap(
                mat_to_peak_dict,
                zip(
                    [
                        os.path.join(self.__folder_path, f)
                        for f in self.__filenames[start:stop:step]
                    ],
                    repeat(channels),
                    repeat(self.__wavelength_multiplier),
                    repeat(r2_threshold),
                    repeat(max_n100dBm_points),
                ),
            ),
            {},
        )

        return {k: peaks_to_traces(v) for k, v in peaks.items()}, peaks

    def analyze_fsr_er_q(
        self,
        channels: set[int],
        start_stop_step: tuple[int, Optional[int], int],
        r2_threshold: float,
        max_n100dBm_points: int,
        enable_multi_processing: bool = True,
    ):
        def __starmap(*args, **kwargs):
            if enable_multi_processing:
                process_num: int = 1 if os.cpu_count() is None else os.cpu_count()  # type: ignore
                return mp.Pool(processes=max(1, process_num - 2)).starmap(
                    *args, **kwargs
                )  # reserve one for GUI and one for other programs
            else:
                return starmap(*args, **kwargs)

        start, stop, step = start_stop_step[0], start_stop_step[1], start_stop_step[2]

        fsr_er_q_dict: dict[
            int,
            list[tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]],
        ] = reduce(
            lambda acc, b: {
                x: acc.get(x, []) + b.get(x, []) for x in set(acc).union(b)  # type: ignore
            },
            __starmap(
                mat_to_fsr_er_q_dict,
                zip(
                    [
                        os.path.join(self.__folder_path, f)
                        for f in self.__filenames[start:stop:step]
                    ],
                    repeat(channels),
                    repeat(self.__wavelength_multiplier),
                    repeat(r2_threshold),
                    repeat(max_n100dBm_points),
                ),
            ),
            {},
        )

        return fsr_er_q_dict


def read_mat(
    file_path: str,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    mat: dict[str, NDArray[np.float64]] = loadmat(file_path)
    power = np.array(mat["power"]).transpose()
    wavelengths = np.array(mat["wavelength"][0])
    if power.shape[1] != wavelengths.shape[0]:
        raise RuntimeError("Number of wavelengths and powers do not match")
    return (power, wavelengths)


def mat_to_peak_dict(
    path: str,
    channels: set[int],
    wavelength_multiplier: float,
    r2_threshold: float,
    max_n100dBm_points: int,
) -> dict[int, list[list[NDArray[np.float64]]]]:
    """_mat_to_peak_dict

    Args:
        path (str): path to .mat file
        channels (list[int]): indices of channels to be parsed
        wavelength_multiplier (float): wavelength multiplier

    Returns:
        dict[int, list[list[NDArray[np.float64]]]]: dict of peaks, key=channel, value=list of peaks
    """
    ret = {}
    power_matrix, wavelengths = read_mat(path)
    wavelengths *= wavelength_multiplier
    for c in channels:
        powers = power_matrix[c]
        temp_peaks = get_lorentzian_peaks(
            powers,
            wavelengths,
            r2_threshold=r2_threshold,
            max_n100dBm_points=max_n100dBm_points,
        )[0]
        ret[c] = ret.get(c, []) + [temp_peaks]

    return ret


def mat_to_fsr_er_q_dict(
    path: str,
    channels: set[int],
    wavelength_multiplier: float,
    r2_threshold: float,
    max_n100dBm_points: int,
) -> dict[int, list[list[NDArray[np.float64]]]]:
    """_mat_to_fsr_er_q_dict

    Args:
        path (str): path to .mat file
        channels (list[int]): indices of channels to be parsed
        wavelength_multiplier (float): wavelength multiplier

    Returns:
        dict[int, list[list[NDArray[np.float64]]]]: dict of fsr,er,q, key=channel, value=list of (fsr,er,q)
    """
    ret = {}
    power_matrix, wavelengths = read_mat(path)
    wavelengths *= wavelength_multiplier
    for c in channels:
        powers = power_matrix[c]
        __peaks, fsr, er, q = get_lorentzian_peaks(
            powers,
            wavelengths,
            r2_threshold=r2_threshold,
            max_n100dBm_points=max_n100dBm_points,
        )
        ret[c] = ret.get(c, []) + [(fsr, er, q)]

    return ret
