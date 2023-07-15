import logging
import os
import sys
import time

from PySide6.QtWidgets import QApplication

from src.window.ra_startup_window import RaStartupWindow

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="{levelname:^7s}::{asctime}::{name}::{message}",
        style="{",
        datefmt="%H:%M:%S",
        force=True,
    )
    log_folder_name = ".log"
    os.makedirs(f"{log_folder_name}", exist_ok=True)
    t = time.strftime("%Y%m%d-%H%M%S", time.localtime())
    file_handler = logging.FileHandler(os.path.join(log_folder_name, f"{t}.log"))
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("{asctime}::{name}::{levelname:^7s}::{message}", style="{")
    )
    logging.getLogger().addHandler(file_handler)

    app = QApplication(sys.argv)

    startup_window = RaStartupWindow()
    startup_window.show()

    sys.exit(app.exec())
