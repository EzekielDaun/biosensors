from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


class RaFigureWidget(QWidget):
    def __init__(self):
        super().__init__()
        fig = Figure()
        self.figure_canvas = FigureCanvas(fig)
        self.toolbar = NavigationToolbar2QT(self.figure_canvas, self)

        self.axes = self.figure_canvas.figure.subplots()

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.figure_canvas)

        self.figure_canvas.draw()
