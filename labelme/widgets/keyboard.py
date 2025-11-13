# keyboard.py
from PyQt5.QtWidgets import (
    QDialog, QFrame, QGridLayout, QVBoxLayout, QLabel, QScrollArea,
    QPushButton, QSizePolicy, QApplication, QDesktopWidget, QWidget, QWhatsThis
)
from PyQt5.QtCore import Qt, QEvent, QSize
from PyQt5.QtGui import QFont, QFontMetrics
from math import isqrt, ceil
from labelme.fonts.slavic import SlavicFont
from labelme.widgets.helper import Helper
from labelme.fonts.letters_description import LETTER_DESCRIPTIONS


class PushButton(QPushButton):
    """Кнопка буквы — шрифт и размер подстраиваются по высоте, set_size задаёт высоту."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setText(text)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # начальный (малый) шрифт — будет изменён в set_size
        try:
            self.setFont(SlavicFont.GetFont(12))
        except Exception:
            self.setFont(QFont("Arial", 12))
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_enlarged_letter)

    def set_size(self, height_px: int):
        """Устанавливаем высоту кнопки и подбираем внутри шрифт так, чтобы буква занимала большую часть."""
        # оставим небольшой внутренний отступ: размер шрифта чуть меньше высоты
        btn_h = max(12, int(height_px))
        self.setFixedHeight(btn_h)
        # шрифт в кнопке — около 70..85% высоты кнопки, но в пунктах
        # получаем ориентир в pt, но SlavicFont.GetFont ожидает px-like integer in your project — используем его
        font_px = max(8, int(btn_h * 0.75))
        try:
            self.setFont(SlavicFont.GetFont(font_px))
        except Exception:
            self.setFont(QFont("Arial", max(8, int(font_px))))

    def show_enlarged_letter(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Информация о букве")
        dlg.setMinimumSize(420, 360)
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # большая буква
        big = QLabel(self.text())
        try:
            big.setFont(SlavicFont.GetFont(200))
        except Exception:
            big.setFont(QFont("Arial", 200))
        big.setAlignment(Qt.AlignCenter)
        layout.addWidget(big)

        # описание
        desc_text = "Описание отсутствует"
        cur = self.text()
        for category in LETTER_DESCRIPTIONS.values():
            if cur in category:
                desc_text = category[cur]
                break
        desc = QLabel(desc_text)
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("font-size: 14px;")
        layout.addWidget(desc)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dlg.close)
        layout.addWidget(close_btn)

        dlg.exec_()


class Keyboard(QDialog):
    """
    Адаптивная клавиатура.
    - popUp() вызывает exec_() (без showMaximized()).
    - При открытии popUp() окно получает размер ~95%×90% экрана (через setGeometry/resize),
      но остаётся модальным диалогом.
    - Каждая ячейка фрейма: 30% высоты — подпись, 70% — кнопка.
    """
    MAX_COLUMNS = 12
    FRAME_SPACING = 12
    FRAME_MARGIN = 12

    def __init__(self, helper, parent=None):
        # НЕ меняю логику создания — parent по умолчанию None (как у тебя)
        super().__init__(parent)
        self.helper = helper
        self.text_from_keyboard = None

        # Окно как диалог, но с кнопками сворачивания/разворачивания
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.WindowMinMaxButtonsHint)
        self.setWindowTitle("Славянская клавиатура")
        self.setMinimumSize(320, 200)

        # основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # подсказка сверху
        self.hint_label = QLabel("ПКМ по кнопке — информация о букве")
        self.hint_label.setAlignment(Qt.AlignCenter)
        self.hint_label.setStyleSheet("background:#f0f0f0; padding:8px; font-size:13px;")
        main_layout.addWidget(self.hint_label)

        # scroll area (widgetResizable=True), но мы не хотим видимых скроллбаров
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        main_layout.addWidget(self.scroll_area)

        # данные символов
        self.symbols = SlavicFont.ALL
        self.columns = min(isqrt(len(self.symbols)) + 1, self.MAX_COLUMNS)
        self.rows = ceil(len(self.symbols) / self.columns)

        # grid widget
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(self.FRAME_MARGIN, self.FRAME_MARGIN,
                                            self.FRAME_MARGIN, self.FRAME_MARGIN)
        self.grid_layout.setSpacing(self.FRAME_SPACING)
        self.scroll_area.setWidget(self.grid_widget)

        # создаём ячейки
        self._frames = []
        self._labels = []
        self._buttons = []

        for i, ch in enumerate(self.symbols):
            r = i // self.columns
            c = i % self.columns

            frame = QFrame()
            frame.setStyleSheet("QFrame { background: white; border: 1px solid #bbb; border-radius: 8px; }")
            vbox = QVBoxLayout(frame)
            vbox.setContentsMargins(6, 6, 6, 6)
            vbox.setSpacing(0)

            # подпись сверху (30%)
            label = QLabel(ch if ch != " " else "Пробел")
            label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            label.setWordWrap(False)
            vbox.addWidget(label, 3)  # вес 3 → 30%

            # кнопка (70%)
            btn = PushButton(ch)
            btn.clicked.connect(self._on_click)
            vbox.addWidget(btn, 7)  # вес 7 → 70%

            self.grid_layout.addWidget(frame, r, c)
            # сохраняем для дальнейшей корректировки
            frame.top_label = label
            frame.button = btn
            self._frames.append(frame)
            self._labels.append(label)
            self._buttons.append(btn)

        # начальная корректировка размеров (будет корректироваться в resizeEvent)
        self._initial_fit_done = False

    def _fit_to_screen_before_show(self):
        """Перед показом выставляем окно почти на весь экран, но НЕ showMaximized()."""
        desktop = QDesktopWidget()
        screen_rect = desktop.availableGeometry()
        # 95% ширины и 90% высоты — можно регулировать
        w = int(screen_rect.width() * 0.95)
        h = int(screen_rect.height() * 0.90)
        x = screen_rect.x() + (screen_rect.width() - w) // 2
        y = screen_rect.y() + (screen_rect.height() - h) // 2
        self.setGeometry(x, y, w, h)

    def popUp(self):
        """
        Метод, который вызывается извне. НЕ ломает логику диалогов:
        - Размер задаём заранее через setGeometry (чтобы окно было большое),
        - затем вызываем exec_() (модальный диалог).
        """
        self._fit_to_screen_before_show()
        # теперь exec_() откроет модальный диалог с заданной геометрией
        self.exec_()
        return self.text_from_keyboard

    def resizeEvent(self, event):
        """
        Пересчитываем размеры слотов и шрифтов при изменении размера диалога.
        Алгоритм:
        - берем доступное пространство (ширина диалога минус отступы и подсказка),
        - делим по колонкам/строкам, учитываем spacing,
        - для каждого слота вычисляем side = min(slot_w, slot_h),
        - внутри фрейма назначаем label_height = 30% side, button_height = 70% side,
        - подбираем шрифты: для подписи — проверяем ширину через QFontMetrics и уменьшаем, если надо.
        """
        super().resizeEvent(event)

        # доступное внутри диалога пространство (учитываем рамки/отступы)
        total_w = max(1, self.width() - 2 * self.FRAME_MARGIN)
        total_h = max(1, self.height() - self.hint_label.height() - 2 * self.FRAME_MARGIN)

        total_w_spacing = (self.columns - 1) * self.FRAME_SPACING
        total_h_spacing = (self.rows - 1) * self.FRAME_SPACING

        slot_w = (total_w - total_w_spacing) / max(1, self.columns)
        slot_h = (total_h - total_h_spacing) / max(1, self.rows)

        # базовый размер слота (квадратная метрика)
        slot_side = max(40, int(min(slot_w, slot_h)))

        # размеры внутри фрейма
        label_h = max(10, int(slot_side * 0.30))   # 30%
        button_h = max(12, int(slot_side * 0.70))  # 70%

        # ограничиваем общий frame size: высота = label_h + button_h + inner margins
        inner_v_margins = 12  # содержимое layout margins (примерное)
        frame_h = label_h + button_h + inner_v_margins
        frame_w = max(40, int(slot_side))

        # применяем размеры и подбираем шрифты
        for frame, label, btn in zip(self._frames, self._labels, self._buttons):
            # устанавливаем фиксированный размер фрейма (чтобы сетка была ровной)
            frame.setFixedSize(int(frame_w), int(frame_h))

            # подпись — подбираем шрифт по ширине фрейма (чтобы не вылезала)
            # стартовый шрифт — относительный к ширине
            max_label_font = max(7, int(frame_w * 0.12))
            font = QFont("Arial", max_label_font)
            fm = QFontMetrics(font)
            text = label.text()
            text_width = fm.horizontalAdvance(text)
            # уменьшаем шрифт пока текст не поместится (оставляем небольшой процент от ширины)
            while text_width > frame_w * 0.9 and font.pointSize() > 6:
                font.setPointSize(font.pointSize() - 1)
                fm = QFontMetrics(font)
                text_width = fm.horizontalAdvance(text)
            label.setFont(font)
            label.setFixedHeight(label_h)

            # кнопка — задаём высоту; в PushButton.set_size шрифт внутри подбирается
            btn.set_size(button_h)
            # ограничиваем ширину кнопки (центрирование внутри frame останется через layout)
            btn.setFixedWidth(int(frame_w * 0.9))

        # скорректируем минимальный размер окна на основе сетки, но держим его небольшим
        total_min_w = int(self.columns * frame_w + total_w_spacing + 2 * self.FRAME_MARGIN + 20)
        total_min_h = int(self.rows * frame_h + total_h_spacing + self.hint_label.height() + 2 * self.FRAME_MARGIN + 20)
        min_w = max(320, min(total_min_w, 1600))
        min_h = max(240, min(total_min_h, 1200))
        self.setMinimumSize(min_w, min_h)

    def _on_click(self):
        btn = self.sender()
        if isinstance(btn, PushButton):
            self.text_from_keyboard = btn.text()
            self.close()

    def event(self, event):
        """WhatsThis behavior сохранён."""
        if event.type() == QEvent.EnterWhatsThisMode:
            QWhatsThis.leaveWhatsThisMode()
            Helper(self.helper.get_keyboard_helper()).popUp()
        return QDialog.event(self, event)
