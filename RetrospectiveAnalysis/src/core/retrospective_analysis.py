import csv
import logging
import multiprocessing as mp
import os
import re
from functools import reduce
from itertools import accumulate, pairwise, product, repeat, starmap

from typing import Optional

import numpy as np
from numpy.typing import NDArray
from scipy.io import loadmat
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
from scipy.spatial.distance import cdist
from scipy.ndimage import gaussian_filter1d
from sklearn.metrics import r2_score

logger = logging.getLogger(__name__)


def lorentzian(x, x0, y0, _i, gamma, a):
    return (
        y0
        + ((_i * (gamma / 2) ** 2) / ((gamma / 2) ** 2 + (x - x0) ** 2))
        + a * (x - x0)
    )


def read_mat(
    file_path: str,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    mat: dict[str, NDArray[np.float64]] = loadmat(file_path)
    power = np.array(mat["power"]).transpose()
    wavelengths = np.array(mat["wavelength"][0])
    if power.shape[1] != wavelengths.shape[0]:
        raise RuntimeError("Number of wavelengths and powers do not match")
    return (power, wavelengths)


def get_lorentzian_peaks(
    powers: NDArray[np.float64],
    wavelengths: NDArray[np.float64],
) -> tuple[
    NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]
]:

    if len(powers) != len(wavelengths):
        raise RuntimeError("Number of wavelengths and powers do not match")

    powers_smoothed: NDArray[np.float64] = gaussian_filter1d(
        powers, sigma=8
    )  # type: ignore
    indices, properties = find_peaks(
        -1 * powers_smoothed,
        prominence=0.1 * (max(powers_smoothed) - min(powers_smoothed)),
        width=0,
        height=min(-1 * powers_smoothed),
    )
    __base_indices = [int(np.mean(p)) for p in pairwise(indices)]
    left_base_indices = [0] + __base_indices
    right_base_indices = __base_indices + [len(powers_smoothed) - 1]

    ret_peaks: list[tuple[float, float, float, float]] = []
    ret_er: list[float] = []
    ret_q: list[float] = []
    for i, peak_index in enumerate(indices):
        left_base_index = max(properties["left_bases"][i], left_base_indices[i])
        right_base_index = min(properties["right_bases"][i], right_base_indices[i])

        wavelength_range = wavelengths[left_base_index:right_base_index]
        power_range = powers[left_base_index:right_base_index]
        indices_fixed = np.argwhere(power_range != float(-100)).flatten()
        if len(indices_fixed) <= 8 or max(np.diff(indices_fixed) > 10):
            continue
        wavelength_fixed = wavelength_range[indices_fixed]
        power_fixed = power_range[indices_fixed]

        try:
            parameters, _ = curve_fit(
                f=lorentzian,
                xdata=wavelength_fixed,
                ydata=power_fixed,
                p0=[
                    wavelengths[peak_index],  # x0
                    np.mean([powers[left_base_index], powers[right_base_index]]),  # y0
                    -100,  # I
                    0.01
                    * (
                        wavelengths[right_base_index] - wavelengths[left_base_index]
                    ),  # gamma
                    0,  # a
                ],
                bounds=(
                    [
                        wavelengths[left_base_index],
                        -100,
                        -100,
                        0,
                        -np.inf,
                    ],
                    [
                        wavelengths[right_base_index],
                        10,
                        0,
                        max(wavelength_fixed) - min(wavelength_fixed),
                        np.inf,
                    ],
                ),
            )

            x0, y0, _i, gamma, a = parameters
            if (
                r2_score(
                    power_fixed,
                    lorentzian(
                        wavelength_fixed,
                        x0,
                        y0,
                        _i,
                        gamma,
                        a,
                    ),
                )
                < 0.80
            ):
                logger.debug(
                    f"R2 score too low for peak at wavelength {wavelengths[peak_index]:.2f}. R2 = {r2_score(power_fixed, lorentzian(wavelength_fixed, x0, y0, _i, gamma, a)):.2f}"
                )
                continue
            else:
                ret_peaks.append(parameters)
                ret_er.append(-parameters[2])
                xs = wavelengths[left_base_index:right_base_index]
                ys_linear = 10 ** ((powers[left_base_index:right_base_index]) / 10)
                ys_linear *= 1e3  # value too small will cause nonsense fitting result

                params_linear, _ = curve_fit(
                    f=lorentzian,
                    xdata=xs,
                    ydata=ys_linear,
                    p0=[
                        x0,
                        0,
                        -1e3 * 1e-3,
                        0.01
                        * (
                            wavelengths[right_base_index] - wavelengths[left_base_index]
                        ),
                        0,
                    ],
                    bounds=(
                        [wavelengths[left_base_index], 0, -1e3, 0, -np.inf],
                        [np.inf, 1, 0, np.inf, np.inf],
                    ),
                )
                ret_q.append(params_linear[0] / params_linear[3])

        except RuntimeError as e:
            logger.debug(
                f"Curve fitting at wavelength {wavelengths[peak_index]:.2f}: {e}"
            )
            continue
    ret_fsr = np.diff(np.array(ret_peaks).T[0]) if len(ret_peaks) > 1 else np.array([])
    return np.array(ret_peaks), np.array(ret_fsr), np.array(ret_er), np.array(ret_q)


