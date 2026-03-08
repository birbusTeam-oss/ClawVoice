from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class SettingsWindow(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowTitle("ClawVoice")
        self.setFixedSize(480, 500)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._drag_pos = None
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        self.container = QFrame(self)
        self.container.setObjectName("container")
        self.container.setGeometry(0, 0, 480, 500)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(0)

        # --- Header ---
        header = QHBoxLayout()
        header.setSpacing(14)

        mic_icon = QLabel("🎙️")
        mic_icon.setObjectName("logo")
        header.addWidget(mic_icon)

        title_col = QVBoxLayout()
        title_col.setSpacing(3)
        title = QLabel("ClawVoice")
        title.setObjectName("title")
        subtitle = QLabel("Open source voice dictation")
        subtitle.setObjectName("subtitle")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        header.addLayout(title_col)
        header.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedSize(32, 32)
        close_btn.clicked.connect(self.hide)
        header.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(header)

        layout.addSpacing(24)

        # --- Divider ---
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setObjectName("divider")
        layout.addWidget(div)

        layout.addSpacing(24)

        # --- API Key label ---
        key_label = QLabel("ANTHROPIC API KEY")
        key_label.setObjectName("sectionLabel")
        layout.addWidget(key_label)

        layout.addSpacing(10)

        # --- Key input + toggle ---
        key_row = QHBoxLayout()
        key_row.setSpacing(10)

        self.key_input = QLineEdit()
        self.key_input.setObjectName("keyInput")
        self.key_input.setPlaceholderText("sk-ant-api03-...")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setText(self.config.anthropic_key)
        self.key_input.setFixedHeight(50)
        key_row.addWidget(self.key_input)

        toggle_btn = QPushButton("👁")
        toggle_btn.setObjectName("toggleBtn")
        toggle_btn.setFixedSize(50, 50)
        toggle_btn.setCheckable(True)
        toggle_btn.toggled.connect(lambda c: self.key_input.setEchoMode(
            QLineEdit.EchoMode.Normal if c else QLineEdit.EchoMode.Password
        ))
        key_row.addWidget(toggle_btn)
        layout.addLayout(key_row)

        layout.addSpacing(10)

        # --- Helper link ---
        link = QLabel('<a href="https://console.anthropic.com" style="color:#7C6EE0; text-decoration:none;">Get your free API key at console.anthropic.com →</a>')
        link.setObjectName("link")
        link.setOpenExternalLinks(True)
        layout.addWidget(link)

        layout.addSpacing(20)

        # --- Hotkey card ---
        hotkey_card = QFrame()
        hotkey_card.setObjectName("hotkeyCard")
        hk_layout = QHBoxLayout(hotkey_card)
        hk_layout.setContentsMargins(20, 16, 20, 16)
        hk_layout.setSpacing(16)

        kb_icon = QLabel("⌨️")
        kb_icon.setObjectName("hotkeyIcon")
        kb_icon.setFixedWidth(28)
        hk_layout.addWidget(kb_icon)

        hk_text = QVBoxLayout()
        hk_text.setSpacing(4)
        h1 = QLabel("Hold Right Alt to dictate")
        h1.setObjectName("hotkeyTitle")
        h2 = QLabel("Release to transcribe and type into any app")
        h2.setObjectName("hotkeyDesc")
        hk_text.addWidget(h1)
        hk_text.addWidget(h2)
        hk_layout.addLayout(hk_text)
        layout.addWidget(hotkey_card)

        layout.addStretch()

        # --- Save button ---
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setObjectName("saveBtn")
        self.save_btn.setFixedHeight(50)
        self.save_btn.clicked.connect(self.save)
        layout.addWidget(self.save_btn)

        layout.addSpacing(12)

        # --- Version ---
        version = QLabel("v0.2 — Built by the Birbus Team")
        version.setObjectName("version")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)

    def apply_styles(self):
        self.setStyleSheet("""
            #container {
                background-color: #111118;
                border-radius: 18px;
                border: 1px solid #2a2a3a;
            }
            #logo { font-size: 36px; }
            #title {
                font-size: 22px;
                font-weight: 700;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
            }
            #subtitle {
                font-size: 13px;
                color: #6b6b8a;
                font-family: 'Segoe UI', sans-serif;
            }
            #closeBtn {
                background: transparent;
                border: none;
                color: #6b6b8a;
                font-size: 15px;
                border-radius: 16px;
            }
            #closeBtn:hover { background: #2a2a3a; color: #ffffff; }
            #divider { background: #2a2a3a; max-height: 1px; border: none; }
            #sectionLabel {
                font-size: 11px;
                font-weight: 700;
                color: #6b6b8a;
                letter-spacing: 2px;
                font-family: 'Segoe UI', sans-serif;
            }
            #keyInput {
                background: #1a1a28;
                border: 1px solid #2a2a3a;
                border-radius: 12px;
                color: #ffffff;
                font-size: 14px;
                padding: 0 16px;
                font-family: 'Consolas', monospace;
            }
            #keyInput:focus { border: 1px solid #7C6EE0; }
            #keyInput::placeholder { color: #3a3a5a; }
            #toggleBtn {
                background: #1a1a28;
                border: 1px solid #2a2a3a;
                border-radius: 12px;
                color: #6b6b8a;
                font-size: 18px;
            }
            #toggleBtn:hover { border: 1px solid #7C6EE0; color: #ffffff; }
            #link {
                font-size: 12px;
                font-family: 'Segoe UI', sans-serif;
            }
            #hotkeyCard {
                background: #1a1a28;
                border: 1px solid #2a2a3a;
                border-radius: 12px;
            }
            #hotkeyIcon { font-size: 20px; }
            #hotkeyTitle {
                font-size: 14px;
                font-weight: 600;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
            }
            #hotkeyDesc {
                font-size: 12px;
                color: #6b6b8a;
                font-family: 'Segoe UI', sans-serif;
            }
            #saveBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6B5ECD, stop:1 #8B7FED);
                border: none;
                border-radius: 12px;
                color: #ffffff;
                font-size: 15px;
                font-weight: 600;
                font-family: 'Segoe UI', sans-serif;
            }
            #saveBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7B6EDD, stop:1 #9B8FFD);
            }
            #saveBtn:pressed { background: #5B4EBD; }
            #version {
                font-size: 11px;
                color: #3a3a5a;
                font-family: 'Segoe UI', sans-serif;
            }
        """)

    def save(self):
        self.config.anthropic_key = self.key_input.text()
        self.save_btn.setText("✓ Saved!")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #2ECC71; border: none; border-radius: 12px;
                color: #ffffff; font-size: 15px; font-weight: 600;
            }
        """)
        QTimer.singleShot(1800, lambda: (
            self.save_btn.setText("Save Settings"),
            self.apply_styles()
        ))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
