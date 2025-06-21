from PyQt5.QtCore import Qt,pyqtSignal, QSettings
from PyQt5.QtWidgets import (
    QVBoxLayout, QWidget, QLabel, QLineEdit, QDialog, QHBoxLayout, 
    QSpacerItem, QSizePolicy, QButtonGroup
)
from PyQt5.QtGui import QPainter, QImage, QFontDatabase, QFont, QIcon, QDoubleValidator
from Constants.Buttons.radio_button import RadioButtonWithAnimation
from Constants.Buttons.save_green_button import SaveGreenButton
from Constants.Buttons.two_state_toggle_button import AnimatedToggle
from Constants.MainNotification import Notification
from Constants.keypad_textbox import NumericKeypad
from Controls.gpio_control import GPIOController
from Controls.uart_control import UARTcontrol
import resources_rc
import threading



class SettingsScreen3(QWidget):
    notify_title_bar = pyqtSignal(str, str, str, str, str)
    def __init__(self, text: str, parent=None, uart_thread=None):
        super().__init__(parent=parent)
        self.setWindowState(Qt.WindowFullScreen)
        self.uart_thread = uart_thread
        self.uart = UARTcontrol()
        self.controller = GPIOController()
        self.notification = Notification(self)
        self.in_out_state = "IN" 
        self.temp_comp_value = 0
        self.sensor_comp_value = 0
        self.intfr_mode_value = None

        self.temp_comp_read=0
        self.sensor_comp_read=0
        self.save_confirmation_comp = False
        self.save_confirmation_intfr = False


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
        self.set_initial_radio_button()
        self._button(
            name="", icon_path=":/Constants/icons/setprev.png",
            action=lambda *args: self.parent().setCurrentIndex(3),
            x=10, y=10, width=90, height=60,
            visible=True, bg_color="rgba(60, 179, 113, 0.0)"
        )
        
        self._button(
            name="", icon_path=":/Constants/icons/setnext.png",
            action=lambda *args: self.parent().setCurrentIndex(5),
            x=930, y=10, width=90, height=60,
            visible=True, bg_color="rgba(60, 179, 113, 0.0)"
        )
       
        self.command_response_comp = False
        self.command_response_intfr = False
        self.createContainer(x=90, y=110, width=850, height=160, bg_color='#180A0A4E', border_radius=15, border_color='#180A0A6F', heading_text='COMPENSATION CONFIG',add_radio_buttons=False)
        self.createContainer(x=90, y=290, width=850, height=160, bg_color='#180A0A4E', border_radius=15, border_color='#180A0A6F', heading_text='INTFR MODE',add_radio_buttons=True)
        self.createContainerUART(x=90, y=470, width=850, height=90, bg_color='#180A0A4E', border_radius=15, border_color='#180A0A6F', heading_text='UART CONFIG',add_radio_buttons=True)
        self.temp_comp = self.NumberInput(x=210, y=170, label_text="TEMP COMP",lspace=100,enable_keypad=True)
        self.sensor_comp = self.NumberInput(x=500, y=170, label_text="SENSOR COMP ",lspace=130,enable_keypad=True)
        self.save_button(name=" READ", icon_path=":/Constants/icons/read.png", action=lambda *args: self.Read_comp_button(),x=700,y=180, width=90, height=40,visible=True,bg_color="rgba(32, 123, 130, 1)")
        self.save_button(name=" SET", icon_path=":/Constants/icons/save.png", action=lambda *args: self.set_button_pressed(),x=820,y=180, width=90, height=40,visible=True, bg_color="rgba(3, 131, 3, 1)")
        self.save_button(name=" READ", icon_path=":/Constants/icons/read.png", action=lambda *args: self.Read_intfr_button(),x=700,y=355, width=90, height=40,visible=True,bg_color="rgba(32, 123, 130, 1)")
        self.save_button(name=" SET", icon_path=":/Constants/icons/save.png", action=lambda *args: self.intfr_set_button(),x=820,y=355, width=90, height=40,visible=True, bg_color="rgba(3, 131, 3, 1)")
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
    def settings_Success(self, data):
        

                
        if data == "4003300073":
              
                self.save_confirmation_comp=True
        if data == "4003260065":
              
                self.save_confirmation_intfr=True



    def update_comp(self, data):
           # Check if the first two characters are '40'
        if data.startswith('40'):

        # Extract and print the data at the 3rd position (index 4:6)
            third_position_data = data[4:6]

        # Check if the data at the 3rd position is '27'
            if third_position_data == '31':
                self.command_response_comp = True

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
                if len(data) >= 11:
                    temp_comp = data[6:8]
                    
                  
                    self.temp_comp_read = int(temp_comp, 16) 
                    self.temp_comp_read = round(self.temp_comp_read, 2)  # Convert combined hex to decimal
                   
                    
                    # Print the infrared temperature reading
                else:
                    self.temp_comp_read = None
                 

            # Combine the 2-byte data at [10:12] and [12:14] for sensor_temp_read
                
                if len(data) >= 11:
                    sensor_comp = data[8:10]
                    
                  
                    self.sensor_comp_read = int(sensor_comp, 16) 
                    self.sensor_comp_read = round(self.sensor_comp_read, 2)  # Convert combined hex to decimal
                    
                    
                    # Print the infrared temperature reading
                else:
                    self.sensor_comp_read = None
                
            #   
            
                if len(data) >= 11:
                  
                    if self.temp_comp is not None:
        # Convert the float to a formatted string and set it in the QLineEdit
                        self.temp_comp.setText(f"{self.temp_comp_read:.2f}")
    
                    if self.sensor_comp is not None:
        # Convert the float to a formatted string and set it in the QLineEdit
                        self.sensor_comp.setText(f"{self.sensor_comp_read:.2f}")
                    # Print the infrared temperature reading
                else:
                  pass
      
            
       
    

   


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
 
       
    def openKeypad(self, event, number_input):
        keypad = NumericKeypad(self)
        if keypad.exec_() == QDialog.Accepted:
            value = keypad.getValue()
            number_input.setText(value)
          
            # Update corresponding variables based on the input field
            if number_input == self.temp_comp:
                self.temp_comp_value = value
                
            elif number_input == self.sensor_comp:
                self.sensor_comp_value = value
          
          
            # Print the current values
    
    def Read_comp(self, *args):
       
    # Send the formatted string via UART
        self.uart.send_uart_hex("31 00")
    
    def Read_comp_button(self, *args):
        
    # Call Read_temp immediately
        self.Read_comp()

        # Define a function to check the command_response after 3 seconds
        def check_command_response():
            if self.command_response_intfr:
                self.command_response_intfr = False
                self.notification.show_notification("Read Compensation Success.", "success", 3000)
            else:
                
                self.notification.show_notification("Read Compensation Failed.", "error", 3000)
         
  
        
        # Start a timer to check command_response after 3 seconds
        timer = threading.Timer(2, check_command_response)
        timer.start()
 

    def Read_intfr_mode(self, *args):
    
    # Send the formatted string via UART
        self.uart.send_uart_hex("32 00")
      
    def Read_intfr_button(self, *args):
    # Call Read_temp immediately
        self.Read_intfr_mode()
        
        # Define a function to check the command_response after 3 seconds
        def check_command_response():
            if self.command_response_comp:
                self.command_response_comp = False
                self.notification.show_notification("Read INTFR mode Success.", "success", 3000)
            else:
                
                self.notification.show_notification("Read INTFR mode Failed.", "error", 3000)
         


        # Start a timer to check command_response after 3 seconds
        timer = threading.Timer(2, check_command_response)
        timer.start()
        
    def update_intfr_mode(self, data):

        

    # Check if the first two characters are '40'
        if data.startswith('40'):
           

        # Extract and print the data at the 3rd position (index 4:6)
            third_position_data = data[4:6]
        
        # Check if the data at the 3rd position is '17'
            if third_position_data == '32':
                self.command_response_intfr = True

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
                        
                if len(data) >= 4:
                    intfr_value = data[6:8]
                    
                  
                    self.intfr_mode_value = int(intfr_value, 16)
                    self.intfr_mode_value = round(self.intfr_mode_value, 2)  # Convert combined hex to decimal
                    
                    if self.intfr_mode_value is not None:
        # Convert the float to a formatted string and set it in the QLineEdit
                        self.intfr_mode_value =    self.intfr_mode_value
                        
                    
                      
                else:
                   pass

        else:
            pass
    def createContainerUART(self, x, y, width, height, bg_color, border_radius, border_color, heading_text, add_radio_buttons=False):
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

        if add_radio_buttons:
            # Initialize QSettings for saving/loading settings
            self.settings = QSettings("psr", "FTIR")

            radio_layout = QHBoxLayout()
            radio_layout.setSpacing(10)

            # Create labels and animated radio buttons
            mode0 = QLabel("MODE - 0", container)
            mode0.setStyleSheet("font-size: 14px;") 
            self.radio_button1 = RadioButtonWithAnimation(container)
            self.radio_button1.toggled.connect(lambda: self.save_mode("00"))

            mode1 = QLabel("MODE - 1", container)
            mode1.setStyleSheet("font-size: 14px;") 
            self.radio_button2 = RadioButtonWithAnimation(container)
            self.radio_button2.toggled.connect(lambda: self.save_mode("01"))

            mode2 = QLabel("MODE - 2", container)
            mode2.setStyleSheet("font-size: 14px;") 
            self.radio_button3 = RadioButtonWithAnimation(container)
            self.radio_button3.toggled.connect(lambda: self.save_mode("10"))

            mode3 = QLabel("MODE - 3", container)
            mode3.setStyleSheet("font-size: 14px;") 
            self.radio_button4 = RadioButtonWithAnimation(container)
            self.radio_button4.toggled.connect(lambda: self.save_mode("11"))

            # Add label-button pairs to layout
            radio_layout.addWidget(mode0)
            radio_layout.addWidget(self.radio_button1)
            radio_layout.addItem(QSpacerItem(80, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))
            radio_layout.addWidget(mode1)
            radio_layout.addWidget(self.radio_button2)
            radio_layout.addItem(QSpacerItem(80, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))
            radio_layout.addWidget(mode2)
            radio_layout.addWidget(self.radio_button3)
            radio_layout.addItem(QSpacerItem(80, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))
            radio_layout.addWidget(mode3)
            radio_layout.addWidget(self.radio_button4)

            radio_group = QButtonGroup(container)
            radio_group.addButton(self.radio_button1)
            radio_group.addButton(self.radio_button2)
            radio_group.addButton(self.radio_button3)
            radio_group.addButton(self.radio_button4)

            # Set layout and initial position for radio buttons
            radio_widget = QWidget(container)
            radio_widget.setLayout(radio_layout)
            radio_widget.setStyleSheet("background-color: transparent; border: none;")
            radio_widget.move(60, 30)

            # Restore the saved mode selection
            self.restore_mode()

        container.show()

    def save_mode(self, mode_value):
        """Saves the selected mode to settings."""
        self.settings.setValue("selected_mode", mode_value)
        self.controller.set_mode(mode_value)
        

    def restore_mode(self):
        """Restores the saved mode selection on startup."""
        saved_mode = self.settings.value("selected_mode", "00")
        if saved_mode == "00":
            self.radio_button1.setChecked(True)
        elif saved_mode == "01":
            self.radio_button2.setChecked(True)
        elif saved_mode == "10":
            self.radio_button3.setChecked(True)
        elif saved_mode == "11":
            self.radio_button4.setChecked(True)

    def createContainer(self, x, y, width, height, bg_color, border_radius, border_color, heading_text, add_toggle=False, add_radio_buttons=False):
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
            toggle_widget.move(700, 5)

        if add_radio_buttons:
            radio_layout = QHBoxLayout()
            radio_layout.setSpacing(10)
            

        # Create labels and animated radio buttons
            label_forward = QLabel("FORWARD", container)
            label_forward.setStyleSheet("font-size: 14px;") 
            self.radio_buttonA = RadioButtonWithAnimation(container)
            self.radio_buttonA.toggled.connect(lambda: self.set_intfr_mode_value(0))

            label_reverse = QLabel("REVERSE", container)
            label_reverse.setStyleSheet("font-size: 14px;") 
            self.radio_buttonB = RadioButtonWithAnimation(container)
            self.radio_buttonB.toggled.connect(lambda: self.set_intfr_mode_value(1))

            label_dual = QLabel("DUAL", container)
            label_dual.setStyleSheet("font-size: 14px;") 
            self.radio_buttonC = RadioButtonWithAnimation(container)
            self.radio_buttonC.toggled.connect(lambda: self.set_intfr_mode_value(2))

        # Add label-button pairs to layout
            radio_layout.addWidget(label_forward)
            radio_layout.addWidget(self.radio_buttonA)
            radio_layout.addItem(QSpacerItem(80, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))
            radio_layout.addWidget(label_reverse)
            radio_layout.addWidget(self.radio_buttonB)
            radio_layout.addItem(QSpacerItem(80, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))
            radio_layout.addWidget(label_dual)
            radio_layout.addWidget(self.radio_buttonC)

            radio_group = QButtonGroup(container)
            radio_group.addButton(self.radio_buttonA)
            radio_group.addButton(self.radio_buttonB)
            radio_group.addButton(self.radio_buttonC)

            radio_widget = QWidget(container)
            radio_widget.setLayout(radio_layout)
            radio_widget.setStyleSheet("background-color: transparent; border: none;")
            radio_widget.move(10, 65)

        container.show()
        
    def set_initial_radio_button(self):
        """Sets the radio button according to the initial value of intfr_mode_value."""
        if self.intfr_mode_value == 0:
            self.radio_buttonA.setChecked(True)  # FORWARD
        elif self.intfr_mode_value == 1:
            self.radio_buttonB.setChecked(True)  # REVERSE
        elif self.intfr_mode_value == 2:
            self.radio_buttonC.setChecked(True)  # DUAL
               
    def set_intfr_mode_value(self, value):
        self.intfr_mode_value = value
       
        
        
    def intfr_set_button(self, *args):
        self.savebutton = True
        
        
        if self.intfr_mode_value == 0:
            self.uart.send_uart_hex("26 00")
        elif self.intfr_mode_value == 1:
            self.uart.send_uart_hex("26 01")
        elif self.intfr_mode_value == 2:
            self.uart.send_uart_hex("26 02")
        def check_command_response():
                if self.save_confirmation_intfr:
                    self.save_confirmation_intfr = False
                    self.notification.show_notification("INTFR mode Set Successfully", "success", 3000)
                else:
                    
                    self.notification.show_notification("INTFR mode setting Failed", "error", 3000)
            


        timer = threading.Timer(1, check_command_response)
        timer.start()
        

        
    def set_button_pressed(self, *args):
        self.savebutton = True
        
        try:
        # Attempt to convert temp_comp_value to an integer
            temp_comp_value = int(float(self.temp_comp_value))
        # Convert to hexadecimal format
            temp_comp_value_hex = hex(temp_comp_value)[2:].zfill(2).upper()
        except ValueError:
        # If conversion fails, skip sending this value
            temp_comp_value_hex = None

        try:
        # Attempt to convert sensor_comp_value to an integer
            sensor_comp_value = int(float(self.sensor_comp_value))
        # Convert to hexadecimal format
            sensor_comp_value_hex = hex(sensor_comp_value)[2:].zfill(2).upper()
        except ValueError:
        # If conversion fails, skip sending this value
            sensor_comp_value_hex = None

    # Send the formatted string only if both values were successfully converted
        if temp_comp_value_hex is not None and sensor_comp_value_hex is not None:
            formatted_string = f"30 {temp_comp_value_hex} {sensor_comp_value_hex}"
            self.uart.send_uart_hex(formatted_string)
            
            def check_command_response():
                if self.save_confirmation_comp:
                    self.save_confirmation_comp = False
                    self.notification.show_notification("Compensation values saved Successfully", "success", 3000)
                else:
                    
                    self.notification.show_notification("Compensation values saving Failed", "error", 3000)
            

            timer = threading.Timer(1, check_command_response)
            timer.start()
   

    



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
