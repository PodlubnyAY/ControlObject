from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox,
    QTableView, QHeaderView, QLineEdit, QTabWidget, QComboBox
)
from PySide6.QtCore import Qt, Signal


class MeasureWindow(QWidget):
    def __init__(self, sig):
        super().__init__()
        self.sig = sig
        self.setWindowTitle("Измерения")
        self.setGeometry(400, 100, 100, 50)

        # Buttons
        run_button = QPushButton("Снять показания", clicked=self.send_params)
        close_button = QPushButton("Закрыть", clicked=self.close)
        
        # Edit fields
        user_line = QLineEdit()
        user_line.setPlaceholderText("ФИО")
        n_frames_line = QLineEdit()
        n_frames_line.setPlaceholderText("Кол-во кадров")
        
        comment_line = QLineEdit()
        comment_line.setPlaceholderText("Комментарий")
        
        # research_number = QLineEdit()
        # TODO set static field with current research number
        # research_number.setPlaceholderText("the research number")
        
        # layout
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(run_button)
        btn_layout.addWidget(close_button)
        
        layout = QVBoxLayout()
        # layout.addWidget(research_number)
        layout.addWidget(user_line)
        layout.addWidget(n_frames_line)
        layout.addWidget(comment_line)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def send_params(self, *args):
        layout = self.layout()
        params = []
        for i in range(layout.count()):
            w = layout.itemAt(i).widget()
            if not isinstance(w, QLineEdit):
                continue
            v = w.text()
            w.clear()
            if v.isdigit():
                v = int(v)
            elif v.replace('.', '', 1).replace(',', '', 1).isdigit():
                v = float(v)
            params.append(v)
        
        self.close()
        self.sig.emit(params)


# TODO filter
class FilterWindow(QWidget):
    def __init__(self, sig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sig = sig
        self.setWindowTitle("Фильтрация")
        self.setGeometry(800, 100, 600, 300)
        

        
        ul = QVBoxLayout()
        # TODO users columns

        el = QVBoxLayout()
        # TODO entry columns
        
        layout = QHBoxLayout()
        layout.addLayout(ul)
        layout.addLayout(el)
        
    def set_cmb(self, name):
        cmb = QComboBox(editable=True, duplicatesEnabled=False)