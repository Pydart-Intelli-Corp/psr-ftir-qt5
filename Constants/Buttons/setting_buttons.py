
from PyQt5.QtWidgets import  QPushButton

from Controls.gpio_control import GPIOController


# Custom Button Class
class SettingsButton(QPushButton):
    def __init__(self, name, action, icon_path, parent=None):
        from PyQt5.QtGui import QIcon, QFontDatabase, QFont
        from PyQt5.QtCore import QSize
        from functools import partial
        super().__init__(parent)
        self.controller = GPIOController()


        # Load custom font
        font_path = ":/Constants/Fonts/JosefinSans-Regular.ttf"
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
           pass
        else:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            custom_font = QFont(font_family, 13)
            self.setFont(custom_font)  # Apply the custom font to the button

        # Set button text, icon, and style
        self.setText(name)
        self.setIcon(QIcon(icon_path))  # Dynamically set the icon
        self.setIconSize(QSize(40, 40))
        self.setStyleSheet("""
          QPushButton {
    background-color: rgba(0, 134, 179, 0.7); 
    border-radius: 10px;
    color: white;  /* Set the text color to white */
    border: 2px solid rgba(14, 14, 14, 0.5);  /* Add a white border */
    }
    QPushButton:hover {
    background-color: rgba(0, 134, 179, 0.9); 
    }
    QPushButton:pressed {
    background-color: rgba(20, 168, 55, 0.4);
    }


        """)

        # Connect the button click to the passed action with the button name as an argument
        self.clicked.connect(partial(action, name))
        self.clicked.connect(lambda: self.controller.start_wave(frequency=650, duration=0.03))