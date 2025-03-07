from pprint import pprint
import sys
import os
import PySide6
from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QListWidgetItem, QMessageBox
from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtCharts
from mainwindow import Ui_MainWindow
from edit_dialog import Ui_Dialog
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from statistics import *

dirname = os.path.dirname(PySide6.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

class ItemsModel(QtCore.QAbstractTableModel):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.items = []
        self.regions = {}

    def setItems(self, items):
        self.beginResetModel()
        self.items = items
        self.endResetModel()

    def setRegion(self, regions):
        self.beginResetModel()
        self.regions = regions
        self.endResetModel()

    def rowCount(self, *args, **kwargs) -> int:
        return len(self.items)
    
    def columnCount(self, *args, **kwargs) -> int:
        return 4
    
    def data(self, index: QtCore.QModelIndex, role: QtCore.Qt.ItemDataRole):
        if not index.isValid():
            return
        
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            region_info = self.items[index.row()]
            col = index.column()
            if col == 0:
                return f'{region_info.id}'
            elif col == 1:
                region_title = self.regions[region_info.region_id].title
                return region_title
            elif col == 2:
                return f'{region_info.year}'
            elif col == 3:
                return f'{region_info.population}'
        elif role == QtCore.Qt.ItemDataRole.UserRole:
            return self.items[index.row()]

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: QtCore.Qt.ItemDataRole):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                return {
                    0: "id",
                    1: "Регион",
                    2: "Год",
                    3: "Население",
                }.get(section)

