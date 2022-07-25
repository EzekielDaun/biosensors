import csv
import logging
import multiprocessing as mp
import os
import re
from functools import reduce
from itertools import accumulate, pairwise, product, repeat, starmap

import numpy as np
from numpy.typing import NDArray
from scipy.io import loadmat
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
from scipy.spatial.distance import cdist

logger = logging.getLogger(__name__)


def lorentzian(x, x0, y0, _i, gamma):
    return y0 + ((_i * (gamma / 2) ** 2) / ((gamma / 2) ** 2 + (x - x0) ** 2))


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
    prominence: float,
) -> NDArray[np.float64]:

    if len(powers) != len(wavelengths):
        raise RuntimeError("Number of wavelengths and powers do not match")

    prominence *= max(powers) - min(powers)

    indices, properties = find_peaks(
        (-1) * powers,
        prominence=prominence,
        distance=int(len(powers) / 6),
        width=int(len(powers) / 300),
        height=0,
    )
    while len(indices) <= 1:
        prominence /= 2
        indices, properties = find_peaks(
            (-1) * powers,
            prominence=prominence,
            distance=int(len(powers) / 6),
            width=int(len(powers) / 1000),
            height=0,
        )

    fsr: float = abs(np.mean(np.diff(wavelengths[indices])))

    ret: list[tuple[float, float, float, float]] = []
    for i, peak_index in enumerate(indices):
        peak_wavelength: float = wavelengths[peak_index]

        left_base_index = int(properties["left_bases"][i])
        right_base_index = int(properties["right_bases"][i])

        left_ips_index = int(properties["left_ips"][i])
        right_ips_index = int(properties["right_ips"][i])

        left_base_avg: float = np.mean(
            powers[
                max(0, left_base_index - 50) : min(
                    len(powers) - 1, left_base_index + 50
                )
            ]
        )
        right_base_avg = np.mean(
            powers[
                max(0, right_base_index - 50) : min(
                    len(powers) - 1, right_base_index + 50
                )
            ]
        )

        base: float = np.mean([left_base_avg, right_base_avg])
        width: float = wavelengths[right_ips_index] - wavelengths[left_ips_index]
        height: float = abs(properties["peak_heights"][i] - abs(base))

        ret.append(
            curve_fit(
                f=lorentzian,
                xdata=wavelengths[left_base_index:right_base_index],
                ydata=powers[left_base_index:right_base_index],
                p0=[
                    peak_wavelength,  # x0
                    base,  # y0
                    -height,  # I
                    width,  # gamma
                ],
                bounds=(
                    [
                        peak_wavelength - fsr * 0.1,
                        base - abs(base * 0.2),
                        -height * 1.5,
                        width * 0.5,
                    ],
                    [
                        peak_wavelength + fsr * 0.1,
                        base + abs(base * 0.2),
                        -height * 0.5,
                        width * 1.5,
                    ],
                ),
            )[0]
        )

    return np.array(ret)


def _mat_to_peak_dict(
    path: str,
    channels: list[int],
    prominence: float,
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
            prominence,
        )
        ret[c] = ret.get(c, []) + [temp_peaks]

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

        if not all(map(lambda x: x[0] + 1 == int(pat.match(x[1]).group(1)), enumerate(self.__filenames))):  # type: ignore
            raise RuntimeError("File numbers are not consecutive")

        self.__timestamps: NDArray[np.float64] = np.array([])
        if type(timestamp) is str:
            with open(os.path.join(self.__folder_path, timestamp), "r") as csv_file:
                self.__timestamps = np.array(
                    [
                        float(row[2]) * timestamp_multiplier
                        for row in csv.reader(csv_file, delimiter=",")
                        if len(row) >= 3 and row[2] != ""
                    ]
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
        self, channels: list[int], step: int = 1
    ) -> dict[int, NDArray[np.float64]]:
        """Get spectrums at a given sample rate for the given channels.

        Args:
            `channels` (List[int]): the channel indexes e.g. [0,2,4] for channel 1,3,5
            `step` (int, optional): the down sample rate. Read one for each `step` files. Defaults to 1 (no down sample).

        Returns:
            `data`: Dict[K:`index`, V:`spectrogram`], where `spectrogram` is ready to be plotted with matplotlib.imshow()
        """
        data: dict[int, NDArray[np.float64]] = {}
        for f in self.__filenames[::step]:
            matrix, _ = read_mat(os.path.join(self.__folder_path, f))
            for key in channels:
                vector = np.flip(np.array([matrix[key]])).transpose()
                data[key] = np.hstack((data[key], vector)) if key in data else vector
        return data

    def analyze(
        self,
        channels: list[int],
        prominence: float,
        enable_multi_processing: bool = True,
    ) -> tuple[
        dict[int, tuple[list[list[float]], float]], dict[int, list[NDArray[np.float64]]]
    ]:
        if enable_multi_processing:
            process_num: int = 1 if os.cpu_count() is None else os.cpu_count()  # type: ignore
            with mp.Pool(
                processes=max(1, process_num - 2)
            ) as pool:  # reserve one for GUI and one for other programs
                peaks: dict[int, list[NDArray[np.float64]]] = reduce(
                    lambda acc, b: {
                        x: acc.get(x, []) + b.get(x, []) for x in set(acc).union(b)  # type: ignore
                    },
                    pool.starmap(
                        _mat_to_peak_dict,
                        zip(
                            [
                                os.path.join(self.__folder_path, f)
                                for f in self.__filenames
                            ],
                            repeat(channels),
                            repeat(prominence),
                            repeat(self.__wavelength_multiplier),
                        ),
                    ),
                    {},
                )
        else:
            peaks: dict[int, list[NDArray[np.float64]]] = reduce(
                lambda acc, b: {
                    x: acc.get(x, []) + b.get(x, []) for x in set(acc).union(b)  # type: ignore
                },
                starmap(
                    _mat_to_peak_dict,
                    zip(
                        [os.path.join(self.__folder_path, f) for f in self.__filenames],
                        repeat(channels),
                        repeat(prominence),
                        repeat(self.__wavelength_multiplier),
                    ),
                ),
                {},
            )

        return {k: peaks_to_shifts_py(v) for k, v in peaks.items()}, peaks


