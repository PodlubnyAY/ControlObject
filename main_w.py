import logging
import numpy as np
from functools import partial
from datetime import datetime
    
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QGridLayout,
    QTableView, QHeaderView, QLineEdit, QTabWidget, QLabel, QComboBox
)
from PySide6.QtCore import Qt, QSortFilterProxyModel, Signal

import plantm
import config
import models
from windows import MeasureWindow, FilterWindow


def fill_cmb(cmb, column_name):
    """Заполняет QComboBox уникальными значениями из столбца БД"""
    cmb.clear()
    cmb.addItem("Все")  # Опция для сброса фильтра

    with models.Session() as session:
        # Получаем уникальные значения столбца
        table = models.users.User if hasattr(models.users.User, column_name) else models.entries.Entries
        values = session.query(getattr(table, column_name)).distinct().all()
        if values and isinstance(values[0][0], float):
            values = map(lambda v: (round(v[0], 3),), values)
        for value in sorted(set(values)):
            cmb.addItem(str(value[0]))


def get_frame(measurements):
    frame = []
    for ch in sorted(measurements):
        if ch in config.BASE_CHANNELS:
            frame.append(round(measurements[ch], 4))
            if (b := config.BORDERS.get(ch)) and b[0] > measurements[ch] > b[1]:
                # TODO make warns for user too
                logging.warning('')
        else:
            frame.append(round(np.mean(measurements[ch]), 4))
            frame.append(round(np.var(measurements[ch]), 4))
    return frame


class MainWindow(QWidget):
    measure_params_sig = Signal(list)
    filter_params_sig = Signal(list)
    def __init__(self):
        super().__init__()
        self.measure_params_sig.connect(self.get_frame)
        # self.filter_params_sig.connect(self.run_filter)
        self.plant = plantm.Plant()
        self.setWindowTitle("ТППОСУ Бригада 9")
        self.setGeometry(200, 200, 1200, 500)
        self.windows = {
            'measure': MeasureWindow(self.measure_params_sig),
            # 'filter': FilterWindow(self.filter_params_sig),
        }
        
        # Кнопки
        add_button = QPushButton(
            "Снять показания",
            clicked=partial(self.show_window, 'measure'))
        filter_button = QPushButton(
            "Фильтровать",
            clicked=self.toggle_filter)
        save_button = QPushButton(
            "Сохранить выборку",
        )
        exit_button = QPushButton("Выход", clicked=self.close_all)
        # delete_button = QPushButton("Удалить")
        # delete_button.clicked.connect(self.delete_user)
        self.filter_layout = QVBoxLayout()
        self.filter_container = QWidget()  # Контейнер для фильтров
        self.filter_container.setLayout(self.filter_layout)
        self.filter_container.setVisible(False)  # По умолчанию скрыт
        self.filter_widgets = []  # Список всех комбобоксов
        # self.create_filter_widgets()  # Создаем фильтры сразу

        # Таблица
        tab_widget = QTabWidget()
        
        self.users_view = QTableView(sortingEnabled=True)
        self.load_users()
        tab_widget.addTab(self.users_view, "Users")
        
        self.entries_view = QTableView(sortingEnabled=True)
        self.load_entries()
        
        tab_widget.addTab(self.entries_view, "Entries")
        
        btns_layout = QHBoxLayout()
        btns_layout.addWidget(add_button)
        btns_layout.addWidget(filter_button)
        btns_layout.addWidget(save_button)
        # btns_layout.addWidget(delete_button)
        
        layout = QVBoxLayout()
        layout.addLayout(btns_layout)
        layout.addWidget(self.filter_container)
        # layout.addWidget(self.table_view)
        layout.addWidget(tab_widget)
        layout.addWidget(exit_button)
        layout.setAlignment(
            exit_button,
            Qt.AlignmentFlag.AlignBottom| Qt.AlignmentFlag.AlignRight)
        self.setLayout(layout)
    
    def close_all(self):
        for w in self.windows.values():
            w.close()
        self.close()

    def toggle_filter(self):
        """Показывает/скрывает все комбобоксы"""
        state = not self.filter_container.isVisible()
        if state:
            self.create_filter_widgets()
        self.filter_container.setVisible(state)

    def create_filter_widgets(self):
        """Создаёт комбобоксы для всех таблиц сразу"""
        columns = {
            "Users": zip(models.users.HEADERS, models.users.COLUMNS),
            "Entries": zip(models.entries.HEADERS, models.entries.COLUMNS)
        }
        for table_name, col_names in columns.items():
            tabs_layout = QHBoxLayout()
            tabs_layout.addWidget(QLabel(table_name))
            for name, col in col_names:
                filter_layout = QVBoxLayout()  # Лейаут для метки + комбобокса
                label = QLabel(f"{name}")  # Метка сверху
                combo = QComboBox()
                combo.setEditable(True)
                combo.addItem("Все")  # Значение для сброса фильтра
                fill_cmb(combo, col)
                # combo.addItems(["Значение 1", "Значение 2", "Значение 3"])  # Заглушка
                filter_layout.addWidget(label)
                filter_layout.addWidget(combo)

                container = QWidget()  # Контейнер для группировки
                container.setLayout(filter_layout)
                tabs_layout.addWidget(container)
                self.filter_widgets.append(container)  # Сохраняем в список
            self.filter_layout.addLayout(tabs_layout)
    
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
        kwargs = dict(zip(models.users.MUTABLE_COLUMNS, [date, username, comment]))
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
            kwargs = dict(zip(models.entries.MUTABLE_COLUMNS, frame))
            entry = models.entries.Entries(**kwargs)
            with models.Session() as session:
                session.add(entry)
                session.commit()

            n_frames -= 1
        self.load_entries()
        self.load_users()
        return frames
