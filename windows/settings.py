from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QFont, QIcon, QPalette, QLinearGradient, QPainter, QBrush

class SettingsWindow(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowTitle("ClawVoice")
        self.setFixedSize(420, 380)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._drag_pos = None
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        # Main container
        self.container = QFrame(self)
        self.container.setObjectName("container")
        self.container.setGeometry(0, 0, 420, 380)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # Header row
        header = QHBoxLayout()

        # Logo + title
        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        logo_label = QLabel("🎙️")
        logo_label.setObjectName("logo")
        title_col.addWidget(logo_label)

        title = QLabel("ClawVoice")
        title.setObjectName("title")
        title_col.addWidget(title)

        subtitle = QLabel("Open source voice dictation")
        subtitle.setObjectName("subtitle")
        title_col.addWidget(subtitle)

        header.addLayout(title_col)
        header.addStretch()

        # Close button
        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedSize(28, 28)
        close_btn.clicked.connect(self.hide)
        header.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignTop)

        layout.addLayout(header)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setObjectName("divider")
        layout.addWidget(divider)

        # API Key section
        key_label = QLabel("ANTHROPIC API KEY")
        key_label.setObjectName("sectionLabel")
        layout.addWidget(key_label)

        # Key input row
        key_row = QHBoxLayout()
        key_row.setSpacing(8)

        self.key_input = QLineEdit()
        self.key_input.setObjectName("keyInput")
        self.key_input.setPlaceholderText("sk-ant-api03-...")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setText(self.config.anthropic_key)
        self.key_input.setFixedHeight(44)
        key_row.addWidget(self.key_input)

        toggle_btn = QPushButton("👁")
        toggle_btn.setObjectName("toggleBtn")
        toggle_btn.setFixedSize(44, 44)
        toggle_btn.setCheckable(True)
        toggle_btn.toggled.connect(lambda checked: self.key_input.setEchoMode(
            QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        ))
        key_row.addWidget(toggle_btn)
        layout.addLayout(key_row)

        # Helper link
        link = QLabel('<a href="https://console.anthropic.com" style="color: #7C6EE0;">Get your free API key →</a>')
        link.setObjectName("link")
        link.setOpenExternalLinks(True)
        layout.addWidget(link)

        # Hotkey info card
        hotkey_card = QFrame()
        hotkey_card.setObjectName("hotkeyCard")
        hotkey_layout = QHBoxLayout(hotkey_card)
        hotkey_layout.setContentsMargins(16, 12, 16, 12)

        hotkey_icon = QLabel("⌨️")
        hotkey_icon.setFixedWidth(24)
        hotkey_layout.addWidget(hotkey_icon)

        hotkey_text = QVBoxLayout()
        hotkey_text.setSpacing(2)
        h1 = QLabel("Hold Right Alt to dictate")
        h1.setObjectName("hotkeyTitle")
        hotkey_text.addWidget(h1)
        h2 = QLabel("Release to transcribe and inject text")
        h2.setObjectName("hotkeyDesc")
        hotkey_text.addWidget(h2)
        hotkey_layout.addLayout(hotkey_text)

        layout.addWidget(hotkey_card)

        layout.addStretch()

        # Save button
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setObjectName("saveBtn")
        self.save_btn.setFixedHeight(44)
        self.save_btn.clicked.connect(self.save)
        layout.addWidget(self.save_btn)

        # Version
        version = QLabel("v0.1 — Built by the Birbus Team")
        version.setObjectName("version")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)

    def apply_styles(self):
        self.setStyleSheet("""
            #container {
                background-color: #111118;
                border-radius: 16px;
                border: 1px solid #2a2a3a;
            }
            #logo {
                font-size: 28px;
            }
            #title {
                font-size: 20px;
                font-weight: 700;
                color: #ffffff;
                font-family: -apple-system, 'Segoe UI', sans-serif;
            }
            #subtitle {
                font-size: 12px;
                color: #6b6b8a;
                font-family: -apple-system, 'Segoe UI', sans-serif;
            }
            #closeBtn {
                background: transparent;
                border: none;
                color: #6b6b8a;
                font-size: 14px;
                border-radius: 14px;
            }
            #closeBtn:hover {
                background: #2a2a3a;
                color: #ffffff;
            }
            #divider {
                color: #2a2a3a;
                background: #2a2a3a;
                max-height: 1px;
            }
            #sectionLabel {
                font-size: 10px;
                font-weight: 700;
                color: #6b6b8a;
                letter-spacing: 1.5px;
                font-family: -apple-system, 'Segoe UI', sans-serif;
            }
            #keyInput {
                background: #1a1a28;
                border: 1px solid #2a2a3a;
                border-radius: 10px;
                color: #ffffff;
                font-size: 13px;
                padding: 0 14px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            #keyInput:focus {
                border: 1px solid #7C6EE0;
                outline: none;
            }
            #keyInput::placeholder {
                color: #3a3a5a;
            }
            #toggleBtn {
                background: #1a1a28;
                border: 1px solid #2a2a3a;
                border-radius: 10px;
                color: #6b6b8a;
                font-size: 16px;
            }
            #toggleBtn:hover {
                border: 1px solid #7C6EE0;
                color: #ffffff;
            }
            #link {
                font-size: 12px;
                color: #7C6EE0;
            }
            #hotkeyCard {
                background: #1a1a28;
                border: 1px solid #2a2a3a;
                border-radius: 10px;
            }
            #hotkeyTitle {
                font-size: 13px;
                font-weight: 600;
                color: #ffffff;
                font-family: -apple-system, 'Segoe UI', sans-serif;
            }
            #hotkeyDesc {
                font-size: 11px;
                color: #6b6b8a;
                font-family: -apple-system, 'Segoe UI', sans-serif;
            }
            #saveBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6B5ECD, stop:1 #8B7FED);
                border: none;
                border-radius: 10px;
                color: #ffffff;
                font-size: 14px;
                font-weight: 600;
                font-family: -apple-system, 'Segoe UI', sans-serif;
            }
            #saveBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7B6EDD, stop:1 #9B8FFD);
            }
            #saveBtn:pressed {
                background: #5B4EBD;
            }
            #version {
                font-size: 10px;
                color: #3a3a5a;
                font-family: -apple-system, 'Segoe UI', sans-serif;
            }
        """)

    def save(self):
        self.config.anthropic_key = self.key_input.text()
        self.save_btn.setText("✓ Saved!")
        self.save_btn.setStyleSheet(self.save_btn.styleSheet().replace("#6B5ECD", "#2ECC71").replace("#8B7FED", "#3EDD81"))
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1500, lambda: (
            self.save_btn.setText("Save Settings"),
            self.apply_styles()
        ))

    # Make window draggable (since frameless)
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