class EditDialog(QDialog):
    def __init__(self, regions, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.btnAdd.clicked.connect(self.accept)
        self.ui.btnCancel.clicked.connect(self.reject)

        print(regions)
        for r in regions.values():
            self.ui.cmbRegions.addItem(r.title, r)

    def get_data(self):
        return {
            "region_id": self.ui.cmbRegions.currentData().id,
            "year": self.ui.txtYear.text(),
            "population": self.ui.txtPopulation.text()
        }


class UpdateDialog(EditDialog):
    def __init__(self, regions, init_data, *args, **kwargs) -> None:
        super().__init__(regions, *args, **kwargs)

        self.ui.btnAdd.setText('Изменить')
        self.ui.cmbRegions.setEnabled(False)

        region_name = regions[init_data.region_id].title
        self.ui.cmbRegions.setCurrentText(region_name)

        self.ui.txtPopulation.setText(str(init_data.population))
        self.ui.txtYear.setText(str(init_data.year))


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.checkboxes = {
            "Город": None,
            "Регион": None,
            "Село": None,
        }

        for key in self.checkboxes:
            checkbox = QtWidgets.QCheckBox()
            checkbox.setText(key)
            self.ui.layoutTypes.addWidget(checkbox)
            self.checkboxes[key] = checkbox

        self.model = ItemsModel()
        self.lastTblItemsItemClicked = None
        self.ui.tblItems.setModel(self.model)
        self.ui.tblItems.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        self.engine = create_engine("sqlite+pysqlite:///mydatabase.db", echo=True)

        self.load_regions()
        self.load_years()
        self.load_population()

        self.ui.cmbRegions.currentIndexChanged.connect(self.load_population)
        self.ui.cmbYear.currentIndexChanged.connect(self.load_population)
        self.ui.btnAdd.clicked.connect(self.on_btnAdd_click)
        self.ui.btnRemove.clicked.connect(self.on_btnRemove_click)
        self.ui.btnEdit.clicked.connect(self.on_btnEdit_click)
        self.ui.btnShow.clicked.connect(self.on_btnShow_click)

        self.ui.tblItems.clicked.connect(self.on_tblItems_clicked)

    def on_btnShow_click(self):
        checkbox: QtWidgets.QCheckBox
        for key, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                print(key)
            

    def on_tblItems_clicked(self, item: QtCore.QModelIndex):
        if self.lastTblItemsItemClicked and self.lastTblItemsItemClicked.row() == item.row():
            return
        
        self.lastTblItemsItemClicked = item

        data = item.data(QtCore.Qt.ItemDataRole.UserRole)
        print(data)

    def on_btnEdit_click(self):
        item = self.ui.tblItems.currentIndex()
        init_data = item.data(QtCore.Qt.ItemDataRole.UserRole)

        dialog = UpdateDialog(self.regions, init_data)
        r = dialog.exec()
        if r == 0:
            return
        
        data = dialog.get_data()

        with Session(self.engine)  as s:
            query = """
            UPDATE populations
            SET year = :y, population = :p
            WHERE id = :id
            """

            s.execute(text(query), {
                "y": data['year'],
                "p": data['population'],
                "id": init_data.id,
            })
            s.commit()

        self.load_population()
        self.load_years()

    def on_btnRemove_click(self):
        item = self.ui.tblItems.currentIndex()
        data = item.data(QtCore.Qt.ItemDataRole.UserRole)

        r = QMessageBox.question(self, "Подтверждение", "Точно ли хотите удалить запись?")
        if r == QMessageBox.StandardButton.No:
            return

        with Session(self.engine) as s:
            query = """
            DELETE 
            FROM populations 
            WHERE id = :id
            """

            s.execute(text(query), {"id": data.id})
            s.commit()

        self.load_population()
        self.load_years()
    
    def on_btnAdd_click(self):
        dialog = EditDialog(self.regions)
        r = dialog.exec()
        if r == 0:
            return

        data = dialog.get_data()
        with Session(self.engine) as s:
            query = """
            INSERT INTO populations(region_id, year, population)
            VALUES (:rid, :y, :p)
            """

            result = s.execute(text(query), {
                "rid": data['region_id'],
                "y": data['year'],
                "p": data['population'],
            })
            s.commit()
            print("id:",  result.lastrowid)

        self.load_population()
        self.load_years()

    def load_population(self):
        regions_data = self.ui.cmbRegions.currentData()
        if regions_data:
            region_id = self.ui.cmbRegions.currentData().id
        else:
            region_id = 0

        year = self.ui.cmbYear.currentText()

        # self.ui.lstItems.clear()
        self.rows = []

        with Session(self.engine) as s:
            query = """
            SELECT *
            FROM populations
            WHERE (:rid = 0 OR region_id = :rid) 
                AND (:y = '-' OR year = :y)
            ORDER BY  year DESC
            """

            rows = s.execute(text(query), {"rid": region_id, "y": year})

            for r in rows:
                self.rows.append(r)

        self.model.setItems(self.rows)

        self.show_statistics()
        self.draw_line_chart()
        self.draw_pie_chart()
        self.draw_bar_chart()

    
    def draw_bar_chart(self):
        self.data_by_regions = {}
        
        years = set()
        for row in self.rows:
            items = self.data_by_regions.setdefault(row.region_id, {})
            items[row.year] = row.population
            years.add(row.year)

        years = sorted(years)
        print('YEARS:', years)

        series = QtCharts.QHorizontalStackedBarSeries()
        series.setLabelsPrecision(20)
        series.setLabelsFormat("@value")

        for region_id, region_info in self.data_by_regions.items():
            region = self.regions[region_id]
            bar_set = QtCharts.QBarSet(region.title)
            for year in years:
                value = region_info.get(year, 0)
                bar_set.append(value) 
            bar_set.setLabelColor("#000")
            series.append(bar_set)

        series.setLabelsVisible(True)
        # series.setLabelsPosition(QtCharts.QAbstractBarSeries.LabelsPosition.LabelsCenter)

        chart = QtCharts.QChart()
        chart.addSeries(series)

        chart.createDefaultAxes()
        
        axis = QtCharts.QBarCategoryAxis()
        axis.append([str(i) for i in years])
        series.attachAxis(axis)
        chart.setAxisY(axis)

        chart.axisX().setLabelFormat("%i")
        chart.setAnimationOptions(QtCharts.QChart.AnimationOption.SeriesAnimations)

        self.ui.chartView3.setChart(chart)

    def draw_pie_chart(self):
        self.data_by_regions = {}

        for row in self.rows:
            items = self.data_by_regions.setdefault(row.region_id, [])
            items.append(row)

        series = QtCharts.QPieSeries()
        for region_id, region_data in self.data_by_regions.items():
            region_name = self.regions[region_id].title
            avg = int(mean([i.population for i in region_data]))
            series.append(f"{region_name}", avg)
        
        series.setLabelsVisible()

        chart = QtCharts.QChart()
        chart.addSeries(series)

        self.ui.chartView2.setChart(chart)


    def draw_line_chart(self):
        self.data_by_regions = {}

        for row in self.rows:
            items = self.data_by_regions.setdefault(row.region_id, [])
            items.append(row)

        chart = QtCharts.QChart()
        for region_id, region_data in self.data_by_regions.items():
            region_name = self.regions[region_id].title

            series = QtCharts.QLineSeries()
            series.setName(region_name)
            series.setPointsVisible(True)
            series.setMarkerSize(4)
            for row in region_data:
                series.append(row.year, row.population)
            
            chart.addSeries(series)
            
        chart.createDefaultAxes()
        chart.axisX().setTitleText("Год")
        chart.axisX().setLabelFormat("%i")
        chart.axisX().setMax(chart.axisX().max() + 1)
        chart.axisX().setMin(chart.axisX().min() - 1)
        
        chart.axisY().setLabelFormat("%i")
        chart.axisY().setTitleText("Население, чел.")
        chart.axisY().setMax(chart.axisY().max() + 100000)
        chart.axisY().setMin(chart.axisY().min() - 100000)

        self.ui.chartView1.setChart(chart)

    def show_statistics(self):
        max_row = max(self.rows, key=lambda row: row.population)
        min_row = min(self.rows, key=lambda row: row.population)
        avg_population = int(mean([i.population for i in self.rows]))

        region_name = self.regions[max_row.region_id].title
        min_region_name = self.regions[min_row.region_id].title

        self.ui.lblStatistics.setText(f"""
        Наибольший показатель числености населения составил 
        <br> <b style="color: #f542c8; font-size: 16px">{max_row.population}</b> человека в  <b style="color: #4290f5">{max_row.year}</b> году в регионе <u><b>{region_name}</b></u>
        <hr>
        Наименьший показатель числености населения составил 
        <br> <b style="color: #f542c8; font-size: 16px">{min_row.population}</b> человека в <b style="color: #4290f5">{min_row.year}</b> году в регионе <u><b>{min_region_name}</b></u>
        <hr>
        Среднее значение населения составило: <span style="background: yellow">{avg_population} человека</span>
        """)



    def load_regions(self):
        self.regions = {}

        with Session(self.engine) as s:
            query = """
            SELECT *
            FROM regions
            """

            rows = s.execute(text(query))
            for r in rows:
                self.regions[r.id] = r

        self.ui.cmbRegions.addItem("-")
        for r in self.regions.values():
            self.ui.cmbRegions.addItem(r.title, r)

        self.model.setRegion(self.regions)
            
    def load_years(self):
        self.ui.cmbYear.clear()
        self.ui.cmbYear.addItem("-")

        with Session(self.engine) as s:
            query = """
            SELECT DISTINCT year
            FROM populations
            ORDER BY 1 DESC
            """

            rows = s.execute(text(query))
            for r in rows:
                self.ui.cmbYear.addItem(str(r.year))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())