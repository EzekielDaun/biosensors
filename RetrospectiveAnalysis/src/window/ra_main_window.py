import os
import sys

from typing import List

from PySide6.QtWidgets import (
    QMainWindow,
    QFileSystemModel,
    QFileDialog,
    QHBoxLayout,
)
from PySide6.QtCore import QDir, QProcess, QProcessEnvironment

from scipy.io import loadmat

from ..uic.ra_main_window import Ui_RaMainWindow
from ..widgets.ra_figure_widget import RaFigureWidget
from ..core.MultiLorentzianFit import LorentzianFitting


class RaMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_RaMainWindow()
        self.ui.setupUi(self)

        self.ui.statusbar.showMessage("Retrospective Analysis")

        model = QFileSystemModel()
        model.setRootPath(QDir.homePath())
        self.ui.treeView.setModel(model)

        # Redirect stdout and stderr to log panel
        sys.stdout = self
        sys.stderr = self
        print("-----Retrospective Analysis-----")

        # Raw data plot for selected file
        self.raw_figure_widget = RaFigureWidget()
        self.ui.plot_widget.setLayout(QHBoxLayout())
        self.ui.plot_widget.layout().addWidget(self.raw_figure_widget)
        self.ui.plot_widget.layout().setContentsMargins(0, 0, 0, 0)

    def write(self, text):
        self.ui.textBrowser.insertPlainText(text)

    # Slots
    def slot_open_clicked(self):
        folder_path = QFileDialog.getExistingDirectory()
        if folder_path != "":
            tree_view = self.ui.treeView
            model: QFileSystemModel = tree_view.model()  # type: ignore
            tree_view.setRootIndex(model.index(folder_path))
            self.ui.statusbar.showMessage(f"Retrospective Analysis - {folder_path}")
        else:
            self.ui.statusbar.showMessage(f"Retrospective Analysis - Open cancelled")

    def slot_file_changed(self, model_index):
        tree_view = self.ui.treeView
        model: QFileSystemModel = tree_view.model()  # type: ignore
        file_path = model.filePath(model_index)
        file_name = os.path.basename(file_path)
        file_basename, file_ext = os.path.splitext(file_name)
        if model.isDir(model.index(file_path)):
            tree_view.setRootIndex(model.index(file_path))
        elif file_ext != ".mat":
            print(f"{file_name} is not a matlab workspace file")
        else:
            matlab_vector = loadmat(file_path)
            raw_power: List[float] = matlab_vector["power1"][0]
            wavelength: List[float] = matlab_vector["wavelength"][0]

            sweep_fit = LorentzianFitting(raw_power, wavelength, 1)

            figure_widget = self.raw_figure_widget
            figure_widget.axes.clear()
            figure_widget.axes.set_title(f"Raw Data: {file_basename}")
            figure_widget.axes.plot(sweep_fit.nm_wavelength, sweep_fit.raw_power_array)
            figure_widget.figure_canvas.draw()

    def slot_analyze_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, filter="*.py *.pyw")
        file_name = os.path.basename(file_path)
        file_basename, file_ext = os.path.splitext(file_name)

        if (
            file_path.__len__() > 0
            and self.ui.treeView.selectedIndexes().__len__() != 0
        ):
            selected_mat_file = self.ui.treeView.model().filePath(  # type: ignore
                self.ui.treeView.selectedIndexes()[0]
            )

            # Start a process to run the specified script
            proc = QProcess(self)
            proc.setProcessEnvironment(QProcessEnvironment.systemEnvironment())
            proc.startDetached("python", [f"{file_path}", f"{selected_mat_file}"])
            self.ui.statusbar.showMessage(
                f"Retrospective Analysis - Running {file_path}"
            )
        elif file_path.__len__() == 0:
            self.ui.statusbar.showMessage(
                f"Retrospective Analysis - Open script file cancelled"
            )

    def slot_analyze_folder(self):
        file_path, _ = QFileDialog.getOpenFileName(self, filter="*.py *.pyw")
        file_name = os.path.basename(file_path)
        file_basename, file_ext = os.path.splitext(file_name)

        if file_path.__len__() > 0:
            selected_folder = self.ui.treeView.model().filePath(  # type: ignore
                self.ui.treeView.rootIndex()
            )

            # Start a process to run specified script
            proc = QProcess(self)
            proc.setProcessEnvironment(QProcessEnvironment.systemEnvironment())
            proc.startDetached("python", [f"{file_path}", f"{selected_folder}"])
            self.ui.statusbar.showMessage(
                f"Retrospective Analysis - Running {file_path}"
            )
        elif file_path.__len__() == 0:
            self.ui.statusbar.showMessage(
                f"Retrospective Analysis - Open script file cancelled"
            )
