
from PyQt5.QtWidgets import  QPushButton

from Controls.gpio_control import GPIOController

class SaveGreenButton(QPushButton):
    def __init__(self, name, action, icon_path, bg_color="rgba(3, 131, 3, 1)", text_color="white", parent=None,H=20,W=20):
                
      
        from PyQt5.QtGui import QIcon, QFontDatabase, QFont
        from PyQt5.QtCore import QSize
        from functools import partial
        super().__init__(parent)
        
      
        # Load custom font
 # Apply the custom font to the button

        # Set button text, icon, and style
        self.setText(name)
        self.setIcon(QIcon(icon_path))  # Dynamically set the icon
        self.setIconSize(QSize(H, W))
        self.controller = GPIOController()

        # Use dynamic colors in the stylesheet
        self.setStyleSheet(f"""
          QPushButton {{
            background-color: {bg_color}; 
            border-radius: 10px;
            color: {text_color};  /* Set the text color */
            border: 2px solid rgba(14, 14, 14, 0.0);  /* Add a transparent border */
          }}
          QPushButton:hover {{
            background-color: {bg_color.replace("0.9", "1")}; 
          }}
          QPushButton:pressed {{
            background-color: rgba(0, 134, 179, 0.7);
          }}
        """)

        # Connect the button click to the passed action with the button name as an argument
        self.clicked.connect(partial(action, name))
        self.clicked.connect(lambda: self.controller.start_wave(frequency=650, duration=0.03))
        
class SaveButtonND(QPushButton):
    def __init__(self, name, action, icon_path, bg_color="rgba(3, 131, 3, 1)", text_color="white", parent=None,H=20,W=20):
                
      
        from PyQt5.QtGui import QIcon, QFontDatabase, QFont
        from PyQt5.QtCore import QSize
        from functools import partial
        super().__init__(parent)
        
      
        # Load custom font
 # Apply the custom font to the button

        # Set button text, icon, and style
        self.controller = GPIOController()
        self.setIcon(QIcon(icon_path))  # Dynamically set the icon
        self.setIconSize(QSize(H, W))

        # Use dynamic colors in the stylesheet
        self.setStyleSheet(f"""
          QPushButton {{
            background-color: {bg_color}; 
            border-radius: 10px;
            color: {text_color};  /* Set the text color */
            border: 2px solid rgba(14, 14, 14, 0.0);  /* Add a transparent border */
          }}
          QPushButton:hover {{
            background-color: {bg_color.replace("0.9", "1")}; 
          }}
          QPushButton:pressed {{
            background-color: rgba(0, 134, 179, 0.7);
          }}
        """)

        # Connect the button click to the passed action with the button name as an argument
        self.clicked.connect(partial(action, name))
        self.clicked.connect(lambda: self.controller.start_wave(frequency=650, duration=0.03))