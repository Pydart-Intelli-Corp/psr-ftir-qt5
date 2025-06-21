from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont, QFontDatabase
from PyQt5.QtWidgets import (QDialog, QPushButton, QLineEdit,
                             QVBoxLayout, QHBoxLayout, QLabel)

from Controls.gpio_control import GPIOController


class NumericKeypad(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Numeric Keypad")
        self.setFixedSize(300, 400)
        self.controller = GPIOController()

        # Remove default window frame
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.result = ""
        self.setStyleSheet("""
            QDialog {
                border: 2px solid #888;  /* Adjust color and width as needed */
                border-radius: 10px;    /* Optional: rounded corners */
                background-color: white;
            }
        """)

        # --- Load Custom Font ---
        font_id = QFontDatabase.addApplicationFont(":/Constants/Fonts/JosefinSans-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Arial"
        custom_font = QFont(font_family)

        # --- Layout Setup ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- Heading ---
        heading = QLabel("Enter ID", self)
        custom_font.setPointSize(20)  # Set font size
        heading.setFont(custom_font)  # Apply custom font
        heading.setStyleSheet("padding: 5px;")
        heading.setAlignment(Qt.AlignLeft)  # Align heading to the left

        # --- Close Button ---
        close_button = QPushButton(self)
        close_icon = QIcon(":/Constants/icons/keypad/close.png")  # Path to your close icon
        close_button.setIcon(close_icon)
        close_button.setIconSize(QSize(30, 30))
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)
        close_button.clicked.connect(self.reject)

        # --- Heading and Close Button Layout ---
        top_heading_layout = QHBoxLayout()
        top_heading_layout.addWidget(heading)
        top_heading_layout.addStretch()  # Add space between the heading and the button
        top_heading_layout.addWidget(close_button)

        # Add the combined layout to the main layout
        main_layout.addLayout(top_heading_layout)

        # --- Display ---
        self.display = QLineEdit(self)
        custom_font.setPointSize(18)  # Smaller font for display
        self.display.setFont(custom_font)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(True)
        self.display.setStyleSheet("padding: 10px;")
        main_layout.addWidget(self.display)

        # --- Buttons (Icons Only) ---
        button_grid = QVBoxLayout()
        button_rows = [
            [":/Constants/icons/keypad/1.png", ":/Constants/icons/keypad/2.png", ":/Constants/icons/keypad/3.png"],
            [":/Constants/icons/keypad/4.png", ":/Constants/icons/keypad/5.png", ":/Constants/icons/keypad/6.png"],
            [":/Constants/icons/keypad/7.png", ":/Constants/icons/keypad/8.png", ":/Constants/icons/keypad/9.png"],
            [":/Constants/icons/keypad/backspace.png", ":/Constants/icons/keypad/0.png", ":/Constants/icons/keypad/start-button.png"]
        ]

        self.icon_mapping = {
            ":/Constants/icons/keypad/1.png": "1",
            ":/Constants/icons/keypad/2.png": "2",
            ":/Constants/icons/keypad/3.png": "3",
            ":/Constants/icons/keypad/4.png": "4",
            ":/Constants/icons/keypad/5.png": "5",
            ":/Constants/icons/keypad/6.png": "6",
            ":/Constants/icons/keypad/7.png": "7",
            ":/Constants/icons/keypad/8.png": "8",
            ":/Constants/icons/keypad/9.png": "9",
            ":/Constants/icons/keypad/backspace.png": "Backspace",
            ":/Constants/icons/keypad/0.png": "0",
            ":/Constants/icons/keypad/start-button.png": "Start"
        }

        for row in button_rows:
            row_layout = QHBoxLayout()
            for icon_path in row:
                button = QPushButton(self)
                button.setIcon(QIcon(QPixmap(icon_path)))

                # Adjust icon size dynamically
                if icon_path == ":/Constants/icons/keypad/start-button.png":
                    button.setIconSize(QSize(50, 50))  # Larger size for "Start" button
                else:
                    button.setIconSize(QSize(32, 32))  # Default size for other buttons

                button.setStyleSheet("""
                    QPushButton {
                        border: 1px solid #ccc;
                        padding: 10px;
                    }
                    QPushButton:hover {
                        background-color: #f0f0f0;
                    }
                """)
                button.clicked.connect(self.handleButtonClick)
                button.setProperty("icon_path", icon_path)
                row_layout.addWidget(button)
            button_grid.addLayout(row_layout)

        main_layout.addLayout(button_grid)

    def handleButtonClick(self):
        self.controller.start_wave(frequency=650, duration=0.03)
        
        sender = self.sender()  # Get the button that triggered the click event
        icon_path = sender.property("icon_path")  # Retrieve the stored icon path

        # Get the corresponding value from the icon mapping
        value = self.icon_mapping.get(icon_path)

        if value == "Start":  # Handle the "Start" button click
            if self.validateInput(self.result):  # Validate the input
                self.accept() 
                # Close the dialog with an accepted state
            else:
                pass

        elif value == "Backspace":  # Handle the "Backspace" button click
            self.result = self.result[:-1]  # Remove the last character from the result
            self.display.setText(self.result)  # Update the display to show the new result

        elif value is not None:  # Handle numeric button clicks (or zero)
            self.result += value  # Append the clicked value to the result
            self.display.setText(self.result)  # Update the display to show the new result

    def validateInput(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False



    def getValue(self):
        return self.result