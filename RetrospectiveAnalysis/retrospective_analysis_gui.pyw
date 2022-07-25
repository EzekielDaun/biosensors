import logging
import os
import sys
import time

from PySide6.QtWidgets import QApplication

from src.window.ra_main_window import RaMainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RaMainWindow()
    window.show()

    logging.basicConfig(
        level=logging.DEBUG,
        format="{levelname:^7s}::{asctime}::{name}::{message}",
        style="{",
        datefmt="%H:%M:%S",
    )

    log_folder_name = ".log"
    try:
        os.makedirs(f"{log_folder_name}")
    except FileExistsError:
        pass
    finally:
        t = time.strftime("%Y%m%d-%H%M%S", time.localtime())
        file_handler = logging.FileHandler(os.path.join(log_folder_name, f"{t}.log"))
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter(
                "{asctime}::{name}::{levelname:^7s}::{message}", style="{"
            )
        )
        logging.getLogger().addHandler(file_handler)

    sys.exit(app.exec())
