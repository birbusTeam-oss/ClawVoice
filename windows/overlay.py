from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor


class RecordingOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFixedSize(220, 52)
        self._setup_ui()
        self._position()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setSpacing(10)

        self.dot = QLabel("●")
        self.dot.setStyleSheet("color: #ff4444; font-size: 13px;")
        self.dot.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(self.dot)

        self.label = QLabel("Listening...")
        self.label.setStyleSheet("color: white; font-size: 13px; font-weight: 600; font-family: 'Segoe UI', sans-serif;")
        self.label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(self.label)
        layout.addStretch()

        self._pulse_state = True
        self._timer = QTimer()
        self._timer.timeout.connect(self._pulse)

    def _pulse(self):
        self._pulse_state = not self._pulse_state
        color = "#ff4444" if self._pulse_state else "#991111"
        self.dot.setStyleSheet(f"color: {color}; font-size: 13px;")

    def _position(self):
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.geometry()
            self.move((geo.width() - self.width()) // 2, geo.height() - 120)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(20, 16, 48, 235))
        painter.setPen(QColor(107, 94, 205, 160))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 26, 26)

    def focusInEvent(self, event):
        pass

    def show_recording(self):
        self.dot.setStyleSheet("color: #ff4444; font-size: 13px;")
        self.label.setText("Listening...")
        self._timer.start(500)
        self._position()
        self.show()

    def show_transcribing(self):
        self._timer.stop()
        self.dot.setStyleSheet("color: #f0a500; font-size: 13px;")
        self.label.setText("Transcribing...")
        self.show()

    def hide_overlay(self):
        self._timer.stop()
        self.hide()
