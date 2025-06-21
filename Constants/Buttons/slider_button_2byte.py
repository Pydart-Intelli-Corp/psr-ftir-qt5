from PyQt5.QtWidgets import QWidget


class SliderButton1(QWidget):
    
    def __init__(self, name, logo_path=None,paddingPx=15, paddingPM=5, padding=10,initial_value=50, parent=None):
        super().__init__(parent)
        self.initUI(name, logo_path,paddingPx, paddingPM, padding,initial_value)

    def initUI(self, name, logo_path,paddingPx, paddingPM, padding,initial_value):
        from PyQt5.QtWidgets import QSlider, QLabel, QHBoxLayout, QPushButton
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFontDatabase, QPixmap

        from Controls.gpio_control import GPIOController
        # Load custom font
        font_id = QFontDatabase.addApplicationFont(":/Constants/Fonts/JosefinSans-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else 'Arial'
        self.controller = GPIOController()
        # Create a horizontal layout for the label, slider, and control buttons
        layout = QHBoxLayout(self)

        # Create an icon label and set the pixmap (image) to it if logo_path is provided
        if logo_path:
            self.icon_label = QLabel(self)
            pixmap = QPixmap(logo_path)  # Load the icon from the given path
            if not pixmap.isNull():  # Check if the image was loaded correctly
                self.icon_label.setPixmap(pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))  # Adjust icon size
            else:
                pass
            layout.addWidget(self.icon_label)

        # Create the label with the provided name
        self.label = QLabel(name)
        self.label.setStyleSheet(f"""
            font-family: '{font_family}';
            font-size: 18px;
            color: black;
        """)
        layout.addWidget(self.label)

        # Add spacing between the label and the slider (padding)
        layout.addSpacing(padding)
        self.slider1 = QSlider(Qt.Horizontal, self)
        self.slider1.setMinimum(1)  # Scaled value for 0.01
        self.slider1.setMaximum(1000)  # Scaled value for 10.0
        self.slider1.setValue(initial_value)

        self.slider1.setTickInterval(10)  # Optional, defines the tick interval
        self.slider1.setTickPosition(QSlider.TicksBelow)  # Show ticks below the slider

        # Customize the appearance of the slider using stylesheets
        self.slider1.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #d3d3d3;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: #0078d7; /* Filled color */
                border-radius: 4px;
            }
            QSlider::add-page:horizontal {
                background: #d3d3d3; /* Unfilled color */
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #FFFFFF;
                border: 2px solid #0078d7;
                width: 16px;
                height: 25px;
                margin: -8px 0; /* Centers the handle on the groove */
                border-radius: 10px;
            }
        """)

        # Add the slider to the layout
        layout.addWidget(self.slider1)
        
        layout.addSpacing(paddingPx)

        # Create the "-" button to decrease the slider value
        self.minus_button = QPushButton("-", self)
        self.minus_button.setStyleSheet("font-size: 30px;")
        self.minus_button.setFixedSize(40, 40)
        layout.addWidget(self.minus_button)
        self.minus_button.clicked.connect(self.decrease_value)
        layout.addSpacing(paddingPM)
        
        # Create a label to display the current value of the slider
        self.value_label = QLabel(f"{self.slider1.value() / 100:.2f}", self)
        self.value_label.setFixedWidth(52)
        self.value_label.setStyleSheet("font-size: 18px;")
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        layout.addSpacing(paddingPM)
        
        self.plus_button = QPushButton("+", self)
        self.plus_button.setStyleSheet("font-size: 30px;")
        self.plus_button.setFixedSize(40, 40)
        layout.addWidget(self.plus_button)
        self.plus_button.clicked.connect(self.increase_value)

        # Set the layout for the widget
        self.setLayout(layout)

        # Connect slider value change to update the value label and save the new value
        self.slider1.valueChanged.connect(self.on_value_changed)

    def on_value_changed(self, value):
        # Update the value label when the slider value changes
        self.value_label.setText(f"{value / 100:.2f}")

    def increase_value(self):
        self.controller.start_wave(frequency=650, duration=0.03)
        
        
        # Increase the slider value by 1 (equivalent to 0.01 in the scaled range)
        current_value = self.slider1.value()
        if current_value < self.slider1.maximum():
            self.slider1.setValue(current_value + 1)

    def decrease_value(self):
        self.controller.start_wave(frequency=650, duration=0.03)
        # Decrease the slider value by 1 (equivalent to 0.01 in the scaled range)
        current_value = self.slider1.value()
        if current_value > self.slider1.minimum():
            self.slider1.setValue(current_value - 1)
