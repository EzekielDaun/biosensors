import re
import os
from itertools import islice

import numpy as np
import matplotlib.pyplot as plt
import pyqtgraph as pg

from PySide6 import QtWidgets, QtGui

from src.core.retrospective_analysis import get_lorentzian_peaks, _peaks_to_traces
from src.core.active_tools import (
    RampUpSweepCSVReader,
    generate_wavelength,
    thermal_simulation,
)

reader = RampUpSweepCSVReader(
    os.path.expanduser(
        # "/Users/yifeiliu/Downloads/2022-05-03_11_17_37_ChipG_10HzRampUp3V/Data"
        "D:/17110/下载/Data"
    ),
    re.compile(r".*measurement(\d+).*.csv"),
    10,
)

w = np.linspace(1309.65, 1310, 100)

app = pg.mkQApp("ImageView")
pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")

## Create window with ImageView widget
win = QtWidgets.QMainWindow()
win.resize(1600, 200)

# Add Plot item to show axis labels
plot = pg.PlotItem()
plot.setLabel(axis="left", text="Y-axis")
plot.setLabel(axis="bottom", text="X-axis")
plot.getAxis("left").setLabel(units="m")

imv = pg.ImageView(view=plot)
imv.ui.roiBtn.hide()
imv.ui.menuBtn.hide()

imv.getView().invertY(False)
imv.getView().setAspectLocked(False)
imv.setColorMap(pg.colormap.getFromMatplotlib("inferno"))
win.setCentralWidget(imv)
win.show()


if __name__ == "__main__":
    print("hello world")

    spectrum = []
    all_peaks = []
    for power, reference in islice(reader, 7540, 7550, 1):
        # wavelength, power = generate_wavelength(power, 0, 3, 0.8)
        reference = thermal_simulation(10, 50, 100, 0.0145)
        wavelength, power = generate_wavelength(power, reference)

        plt.plot(wavelength, power)
        # plt.plot(power)
        peaks, fsr, er, q = get_lorentzian_peaks(power, wavelength)
        for i,p in enumerate(peaks):
            plt.plot(p[0], p[1]+p[2], "o")
            plt.text(p[0],p[1]+p[2],f"{p[0]:.5f}")
        plt.show()
        # exit()

        # p = np.interp(w, wavelength, power)
        # spectrum.append(p)

        # try:
        #     peaks, fsr, er, q = get_lorentzian_peaks(power, wavelength)
        #     all_peaks.append(peaks)
        #     # plt.scatter(peaks.T[0][0:-1] + np.diff(peaks.T[0]) / 2, fsr, color="blue")
        # except Exception as e:
        #     all_peaks.append([])

    spectrum = np.array(spectrum)
    # plt.imshow(spectrum.T, aspect="auto", origin="lower", cmap="inferno")s
    imv.setImage(spectrum)
    tr = QtGui.QTransform()
    tr.translate(0, min(w) / 1e9)
    tr.scale(1, (max(w) - min(w)) * 1e-9 / len(w))
    imv.imageItem.setTransform(tr)

    traces, fsr = _peaks_to_traces(all_peaks)
    x0 = 0
    for trace in traces:
        x = np.arange(x0, x0 + len(trace))
        # trace = (trace - np.min(w)) / (np.max(w) - np.min(w)) * len(w)  # type:ignore
        # plt.plot(x, trace)
        imv.getView().addItem(
            pg.PlotCurveItem(
                x,
                np.array(trace) / 1e9,
                pen={"color": "green", "width": 5, "cosmetic": True},
            )
        )
        x0 += len(trace)
    # plt.show()
    imv.getView().autoRange()
    pg.exec()
