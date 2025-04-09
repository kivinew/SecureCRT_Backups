# Проект GUI приложения на QT

import sys

from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import os
# os.add_dll_directory("C:/PythonXX/Lib/site-packages/PyQt6/Qt6/bin")

class MainWindow(QMainWindow):
    pass
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Окно программы")
        
        label = QLabel("Приложение")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.setCentralWidget(label)

app = QApplication(sys.argv)

windows = MainWindow()
windows.show()

app.exec()