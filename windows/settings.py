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
        self._raw_key = config.anthropic_key or ""
        self._editing = False
        self._required = False  # Set True on first run — blocks closing

        self.setWindowTitle("ClawVoice Settings")
        self.setFixedSize(500, 460)
        self.setWindowFlags(Qt.WindowType.Window)
        self.setup_ui()
        self.apply_styles()
        self._refresh_key_display()

    def set_required(self, required: bool):
        """When True, window cannot be closed until a valid API key is saved."""
        self._required = required
        if required:
            # Remove close button so it can't be dismissed
            self.setWindowFlags(
                Qt.WindowType.Window |
                Qt.WindowType.CustomizeWindowHint |
                Qt.WindowType.WindowTitleHint
            )
            self.show()
            # Show edit fields immediately — user must enter a key
            self._editing = True
            self.edit_row.setVisible(True)
            self.save_btn.setVisible(True)
            self.edit_btn.setVisible(False)
            self.setup_banner.setVisible(True)

    def closeEvent(self, event):
        if self._required and not self.config.anthropic_key:
            # Block close until key is provided
            event.ignore()
        else:
            self._required = False
            self.setWindowFlags(Qt.WindowType.Window)
            event.accept()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(0)

        # First-run banner (hidden unless required)
        self.setup_banner = QFrame()
        self.setup_banner.setObjectName("setupBanner")
        banner_layout = QHBoxLayout(self.setup_banner)
        banner_layout.setContentsMargins(16, 12, 16, 12)
        banner_icon = QLabel("👋")
        banner_icon.setStyleSheet("font-size: 20px;")
        banner_layout.addWidget(banner_icon)
        banner_text = QLabel("Welcome! Paste your Anthropic API key below to get started.")
        banner_text.setObjectName("bannerText")
        banner_text.setWordWrap(True)
        banner_layout.addWidget(banner_text)
        self.setup_banner.setVisible(False)
        layout.addWidget(self.setup_banner)
        layout.addSpacing(16)

        # Header
        header = QHBoxLayout()
        icon = QLabel("🎙️")
        icon.setObjectName("logo")
        header.addWidget(icon)
        titles = QVBoxLayout()
        titles.setSpacing(3)
        t = QLabel("ClawVoice")
        t.setObjectName("title")
        s = QLabel("Voice dictation powered by Claude AI")
        s.setObjectName("subtitle")
        titles.addWidget(t)
        titles.addWidget(s)
        header.addLayout(titles)
        header.addStretch()
        layout.addLayout(header)
        layout.addSpacing(24)

        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setObjectName("divider")
        layout.addWidget(div)
        layout.addSpacing(24)

        key_label = QLabel("ANTHROPIC API KEY")
        key_label.setObjectName("sectionLabel")
        layout.addWidget(key_label)
        layout.addSpacing(8)

        # Masked display row
        display_row = QHBoxLayout()
        display_row.setSpacing(10)
        self.key_display = QLabel("No key saved")
        self.key_display.setObjectName("keyDisplay")
        self.key_display.setFixedHeight(50)
        display_row.addWidget(self.key_display)

        self.edit_btn = QPushButton("Change")
        self.edit_btn.setObjectName("editBtn")
        self.edit_btn.setFixedSize(80, 50)
        self.edit_btn.clicked.connect(self._toggle_edit)
        display_row.addWidget(self.edit_btn)
        layout.addLayout(display_row)

        # Edit row
        self.edit_row = QFrame()
        edit_layout = QHBoxLayout(self.edit_row)
        edit_layout.setContentsMargins(0, 0, 0, 0)
        edit_layout.setSpacing(10)
        self.key_input = QLineEdit()
        self.key_input.setObjectName("keyInput")
        self.key_input.setPlaceholderText("sk-ant-api03-...")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setFixedHeight(50)
        self.key_input.returnPressed.connect(self.save)
        edit_layout.addWidget(self.key_input)
        show_btn = QPushButton("👁")
        show_btn.setObjectName("toggleBtn")
        show_btn.setFixedSize(50, 50)
        show_btn.setCheckable(True)
        show_btn.toggled.connect(lambda c: self.key_input.setEchoMode(
            QLineEdit.EchoMode.Normal if c else QLineEdit.EchoMode.Password
        ))
        edit_layout.addWidget(show_btn)
        self.edit_row.setVisible(False)
        layout.addWidget(self.edit_row)

        # Validation message
        self.validation_label = QLabel("")
        self.validation_label.setObjectName("validationLabel")
        self.validation_label.setVisible(False)
        layout.addWidget(self.validation_label)

        layout.addSpacing(8)
        link = QLabel('<a href="https://console.anthropic.com" style="color:#7C6EE0;text-decoration:none;">Get your free API key at console.anthropic.com →</a>')
        link.setObjectName("link")
        link.setOpenExternalLinks(True)
        layout.addWidget(link)
        layout.addSpacing(20)

        # Hotkey card
        card = QFrame()
        card.setObjectName("hotkeyCard")
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(14)
        kb = QLabel("⌨️")
        kb.setObjectName("hotkeyIcon")
        card_layout.addWidget(kb)
        text_col = QVBoxLayout()
        text_col.setSpacing(4)
        h1 = QLabel("Hold Ctrl+Space to dictate")
        h1.setObjectName("hotkeyTitle")
        h2 = QLabel("Release to transcribe and type into any app")
        h2.setObjectName("hotkeyDesc")
        text_col.addWidget(h1)
        text_col.addWidget(h2)
        card_layout.addLayout(text_col)
        layout.addWidget(card)
        layout.addStretch()

        self.save_btn = QPushButton("Save & Start")
        self.save_btn.setObjectName("saveBtn")
        self.save_btn.setFixedHeight(50)
        self.save_btn.clicked.connect(self.save)
        self.save_btn.setVisible(False)
        layout.addWidget(self.save_btn)
        layout.addSpacing(12)

        version = QLabel("v0.2 — Built by the Birbus Team")
        version.setObjectName("version")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)

    def _mask_key(self, key: str) -> str:
        if not key:
            return "No key saved"
        if len(key) <= 4:
            return "••••"
        return "sk-ant-••••••••••••" + key[-4:]

    def _refresh_key_display(self):
        self._raw_key = self.config.anthropic_key or ""
        self.key_display.setText(self._mask_key(self._raw_key))
        self.key_display.setStyleSheet(
            "color: #2ECC71;" if self._raw_key else "color: #E05555;"
        )

    def _toggle_edit(self):
        self._editing = not self._editing
        self.edit_row.setVisible(self._editing)
        self.save_btn.setVisible(self._editing)
        self.validation_label.setVisible(False)
        self.edit_btn.setText("Cancel" if self._editing else "Change")
        if self._editing:
            self.key_input.clear()
            self.key_input.setFocus()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget { background: #111118; }
            #setupBanner { background: #1a2035; border: 1px solid #7C6EE0; border-radius: 10px; }
            #bannerText { font-size: 13px; color: #c0b8f0; font-family: 'Segoe UI', sans-serif; }
            #logo { font-size: 36px; }
            #title { font-size: 22px; font-weight: 700; color: #ffffff; font-family: 'Segoe UI', sans-serif; }
            #subtitle { font-size: 13px; color: #6b6b8a; font-family: 'Segoe UI', sans-serif; }
            #divider { background: #2a2a3a; max-height: 1px; border: none; }
            #sectionLabel { font-size: 11px; font-weight: 700; color: #6b6b8a; letter-spacing: 2px; font-family: 'Segoe UI', sans-serif; }
            #keyDisplay { background: #1a1a28; border: 1px solid #2a2a3a; border-radius: 12px; color: #ffffff; font-size: 14px; padding: 0 16px; font-family: 'Consolas', monospace; qproperty-alignment: AlignVCenter; }
            #editBtn { background: #1a1a28; border: 1px solid #2a2a3a; border-radius: 12px; color: #7C6EE0; font-size: 13px; font-weight: 600; font-family: 'Segoe UI', sans-serif; }
            #editBtn:hover { border: 1px solid #7C6EE0; color: #ffffff; }
            #keyInput { background: #1a1a28; border: 1px solid #7C6EE0; border-radius: 12px; color: #ffffff; font-size: 14px; padding: 0 16px; font-family: 'Consolas', monospace; }
            #toggleBtn { background: #1a1a28; border: 1px solid #2a2a3a; border-radius: 12px; color: #6b6b8a; font-size: 18px; }
            #toggleBtn:hover { border: 1px solid #7C6EE0; color: #ffffff; }
            #link { font-size: 12px; font-family: 'Segoe UI', sans-serif; }
            #validationLabel { font-size: 12px; color: #E05555; font-family: 'Segoe UI', sans-serif; padding-left: 4px; }
            #hotkeyCard { background: #1a1a28; border: 1px solid #2a2a3a; border-radius: 12px; }
            #hotkeyIcon { font-size: 20px; }
            #hotkeyTitle { font-size: 14px; font-weight: 600; color: #ffffff; font-family: 'Segoe UI', sans-serif; }
            #hotkeyDesc { font-size: 12px; color: #6b6b8a; font-family: 'Segoe UI', sans-serif; }
            #saveBtn { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #6B5ECD,stop:1 #8B7FED); border: none; border-radius: 12px; color: #ffffff; font-size: 15px; font-weight: 600; font-family: 'Segoe UI', sans-serif; }
            #saveBtn:hover { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #7B6EDD,stop:1 #9B8FFD); }
            #version { font-size: 11px; color: #3a3a5a; font-family: 'Segoe UI', sans-serif; }
        """)

    def save(self):
        key = self.key_input.text().strip()
        if not key:
            self.validation_label.setText("⚠️ Please enter your API key")
            self.validation_label.setVisible(True)
            return

        if not self.config.is_valid_key(key):
            self.validation_label.setText("⚠️ Invalid format — key should start with sk-ant-")
            self.validation_label.setVisible(True)
            return

        self.validation_label.setVisible(False)
        self.config.anthropic_key = key
        self._required = False
        self._refresh_key_display()

        if self._editing:
            self._toggle_edit()

        self.save_btn.setText("✓ Saved!")
        self.save_btn.setStyleSheet("QPushButton { background: #2ECC71; border: none; border-radius: 12px; color: white; font-size: 15px; font-weight: 600; }")
        QTimer.singleShot(1200, lambda: (
            self.save_btn.setText("Save & Start"),
            self.apply_styles(),
            self.hide()
        ))
