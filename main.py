import sys
from PySide6.QtWidgets import QApplication

from main_w import MainWindow, logger


if __name__ == "__main__":
    app = QApplication(sys.argv[1:])
    window = MainWindow()
    window.showFullScreen()
    logger.info('Приложение запущено')
    # window.show()
    returncode = app.exec()
    sys.exit(returncode)