def _mat_to_peak_dict(
    path: str,
    channels: list[int],
    wavelength_multiplier: float,
) -> dict[int, list[list[NDArray[np.float64]]]]:
    ret = {}
    power_matrix, wavelengths = read_mat(path)
    wavelengths *= wavelength_multiplier
    for c in channels:
        powers = power_matrix[c]
        temp_peaks = get_lorentzian_peaks(
            powers,
            wavelengths,
        )[0]
        ret[c] = ret.get(c, []) + [temp_peaks]

    return ret


def _mat_to_fsr_er_q_dict(
    path: str,
    channels: list[int],
    wavelength_multiplier: float,
) -> dict[int, list[list[NDArray[np.float64]]]]:
    ret = {}
    power_matrix, wavelengths = read_mat(path)
    wavelengths *= wavelength_multiplier
    for c in channels:
        powers = power_matrix[c]
        __peaks, fsr, er, q = get_lorentzian_peaks(
            powers,
            wavelengths,
        )
        ret[c] = ret.get(c, []) + [(fsr, er, q)]

    return ret


class RetrospectiveAnalyzer(object):
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

        # check the first file for wavelengths
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
        channels: list[int],
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
        channels: list[int],
        start_stop_step: tuple[int, Optional[int], int],
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
                _mat_to_peak_dict,
                zip(
                    [
                        os.path.join(self.__folder_path, f)
                        for f in self.__filenames[start:stop:step]
                    ],
                    repeat(channels),
                    repeat(self.__wavelength_multiplier),
                ),
            ),
            {},
        )

        return {k: _peaks_to_traces(v) for k, v in peaks.items()}, peaks

    def analyze_fsr_er_q(
        self,
        channels: list[int],
        start_stop_step: tuple[int, Optional[int], int],
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
                _mat_to_fsr_er_q_dict,
                zip(
                    [
                        os.path.join(self.__folder_path, f)
                        for f in self.__filenames[start:stop:step]
                    ],
                    repeat(channels),
                    repeat(self.__wavelength_multiplier),
                ),
            ),
            {},
        )

        return fsr_er_q_dict


