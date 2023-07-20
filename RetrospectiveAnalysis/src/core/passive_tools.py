import csv
import logging
import multiprocessing as mp
import os
import re
from functools import partial, reduce
from typing import Optional

import numpy as np
from numpy.typing import NDArray
from scipy.io import loadmat
from tqdm import tqdm

from .lib import SweepFitResult, peaks_to_traces

logger = logging.getLogger(__name__)


class PassiveAnalyzer(object):
    def __init__(
        self,
        folder_path: str,
        timestamp: str | float,
        pattern: str = r".*sweep_(\d+)\.mat",
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
                self.__filenames = [
                    f
                    for f in self.__filenames
                    if int(pat.match(f).group(1)) in time_dict  # type: ignore
                ]
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
        self.__wavelengths = read_mat(
            os.path.join(self.__folder_path, self.__filenames[0])
        )[1]
        self.__wavelengths *= 1e9  # assume input in m and convert to nm

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
    ):
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

        def __map(*args, **kwargs):
            if enable_multi_processing:
                process_num: int = 1 if os.cpu_count() is None else os.cpu_count()  # type: ignore
                return mp.Pool(processes=max(1, process_num - 2)).imap(
                    *args, **kwargs
                )  # reserve one for GUI and one for other programs
            else:
                return map(*args, **kwargs)

        start, stop, step = start_stop_step[0], start_stop_step[1], start_stop_step[2]

        sweep_fit_dict: dict[int, list[SweepFitResult]] = reduce(
            lambda acc, b: {
                x: acc.get(x, []) + b.get(x, []) for x in set(acc).union(b)  # type: ignore
            },
            tqdm(
                __map(
                    partial(mat_to_sweep_fit_results, channels=channels),
                    self.__filenames[start:stop:step],
                ),
                total=len(self.__filenames[start:stop:step]),
            ),
            {},
        )

        peaks_dict = {
            k: [s.get_peaks(r2_threshold, max_n100dBm_points) for s in v]
            for k, v in sweep_fit_dict.items()
        }

        return {k: peaks_to_traces(v) for k, v in peaks_dict.items()}, peaks_dict

    def analyze_fsr_er_q(
        self,
        channels: set[int],
        start_stop_step: tuple[int, Optional[int], int],
        r2_threshold: float,
        max_n100dBm_points: int,
        enable_multi_processing: bool = True,
    ):
        def __map(*args, **kwargs):
            if enable_multi_processing:
                process_num: int = 1 if os.cpu_count() is None else os.cpu_count()  # type: ignore
                return mp.Pool(processes=max(1, process_num - 2)).imap(
                    *args, **kwargs
                )  # reserve one for GUI and one for other programs
            else:
                return map(*args, **kwargs)

        start, stop, step = start_stop_step[0], start_stop_step[1], start_stop_step[2]

        sweep_fit_dict: dict[int, list[SweepFitResult]] = reduce(
            lambda acc, b: {
                x: acc.get(x, []) + b.get(x, []) for x in set(acc).union(b)  # type: ignore
            },
            tqdm(
                __map(
                    partial(mat_to_sweep_fit_results, channels=channels),
                    self.__filenames[start:stop:step],
                ),
                total=len(self.__filenames[start:stop:step]),
            ),
            {},
        )

        return {
            k: [
                (
                    s.get_fsr(r2_threshold, max_n100dBm_points),
                    s.get_er(r2_threshold, max_n100dBm_points),
                    s.get_q(r2_threshold, max_n100dBm_points),
                )
                for s in v
            ]
            for k, v in sweep_fit_dict.items()
        }


def read_mat(
    file_path: str,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    mat: dict[str, NDArray[np.float64]] = loadmat(file_path)
    power = np.array(mat["power"]).transpose()
    wavelengths = np.array(mat["wavelength"][0])
    if power.shape[1] != wavelengths.shape[0]:
        raise RuntimeError("Number of wavelengths and powers do not match")
    return (power, wavelengths)


def mat_to_sweep_fit_results(file_path: str, channels: set[int]):
    power, wavelength = read_mat(file_path)
    return {c: [SweepFitResult.from_data(power[c], wavelength * 1e9)] for c in channels}
