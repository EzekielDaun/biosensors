import csv
import logging
import multiprocessing as mp
import os
import re
from abc import abstractmethod
from dataclasses import dataclass
from functools import lru_cache, partial, reduce
from itertools import islice
from typing import Iterator

import numpy as np
from numpy.typing import NDArray
from scipy.io import loadmat
from tqdm import tqdm

from .lib import SweepFitResult, peaks_to_traces_default
from .utils.tqdm_qt import tqdm_qt

logger = logging.getLogger(__name__)


Data = tuple[float, NDArray[np.floating], NDArray[np.floating]]
Sweep = NDArray[np.floating]


class DataReaderBase:
    @abstractmethod
    def __iter__(self) -> Iterator[Data]:
        # return the timestamp, wavelength of a sweep and the sweep 2D power data itself
        ...

    @abstractmethod
    def __len__(self) -> int:
        ...

    @abstractmethod
    def __getitem__(self, index: int) -> Data:
        ...

    @abstractmethod
    def sweep_only(self) -> Iterator[Sweep]:
        ...


@lru_cache
def read_mat(file_path: str) -> tuple[NDArray[np.floating], NDArray[np.floating]]:
    mat: dict[str, NDArray[np.floating]] = loadmat(file_path)
    power = np.array(mat["power"]).transpose()
    wavelengths = np.array(mat["wavelength"][0])
    if power.shape[1] != wavelengths.shape[0]:
        raise RuntimeError("Number of wavelengths and powers do not match")
    return (power, wavelengths)


@dataclass(frozen=True)
class MatDataReader(DataReaderBase):
    files: list[str]
    timestamps: NDArray[np.floating]

    @staticmethod
    def new(
        dir: str,
        files: list[str],
        timestamp_input: str | float,
        multiplier: float = 1,
    ):
        files = [os.path.join(dir, f) for f in files]
        match timestamp_input:
            case float():
                return MatDataReader(
                    files=files,
                    timestamps=np.arange(len(files)) * timestamp_input,
                )
            case str():
                with open(timestamp_input) as csv_file:
                    time_dict: dict[str, float] = {
                        str(row[1]): float(row[2])
                        for row in csv.reader(csv_file, delimiter=",")
                        if len(row) >= 3 and row[2] != ""
                    }
                    base_names = [b for f in files if (b := os.path.basename(f)) in time_dict]  # type: ignore
                    timestamps = (
                        np.array(
                            [time_dict.get(k) for k in base_names], dtype=np.float64
                        )
                        * multiplier
                    )
                    return MatDataReader(files=files, timestamps=timestamps)

    def __iter__(self) -> Iterator[Data]:
        for t, f in zip(self.timestamps, self.files):
            power, wavelength = read_mat(f)
            yield t, wavelength, power

    def __len__(self) -> int:
        return len(self.files)

    def __getitem__(self, index: int) -> Data:
        power, wavelength = read_mat(self.files[index])
        timestamp = self.timestamps[index]
        return timestamp, wavelength, power

    def sweep_only(self) -> Iterator[Sweep]:
        for _, _, power in self:
            yield power


def _powers_to_sweep_fit_results(
    powers: NDArray[np.floating], wavelengths: NDArray[np.floating], channels: set[int]
):
    return {c: [SweepFitResult.from_data(powers[c], wavelengths)] for c in channels}


class PassiveAnalyzer(object):
    def __init__(
        self,
        folder_path: str,
        timestamp: str | float,
        pattern: str = r".*sweep_(\d+)\.mat",
        timestamp_multiplier: float = 1 / 60,
    ):
        pat = re.compile(pattern)
        filenames = sorted(
            list(filter(lambda x: pat.match(x), iter(os.listdir(folder_path)))),
            key=lambda x: int(pat.match(x).group(1)),  # type: ignore
        )
        self.__data_reader: DataReaderBase = MatDataReader.new(
            folder_path, filenames, timestamp, timestamp_multiplier
        )

    @property
    def timestamps(self):
        return [t for t, _, _ in self.__data_reader]

    @property
    def wavelengths(self):
        _, wavelengths, _ = self.__data_reader[0]
        return wavelengths * 1e9

    def info(self) -> tuple[int, int]:
        """Get the number of files in the folder and the number of powers in the first file.

        Returns:
            Tuple[number_of_files, number_of_powers]
        """
        _, _, powers = self.__data_reader[0]

        return len(self.__data_reader), powers.shape[0]

    def get_spectrograms(
        self,
        channels: set[int],
        step: int = 1,
        start_index: int = 0,
        stop_index: int | None = None,
    ) -> dict[int, NDArray[np.floating]]:
        """Get spectrums at a given sample rate for the given channels.

        Args:
            `channels` (List[int]): the channel indexes e.g. [0,2,4] for channel 1,3,5
            `step` (int, optional): the down sample rate. Read one for each `step` files. Defaults to 1 (no down sample).

        Returns:
            `data`: Dict[K:`index`, V:`spectrogram`], where `spectrogram` is ready to be plotted with matplotlib.imshow()
        """
        data: dict[int, NDArray[np.floating]] = {}
        for matrix in islice(
            self.__data_reader.sweep_only(), start_index, stop_index, step
        ):
            for key in channels:
                vector = np.flip(np.array([matrix[key]])).transpose()
                data[key] = np.hstack((data[key], vector)) if key in data else vector
        return data

    def analyze(
        self,
        channels: set[int],
        start_stop_step: tuple[int, int, int],
        r2_threshold: float,
        max_n100dBm_points: int,
        qt_signal=None,
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
        start, stop, step = start_stop_step[0], start_stop_step[1], start_stop_step[2]

        with mp.Pool() as pool:
            sweep_fit_dict: dict[int, list[SweepFitResult]] = reduce(
                lambda acc, b: {
                    x: acc.get(x, []) + b.get(x, []) for x in set(acc).union(b)  # type: ignore
                },
                tqdm_qt(
                    pool.imap(
                        partial(
                            _powers_to_sweep_fit_results,
                            wavelengths=self.wavelengths,
                            channels=channels,
                        ),
                        islice(self.__data_reader.sweep_only(), start, stop, step),
                    ),
                    total=(stop - start) // step,
                    qt_signal=qt_signal,
                ),
                {},
            )

        peaks_dict = {
            k: [s.get_peaks(r2_threshold, max_n100dBm_points) for s in v]
            for k, v in sweep_fit_dict.items()
        }

        for k, v in peaks_dict.items():
            if v[0].shape[0] == 0:
                raise RuntimeError(
                    f"The first sweep in channel {k+1} has no peaks detected. Consider adjusting the R2 threshold, -100dBm threshold or skipping this sweep."
                )

        return {k: peaks_to_traces_default(v) for k, v in peaks_dict.items()}, peaks_dict  # type: ignore

    def analyze_fsr_er_q(
        self,
        channels: set[int],
        start_stop_step: tuple[int, int, int],
        r2_threshold: float,
        max_n100dBm_points: int,
    ):
        start, stop, step = start_stop_step[0], start_stop_step[1], start_stop_step[2]

        with mp.Pool() as pool:
            sweep_fit_dict: dict[int, list[SweepFitResult]] = reduce(
                lambda acc, b: {
                    x: acc.get(x, []) + b.get(x, []) for x in set(acc).union(b)  # type: ignore
                },
                tqdm(
                    pool.imap(
                        partial(
                            _powers_to_sweep_fit_results,
                            wavelengths=self.wavelengths,
                            channels=channels,
                        ),
                        islice(self.__data_reader.sweep_only(), start, stop, step),
                    ),
                    total=(stop - start) // step,
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
