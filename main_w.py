import logging
import numpy as np
from functools import partial
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox,
    QTableView, QHeaderView, QLineEdit, QTabWidget
)
from PySide6.QtCore import Qt, QSortFilterProxyModel, Signal

import plantm
import config
import models
from windows import MeasureWindow, FilterWindow


def get_frame(measurements):
    frame = []
    for ch in sorted(measurements):
        if ch in config.BASE_CHANNELS:
            frame.append(measurements[ch])
            if (b := config.BORDERS.get(ch)) and b[0] > measurements[ch] > b[1]:
                logging.warning('')
        else:
            frame.append(np.mean(measurements[ch]))
            frame.append(np.var(measurements[ch]))
    return frame


class MainWindow(QWidget):
    measure_params_sig = Signal(list)
    def __init__(self):
        super().__init__()
        self.measure_params_sig.connect(self.get_frame)
        self.plant = plantm.Plant()
        self.setWindowTitle("ТППОСУ Бригада 9")
        self.setGeometry(200, 200, 1200, 500)
        self.windows = {
            'measure': MeasureWindow(self.measure_params_sig),
            'filter': FilterWindow(),
        }
        
        # Кнопки
        add_button = QPushButton(
            "Снять показания",
            clicked=partial(self.show_window, 'measure'))
        filter_button = QPushButton(
            "Фильтровать",
            clicked=partial(self.show_window, 'filter'))
        exit_button = QPushButton("Выход", clicked=self.close_all)
        # delete_button = QPushButton("Удалить")
        # delete_button.clicked.connect(self.delete_user)

        # Таблица
        tab = QTabWidget()
        
        self.users_view = QTableView(sortingEnabled=True)
        self.load_users()
        tab.addTab(self.users_view, "Users")
        
        self.entries_view = QTableView(sortingEnabled=True)
        self.load_entries()
        
        tab.addTab(self.entries_view, "Entries")
        
        btns_layout = QHBoxLayout()
        btns_layout.addWidget(add_button)
        btns_layout.addWidget(filter_button)
        # btns_layout.addWidget(delete_button)
        
        layout = QVBoxLayout()
        layout.addLayout(btns_layout)
        # layout.addWidget(self.table_view)
        layout.addWidget(tab)
        layout.addWidget(exit_button)
        layout.setAlignment(
            exit_button,
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        self.setLayout(layout)
    
    def close_all(self):
        for w in self.windows.values():
            w.close()
        self.close()
    
    def show_window(self, name, *args):
        if self.windows.get(name) is None:
            return
        if self.windows[name].isVisible():
            self.windows[name].raise_()
        else:
            self.windows[name].show()

    def load_entries(self):
        """Загружает данные из базы и обновляет модель"""
        with models.Session() as session:
            entries = session.query(models.entries.Entries).all()
        self.entry_model = models.entries.DataTableModel(entries)
        self.entries_view.setModel(self.entry_model)
        self.entries_view.resizeColumnsToContents()
        header = self.entries_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
    def load_users(self):
        """Загружает данные из базы и обновляет модель"""
        with models.Session() as session:
            users = session.query(models.users.User).all()
        self.user_model = models.users.UserTableModel(users)
        self.users_view.setModel(self.user_model)
        self.users_view.resizeColumnsToContents()
        header = self.users_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        # header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
    def measure(self):
        results, stable = {}, {}
        for ch in config.FRMAME_ORDER:
            if ch in config.BASE_CHANNELS:
                results[ch] = self.plant.measure(ch)
            elif ch in config.STABLE_CHANNELS:
                m = self.plant.measure(ch)
                if (last := stable.get(ch)) is not None and last != m:
                    logging.error(f'{ch} not stable ({last}->{m})')
                    return None
                stable[ch] = m
            elif ch in config.MV_CHANNELS:
                results[ch] = [
                    self.plant.measure(ch) for _ in range(config.MV_CHANNELS[ch])]

        return results
        
    def get_frame(self, args):
        username, n_frames, comment = args
        date = datetime.now().date()
        kwargs = dict(zip(models.users.COLUMNS, [date, username, comment]))
        user = models.users.User(**kwargs)
        with models.Session() as session:
            session.add(user)
            session.commit()
            cur_research = session.query(
                models.users.User).order_by(
                    models.users.User.research.desc()).first().research

        base_frame = [cur_research]
        frames = []
        while n_frames > 0:
            frame = base_frame + [datetime.now().time()]
            results = self.measure()
            if results is None:
                continue
            frame += get_frame(results)
            kwargs = dict(zip(models.entries.COLUMNS, frame))
            entry = models.entries.Entries(**kwargs)
            with models.Session() as session:
                session.add(entry)
                session.commit()
            # frames.append()
            n_frames -= 1
        self.load_entries()
        self.load_users()
        return frames
