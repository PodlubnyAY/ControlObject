import logging
import os
import numpy as np
from functools import partial
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout,
    QTableView, QHeaderView, QLineEdit, QTabWidget, QLabel, QComboBox, QFileDialog
)
from PySide6.QtCore import Qt, Signal

import plantm
import config
import models
import widgets
from openpyxl import Workbook
from windows import MeasureWindow

logger = logging.getLogger('measuring')
logger.setLevel(10)


def fill_cmb(cmb, column_name):
    """Заполняет QComboBox уникальными значениями из столбца БД"""
    cmb.clear()
    cmb.addItem("Все")  # Опция для сброса фильтра

    with models.Session() as session:
        # Получаем уникальные значения столбца
        table = models.entries.Entries
        if hasattr(models.users.User, column_name):
            table = models.users.User
        data = session.query(getattr(table, column_name)).distinct().all()
        if data and isinstance(data[0][0], float):
            data = map(lambda v: (round(v[0], 3),), data)
        for line in sorted(set(data)):
            cmb.addItem(str(line[0]))


def get_frame(measurements):
    frame = []
    for ch in sorted(measurements):
        if ch in config.BASE_CHANNELS:
            frame.append(round(measurements[ch], 4))
            if (
                (b := config.BORDERS.get(ch))
                and (b[0] > measurements[ch] or measurements[ch] > b[1])
            ):
                logger.warning(
                    f'канал {ch}: значение {measurements[ch]} вне диапазона '
                    f'[{b[0]}, {b[1]}]')
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
        self.setGeometry(50, 50, 1600, 700)
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
            clicked=self.save_view
        )
        exit_button = QPushButton("Выход", clicked=self.close_all)

        self.filter_layout = QVBoxLayout()
        self.filter_container = QWidget()  # Контейнер для фильтров
        self.filter_container.setLayout(self.filter_layout)
        self.filter_container.setVisible(False)  # По умолчанию скрыт
        self.filter_widgets = {}  # Список всех комбобоксов
        self.general_widgets = []
        # self.create_filter_widgets()  # Создаем фильтры сразу

        # Таблицы
        tab_widget = QTabWidget()
        
        self.users_view = QTableView(sortingEnabled=True)
        self.load_users()
        tab_widget.addTab(self.users_view, "Пользователи")
        
        self.entries_view = QTableView(sortingEnabled=True)
        self.stats_table = QTableView()        
        self.load_entries()
        vHeader = self.stats_table.verticalHeader()
        vHeader.setSectionResizeMode(QHeaderView.Stretch)
        width = sum(self.entries_view.columnWidth(i) for i in range(4))
        vHeader.setFixedWidth(width)
        vHeader.setMinimumWidth(width)
        
        tab_widget.addTab(self.entries_view, "Кадры")
        btns_layout = QHBoxLayout()
        btns_layout.addWidget(add_button)
        btns_layout.addWidget(filter_button)
        btns_layout.addWidget(save_button)
        
        logpane = widgets.LogWidget(level=logger.level)
        logger.addHandler(logpane)
        
        layout = QVBoxLayout()
        layout.addLayout(btns_layout)
        layout.addWidget(self.filter_container, stretch=2)
        # layout.addWidget(self.table_view)
        layout.addWidget(tab_widget, stretch=6)
        self.stats_table.setFixedHeight(80)
        layout.addWidget(self.stats_table)
        layout.addWidget(logpane, stretch=1)
        layout.addWidget(exit_button)
        layout.setAlignment(
            exit_button,
            Qt.AlignmentFlag.AlignBottom| Qt.AlignmentFlag.AlignRight)
        self.setLayout(layout)
    
    def close_all(self):
        for w in self.windows.values():
            w.close()
        logger.info('Завершение работы')
        logger.removeHandler(self.layout().itemAt(4).widget())
        self.close()

    def toggle_filter(self):
        """Показывает/скрывает все комбобоксы и сбрасывает фильтры"""
        state = not self.filter_container.isVisible()
        filter_button = self.layout().itemAt(0).itemAt(1).widget()
        if state:
            filter_button.setText('Сброс')
            if not self.filter_widgets:  # Проверяем, если комбобоксы еще не созданы
                self.create_filter_widgets()
        else:
            filter_button.setText('Фильтровать')
            self.clear_filters()
        self.filter_container.setVisible(state)

    def get_cmb(self, table_name, column_name):
        combo = QComboBox()
        combo.setEditable(True)
        combo.addItem("Все")
        fill_cmb(combo, column_name)
        combo.currentIndexChanged.connect(
            partial(self.update_filter_cmb, table_name, column_name, combo))
        return combo

    def get_line_edit(self, table_name, column_number, placeholder):
        edit = QLineEdit(placeholderText=placeholder)
        edit.setFixedSize(100, 20)
        edit.textChanged.connect(
            partial(
                self.update_range_filter,
                table_name, column_number,
                placeholder=="От"))
        return edit
        
    def create_filter_widgets(self):
        """Создаёт комбобоксы для всех таблиц сразу"""
        if self.filter_widgets:
            return
        columns = {
            "Users": zip(models.users.HEADERS, models.users.COLUMNS),
            "Entries": zip(models.entries.HEADERS, models.entries.COLUMNS)}
        nonbordered = {'research', 'comment', 'user'}
        skip = {'id', 'comment'}
        # processed_columns = set()
        filter_container = QWidget()
        layout = widgets.WrapLayout()
        for table_name, col_names in columns.items():
            # layout.addWidget(QLabel(table_name))
            for i, (name, col) in enumerate(col_names):
                if col in skip:
                    continue
                label = QLabel(name)
                if col in nonbordered:
                    if col in self.filter_widgets:
                        combo = self.filter_widgets[col].findChild(QComboBox)
                        combo.currentIndexChanged.connect(
                                partial(
                                    self.update_filter_cmb, 
                                    table_name, col, combo))
                        continue
                    combo = self.get_cmb(table_name, col)
                    filter_layout = QVBoxLayout()
                    filter_layout.addWidget(label)
                    filter_layout.addWidget(combo)
                        
                else:
                    filter_layout = QGridLayout()
                    filter_layout.addWidget(
                        label, 0, 0, 2, 1,
                        alignment=Qt.AlignmentFlag.AlignRight)
                    filter_layout.addWidget(
                        self.get_line_edit(table_name, i, "От"),
                        2, 0)
                    filter_layout.addWidget(
                        self.get_line_edit(table_name, i, "До"),
                        2, 1)

                container = QWidget()  # Контейнер для группировки
                container.setLayout(filter_layout)
                layout.addWidget(container)
                self.filter_widgets[col] = container  # Сохраняем в список
                filter_container.setLayout(layout)
            self.filter_layout.addWidget(filter_container)

    def update_filter_cmb(self, table_name, column_name, combo, *args):
        """Применяет фильтр к таблице"""
        filter_value = combo.currentText()
        if filter_value == "Все":
            filter_value = ""
        proxy_model = self.user_proxy_model
        if table_name != "Users":
            proxy_model = self.entry_proxy_model
        proxy_model.set_combo_filter(column_name, filter_value)
        self.stats_model.updateStats()
    
    def update_range_filter(self, table_name, column, ismin, text, *args):
        proxy_model = self.user_proxy_model
        if table_name != "Users":
            proxy_model = self.entry_proxy_model
        value = text or None
        min_value, max_value = proxy_model.range_filters.get(column, (None, None))
        if ismin:
            min_value = value
        else:
            max_value = value

        proxy_model.set_range_filter(column, min_value, max_value)
        self.stats_model.updateStats()

    def clear_filters(self):
        """Очищает все фильтры и сбрасывает комбобоксы"""
        for container in self.filter_widgets.values():
            element = container.findChild(QComboBox)
            if element is None:
                for elem in container.findChildren(QLineEdit):
                    elem.clear()
            else:
                element.setCurrentIndex(0)
        self.user_proxy_model.clear_combo_filters()
        self.entry_proxy_model.clear_combo_filters()
        logger.info('Фильтры сброшены')
    
    def remove_filter(self):
        while self.filter_layout.count():
            item = self.filter_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        # self.filter_container.setLayout(None)
        # del self.filter_layout

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
        self.entry_proxy_model = models.FilterProxyModel(models.entries.COLUMNS)
        self.entry_proxy_model.setSourceModel(self.entry_model)
        self.entries_view.setModel(self.entry_proxy_model)
        self.entries_view.resizeColumnsToContents()
        header = self.entries_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
        self.stats_model = models.entries.EntryStatsModel()
        self.stats_model.setProxyModel(self.entry_proxy_model)
        self.stats_model.setStatsColumns(
            list(range(3, len(models.entries.COLUMNS))),
            models.entries.HEADERS)       
        self.stats_table.setModel(self.stats_model)
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stats_model.updateStats()

    def load_users(self):
        """Загружает данные из базы и обновляет модель"""
        with models.Session() as session:
            users = session.query(models.users.User).all()
        self.user_model = models.users.UserTableModel(users)
        self.user_proxy_model = models.FilterProxyModel(models.users.COLUMNS)
        self.user_proxy_model.setSourceModel(self.user_model)
        self.users_view.setModel(self.user_proxy_model)
        self.users_view.resizeColumnsToContents()
        header = self.users_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
    def measure(self):
        results, stable = {}, {}
        for ch in config.FRMAME_ORDER:
            if ch in config.BASE_CHANNELS:
                results[ch] = self.plant.measure(ch)
            elif ch in config.STABLE_CHANNELS:
                m = self.plant.measure(ch)
                if (last := stable.get(ch, m)) != m:
                    logger.error(f'канал {ch}: нарушение стабильности ({last}->{m})')
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
        for _ in range(n_frames):
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

        self.load_users()
        self.filter_container.close()
        self.remove_filter()
        self.filter_widgets.clear()
        self.create_filter_widgets()
        self.load_entries()
        logger.info(
            f'Пользователь "{username}" снял показания {n_frames} кадров, '
            f'комментарий: "{comment}"')
        return frames

    def calculate_statistics(self):
        stats = {}
        rows = self.entry_proxy_model.rowCount()
        cols = self.entry_proxy_model.columnCount()
        
        for col in range(cols):
            values = []
            for row in range(rows):
                idx = self.entry_proxy_model.index(row, col)
                val = self.entry_proxy_model.data(idx, Qt.DisplayRole)
                try:
                    values.append(float(val))
                except:
                    continue

            if values:
                mean = sum(values) / len(values)
                variance = sum((x - mean)**2 for x in values) / len(values)
                stats[col] = (mean, variance)
            else:
                stats[col] = (None, None)
        
        return stats

    def update_statistics(self):
        stats = self.calculate_statistics()
        self.stats_model.setStats(stats)

    def save_view(self):
        path, ok = QFileDialog.getSaveFileName(
            self, 'Сохранение', os.getenv('HOME'),
            ';;'.join((
                'Excel Files (*.xls, *.xlsx)',
                'All Files (*.*)')))
        if not ok:
            logger.error(f'Ошибка сохранения в файл {path}')
            return
        wb = Workbook(write_only=True)
        for i, t, model, h in zip(
                range(2),
                ('Пользователи', 'Записи'),
                (self.user_proxy_model, self.entry_proxy_model),
                (models.users.HEADERS, models.entries.HEADERS)):
            ws = wb.create_sheet(t, i)
            ws.append(h)
            for line in model.data_generator():
                ws.append(line)
        wb.save(path)
        logger.info(f'Выборка сохранена в файл {path}')
