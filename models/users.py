from sqlalchemy import Column, Integer, String, Date
from PySide6.QtCore import Qt, QAbstractTableModel
from .models import Base

HEADERS = ["Эксперимент", "Дата", "Пользователь", 'Комментарий']
COLUMNS = ['research', 'date', 'user', 'comment']
MUTABLE_COLUMNS = ['date', 'user', 'comment']


class User(Base):
    __tablename__ = "users"
    
    research = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    user = Column(String, nullable=False)
    comment = Column(String)


class UserTableModel(QAbstractTableModel):
    def __init__(self, users, parent=None):
        super().__init__(parent)
        self.users = users

    def rowCount(self, parent=None):
        return len(self.users)

    def columnCount(self, parent=None):
        return 4

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        user = self.users[index.row()]
        column = index.column()
        column_map = [
            user.research,
            str(user.date),
            user.user,
            user.comment,
        ]
        return column_map[column]

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return HEADERS[section]

