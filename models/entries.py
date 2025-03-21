from sqlalchemy import Column, Integer, Float, Time
from PySide6.QtCore import Qt, QAbstractTableModel
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
        self.show_statistics = True
        self.means = [None] * 13
        self.variances = [None] * 13

    def enable_statistics(self, enable=True):
        self.show_statistics = enable
        if enable:
            self.calculate_statistics()
        self.layoutChanged.emit()

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

            if column_data:
                self.means[col] = np.mean(column_data)
                self.variances[col] = np.var(column_data)
            else:
                self.means[col] = None
                self.variances[col] = None

    def rowCount(self, parent=None):
        count = len(self.entries)
        if self.show_statistics:
            count += 2
        return count

    def columnCount(self, parent=None):
        return 13

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        row = index.row()
        column = index.column()

        if row < len(self.entries):
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
        elif row == len(self.entries):
            if self.means[column] is not None:
                m = self.means[column]
                return f'{m:.3f}'
            return '-'
        else:
            if self.variances[column] is not None:
                v = self.variances[column]
                return f'{v:.3f}'
            return '-'

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return HEADERS[section]
            elif orientation == Qt.Vertical and self.show_statistics:
                if section == len(self.entries):
                    return "Среднее"
                elif section == len(self.entries) + 1:
                    return "Дисперсия"
        return None