def _peaks_to_traces(
    peaks: list[NDArray[np.float64]],
) -> tuple[list[list[float]], float]:
    """__peaks_to_traces

    Convert sweeps (in matrix form) into a few traces with FSR

    Args:
        peaks (list[NDArray[np.float64]]): list of sweeps in matrix form where each row is a peak vector

    Returns:
        tuple[list[list[float]], float]: ([traces], FSR)
    """

    FSR = float(
        np.mean(
            [d for sweep in peaks[::10] if sweep.ndim > 1 for d in np.diff(sweep[:, 0])]
        )
    )
    population: NDArray[np.float64] = np.array(
        [p for sweep in peaks[::10] for p in sweep]
    )
    mean_population = np.mean(population, axis=0)
    std_population = np.std(population, axis=0)

    pair_iter = enumerate(pairwise(peaks))

    ret: list[list[float]] = []
    shifts: list[float] = []
    start_wavelength: float = peaks[0][0][0]
    last_peak = peaks[0][0]
    for i, (p1s, p2s) in pair_iter:
        ps = sorted(  # possible peaks in p2s to pair with the last peak
            [p for p in p2s if abs(p[0] - last_peak[0]) < 0.3 * FSR],
            key=lambda x: cdist(
                [(x[1:] - mean_population[1:]) / std_population[1:]],
                [(last_peak[1:] - mean_population[1:]) / std_population[1:]],
                "cosine",
            )[0][0],
        )
        if (  # normal case, a small shift near the last tracked peak is found and their shapes are similar
            ps and cdist([ps[0][1:]], [last_peak[1:]], "cosine")[0][0] < 0.1
        ):
            shifts.append(ps[0][0] - last_peak[0])
            last_peak: NDArray[np.float64] = ps[0]
            continue
        else:
            pairs = sorted(  # match other peaks in case that the peak correspond to the last peak is missing due to noise
                product([p for p in p1s if p[0] != last_peak[0]], p2s),
                key=lambda x: cdist(
                    # [(x[0][1:] - mean_population[1:]) / std_population[1:]],
                    # [(x[1][1:] - mean_population[1:]) / std_population[1:]],
                    [(x[0][:] - mean_population[:]) / std_population[:]],
                    [(x[1][:] - mean_population[:]) / std_population[:]],
                    "cosine",
                )[0][0],
            )
            if (
                # if no other peaks in p1s
                len(pairs) <= 0
                or
                # if the minimum difference in shape is still too large
                cdist(
                    [(pairs[0][0][1:] - mean_population[1:]) / std_population[1:]],
                    [(pairs[0][1][1:] - mean_population[1:]) / std_population[1:]],
                    "cosine",
                )[0][0]
                > 0.1
            ):
                shifts.append(np.nan)
                logger.warning(
                    f"Peak shift from sweep index {i} to {i+1} cannot be determined. Cannot find matching peaks at wavelength {last_peak[0]:.2f}."
                )
                _, (_, temp) = next(pair_iter, (None, (None, None)))
                if temp is not None:
                    ret.append(list(accumulate([start_wavelength] + shifts)))
                    shifts = []
                    if temp.size > 0:
                        last_peak = temp[0]
                        start_wavelength = temp[0][0]
                continue
            elif (  # if the peak shift is too large but the shapes match
                abs(pairs[0][1][0] - pairs[0][0][0]) > 0.5 * FSR
            ):
                logger.warning(
                    f"Peak shift from sweep index {i} to {i+1} is too large and may be incorrect."
                )
                logger.debug(f"Peak index {i}: {pairs[0][0]}")
                logger.debug(f"Peak index {i+1}: {pairs[0][1]}")
                logger.debug(f"Peak shift: {pairs[0][1][0] - pairs[0][0][0]}")

                is_swapped: bool = False
                if len(p1s) >= len(p2s):
                    pass
                else:
                    p1s, p2s = p2s, p1s
                    is_swapped = True

                temp = sorted(
                    [p1s[ii : ii + len(p2s)] for ii in range(len(p1s) - len(p2s) + 1)],
                    key=lambda ps: sum(
                        starmap(
                            lambda a, b: float(cdist([a], [b], "cosine")), zip(p2s, ps)
                        )
                    ),
                )

                (p1s, p2s) = (p2s, p1s) if is_swapped else (p1s, p2s)
                if not is_swapped:
                    wl_shift = float(np.mean(p2s.T[0]) - np.mean(temp[0].T[0]))
                else:
                    wl_shift = float(np.mean(temp[0].T[0]) - np.mean(p1s.T[0]))

                if abs(wl_shift) < pairs[0][1][0] - pairs[0][0][0]:
                    logger.debug(f"Shift fixed by {wl_shift}")
                    shifts.append(wl_shift)
                    last_peak = p2s[0]
                else:
                    shifts.append(pairs[0][1][0] - pairs[0][0][0])
                    last_peak = pairs[0][1]

                _, (_, temp) = next(pair_iter, (None, (None, None)))
                if temp is not None:
                    ret.append(list(accumulate([start_wavelength] + shifts)))
                    shifts = []
                    if temp.size > 0:
                        last_peak = temp[0]
                        start_wavelength = temp[0][0]
                continue
            else:  # normal case, an acceptable pair in other peaks is found
                shifts.append(pairs[0][1][0] - pairs[0][0][0])
                last_peak = pairs[0][1]

    ret.append(list(accumulate([start_wavelength] + shifts)))

    return ret, FSR


if __name__ == "__main__":

    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter

    channels = [0, 1, 2, 3, 4, 5]
    analyzer = RetrospectiveAnalyzer(
        os.path.expanduser("~/path/to/data/folder"),
        0.25,
        wavelength_multiplier=1e9,
    )

    # Plot spectrogram

    step = 1
    data = analyzer.get_spectrograms(channels, step)
    x_labels = np.vectorize(lambda x: "{:.2f}".format(x))(analyzer.timestamps[::step])
    y_labels = np.vectorize(lambda x: "{:.2f}".format(x))(analyzer.wavelengths[::-1])
    x_formatter = FuncFormatter(lambda x, _: x_labels[int(x)])
    y_formatter = FuncFormatter(lambda y, _: y_labels[int(y)])
    for c in channels:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.imshow(data[c], cmap="inferno")
        tick_step = 50
        ax.set_xticks(list(range(len(x_labels)))[::tick_step], x_labels[::tick_step])
        ax.set_yticks(list(range(len(y_labels)))[::tick_step], y_labels[::tick_step])
        ax.xaxis.set_major_formatter(x_formatter)
        ax.yaxis.set_major_formatter(y_formatter)
        fig.tight_layout()
    plt.show()

    # Plot traces

    all_traces, all_peaks = analyzer.analyze(channels, (0, None, 1))
    for c in channels:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title(f"Power{c+1}")

        ys = [x for x in all_traces[c][0]]

        for y in ys:
            ax.plot(y)

    plt.show()
