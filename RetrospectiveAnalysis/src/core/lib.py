import logging
from dataclasses import dataclass
from itertools import accumulate, pairwise, product

import numpy as np
from cv2 import HoughLinesPointSet
from numpy.typing import NDArray
from scipy.ndimage import gaussian_filter1d
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
from scipy.spatial.distance import cdist
from sklearn.metrics import r2_score

logger = logging.getLogger(__name__)


def lorentzian(x, x0, y0, _i, gamma, a):
    return (
        y0
        + ((_i * (gamma / 2) ** 2) / ((gamma / 2) ** 2 + (x - x0) ** 2))
        + a * (x - x0)
    )


@dataclass
class LorentzianPeakFitResult:
    peak_params: NDArray[np.floating]
    er: float
    q: float
    r2: float
    n100dbm_points: int


@dataclass
class SweepFitResult:
    peaks: list[LorentzianPeakFitResult]

    @staticmethod
    def from_data(powers: NDArray[np.floating], wavelengths: NDArray[np.floating]):
        if len(powers) != len(wavelengths):
            raise RuntimeError("Number of wavelengths and powers do not match")

        powers_smoothed: NDArray[np.floating] = gaussian_filter1d(
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

        peaks: list[LorentzianPeakFitResult] = []
        for i, peak_index in enumerate(indices):
            left_base_index = max(properties["left_bases"][i], left_base_indices[i])
            right_base_index = min(properties["right_bases"][i], right_base_indices[i])

            wavelength_range = wavelengths[left_base_index:right_base_index]
            power_range = powers[left_base_index:right_base_index]

            # -100 is a bug value and should be ignored
            indices_fixed = np.argwhere(power_range != float(-100)).flatten()
            if len(indices_fixed) <= 8:
                # nearly all points are -100
                continue
            n100dbm_points = max(np.diff(indices_fixed))
            wavelength_fixed = wavelength_range[indices_fixed]
            power_fixed = power_range[indices_fixed]

            try:
                parameters, _ = curve_fit(
                    f=lorentzian,
                    xdata=wavelength_fixed,
                    ydata=power_fixed,
                    p0=[
                        wavelengths[peak_index],  # x0
                        np.mean(
                            [powers[left_base_index], powers[right_base_index]]
                        ),  # y0
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
                            100,
                            0,
                            max(wavelength_fixed) - min(wavelength_fixed),
                            np.inf,
                        ],
                    ),
                )

                x0, y0, _i, gamma, a = parameters
                r2: float = r2_score(  # type: ignore
                    power_fixed, lorentzian(wavelength_fixed, x0, y0, _i, gamma, a)
                )
                xs = wavelengths[left_base_index:right_base_index]

                # convert to linear scale for Q calculation
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

                peaks.append(
                    LorentzianPeakFitResult(
                        peak_params=parameters,
                        er=-parameters[2],
                        q=params_linear[0] / params_linear[3],  # Q = x0/gamma
                        r2=r2,
                        n100dbm_points=n100dbm_points,
                    )
                )

            except RuntimeError as e:
                logger.debug(
                    f"Curve fitting at wavelength {wavelengths[peak_index]:.2f}: {e}"
                )
                continue
        return SweepFitResult(peaks)

    def get_peaks(self, r2_threshold: float = 0.5, n100dbm_threshold: int = 30):
        return np.array(
            [
                p.peak_params
                for p in self.peaks
                if p.r2 > r2_threshold and p.n100dbm_points < n100dbm_threshold
            ]
        )

    def get_fsr(self, r2_threshold: float = 0.5, n100dbm_threshold: int = 30):
        if len(self.peaks) <= 1:
            return np.array([])
        else:
            peaks = np.array(
                [
                    p.peak_params
                    for p in self.peaks
                    if p.r2 > r2_threshold and p.n100dbm_points < n100dbm_threshold
                ]
            )
            return np.diff(peaks[:, 0])

    def get_er(self, r2_threshold: float = 0.5, n100dbm_threshold: int = 30):
        return np.array(
            [
                p.er
                for p in self.peaks
                if p.r2 > r2_threshold and p.n100dbm_points < n100dbm_threshold
            ]
        )

    def get_q(self, r2_threshold: float = 0.5, n100dbm_threshold: int = 30):
        return np.array(
            [
                p.q
                for p in self.peaks
                if p.r2 > r2_threshold and p.n100dbm_points < n100dbm_threshold
            ]
        )


