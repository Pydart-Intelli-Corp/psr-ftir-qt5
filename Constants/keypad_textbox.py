from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (QDialog, QPushButton, QLineEdit, 
                             QMessageBox, QVBoxLayout, QHBoxLayout)

from Controls.gpio_control import GPIOController

class NumericKeypad(QDialog):
    """ 
    An advanced numeric keypad with a modern UI, 
    using only icons for buttons, and a close button in the top right corner. 
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Numeric Keypad")
        self.setFixedSize(300, 400) 

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


        # --- Layout Setup ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)  # Add margins: left, top, right, bottom
        main_layout.setSpacing(10)
        self.controller = GPIOController()

        # --- Display ---
        self.display = QLineEdit(self)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(True)
        self.display.setStyleSheet("font-size: 20px; padding: 10px;")
        main_layout.addWidget(self.display)

        # --- Close Button ---
        close_button = QPushButton(self)
        close_icon = QIcon(":/Constants/icons/keypad/close.png")  # Path to your close icon
        close_button.setIcon(close_icon)
        close_button.setIconSize(QSize(30, 30))  # Adjust icon size as needed
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
        close_button.setParent(self)
        close_button.setGeometry(self.width() - 40, 10, 30, 30)
        # Layout for display and close button
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.display)
        top_layout.addWidget(close_button, alignment=Qt.AlignRight)
        main_layout.addLayout(top_layout)

        # --- Buttons (Icons Only) ---
        button_grid = QVBoxLayout()
        button_rows = [
            [":/Constants/icons/keypad/1.png", ":/Constants/icons/keypad/2.png", ":/Constants/icons/keypad/3.png"],
            [":/Constants/icons/keypad/4.png", ":/Constants/icons/keypad/5.png", ":/Constants/icons/keypad/6.png"],
            [":/Constants/icons/keypad/7.png", ":/Constants/icons/keypad/8.png", ":/Constants/icons/keypad/9.png"],
            [":/Constants/icons/keypad/DOT.png", ":/Constants/icons/keypad/0.png", ":/Constants/icons/keypad/OK.png"]
        ]

        # Create buttons and assign their click handler
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
            ":/Constants/icons/keypad/DOT.png": ".",
            ":/Constants/icons/keypad/0.png": "0",
            ":/Constants/icons/keypad/OK.png": "OK"
        }

        for row in button_rows:
            row_layout = QHBoxLayout()
            for icon_path in row:
                button = QPushButton(self)
                button.setIcon(QIcon(QPixmap(icon_path))) 
                button.setIconSize(QSize(32, 32))  # Adjust icon size as needed
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
                # Store the icon path for later retrieval in handleButtonClick
                button.setProperty("icon_path", icon_path)
                row_layout.addWidget(button)
            button_grid.addLayout(row_layout)

        main_layout.addLayout(button_grid)

    def handleButtonClick(self):
        self.controller.start_wave(frequency=650, duration=0.03)
        
        sender = self.sender()
        icon_path = sender.property("icon_path")  # Retrieve the stored icon path

        # Get the value from the mapping
        value = self.icon_mapping.get(icon_path)

        if value == "OK":
            if self.validateInput(self.result):
                self.accept()
            else:
                self.showError("Invalid input. Please enter a valid number.")
        elif value is not None:  # Avoid appending None values
            # Check if appending the value will exceed 100
            if value == ".":
                if "." in self.result:  # Avoid multiple dots
                    return
            else:
                new_result = self.result + value
                try:
                    # Check if the new result as a float is greater than 100
                    if float(new_result) > 100:
                        return
                except ValueError:
                    pass

            self.result += value  # Append the value to the result
            self.display.setText(self.result)  # Update the display


    def validateInput(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def showError(self, message):
        error_dialog = QMessageBox(self)
        error_dialog.setWindowTitle("Input Error")
        error_dialog.setText(message)
        error_dialog.setIcon(QMessageBox.Warning)
        error_dialog.exec_()

    def getValue(self):
        return self.result
