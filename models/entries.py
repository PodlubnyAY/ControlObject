from sqlalchemy import Column, Integer, Float, Time
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
import numpy as np
from . import Base

HEADERS = [
    "ID", "Эксперимент", "Время (ЧЧ:ММ:СС)", "Температура", "Давление", 'Влажность', 'Датчик4',
    'Датчик5', 'Датчик6(Сред)', 'Датчик6(Дисп)', 'Набл20', 'Набл43', 'Набл58']
MUTABLE_COLUMNS = [
    'research', 'time', 'temperature', 'pressure', 'humidity', 'sensor4' ,'sensor5', 
    'sensor6_mean', 'sensor6_var', 'observation20', 'observation43', 'observation58']
COLUMNS = ['id'] + MUTABLE_COLUMNS
TIME_FORMAT = '%H:%M:%S'

class Entries(Base):
    __tablename__ = "entries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    research = Column(Integer)
    time = Column(Time)
    temperature = Column(Float, nullable=False)
    pressure = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    sensor4 = Column(Float, nullable=False)
    sensor5 = Column(Float, nullable=False)
    sensor6_mean = Column(Float, nullable=False)
    sensor6_var = Column(Float, nullable=False)
    observation20 = Column(Float, nullable=False)
    observation43 = Column(Float, nullable=False)
    observation58 = Column(Float, nullable=False)


class DataTableModel(QAbstractTableModel):
    def __init__(self, entries, parent=None):
        super().__init__(parent)
        self.entries = entries

    def calculate_statistics(self):
        for col in range(3, 13):  # Столбцы для статистики
            column_data = []
            for entry in self.entries:
                column_map = [
                    entry.id, entry.research, entry.time.strftime(TIME_FORMAT),
                    entry.temperature, entry.pressure, entry.humidity,
                    entry.sensor4, entry.sensor5, entry.sensor6_mean,
                    entry.sensor6_var, entry.observation20, entry.observation43,
                    entry.observation58
                ]
                value = column_map[col]
                if isinstance(value, (int, float)):
                    column_data.append(value)

    def rowCount(self, parent=None):
        return len(self.entries)

    def columnCount(self, parent=None):
        return 13

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        row = index.row()
        column = index.column()

        entry = self.entries[row]
        column_map = [
            entry.id, entry.research, entry.time.strftime(TIME_FORMAT),
            entry.temperature, entry.pressure, entry.humidity,
            entry.sensor4, entry.sensor5, entry.sensor6_mean,
            entry.sensor6_var, entry.observation20, entry.observation43,
            entry.observation58
        ]
        res = column_map[column]
        if not isinstance(res, (int, float)):
            return res
        return round(res, 3)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return HEADERS[section]

        return None


class EntryStatsModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._stats = {}
        self._cols = []
        self.headers = []
        
    def setStats(self, stats_data):
        self.beginResetModel()
        self._stats = stats_data
        self.endResetModel()
        
    def setStatsColumns(self, numeric_columns, labels=None):
        self._cols = numeric_columns
        self.headers = labels or self._cols
        
    def rowCount(self, parent=QModelIndex()):
        return 2
        
    def columnCount(self, parent=QModelIndex()):
        return len(self._cols)
        
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            column_index = self._cols[index.column()]
            if index.row() == 0:  # Среднее
                mean = self._stats.get(column_index, (None, None))[0]
                return f"{mean:.2f}" if mean is not None else "-"
            else:  # Дисперсия
                var = self._stats.get(column_index, (None, None))[1]
                return f"{var:.2f}" if var is not None else "-"
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                i = self._cols[section]
                return self.headers[i]
            elif orientation == Qt.Vertical:
                return ["Среднее", "Дисперсия"][section]
        return None
