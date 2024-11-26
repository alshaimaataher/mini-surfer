# main.py
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
#import matplotlib.pyplot as plt

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QApplication, QFileDialog, QTableWidget, QTableWidgetItem, QMessageBox
#from PyQt5 import uic
#import numpy as np
import pandas as pd
import calculations as cal
from mysurfer import Ui_MainWindow

#ui_path = os.path.dirname(os.path.abspath(__file__))
#form_class = uic.loadUiType(os.path.join(ui_path, "mySurfer.ui"))[0]

#class Window(QMainWindow, form_class):
class Window(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.radius = None
        self.overlap = None
        self.width = None
        self.length = None
        self.mode = None
        self.sheet_counter = 1
        self.sheet = None
        self.tables={}

        
#--------------------------------------------------------------------------------------------
#Set layout for image view in the gui label
#--------------------------------------------------------------------------------------------
        self.plot_layout= QVBoxLayout()
        self.plotting_label.setLayout(self.plot_layout)
        self.plot_fig = Figure()
        self.plot_canvas = FigureCanvas(self.plot_fig)
        self.plot_layout.addWidget(self.plot_canvas)
        self.plot_ax = self.plot_fig.add_subplot(111, projection='3d')
        
        self.sheet_comboBox.addItem("--")
        self.sheet_comboBox.activated[str].connect(self.select_sheet)  
        self.shape_comboBox.addItems(["--","Square", "Rectangle", "Triangle"])
        self.shape_comboBox.activated[str].connect(self.select_landscape_mode)  
        self.actionImport.triggered.connect(self.import_file)
        self.actionAdd_Sheet.triggered.connect(self.add_sheet)

        self.radius_input.textEdited.connect(self.get_radius)
        self.first_input.returnPressed.connect(self.get_mode_dims)
        self.second_input.returnPressed.connect(self.get_mode_dims)
        self.mode_groupBox.hide()
        self.cal_groupBox.hide()
        
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Critical)
        self.msg.setWindowTitle("Error")



    def select_sheet(self,sheet):
        if(sheet != '--'):
            self.sheet=sheet
            self.radius_input.setText('')
            self.mode_groupBox.hide()
            self.hide_labels()
            self.table = self.tables[sheet]


    def get_radius(self):
        if(self.radius_input.text().isnumeric()):
            self.radius = int(self.radius_input.text())
            self.mode_groupBox.show()
        else:
            self.mode_groupBox.hide()
        self.hide_labels()


    def hide_labels(self):
        self.x_label.hide()
        self.y_label.hide()
        self.first_input.hide()
        self.second_input.hide()
        self.first_input.setText('')
        self.second_input.setText('')
        self.cal_groupBox.hide()
        self.plot_ax.clear()
        self.plot_canvas.draw()


    def select_landscape_mode(self,choice):
        self.hide_labels()
        self.mode = choice
        if choice == 'Square':
            self.x_label.show()
            self.first_input.show()
        elif choice =='Rectangle':
            self.x_label.show()
            self.first_input.show()
            self.y_label.show()
            self.second_input.show()
        elif choice == 'Triangle':
            self.overlap=100
            self.overlap_percent.setText(str(self.overlap)+' %')


    def get_mode_dims(self):
        self.cal_groupBox.hide()
        self.plot_ax.clear()
        self.plot_canvas.draw()
        if self.mode == 'Square' and self.first_input.text():
            if(self.first_input.text().isnumeric()):
                self.length = int(self.first_input.text())
                self.width = self.length
                if self.width >= self.radius and self.width <= self.radius*2:
                    try:
                        self.show_cals()
                    except:
                        self.msg.setText("Invalid dimensions")
                        self.msg.exec_()
                else:
                    self.msg.setText("length must be >= radious or <= radious*2 ")
                    self.msg.exec_()
                

        elif self.mode == 'Rectangle' and self.first_input.text() and self.second_input.text():
                if(self.first_input.text().isnumeric() and self.second_input.text().isnumeric):
                    self.length = int(self.first_input.text())
                    self.width = int(self.second_input.text())
                    if self.width >= self.radius and self.width <= self.radius*2 and self.length >= self.radius and self.length <= self.radius*2:  
                        try:
                            self.show_cals()
                        except:
                            self.msg.setText("Invalid dimensions")
                            self.msg.exec_()
                    else:
                        self.msg.setText("length and width must be >= radious or <= radious*2 ")
                        self.msg.exec_()
        
        
    def show_cals(self):
        cal_object=cal.Calculations(self.table,self.radius,self.length,self.width)

        self.cal_groupBox.show()
        self.overlap_percent.setText("{:.2f}".format(cal_object.cal_overlap())+' %')
        self.cu_percent.setText("{:.2f}".format(cal_object.cal_cu())+' %')
        self.du_percent.setText("{:.2f}".format(cal_object.cal_du())+' %')
        self.plot_ax.clear()
        cal_object.plot(self.plot_ax,self.plot_canvas)



    def import_file(self):
        fileName,_ = QFileDialog.getOpenFileName(self, 'Select Excel File','','*.xlsx *.xls')
        try:
            if fileName:
                df = pd.read_excel(fileName,index_col=None, header=None)
                if df.size == 0:
                    return
                table = self.add_sheet()
        
        
                # returns pandas array object
                for row in df.iterrows():
                    values = row[1]
                    for col_index, value in enumerate(values):
                        if isinstance(value, (float, int)):
                            value = '{0:0,.0f}'.format(value)
                        tableItem = QTableWidgetItem(str(value))
                        table.setItem(row[0], col_index, tableItem)
        except:
            self.msg.setText("Invalid sheet file!")
            self.msg.exec_()


    def add_sheet(self):
        table = QTableWidget()
        sheet_name = "Sheet "+str(self.sheet_counter)
        self.tabWidget.addTab(table,sheet_name)
        self.sheet_comboBox.addItem(sheet_name)
        self.sheet_counter+=1;
        
        table.setRowCount(500)
        table.setColumnCount(int(table.width()))
        table.setColumnWidth(int(table.width()), 300)
        table.setHorizontalHeaderLabels(['X','Y','Z'])
        self.tables[sheet_name] = table
        return table


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())


