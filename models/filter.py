from datetime import datetime, time
from PySide6.QtCore import QSortFilterProxyModel, Qt
from .users import DATE_FORMAT
from .entries import TIME_FORMAT


class FilterProxyModel(QSortFilterProxyModel):
# class FilterProxyModel(QSortFilterProxyModel):
    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.columns = columns
        self.combo_filters = {}
        self.range_filters = {}

    def set_combo_filter(self, column_name, value):
        self.combo_filters[column_name] = value
        self.invalidateFilter()

    def clear_combo_filters(self):
        self.combo_filters.clear()
        self.invalidateFilter()

    def set_range_filter(self, column, min_value=None, max_value=None):
        self.range_filters[column] = (min_value, max_value)
        self.invalidateFilter()
    
    def cmp(self, value, min_value, max_value, transform_func):
        value = transform_func(value)
        if min_value is not None and value < transform_func(min_value):
            return False
        if max_value is not None and value > transform_func(max_value):
            return False
        return True

    def filterAcceptsRow(self, source_row, source_parent):
        # Фильтры QComboBox (точное соответствие)
        for column_name, value in self.combo_filters.items():
            if value:
                index = self.sourceModel().index(source_row, self.columns.index(column_name), source_parent)
                try:
                    i = self.sourceModel().data(index)
                    if value.isdigit():
                        value = float(value)
                        i = float(self.sourceModel().data(index))
                    if value != i:
                        return False
                except ValueError:
                    return False
        accept = True
        # Фильтры QLineEdit (диапазон значений)
        for column, (min_value, max_value) in self.range_filters.items():
            index = self.sourceModel().index(source_row, column, source_parent)
            value = self.sourceModel().data(index, Qt.DisplayRole)
            if not isinstance(value, str):
                try:
                    accept &= self.cmp(value, min_value, max_value, float)
                except ValueError:
                    pass  # Игнорируем ошибки преобразования, если фильтр установлен
                continue

            f = None
            if ':' in value:
                f = TIME_FORMAT
            elif value.count('.') > 1:
                f = DATE_FORMAT
            if f:
                try:
                    accept &= self.cmp(
                        value, min_value, max_value, lambda x: datetime.strptime(x, f))
                except ValueError:
                    pass
        return accept
    
    def lessThan(self, source_left, source_right):
        if self.sourceModel().data(source_left) == '-':
            return False
        if self.sourceModel().data(source_right) == '-':
            return True
        return super().lessThan(source_left, source_right)
        