def peaks_to_shifts_py(
    peaks: list[NDArray[np.float64]],
) -> tuple[list[list[float]], float]:
    FSR: float = np.mean([d for sweep in peaks[::10] for d in np.diff(sweep[:, 0])])
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

            if (  # if the minimum difference in shape is still too large
                cdist(
                    [(pairs[0][0][1:] - mean_population[1:]) / std_population[1:]],
                    [(pairs[0][1][1:] - mean_population[1:]) / std_population[1:]],
                    "cosine",
                )[0][0]
                > 0.1
            ):
                shifts.append(np.nan)
                logger.warning(
                    f"Peak shift from sweep index {i} to {i+1} cannot be determined. Cannot find matching peaks."
                )
                _, (_, temp) = next(pair_iter, (None, (None, None)))
                if temp is not None:
                    ret.append(list(accumulate([start_wavelength] + shifts)))
                    shifts = []
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
                    wl_shift = np.mean(p2s.T[0]) - np.mean(temp[0].T[0])
                else:
                    wl_shift = np.mean(temp[0].T[0]) - np.mean(p1s.T[0])

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

    channels = [4]
    # channels = [0, 1, 2, 3, 4, 5]
    analyzer = RetrospectiveAnalyzer(
        # r"D:\17110\下载\2022-06-15_Gemina-Phase-3b_Trial-2\Bulk_RI",
        # r"D:\17110\下载\2022-06-15_Gemina-Phase-3b_Trial-2\Bioassay",
        # r"D:\17110\下载\decending modified",
        r"D:\17110\下载\BulkRI",
        0.25,
        wavelength_multiplier=1e9,
    )

    # Plot spectrogram

    # step = 1
    # data = analyzer.get_spectrograms(channels, step)
    # x_labels = np.vectorize(lambda x: "{:.2f}".format(x))(analyzer.timestamps[::step])
    # y_labels = np.vectorize(lambda x: "{:.2f}".format(x))(analyzer.wavelengths[::-1])
    # x_formatter = FuncFormatter(lambda x, _: x_labels[int(x)])
    # y_formatter = FuncFormatter(lambda y, _: y_labels[int(y)])
    # for c in channels:
    #     fig = plt.figure()
    #     ax = fig.add_subplot(111)
    #     ax.imshow(data[c], cmap="inferno")
    #     tick_step = 50
    #     ax.set_xticks(list(range(len(x_labels)))[::tick_step], x_labels[::tick_step])
    #     ax.set_yticks(list(range(len(y_labels)))[::tick_step], y_labels[::tick_step])
    #     ax.xaxis.set_major_formatter(x_formatter)
    #     ax.yaxis.set_major_formatter(y_formatter)
    #     fig.tight_layout()
    # plt.show()

    # Plot traces

    all_traces = analyzer.analyze(channels, 0.05)
    for c in channels:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title(f"Power{c+1}")

        ys = [x for x in all_traces[c][0]]

        for y in ys:
            ax.plot(y)

    plt.show()
