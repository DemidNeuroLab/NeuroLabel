from qtpy import QtWidgets

class ManuscriptTypeWidget(QtWidgets.QWidget):
    def __init__(self, value):
        super().__init__()
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(QtWidgets.QLabel(self.tr("Тип письма:")))
        self.combo_box = TypeComboBox(value)
        self.layout().addWidget(self.combo_box)
    
    def GetCurrentValue(self):
        return self.combo_box.currentText()
    
    def LoadSetType(self, type):
        self.combo_box.setCurrentText(type)

class TypeComboBox(QtWidgets.QComboBox):
    def __init__(self, value):
        super().__init__()
        self.addItems(["Устав", "Полуустав", "Скоропись"])
        self.setCurrentText(value)