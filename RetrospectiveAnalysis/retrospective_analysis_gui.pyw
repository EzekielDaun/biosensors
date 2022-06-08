import sys
from PySide6.QtWidgets import QApplication
from src.window.ra_main_window import RaMainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = RaMainWindow()
    window.show()

    sys.exit(app.exec())
