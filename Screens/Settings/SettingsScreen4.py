from PyQt5.QtCore import Qt,pyqtSignal,QTime
from PyQt5.QtWidgets import (
    QVBoxLayout, QWidget, QLabel, QLineEdit, QDialog, QHBoxLayout, QApplication,
    QSpacerItem, QSizePolicy, QButtonGroup,QTimeEdit,QPushButton,QComboBox,QMenu,QRadioButton,QWidgetAction
)
from PyQt5.QtGui import QPainter, QImage, QFontDatabase, QFont, QIcon, QDoubleValidator
from Constants.Buttons.radio_button import RadioButtonWithAnimation
from Constants.Buttons.save_green_button import SaveGreenButton
from Constants.Buttons.two_state_toggle_button import AnimatedToggle
from Constants.keypad_textbox import NumericKeypad
from Constants.MainNotification import Notification
from Controls.gpio_control import GPIOController
from Controls.uart_control import UARTcontrol
import resources_rc
import json
import os 


class SettingsScreen4(QWidget):
    notify_title_bar = pyqtSignal(str, str, str, str, str)

    def __init__(self, text: str, parent=None, uart_thread=None):
       
        super().__init__(parent=parent)
        self.setWindowState(Qt.WindowFullScreen)
        self.uart_thread = uart_thread
        self.uart = UARTcontrol()
        self.notification = Notification(self)
        self.toggle_state_file = "toggle_state.json"
        self.toggle_state = self.load_toggle_state()
    

        self.in_out_state = "IN" 
        self.salt_comp_value = 0
        self.sensor_comp_value = 0
        self.intfr_mode_value = None

        self.salt_comp_read=0
        self.sensor_comp_read=0


        layout = QVBoxLayout()
        font_id = QFontDatabase.addApplicationFont(":/Constants/Fonts/JosefinSans-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else 'Arial'
        self.heading_label = QLabel("DEVICE SETTINGS", self)
        font = QFont(font_family, 13, QFont.Bold)
        self.heading_label.setFont(font)
        self.heading_label.setStyleSheet("color: black; font-weight: bold;")
        self.heading_label.setGeometry(110, -10, 200, 100)
        layout.addWidget(self.heading_label)
        spacer = QSpacerItem(100, 100, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addSpacerItem(spacer)
        image_path = ":/Constants/images/settingsbg.png"
 

        self.original_image = QImage(image_path)
        if self.original_image.isNull():
            pass
        else:
            self.background_image = self.original_image.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
  

        self._button(
            name="", icon_path=":/Constants/icons/setprev.png",
            action=lambda *args: self.parent().setCurrentIndex(4),
            x=10, y=10, width=90, height=60,
            visible=True, bg_color="rgba(60, 179, 113, 0.0)"
        )
        self.createContainer(x=90, y=110, width=850, height=160, bg_color='#180A0A4E', border_radius=15, border_color='#180A0A6F', heading_text='TIME SHIFT CONFIG')
        self.createContainer(x=90, y=290, width=850, height=160, bg_color='#180A0A4E', border_radius=15, border_color='#180A0A6F', heading_text='PARAMETER CONFIG')
        self.createContainer1(x=90, y=470, width=850, height=90, bg_color='#180A0A4E', border_radius=15, border_color='#180A0A6F', heading_text='MOUSE CURSOR',add_toggle=True)
        self.updateToggleLabelStyles(self.toggle_state)
        self.toggle_button.setChecked(self.toggle_state)
        self.MR_ST = self.NumberInput(x=210, y=170, label_text="MR START",lspace=80,enable_keypad=True)
        self.MR_ND = self.NumberInput(x=420, y=170, label_text="MR END ",lspace=60,enable_keypad=True)
        self.EV_ST = self.NumberInput(x=610, y=170, label_text="EV START",lspace=80,enable_keypad=True)
        self.EV_ND = self.NumberInput(x=810, y=170, label_text="EV END ",lspace=60,enable_keypad=True)
        self.save_button(name=" Select Parameter", icon_path=":/Constants/icons/save.png", action=lambda *args: self.parent().setCurrentIndex(6),x=110,y=355, width=800, height=50,visible=True, bg_color="rgba(3, 131, 3, 1)")
 
       




        
        
        
    def save_button(self, name, icon_path,bg_color, action, x=60, y=457, width=170, height=60, visible=True,):
        self.custom_button = SaveGreenButton(name=name, action=action, icon_path=icon_path,bg_color=bg_color,  # Custom background color
    text_color="white" )
        self.custom_button.setParent(self)

        if icon_path:
            icon = QIcon(icon_path)
            self.custom_button.setIcon(icon)

        self.custom_button.setGeometry(x, y, width, height)

        # Explicitly raise the button to make sure it is on top of other widgets
        self.custom_button.raise_()
        self.custom_button.setFocusPolicy(Qt.StrongFocus)
        self.custom_button.setVisible(visible)
 # Import to check for file existence

    def NumberInput(self, x, y, label_text, lspace, enable_keypad=True, initial_value="0:00 AM"):
        """Create a labeled number input field with an optional keypad."""
        # Read initial value from JSON file if it exists
        json_file_name = f"{label_text.lower().replace(' ', '_')}_time.json"
        if os.path.exists(json_file_name):
            try:
                with open(json_file_name, "r") as json_file:
                    time_data = json.load(json_file)
                    initial_value = time_data.get(label_text.lower(), initial_value)
            except (json.JSONDecodeError, KeyError):
                pass  # Fall back to the default value if the file is corrupted or the key is missing

        # Create label
        label = QLabel(label_text, self)
        label.setGeometry(x - lspace, y + 20, 100, 20)
        label.setStyleSheet("color: black; font-size: 14px; background-color: transparent;")
        
        # Create input field
        number_input = QLineEdit(self)
        number_input.setPlaceholderText("0:00 AM")
        number_input.setValidator(QDoubleValidator(0.0, 999999.0, 2))
        number_input.setReadOnly(True)
        number_input.setGeometry(x, y, 100, 60)
        number_input.setAlignment(Qt.AlignCenter)
        
        # Set initial value from JSON or default
        number_input.setText(initial_value)

        # Attach the keypad dialog if enabled
        if enable_keypad:
            number_input.mousePressEvent = lambda event: self.show_time_filter_dialog(label_text, number_input)
        else:
            number_input.mousePressEvent = lambda event: None

        return number_input

        
        
        

    def createContainer(self, x, y, width, height, bg_color, border_radius, border_color, heading_text):
        container = QWidget(self)
        container.setGeometry(x, y, width, height)
        container.setStyleSheet(f"""
        background-color: {bg_color};
        border-radius: {border_radius}px;
        border: 2px solid {border_color};
        """)

        heading = QLabel(heading_text, container)
        heading.move(10, 10)
        heading.setStyleSheet("color: black; font-weight: bold; font-size: 16px; border: none; background-color: transparent;")

       

        

        container.show()
        
    def createContainer1(self, x, y, width, height, bg_color, border_radius, border_color, heading_text, add_toggle=True):
        container = QWidget(self)
        container.setGeometry(x, y, width, height)
        container.setStyleSheet(f"""
        background-color: {bg_color};
        border-radius: {border_radius}px;
        border: 2px solid {border_color};
        """)

        heading = QLabel(heading_text, container)
        heading.move(10, 35)
        heading.setStyleSheet("color: black; font-weight: bold; font-size: 16px; border: none; background-color: transparent;")

        if add_toggle:
            toggle_layout = QHBoxLayout()

            self.label_off = QLabel("OFF")
            self.label_on = QLabel("ON")

            # Initial styles for the labels
            self.label_on.setStyleSheet("color: grey; border: none; background: transparent; font-weight: bold;")
            self.label_off.setStyleSheet("color: black; border: none; background: transparent; font-weight: bold;")

            toggle_layout.addWidget(self.label_off)
            self.toggle_button = AnimatedToggle()
            self.toggle_button.setFixedSize(60, 40)
            toggle_layout.addWidget(self.toggle_button)
            toggle_layout.addWidget(self.label_on)

            toggle_layout.addItem(QSpacerItem(40, 35, QSizePolicy.Expanding, QSizePolicy.Minimum))

            toggle_widget = QWidget(container)  # Make toggle_widget a child of container
            toggle_widget.setLayout(toggle_layout)
            toggle_widget.setStyleSheet("background-color: transparent; border: none;")

            toggle_layout.setAlignment(Qt.AlignBottom)
            toggle_widget.move(700, 5)

            # Connect the toggle state to a function to handle style changes
            self.toggle_button.stateChanged.connect(self.updateToggleLabelStyles)

        container.show()

    def save_toggle_state(self, state):
        """Save the toggle state to a JSON file."""
        try:
            with open(self.toggle_state_file, "w") as file:
                json.dump({"toggle_state": state}, file)
        except Exception as e:
            print(f"Error saving toggle state: {e}")

    def load_toggle_state(self):
        """Load the toggle state from a JSON file."""
        try:
            if os.path.exists(self.toggle_state_file):
                with open(self.toggle_state_file, "r") as file:
                    data = json.load(file)
                    return data.get("toggle_state", False)
        except Exception as e:
            print(f"Error loading toggle state: {e}")
        return False  # Default to OFF if loading fails

    def updateToggleLabelStyles(self, state):
        """
        Updates the styles of the ON and OFF labels based on the toggle state.
        """
        if state:  # Toggle is ON
            self.label_on.setStyleSheet("color: black; border: none; background: transparent; font-weight: bold;")
            self.label_off.setStyleSheet("color: grey; border: none; background: transparent; font-weight: bold;")
            self.enable_cursor()
        else:  # Toggle is OFF
            self.label_on.setStyleSheet("color: grey; border: none; background: transparent; font-weight: bold;")
            self.label_off.setStyleSheet("color: black; border: none; background: transparent; font-weight: bold;")
            self.disable_cursor()

        # Save the updated state to memory
        self.save_toggle_state(state)

    def enable_cursor(self):
        """Enable the mouse cursor globally."""
        QApplication.restoreOverrideCursor()
        print("Mouse cursor enabled.")
        self.notification.show_notification("Cursor turned ON, Please Restart System", "success", 4000)

    def disable_cursor(self):
        """Disable the mouse cursor globally."""
        QApplication.setOverrideCursor(Qt.BlankCursor)
        print("Mouse cursor disabled.")
        self.notification.show_notification("Cursor turned OFF, Please Restart System", "error", 4000)


    

        
    def _button(self, name, icon_path, bg_color, action, x=60, y=457, width=170, height=60, visible=True, H=50, W=50):
        from PyQt5.QtGui import QIcon
        from Constants.Buttons.save_green_button import SaveGreenButton
        self.custom_button = SaveGreenButton(name=name, action=action, icon_path=icon_path, bg_color=bg_color,
                                            text_color="white", H=H, W=W)
        self.custom_button.setParent(self)

        if icon_path:
            icon = QIcon(icon_path)
            self.custom_button.setIcon(icon)

        self.custom_button.setGeometry(x, y, width, height)
        self.custom_button.raise_()  # Ensure button is on top
        self.custom_button.setVisible(visible)

        # Add label below the button
        self.button_label = QLabel(name, self)
        self.button_label.setGeometry(x, y + height + 0, width, 30)  # Positioning below the button
        self.button_label.setAlignment(Qt.AlignCenter)
        self.button_label.setStyleSheet("font-size: 14px;  color: white;")
        self.button_label.raise_()  # Ensure the label is on top
        self.button_label.show() 

        
    def set_button_pressed(self, *args):
        self.savebutton = True
        
        try:
        # Atsaltt to convert salt_comp_value to an integer
            salt_comp_value = int(float(self.salt_comp_value))
        # Convert to hexadecimal format
            salt_comp_value_hex = hex(salt_comp_value)[2:].zfill(2).upper()
        except ValueError:
        # If conversion fails, skip sending this value
            salt_comp_value_hex = None

        try:
        # Atsaltt to convert sensor_comp_value to an integer
            sensor_comp_value = int(float(self.sensor_comp_value))
        # Convert to hexadecimal format
            sensor_comp_value_hex = hex(sensor_comp_value)[2:].zfill(2).upper()
        except ValueError:
        # If conversion fails, skip sending this value
            sensor_comp_value_hex = None

    # Send the formatted string only if both values were successfully converted
        if salt_comp_value_hex is not None and sensor_comp_value_hex is not None:
            formatted_string = f"30 {salt_comp_value_hex} {sensor_comp_value_hex}"
            self.uart.send_uart_hex(formatted_string)
                
    def show_time_filter_dialog(self, field_label, target_field):
        """Show a dialog to input time for the specified field and update the field value."""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Set Time for {field_label}")
        dialog.setFixedSize(400, 250)

        layout = QVBoxLayout(dialog)

        label = QLabel(f"Set {field_label} Time", dialog)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Extract the current value from the target field
        current_time_text = target_field.text()
        try:
            current_time = QTime.fromString(current_time_text, "hh:mm AP")
            if not current_time.isValid():
                raise ValueError
        except ValueError:
            current_time = QTime(0, 0)  # Default to 12:00 AM if the value is invalid

        # Time edit widget
        time_edit = QTimeEdit(dialog)
        time_edit.setDisplayFormat("hh:mm AP")  # 12-hour format
        time_edit.setTime(current_time)  # Set initial time to current value
        time_edit.setStyleSheet("""
        QTimeEdit {
            height: 100px;
            font-size: 25px;
        }

        QTimeEdit::up-button, QTimeEdit::down-button {
            width: 40px;  /* Increase width of the up and down buttons */
            height: 40px;  /* Adjust height for better appearance */
        }

        QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {
            background-color: #016B0AFF;  /* Hover effect */
        }

        QTimeEdit::up-button:pressed, QTimeEdit::down-button:pressed {
            background-color: #c0c0c0;  /* Pressed effect */
        }
    """)
        layout.addWidget(time_edit)

        # Action buttons
        button_layout = QHBoxLayout()
        apply_button = QPushButton("Apply", dialog)
        close_button = QPushButton("Close", dialog)

        # Set the desired height for the buttons
        button_height = 40  # Adjust this value as needed
        apply_button.setFixedHeight(button_height)
        close_button.setFixedHeight(button_height)

        button_layout.addWidget(apply_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        # Function to save time to JSON and update the field
        def save_time_to_field_and_json(field, selected_time):
           
            time_string = selected_time.toString("hh:mm AP")
            target_field.setText(time_string)  # Update the QLineEdit field

            # Create a dynamic file name based on the field label
            json_file_name = f"{field_label.lower().replace(' ', '_')}_time.json"

            # Save time to JSON file
            time_data = {field.lower(): time_string}
            with open(json_file_name, "w") as json_file:
                json.dump(time_data, json_file, indent=4)

        # Connect buttons
        apply_button.clicked.connect(lambda: save_time_to_field_and_json(field_label, time_edit.time()))
        apply_button.clicked.connect(dialog.accept)
        apply_button.clicked.connect(lambda:self.notification.show_notification("Updated Successfully", "success", 3000))
        
        close_button.clicked.connect(dialog.reject)

        dialog.exec_()
        
            

        
        
        


     

