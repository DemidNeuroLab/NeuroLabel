from qtpy import QtWidgets
from enum import Enum

class ManuscriptType(Enum):
    устав = 0
    полуустав = 1
    скоропись = 2

class ManuscriptTypeWidget(QtWidgets.QWidget):
    def __init__(self, value):
        super().__init__()
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(QtWidgets.QLabel(self.tr("Тип письма:")))
        self.combo_box = TypeComboBox(value)
        self.layout().addWidget(self.combo_box)
    
    def GetCurrentValue(self):
        value = self.combo_box.currentData()
        return ManuscriptType(value)
    
    def LoadSetType(self, type):
        self.combo_box.setCurrentText(type)

class TypeComboBox(QtWidgets.QComboBox):
    def __init__(self, value):
        super().__init__()
        for type in ManuscriptType:
            self.addItem(type.name, type.value)
        self.setCurrentText(value)