def get_lorentzian_peaks(
    powers: NDArray[np.floating],
    wavelengths: NDArray[np.floating],
    r2_threshold: float = 0.5,
    max_n100dBm_points: int = 30,
) -> tuple[
    NDArray[np.floating],
    NDArray[np.floating],
    NDArray[np.floating],
    NDArray[np.floating],
]:
    """get_lorentzian_peaks

    Args:
        powers (NDArray[np.float64]): 1D array of power
        wavelengths (NDArray[np.float64]): 1D array of wavelength

    Returns:
        tuple[ NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64] ]: [[x0,y0,I,gamma,a]], [FSR], [ER], [Q]
    """

    # This is to mimic the old API
    sweep_fitted = SweepFitResult.from_data(powers, wavelengths)
    peaks = sweep_fitted.get_peaks(
        r2_threshold=r2_threshold, n100dbm_threshold=max_n100dBm_points
    )
    fsr = sweep_fitted.get_fsr(
        r2_threshold=r2_threshold, n100dbm_threshold=max_n100dBm_points
    )
    er = sweep_fitted.get_er(
        r2_threshold=r2_threshold, n100dbm_threshold=max_n100dBm_points
    )
    q = sweep_fitted.get_q(
        r2_threshold=r2_threshold, n100dbm_threshold=max_n100dBm_points
    )
    return peaks, fsr, er, q


def group_peaks(
    peaks_wl: list[NDArray[np.floating]],
    reference: NDArray[np.floating],
) -> list[list[tuple[int, int]]]:
    """group_peaks

    Args:
        peaks_wl (list[NDArray[np.float64]]): jagged array of peak wavelengths
        reference (NDArray[np.float64]): 1D array of reference wavelengths from peak tracking result

        The above two arguments should have the same length in their first dimension

    Returns:
        list[list[tuple[int, int]]]: 1D array of trace, where a trace is [(i,j)], peaks_wl[i][j] is a peak in this trace
    """
    peaks_wl_horizontal = [p - reference[i] for i, p in enumerate(peaks_wl)]
    point_set = np.array([[i, p] for i, ps in enumerate(peaks_wl_horizontal) for p in ps], dtype=np.float32)  # type: ignore
    lines = np.squeeze(
        HoughLinesPointSet(
            point_set.reshape(-1, 1, 2),
            lines_max=15,
            threshold=20,
            min_rho=-100,
            max_rho=100,
            rho_step=0.1,
            min_theta=(min_theta := np.pi / 2 - np.pi / 180 * 10),  # -10 deg
            max_theta=(max_theta := np.pi / 2 + np.pi / 180 * 10),  # +10 deg
            theta_step=(max_theta - min_theta)
            / 2,  # set a large step to check horizontal line only
        )
    )
    rhos = lines.T[1]

    groups: list[list[tuple[int, int]]] = [[] for _ in range(len(rhos))]
    EPSILON = 0.1
    for i, ps in enumerate(peaks_wl_horizontal):
        for j, p in enumerate(ps):
            for k, r in enumerate(rhos):
                if abs(p - r) < EPSILON:
                    groups[k].append((i, j))
                    break

    return groups


def peaks_to_traces(
    peaks: list[NDArray[np.floating]],
) -> tuple[list[list[float]], float]:
    """__peaks_to_traces

    Convert sweeps (in matrix form) into a few traces with FSR

    Args:
        peaks (list[NDArray[np.float64]]): list of sweeps in matrix form where each row is a peak vector

    Returns:
        tuple[list[list[float]], float]: ([traces], FSR)
    """

    try:
        FSR = float(
            np.mean(
                [
                    d
                    for sweep in peaks[::10]
                    if sweep.ndim > 1
                    for d in np.diff(sweep[:, 0])
                ]
            )
        )
        population: NDArray[np.floating] = np.array(
            [p for sweep in peaks[::10] for p in sweep]
        )
        mean_population = np.mean(population, axis=0)
        std_population = np.std(population, axis=0)

        pair_iter = enumerate(pairwise(peaks))

        ret: list[list[float]] = []
        shifts: list[float] = []
        start_wavelength: float = peaks[0][0][0]
        last_peak = peaks[0][0]
    except IndexError as e:
        raise IndexError("No peaks found in the first sweep.") from e

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
            last_peak: NDArray[np.floating] = ps[0]
            continue
        else:
            pairs = sorted(  # match other peaks in case that the peak correspond to the last peak is missing due to noise
                product([p for p in p1s if p[0] != last_peak[0]], p2s),
                key=lambda x: cdist(
                    # contain x0 or not
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

                # degrade to the nearest peak
                pair = sorted(  # do not match the last on-track peak in case that the corresponding peak is missing in the next sweep
                    product([p for p in p1s if p[0] != last_peak[0]], p2s),
                    key=lambda x: abs(x[1][0] - x[0][0]),
                )[
                    0
                ]
                shifts.append(pair[1][0] - pair[0][0])
                last_peak = pair[1]

                # append the current trace and start a new trace
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
