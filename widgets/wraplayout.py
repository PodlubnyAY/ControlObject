from PySide6.QtWidgets import QLayout, QSizePolicy
from PySide6.QtCore import QSize, QPoint, QRect

class WrapLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        self.itemlist = []
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

    def __del__(self):
        item = self.takeAt(0)
        while item:
            del item
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemlist.append(item)

    def count(self):
        return len(self.itemlist)

    def itemAt(self, index):
        if 0 <= index < len(self.itemlist):
            return self.itemlist[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemlist):
            return self.itemlist.pop(index)
        return None

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.do_layout(rect, False)

    def sizeHint(self):
        return self.do_layout(self.contentsRect(), True)

    def do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()

        for item in self.itemlist:
            widget = item.widget()
            space = spacing if spacing > 0 else widget.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
            next_x = x + item.sizeHint().width() + space

            if next_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + spacing
                next_x = x + item.sizeHint().width() + space
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return QSize(rect.width(), y + line_height - rect.y())