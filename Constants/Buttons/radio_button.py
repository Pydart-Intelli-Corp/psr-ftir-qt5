from PyQt5.QtWidgets import QRadioButton

class RadioButtonWithAnimation(QRadioButton):
    def __init__(self, text, parent=None):
        from PyQt5.QtWidgets import  QVBoxLayout, QLabel
        from PyQt5.QtCore import  QPropertyAnimation
        from PyQt5.QtGui import QColor

        from Controls.gpio_control import GPIOController
        super().__init__(parent)
        self._color = QColor("lightgrey")  # Default color for unchecked state
        self.setStyleSheet(self._unchecked_style())
        self.controller = GPIOController()

        # Animation setup
        self.animation = QPropertyAnimation(self, b"color")
        self.animation.setDuration(300)

        # Connect the toggle event to trigger the animation
        self.toggled.connect(self.start_animation)

        # Label setup
        self.setText("")  # Remove default button text
        self.label = QLabel(text)  # Only text is passed here
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addStretch()  # Push the indicator down, so label stays on top
        layout.setContentsMargins(0, 0, 0, 0)

    # Property getter and setter for 'color'
    def getColor(self):
        return self._color

    def setColor(self, color):
        
        self._color = color
        self.update_style()  # Update style each time color changes
    from PyQt5.QtCore import pyqtProperty
    from PyQt5.QtGui import QColor
    color = pyqtProperty(QColor, fget=getColor, fset=setColor)

    def start_animation(self, checked):
        from PyQt5.QtGui import QColor
        self.controller.start_wave(frequency=650, duration=0.03)
        
        self.animation.stop()
        # Set the specified color when checked
        start_color = QColor("lightgrey") if not checked else QColor(4, 129, 155, 229)
        end_color = QColor(4, 129, 155, 229) if checked else QColor("lightgrey")
        self.animation.setStartValue(start_color)
        self.animation.setEndValue(end_color)
        self.animation.start()

    def update_style(self):
        self.setStyleSheet(self._checked_style() if self.isChecked() else self._unchecked_style())

    def _checked_style(self):
        return f"""
            QRadioButton::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 10px;
                background-color: {self._color.name()};
                border: 2px solid #005cb2;
            }}
        """

    def _unchecked_style(self):
        return f"""
            QRadioButton::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 10px;
                background-color: {self._color.name()};
                border: 2px solid grey;
            }}
        """
