from qtpy import QT_VERSION
from qtpy import QtCore
from qtpy import QtWidgets
from PyQt5.QtWidgets import QLabel, QTextEdit, QLineEdit
from PyQt5.QtCore import Qt, QSize, QEvent
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import *
from labelme.widgets.helper import Helper
import re

import labelme.utils
from labelme.widgets.keyboard import Keyboard
from labelme.fonts.slavic import SlavicFont
from labelme.widgets.label_letter_dialog import Literal
from labelme.fonts.titla_relation import TITLA_RELATIONS

QT5 = QT_VERSION[0] == "5"

# =============================================================================
#                          CONSTANTS FOR ADAPTIVE SIZING
# =============================================================================

MIN_TEXTVIEW_HEIGHT = 45
MIN_TEXTVIEW_WIDTH  = 300
FONT_MIN_SIZE = 20
FONT_MAX_SIZE = 36


class LabelLineDialog(QtWidgets.QDialog):
    """
        Окно, выдающее ту строку, которую пользователь ввёл со своей и/или с экранной клавиатуры.
        Если пользователь нажал cancel или закрыл окно, то вернётся None
        Если пользователь ввёл всё корректно, то вернётся строка
        Славянская клавиатура добавляет символы в конец вводимой строки 
    """
    def __init__(
        self,
        helper,
        parent=None,
        old_text=None
    ):
        super(LabelLineDialog, self).__init__(parent)
        self.recognised_line = None
        self.helper = helper
        self.workWithKeyboard = False

        # окно можно уменьшать, но только пока всё не наложится
        self.setMinimumSize(QSize(400, 100))

        layout = QtWidgets.QVBoxLayout()
        
        invite_label = QLabel()
        invite_label.setText("Разметка строки")
        invite_label.setFont(QFont('Arial', 18))
        layout.addWidget(invite_label, 0, Qt.AlignTop | Qt.AlignHCenter)
        
        layout_slavic_text = QtWidgets.QHBoxLayout()
        invite_text_label = QLabel()
        invite_text_label.setText("Введённая строка:")
        invite_text_label.setFont(QFont('Arial', 8))
        layout_slavic_text.addWidget(invite_text_label, 2)

        # =====================================================================
        #                          TEXT VIEW (MODIFIED)
        # =====================================================================
        self.text_view = QTextEdit()
        if old_text is not None:
            displayed_text = self.convert_titla_to_displayable_text(old_text)
            self.text_view.setText(displayed_text)

        # базовый шрифт
        self.text_view.setFont(SlavicFont.GetFont(14))

        self.text_view.setReadOnly(True)
        self.text_view.setWordWrapMode(QTextOption.NoWrap)

        # ОТКЛЮЧАЕМ СКРОЛЛЕРЫ
        self.text_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.text_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # минимальные размеры (константы)
        self.text_view.setMinimumHeight(MIN_TEXTVIEW_HEIGHT)
        self.text_view.setMinimumWidth(MIN_TEXTVIEW_WIDTH)

        # Убираем фиксированную высоту
        # self.text_view.setFixedHeight(65)   <-- удалено

        self.text_view.textChanged.connect(self.cursor_to_right)
        layout_slavic_text.addWidget(self.text_view, 9)

        layout.addLayout(layout_slavic_text)

        layout_enter = QtWidgets.QHBoxLayout()
        self.edit = QLineEdit()
        self.edit.setPlaceholderText("Аннотация строки")
        if old_text is not None:
            self.edit.setText(old_text)
        self.edit.textChanged.connect(self.changeLabel)
        layout_enter.addWidget(self.edit, 6)

        keyboard_button = QtWidgets.QPushButton("Славянская клавиатура")
        keyboard_button.clicked.connect(self.get_keyboard)
        layout_enter.addWidget(keyboard_button, 2)
        
        layout.addLayout(layout_enter)

        # кнопки
        self.buttonBox = bb = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal,
            self,
        )
        bb.button(bb.Ok).setIcon(labelme.utils.newIcon("done"))
        bb.button(bb.Cancel).setIcon(labelme.utils.newIcon("undo"))
        bb.button(bb.Ok).setText("Ок")
        bb.button(bb.Cancel).setText("Отменить")
        bb.accepted.connect(self.validate_input)
        bb.rejected.connect(self.reject)
        layout.addWidget(bb)

        self.setLayout(layout)
        
        # После всех настроек, сразу после self.show()
        self.adjustSize()  # корректируем размеры элементов
        self.setMinimumSize(self.minimumSizeHint())  # чтобы окно нельзя было уменьшить дальше
        self.resize(self.width(), self.minimumSizeHint().height())  # стартовая высота = минимально возможная


    # =====================================================================
    #                   АДАПТИВНОЕ ИЗМЕНЕНИЕ РАЗМЕРА ПОЛЯ
    # =====================================================================
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_text_view_size()
        self.update_minimum_dialog_size()

    def adjust_text_view_size(self):
        """
        1. Подбираем подходящий размер шрифта (без скроллов)
        2. Автоматически выставляем высоту поля исходя из высоты шрифта
        """

        text = self.text_view.toPlainText()
        if not text:
            text = " "  # измерение минимальной ширины

        allowed_width = self.text_view.viewport().width()

        # адаптивный подбор размера шрифта
        best_size = FONT_MIN_SIZE
        for size in range(FONT_MIN_SIZE, FONT_MAX_SIZE + 1):
            f = self.text_view.font()
            f.setPointSize(size)
            fm = QFontMetrics(f)
            pixel_width = fm.horizontalAdvance(text)

            if pixel_width > allowed_width - 10:
                break
            best_size = size

        # применяем лучший размер
        f = self.text_view.font()
        f.setPointSize(best_size)
        self.text_view.setFont(f)

        # вычисляем высоту одной строки
        fm = QFontMetrics(self.text_view.font())
        line_h = fm.height() + 12

        if line_h < MIN_TEXTVIEW_HEIGHT:
            line_h = MIN_TEXTVIEW_HEIGHT

        self.text_view.setFixedHeight(line_h)

    def update_minimum_dialog_size(self):
        """
        Обновляет минимальный размер окна исходя из текущего layout,
        чтобы элементы не могли наехать друг на друга.
        """
        self.layout().activate()
        minsize = self.layout().minimumSize()
        self.setMinimumSize(minsize)

    # =====================================================================
    #                      ОРИГИНАЛЬНАЯ ЛОГИКА (НЕ ТРОГАЛ!)
    # =====================================================================

    def validate_input(self):
        text = self.edit.text()
        if text == "":
            self.recognised_line = Literal(text)
            self.close()
            return
        if not all(letter in SlavicFont.ALL for letter in text):
            self.getMessageBox("Введён некорректный символ!")
        elif text[0] in SlavicFont.DIACRITICAL_SIGNS:
            self.getMessageBox("Диакритический знак не может быть в начале строки!") 
        elif text[-1] == "=":
            self.getMessageBox("Титло не может быть в конце строки без буквы!") 
        else:
            for i in range(len(text) - 1):
                if text[i] in SlavicFont.DIACRITICAL_SIGNS and text[i + 1] in SlavicFont.DIACRITICAL_SIGNS:
                    self.getMessageBox("В строке не могут подряд идти 2 диакритических знака!")
                    return
                if text[i] == "=" and text[i+1] not in SlavicFont.LETTERS:
                    self.getMessageBox("После титла обязана идти буква!")
                    return
            self.recognised_line = Literal(text)
            self.close()

    def convert_titla_to_displayable_text(self, text):
        pattern = re.compile(r'=(\w)')

        def replacer(match):            
            char = match.group(1)
            full_match = match.group(0)

            if char in SlavicFont.ALL:
                key = full_match 
                return TITLA_RELATIONS.get(key, full_match)
            else:
                return full_match

        return pattern.sub(replacer, text)

    def getMessageBox(self, text):
        messageBox = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Warning,
                "Ошибка",
                text
            )
        messageBox.addButton("Ок", QtWidgets.QMessageBox.YesRole)
        messageBox.exec_()
        
    def changeLabel(self):
        text = self.edit.text()
        
        if not all(letter in SlavicFont.ALL for letter in text):
            self.text_view.setText("")
            self.getMessageBox("Введён некорректный символ! Отображение строки отключено, пока ввод не будет исправен!")
        else:
            displayed_text = self.convert_titla_to_displayable_text(text)
            self.text_view.setText(displayed_text)
        
    def cursor_to_right(self):
        cursor = self.text_view.textCursor()     
        cursor.movePosition(QTextCursor.End) 
        self.text_view.setTextCursor(cursor)
        
    def get_keyboard(self):
        self.workWithKeyboard = True
        letter = Keyboard(self.helper).popUp()
        self.workWithKeyboard = False
        if letter is not None:
            self.edit.setText(self.edit.text() + letter)
            self.changeLabel()

    def event(self, event):
        if not self.workWithKeyboard and event.type() == QEvent.EnterWhatsThisMode:
            QWhatsThis.leaveWhatsThisMode()
            Helper(self.helper.get_line_helper()).popUp()
        return QDialog.event(self, event)

    def popUp(self):
        self.exec_()
        return self.recognised_line
