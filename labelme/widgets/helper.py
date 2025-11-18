import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QTextBrowser, QDesktopWidget,
)
from PyQt5.QtGui import QFont, QTextOption
from PyQt5.QtCore import (
    Qt, QFile, QIODevice, QTextStream, QTextCodec, QSize
)
from qtpy import QtCore, QtWidgets 

import labelme.widgets.helper_text.help

# --- Класс для отображения Markdown-подсказок ---

class Helper(QtWidgets.QDialog):
    """
    Диалог для отображения Markdown-текста с использованием QTextBrowser.
    Настроен на полноэкранное отображение с фиксированным размером.
    """
    def __init__(self, markdown_text, parent=None):
        # Устанавливаем флаги окна
        super(Helper, self).__init__(
            parent,
            Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint
        )
        self.setWindowTitle("Справка")
        
        # 1. Настройка размеров окна
        desktop = QDesktopWidget()
        # Получаем размеры рабочего пространства экрана
        screen_rect = desktop.availableGeometry(desktop.primaryScreen())
        
        # Устанавливаем отступы от краев экрана
        margin = 50 
        
        # Вычисляем нужные размеры окна
        width = screen_rect.width() - 2 * margin
        height = screen_rect.height() - 2 * margin

        # Устанавливаем фиксированный размер и позицию окна
        self.setGeometry(
            screen_rect.x() + margin, 
            screen_rect.y() + margin, 
            width, 
            height
        )
        # Запрещаем изменение размера окна
        self.setFixedSize(QSize(width, height))

        # 2. Создание и настройка QTextBrowser
        self.browser = QTextBrowser(self)
        
        # Загружаем Markdown-текст
        self.browser.setMarkdown(markdown_text)
        
        # Включаем перенос текста по словам, чтобы не было горизонтальной прокрутки
        self.browser.setWordWrapMode(QTextOption.WordWrap)
        
        # Устанавливаем базовый шрифт
        font = QFont("Arial", 12)
        self.browser.setFont(font)
        
        # 3. Настройка макета
        layout = QVBoxLayout(self)
        layout.addWidget(self.browser)
        self.setLayout(layout)

    def popUp(self):
        """Отображает диалог как модальное окно."""
        self.exec_() 

# --- Класс для извлечения текста из ресурсов (HelperText) ---

class HelperString:
    """
    Извлекает текст справки из ресурсов Qt. 
    Использует оригинальные имена файлов с расширением .md.
    """
    def __init__(self):
        # Префикс ресурса для организации файлов справки
        resource_prefix = ":/" 
        
        try:
            # Используем оригинальные названия файлов, заменяя .txt на .md
            self.keyboard = self.__read_resource_file(resource_prefix + "keyboard.md")
            self.letter = self.__read_resource_file(resource_prefix + "letter.md")
            self.line = self.__read_resource_file(resource_prefix + "line.md")
            self.main = self.__read_resource_file(resource_prefix + "main.md")
        except Exception as e:
            # Обработка ошибки загрузки ресурсов
            print(f"Ошибка загрузки файлов справки: {e}") 
            self.keyboard = "**Ошибка загрузки:** keyboard.md"
            self.letter = "**Ошибка загрузки:** letter.md"
            self.line = "**Ошибка загрузки:** line.md"
            self.main = "**Ошибка загрузки:** main.md"

    def __read_resource_file(self, path):
        """Считывает содержимое файла из ресурсов Qt с кодировкой UTF-8."""
        f = QFile(path)
        if not f.open(QIODevice.ReadOnly | QFile.Text):
            raise Exception(f"Не удалось открыть файл ресурса: {path}")
            
        text = QTextStream(f)
        text.setCodec(QTextCodec.codecForName("UTF-8"))
        
        result = text.readAll()
        f.close()
        return result
        
    # Оригинальные методы-геттеры
    def get_letter_helper(self):
        return self.letter
    
    def get_keyboard_helper(self):
        return self.keyboard
    
    def get_line_helper(self):
        return self.line 
    
    def get_main_helper(self):
        return self.main