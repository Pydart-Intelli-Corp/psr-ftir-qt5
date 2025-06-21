from PyQt5.QtCore import Qt,pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel, QLineEdit, QDialog, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPainter, QImage, QFontDatabase, QFont, QIcon, QDoubleValidator
from Constants.Buttons.save_green_button import SaveGreenButton
from Constants.Buttons.two_state_toggle_button import AnimatedToggle
from Constants.MainNotification import Notification
from Constants.keypad_textbox import NumericKeypad
from Controls.gpio_control import GPIOController
from Controls.uart_control import UARTcontrol
import os
import json
import resources_rc
import time
import threading



class SettingsScreen2(QWidget):
    notify_title_bar = pyqtSignal(str, str, str, str, str)
    CONFIG_FILE = "settings_config.json"
    def __init__(self, text: str, parent=None, uart_thread=None):
        super().__init__(parent=parent)
        self.setWindowState(Qt.WindowFullScreen)
        self.uart_thread = uart_thread
        self.uart = UARTcontrol()
        self.notification = Notification(self)
        self.in_out_state = "IN" 
        self.speed1_value = 0
        self.speed2_value = 0
        self.time1_value = 0
        self.time2_value = 0
        self.out_speed_value = 0
        self.out_time_value = 0
        self.sample_hold_value = 0
        self.intfr_temp_value = 0
        self.sensor_temp_value = 0
        self.sensor_rh_value = 0
        self.intfr_temp_read=0
        self.sensor_temp_read=0
        self.sensor_rh_read=0
        self.clean_count=0
        self.inTest=False
        self.load_values()
        self.command_response=False

        # Create a vertical layout for the settings screen
        layout = QVBoxLayout()
        font_id = QFontDatabase.addApplicationFont(":/Constants/Fonts/JosefinSans-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else 'Arial'
        self.heading_label = QLabel("MILK TEST SETTINGS", self)
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
            action=lambda *args:  self.parent().setCurrentIndex(2),
            x=10, y=10, width=90, height=60,
            visible=True, bg_color="rgba(60, 179, 113, 0.0)"
        )
        
        self._button(
            name="", icon_path=":/Constants/icons/setnext.png",
            action=lambda *args:  self.parent().setCurrentIndex(4),
            x=930, y=10, width=90, height=60,
            visible=True, bg_color="rgba(60, 179, 113, 0.0)"
        )
        self.createContainer(x=90, y=110, width=850, height=250, bg_color='#180A0A4E', border_radius=15, border_color='#180A0A6F', heading_text='PUMP CONFIG',add_toggle=True)
        self.createContainer(x=90, y=390, width=850, height=160, bg_color='#180A0A4E', border_radius=15, border_color='#180A0A6F', heading_text='MEASURED TEMP',add_toggle=False)
        
       
        self.speed1 = self.NumberInput(x=210, y=170, label_text="IN SPEED 1 ", lspace=83, enable_keypad=True, initial_value=self.speed1_value)
        self.time1 = self.NumberInput(x=410, y=170, label_text="IN TIME 1 ", lspace=80, enable_keypad=True, initial_value=self.time1_value)
        self.speed2 = self.NumberInput(x=610, y=170, label_text="IN SPEED 2 ", lspace=83, enable_keypad=True, initial_value=self.speed2_value)
        self.time2 = self.NumberInput(x=810, y=170, label_text="IN TIME 2 ", lspace=80, enable_keypad=True, initial_value=self.time2_value)
        self.out_speed = self.NumberInput(x=210, y=270, label_text="OUT SPEED ", lspace=85, enable_keypad=True, initial_value=self.out_speed_value)
        self.out_time = self.NumberInput(x=410, y=270, label_text="OUT TIME ", lspace=80, enable_keypad=True, initial_value=self.out_time_value)
        self.sample_hold = self.NumberInput(x=610, y=270, label_text="SMPL HOLD", lspace=86, enable_keypad=True, initial_value=self.sample_hold_value)
        self.clean = self.NumberInput(x=810, y=270, label_text="CLN COUNT", lspace=85, enable_keypad=True, initial_value=self.clean_count)
        self.save_button(name=" TEST", icon_path=":/Constants/icons/save.png", action=lambda *args: self.save_button_pressed(),x=815,y=120, width=90, height=40,visible=True, bg_color="rgba(3, 131, 3, 1)")
       
        self.speed1.setText(str(self.speed1_value))
        self.time1.setText(str(self.time1_value))
        self.speed2.setText(str(self.speed2_value))
        self.time2.setText(str(self.time2_value))
        self.out_speed.setText(str(self.out_speed_value))
        self.out_time.setText(str(self.out_time_value))
        self.sample_hold.setText(str(self.sample_hold_value))
        self.clean.setText(str(self.clean_count))


        self.save_button(name=" READ", icon_path=":/Constants/icons/read.png", action=lambda *args: self.Read_temp_button(),x=815,y=400, width=90, height=40,visible=True,bg_color="rgba(32, 123, 130, 1)")
       
        self.intfr_temp_value = self.NumberInput(x=210, y=450, label_text="INTFR TEMP ",lspace=100,enable_keypad=False)
        self.sensor_temp_value = self.NumberInput(x=520, y=450, label_text="SENSOR TEMP ",lspace=120,enable_keypad=False)
        self.sensor_rh_value = self.NumberInput(x=810, y=450, label_text="SENSOR RH",lspace=100,enable_keypad=False)
    
    
    
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
                
 

    def load_values(self):
        # Load values from JSON if available
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r') as file:
                data = json.load(file)
                self.speed1_value = data.get("speed1_value", 0)
                self.speed2_value = data.get("speed2_value", 0)
                self.time1_value = data.get("time1_value", 0)
                self.time2_value = data.get("time2_value", 0)
                self.out_speed_value = data.get("out_speed_value", 0)
                self.out_time_value = data.get("out_time_value", 0)
                self.sample_hold_value = data.get("sample_hold_value", 0)
                self.clean_count = data.get("clean_count", 0)
        else:
            # Default values if JSON file doesn't exist
            self.speed1_value = 0
            self.speed2_value = 0
            self.time1_value = 0
            self.time2_value = 0
            self.out_speed_value = 0
            self.out_time_value = 0
            self.sample_hold_value = 0
            self.clean_count = 0
    
    def save_values(self):
        # Save current values to JSON
        data = {
            "speed1_value": self.speed1_value,
            "speed2_value": self.speed2_value,
            "time1_value": self.time1_value,
            "time2_value": self.time2_value,
            "out_speed_value": self.out_speed_value,
            "out_time_value": self.out_time_value,
            "sample_hold_value": self.sample_hold_value,
            "clean_count": self.clean_count
        }
        with open(self.CONFIG_FILE, 'w') as file:
            json.dump(data, file)

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
    
    
    
    def NumberInput(self, x, y, label_text, lspace, enable_keypad=True, initial_value=0):
        label = QLabel(label_text, self)
        label.setGeometry(x - lspace, y + 20, 100, 20)
        label.setStyleSheet("color: black; font-size: 14px; background-color: transparent;")
        
        number_input = QLineEdit(self)
        number_input.setPlaceholderText("0")
        number_input.setValidator(QDoubleValidator(0.0, 999999.0, 2))
        number_input.setReadOnly(True)
        number_input.setGeometry(x, y, 100, 60)
        number_input.setAlignment(Qt.AlignCenter)
        
        # Set initial value
        number_input.setText(str(initial_value))

        if enable_keypad:
            number_input.mousePressEvent = lambda event: self.openKeypad(event, number_input)
        else:
            number_input.mousePressEvent = lambda event: None

        return number_input
    def update_measured_temp(self, data):
        


    # Check if the first two characters are '40'
        if data.startswith('40'):

        # Extract and print the data at the 3rd position (index 4:6)
            third_position_data = data[4:6]

        # Check if the data at the 3rd position is '27'
            if third_position_data == '27':
                self.command_response=True

            # Split the data after the 3rd position (from index 6 onwards), exclude the last two characters (LRC - 59)
                relevant_data = data[6:-2]

            # Split the relevant data into groups of 2 characters each (hex values)
                split_data = [relevant_data[i:i+2] for i in range(0, len(relevant_data), 2)]

            # Convert each hex pair to ASCII one by one and print
                decimal_data = []
                for byte in split_data:
                    try:
                        decimal_value = int(byte, 16)  # Convert hex to decimal
                        decimal_data.append(decimal_value)
                    except ValueError as e:
                        decimal_data.append(None)

            # Combine the 2-byte data at [14:16] and [16:18] into a single decimal value for intfr_temp_read
                if len(data) >= 18:
                    byte_2 = data[8:10]
                    byte_1 = data[6:8]
                    combined_hex = byte_2 + byte_1  # Combine the two hex bytes
                    self.intfr_temp_read = int(combined_hex, 16) / 100 
                    self.intfr_temp_read = round(self.intfr_temp_read, 2)  # Convert combined hex to decimal
                  
                    
                    # Print the infrared temperature reading
                else:
                    self.intfr_temp_read = None
                   

            # Combine the 2-byte data at [10:12] and [12:14] for sensor_temp_read
                if len(data) >= 18:
                    byte_2 = data[12:14]
                    byte_1 = data[10:12]
                    combined_hex = byte_2 + byte_1  # Combine the two hex bytes
                    self.sensor_temp_read = int(combined_hex, 16) / 100
                    self.sensor_temp_read = round(self.sensor_temp_read, 2)  # Convert combined hex to decimal
                  
                else:
                    self.sensor_temp_read = None
                 

            # Combine the 2-byte data at [14:16] and [16:18] for sensor_rh_read
                if len(data) >= 18:
                    byte_2 = data[16:18]
                    byte_1 = data[14:16]
                    combined_hex = byte_2 + byte_1  # Combine the two hex bytes
                    self.sensor_rh_read = int(combined_hex, 16) / 100
                    self.sensor_rh_read = round(self.sensor_rh_read, 2)  # Convert combined hex to decimal
                  
                    
                else:
                    sensor_rh_read = None
                   

            # 

           
              
       
        if self.intfr_temp_value is not None:
        # Convert the float to a formatted string and set it in the QLineEdit
            self.intfr_temp_value.setText(f"{self.intfr_temp_read:.2f}")
    
        if self.sensor_temp_value is not None:
        # Convert the float to a formatted string and set it in the QLineEdit
            self.sensor_temp_value.setText(f"{self.sensor_temp_read:.2f}")
    
        if self.sensor_rh_value is not None:
        # Convert the float to a formatted string and set it in the QLineEdit
            self.sensor_rh_value.setText(f"{self.sensor_rh_read:.2f}")

    # Assuming intfr_temp_read, sensor_temp_read, and sensor_rh_read are float values
       
    def openKeypad(self, event, number_input):
        keypad = NumericKeypad(self)
        if keypad.exec_() == QDialog.Accepted:
            value = keypad.getValue()
            number_input.setText(value)
            self.save_values()
            # Update corresponding variables based on the input field
            if number_input == self.speed1:
                self.speed1_value = value
            elif number_input == self.speed2:
                self.speed2_value = value
            elif number_input == self.time1:
                self.time1_value = value
            elif number_input == self.time2:
                self.time2_value = value
            elif number_input == self.out_speed:
                self.out_speed_value = value
            elif number_input == self.out_time:
                self.out_time_value = value
            elif number_input == self.sample_hold:
                self.sample_hold_value = value
            elif number_input == self.clean:
                self.clean_count = value

            # Print the current values
       
   
    def Read_pump_config(self, *args):
    
    # Send the formatted string via UART
        self.uart.send_uart_hex("18 00 00")
    def Read_temp(self, *args):
        # Send the formatted string via UART
        self.uart.send_uart_hex("27 00 00")
      
        # Wait for 3 seconds


    def Read_temp_button(self, *args):
        
    # Call Read_temp immediately
        self.Read_temp()

        # Define a function to check the command_response after 3 seconds
        def check_command_response():
            if self.command_response:
                self.command_response = False
                
                self.notification.show_notification("Read Temp Success.", "success", 3000)
            else:
                
                self.notification.show_notification("Read Temp Failed.", "error", 3000)
         

        # Start a timer to check command_response after 3 seconds
        timer = threading.Timer(2, check_command_response)
        timer.start()

        
    
    
    def createContainer(self, x, y, width, height, bg_color, border_radius, border_color, heading_text, add_toggle=False):
        container = QWidget(self)
        container.setGeometry(x, y, width, height)
        container.setStyleSheet(f"""
        background-color: {bg_color};
        border-radius: {border_radius}px;
        border: 2px solid {border_color};
    """)

        heading = QLabel(heading_text, container)
        heading.move(10, 10) 
        heading.setStyleSheet(f"color: black; font-weight: bold; font-size: 16px; border: none; background-color: transparent;")

        if add_toggle:
            toggle_layout = QHBoxLayout()

            self.label_off = QLabel("IN")
            self.label_on = QLabel("OUT")

            self.label_on.setStyleSheet("color: grey; border: none; background: transparent;font-weight: bold;")
            self.label_off.setStyleSheet("color: black; border: none; background: transparent;font-weight: bold;")

            toggle_layout.addWidget(self.label_off)
            self.toggle_button = AnimatedToggle()
            self.toggle_button.setFixedSize(60, 40)
            toggle_layout.addWidget(self.toggle_button)
            toggle_layout.addWidget(self.label_on)

            toggle_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)) 

            toggle_widget = QWidget(container)  # Make toggle_widget a child of container
            toggle_widget.setLayout(toggle_layout)
            toggle_widget.setStyleSheet("background-color: transparent;border: none;")

            toggle_layout.setAlignment(Qt.AlignBottom) 
            toggle_widget.move(550, 5)  

            self.toggle_button.stateChanged.connect(self.update_labels)

        container.show() 
        
    def update_labels(self, state):
        if state == Qt.Checked:
            self.label_on.setStyleSheet("color: black; border: none; background: transparent;font-weight: bold;")
            self.label_off.setStyleSheet("color: grey; border: none; background: transparent;")
            self.inTest=True
          
        else:
            self.label_on.setStyleSheet("color: grey; border: none; background: transparent;")
            self.label_off.setStyleSheet("color: black; border: none; background: transparent;font-weight: bold;")
            self.inTest=False
         
            
            
    def save_button_pressed(self, *args):
        
        self.save_values()
        
        self.savebutton = True
        
    # Initialize formatted strings as empty in case of invalid values
        formatted_string1, formatted_string2 = "", ""

    # Convert and transform speed1_value, speed2_value, and time1_value, handling possible conversion issues
        try:
        # Transform speed1_value if within range [1, 100]
            speed1_value_int = int(float(self.speed1_value))
            if 1 <= speed1_value_int <= 100:
                speed1_value_int = 101 - speed1_value_int

        # Transform speed2_value if within range [1, 100]
            speed2_value_int = int(float(self.speed2_value))
            if 1 <= speed2_value_int <= 100:
                speed2_value_int = 101 - speed2_value_int

            time1_value_int = int(float(self.time1_value)) * 100
            clean_count_int = int(float(self.clean_count))
        # Convert to hexadecimal format
            speed1_hex = f"{speed1_value_int:02X}"
            speed2_hex = f"{speed2_value_int:02X}"
            time1_msb_hex = f"{(time1_value_int >> 8) & 0xFF:02X}"
            time1_lsb_hex = f"{time1_value_int & 0xFF:02X}"
            clean_msb_hex = f"{(clean_count_int >> 8) & 0xFF:02X}"
            clean_lsb_hex = f"{clean_count_int & 0xFF:02X}"
            formatted_string1 = f"18 00 {speed1_hex} {time1_lsb_hex} {time1_msb_hex}"
        except (ValueError, TypeError):
           pass

    # Convert and transform out_speed_value and out_time_value, handling possible conversion issues
        try:
        # Transform out_speed_value if within range [1, 100]
            out_speed_value_int = int(float(self.out_speed_value))
            if 1 <= out_speed_value_int <= 100:
                out_speed_value_int = 101 - out_speed_value_int

            out_time_value_int = int(float(self.out_time_value)) * 100
        # Convert to hexadecimal format
            out_speed_value_hex = f"{out_speed_value_int:02X}"
            out_time_value_msb_hex = f"{(out_time_value_int >> 8) & 0xFF:02X}"
            out_time_value_lsb_hex = f"{out_time_value_int & 0xFF:02X}"
            formatted_string2 = f"18 01 {out_speed_value_hex} {out_time_value_lsb_hex} {out_time_value_msb_hex}"
        except (ValueError, TypeError):
            pass
            
    # Send the appropriate formatted string based on inTest flag, if valid
        if self.inTest and formatted_string2:
        
            self.uart.send_uart_hex(formatted_string2)
           
        elif not self.inTest and formatted_string1:
          
            self.uart.send_uart_hex(formatted_string1)

       
    def settings_Success(self, data):
        
        if data == "400318005B":
            pass
              
         
            

    def resizeEvent(self, event):
        if hasattr(self, 'original_image'):
            self.background_image = self.original_image.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        # Draw the background image
        if hasattr(self, 'background_image') and not self.background_image.isNull():
            painter.drawImage(self.rect(), self.background_image)

        super().paintEvent(event)
