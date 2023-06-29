import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PySide6.QtWidgets import QWidget, QVBoxLayout

matplotlib.set_loglevel("info")


class RaFigureWidget(QWidget):
    def __init__(self):
        super().__init__()
        fig = Figure()
        self.figure_canvas = FigureCanvas(fig)
        self.toolbar = NavigationToolbar2QT(self.figure_canvas, self)

        self.figure: Figure = self.figure_canvas.figure

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.figure_canvas)

        self.figure_canvas.draw()
