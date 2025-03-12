from sqlalchemy import Column, Integer, Float, Time
from PySide6.QtCore import Qt, QAbstractTableModel
from .models import Base

HEADERS = [
    "ID", "Эксперимент", "Время", "Температура", "Давление", 'Влажность', 'Датчик4',
    'Датчик5', 'Датчик6(Сред)', 'Датчик6(Дисп)', 'Набл20', 'Набл43', 'Набл58']
MUTABLE_COLUMNS = [
    'research', 'time', 'temperature', 'pressure', 'humidity', 'sensor4' ,'sensor5', 
    'sensor6_mean', 'sensor6_var', 'observation20', 'observation43', 'observation58']
COLUMNS = ['id'] + MUTABLE_COLUMNS


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

    def rowCount(self, parent=None):
        return len(self.entries)

    def columnCount(self, parent=None):
        return 13

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        entry = self.entries[index.row()]
        column = index.column()
        column_map = [
            entry.id,
            entry.research,
            str(entry.time),
            entry.temperature,
            entry.pressure,
            entry.humidity,
            entry.sensor4,
            entry.sensor5,
            entry.sensor6_mean,
            entry.sensor6_var,
            entry.observation20,
            entry.observation43,
            entry.observation58
        ]
        res = column_map[column]
        if not isinstance(res, float):
            return res
        return round(res, 4)
        # return column_map[column]

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return HEADERS[section]

