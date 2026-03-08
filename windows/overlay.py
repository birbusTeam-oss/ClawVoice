"""
Floating recording indicator — shows when ClawVoice is listening.
Appears bottom-center of screen, auto-hides when done.
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QRect
from PyQt6.QtGui import QColor, QPainter, QFont

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
        self.setFixedSize(220, 52)
        self._setup_ui()
        self._position_bottom_center()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(10)

        self.dot = QLabel("●")
        self.dot.setStyleSheet("color: #ff4444; font-size: 14px;")
        layout.addWidget(self.dot)

        self.label = QLabel("Listening...")
        self.label.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: 600;
            font-family: 'Segoe UI', sans-serif;
        """)
        layout.addWidget(self.label)
        layout.addStretch()

        # Pulse timer for the dot
        self._pulse = True
        self._timer = QTimer()
        self._timer.timeout.connect(self._pulse_dot)
        self._timer.start(500)

    def _pulse_dot(self):
        self._pulse = not self._pulse
        self.dot.setStyleSheet(f"color: {'#ff4444' if self._pulse else '#aa2222'}; font-size: 14px;")

    def _position_bottom_center(self):
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = screen.height() - 120
        self.move(x, y)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(20, 16, 48, 230))
        painter.setPen(QColor(107, 94, 205, 180))
        painter.drawRoundedRect(self.rect().adjusted(1,1,-1,-1), 26, 26)

    def show_recording(self):
        self.dot.setStyleSheet("color: #ff4444; font-size: 14px;")
        self.label.setText("Listening...")
        self._timer.start(500)
        self._position_bottom_center()
        self.show()
        self.raise_()

    def show_transcribing(self):
        self._timer.stop()
        self.dot.setStyleSheet("color: #f0a500; font-size: 14px;")
        self.label.setText("Transcribing...")
        self.show()
        self.raise_()

    def hide_overlay(self):
        self._timer.stop()
        self.hide()
