from PySide6.QtWidgets import QApplication, QPlainTextEdit
import logging

class LogWidget(QPlainTextEdit, logging.StreamHandler):
    def __init__(self, parent=None, log_format=None, level=None):
        super().__init__(parent)
        logging.StreamHandler.__init__(self)
        if log_format is None:
            log_format = "%(asctime)s [%(levelname)s] %(message)s"
        if level is None:
            level = logging.WARNING
        self.setReadOnly(1)
        formatter = logging.Formatter(log_format)
        self.setFormatter(formatter)
        self.setLevel(level)

    def emit(self, record):
        log_msg = self.format(record)
        self.appendPlainText(log_msg)
        self.__scrollDown()

    def __scrollDown(self):
        scroll_bar = self.verticalScrollBar()
        end_text = scroll_bar.maximum()
        scroll_bar.setValue(end_text)

# Создание логгера и добавление виджета как обработчика
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    log_widget = LogWidget()
    log_widget.setReadOnly(1)
    logger.addHandler(log_widget)

    # Вывод логов
    logger.debug("Это дебаг сообщение")
    logger.info("Это информационное сообщение")
    logger.warning("Это предупреждение")
    logger.error("Это ошибка")
    logger.critical("Это критическая ошибка")

    # Отображение виджета
    log_widget.show()
    sys.exit(app.exec())
