from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import  QVBoxLayout, QWidget, QLabel,QSpacerItem,QSizePolicy
from PyQt5.QtGui import QPainter, QImage, QFontDatabase, QFont, QIcon
from Constants.Buttons.save_green_button import SaveGreenButton
from Constants.Buttons.slider_button1_1byte import SliderButton
from Constants.Buttons.slider_button_2byte import SliderButton1
from Constants.Buttons.setting_buttons import SettingsButton

from Constants.MainNotification import Notification
from Controls.uart_control import UARTcontrol
from Controls.gpio_control import GPIOController
import resources_rc
import time
import threading


var1=0
var2=0 
var3=0
var4=0
var5=0 
var6=0


class SettingsScreen(QWidget):
    notify_title_bar = pyqtSignal(str, str, str, str, str)
    def __init__(self, text: str, parent=None, uart_thread=None):
        super().__init__(parent=parent)
        self.setWindowState(Qt.WindowFullScreen)
        self.uart_thread = uart_thread
   
        self.uart = UARTcontrol()

        self.nextcount = 0
        self.isNextPressed = False
        self.notification = Notification(self)
        
 

        # Initialize variables to store the slider values (MOVED TO __init__)
        self.lamp_power_value = var1  
        self.mvm_symmetry_value = var2  
        self.trigger_count_value = var3
        self.mvm_span_value = var4  
        self.intr_gain_value = var5
        self.amp_gain_value = var6  
        self.savebutton=False
        self.command_response=False
        self.save_confirmation = False
        # Create a vertical layout for the settings screen
        layout = QVBoxLayout()
        font_id = QFontDatabase.addApplicationFont(":/Constants/Fonts/JosefinSans-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else 'Arial'
        self.heading_label = QLabel("SETTINGS", self)
        font = QFont(font_family, 13, QFont.Bold)
        self.heading_label.setFont(font)
        self.heading_label.setStyleSheet("color: black; font-weight: bold;")
        self.heading_label.setGeometry(110, -10, 150, 100)
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

            # Initial vertical position for sliders
        y_position = 80
        vertical_spacing = 8 
        self.isNextPressed = False# 30 pixels of vertical spacing
        
        
        self._button(
            name="", icon_path=":/Constants/icons/setprev.png",
            action=lambda *args: self.goto_HOME(),
            x=10, y=10, width=90, height=60,
            visible=True, bg_color="rgba(60, 179, 113, 0.0)"
        )
        
        self._button(
            name="", icon_path=":/Constants/icons/setnext.png",
            action=lambda *args:  self.parent().setCurrentIndex(3),
            x=930, y=10, width=90, height=60,
            visible=True, bg_color="rgba(60, 179, 113, 0.0)"
        )
        self.createContainer(x=90, y=470, width=850, height=90, bg_color='#180A0A4E', border_radius=15, border_color='#180A0A6F')

            # Create the sliders with 30-pixel vertical spacing
        self.createSlider(name="LAMP POWER", logo_path=":/Constants/icons/lamp_power.png", y=y_position)
        y_position += 48 + vertical_spacing
        self.createSlider(name="MVM SYMMETRY", logo_path=":/Constants/icons/mvm_speed.png", y=y_position, padding=10)
        y_position += 48 + vertical_spacing
        self.createSlider(name="TRIGGER COUNT", logo_path=":/Constants/icons/trigger.png", y=y_position, padding=11)
        y_position += 48 + vertical_spacing
        self.createSlider(name="MVM SPAN", logo_path=":/Constants/icons/MVM_gain.png", y=y_position, padding=62)
        y_position += 48 + vertical_spacing
        self.createSlider1(name="INTR GAIN", logo_path=":/Constants/icons/mvm_location.png", y=y_position, padding=67)
        y_position += 48 + vertical_spacing
        self.createSlider(name="AMP GAIN", logo_path=":/Constants/icons/gain.png", y=y_position, padding=70)
        self.createButton1(name=" SAVE", icon_path=":/Constants/icons/save.png", action=lambda *args: self.save_button(),x=830,y=30, width=100, height=40,visible=True)
        
        self.createButton(name="CALIBRATION", icon_path=":/Constants/icons/calibration.png", action=lambda *args: self.goToCalibration(), width=170, height=60)
        self.createButton(name="INTF.TEST", icon_path=":/Constants/icons/intf_test.png", action=lambda *args: self.INTF_TEST(),x=330, width=170, height=60)
        self.createButton(name="CYCLE MODE", icon_path=":/Constants/icons/cyclemode.png", action=lambda *args: self.cyclemode(),x=530, width=170, height=60)
        self.createButton(name="GRAPH", icon_path=":/Constants/icons/graph.png", action=lambda *args: self.graph(),x=730, width=170, height=60)

    def goto_HOME(self):
        
        self.parent().setCurrentIndex(0)
        
    def _button(self, name, icon_path, bg_color, action, x=60, y=457, width=170, height=60, visible=True, H=50, W=50):
        from PyQt5.QtGui import QIcon
        from Constants.Buttons.save_green_button import SaveButtonND
        self.custom_button = SaveButtonND(name=name, action=action, icon_path=icon_path, bg_color=bg_color,
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
        self.button_label.setStyleSheet("font-size: 14px; color: white;background-color: transparent;")
        self.button_label.raise_()  # Ensure the label is on top
        self.button_label.show()
    def INTF_TEST(self):
        
        pass
    def cyclemode(self):
        
        pass
    def graph(self):
        
        pass
    
    
    
    def goToCalibration(self):
        
        self.parent().setCurrentIndex(7)
    
        
        
           
    def showEvent(self, event):
        super().showEvent(event)
        self.centerPopupNotification()

    # Override the resizeEvent to reposition the popup when the window is resized
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.centerPopupNotification()

    # Method to center the popup notification
    def centerPopupNotification(self):

        # Center horizontally, with a small margin from the top
        x = 230
        y = 12  # Adjust y to your liking, this is the distance from the top

   
   
 

        
    
   
    def reload_sliders(self):
        """Reloads the slider positions based on the current values 
           of the settings variables."""

        lamp_power_slider = self.findChild(SliderButton, "LAMP POWER")
        mvm_symmetry_slider = self.findChild(SliderButton, "MVM SYMMETRY")
        trigger_count_slider = self.findChild(SliderButton, "TRIGGER COUNT")
        mvm_span_slider = self.findChild(SliderButton, "MVM SPAN")
        amp_gain_slider = self.findChild(SliderButton, "AMP GAIN")
        intr_gain_slider = self.findChild(SliderButton1, "INTR GAIN")  

        if lamp_power_slider:
            lamp_power_slider.slider.setValue(self.lamp_power_value)
        if mvm_symmetry_slider:
            mvm_symmetry_slider.slider.setValue(self.mvm_symmetry_value)
        if trigger_count_slider:
            trigger_count_slider.slider.setValue(self.trigger_count_value)
        if mvm_span_slider:
            mvm_span_slider.slider.setValue(self.mvm_span_value)
        if amp_gain_slider:
            amp_gain_slider.slider.setValue(self.amp_gain_value)
        if intr_gain_slider:
            intr_gain_slider.slider1.setValue(self.intr_gain_value)
       

    def save_button(self, *args):
        
        self.savebutton=True

        
    # Convert each value to hexadecimal format
        lamp_power_hex = hex(self.lamp_power_value)[2:].zfill(2).upper()  
        mvm_symmetry_hex = hex(self.mvm_symmetry_value)[2:].zfill(2).upper()
        trigger_count_hex = hex(self.trigger_count_value)[2:].zfill(2).upper()
        mvm_span_hex = hex(self.mvm_span_value)[2:].zfill(2).upper()
        amp_gain_hex = hex(self.amp_gain_value)[2:].zfill(2).upper()

    # Convert intr_gain_value to a 16-bit integer representing the fixed-point value
        intr_gain_fixed_point = int(self.intr_gain_value * 1)  

    # Extract the most significant byte (MSB) and least significant byte (LSB)
        intr_gain_msb = (intr_gain_fixed_point >> 8) & 0xFF 
        intr_gain_lsb = intr_gain_fixed_point & 0xFF

    # Convert to hexadecimal format
        intr_gain_msb_hex = f"{intr_gain_msb:02X}"
        intr_gain_lsb_hex = f"{intr_gain_lsb:02X}"

    # Create the formatted string with the hexadecimal values (LSB before MSB)
        formatted_string = f"0A {lamp_power_hex} {mvm_symmetry_hex} {trigger_count_hex} {mvm_span_hex} " \
                       f"{intr_gain_lsb_hex} {intr_gain_msb_hex} {amp_gain_hex}" 

   
    # Send the formatted string via UART
        self.uart.send_uart_hex(formatted_string) 
        def check_command_response():
            if self.save_confirmation:
                self.save_confirmation = False
                self.notification.show_notification("Slider values saved successfully", "success", 3000)
            else:
                self.notification.show_notification("Error Saving values", "error", 3000)
        

        # Start a timer to check command_response after 3 seconds
        timer = threading.Timer(1, check_command_response)
        timer.start()
   

    def Read_button(self, *args):
    
    # Send the formatted string via UART
        self.uart.send_uart_hex("17 00")
        
   
 
        
    def update_slider(self, data):

        global var1, var2, var3, var4, var5, var6

    # Check if the first two characters are '40'
        if data.startswith('40'):
           

        # Extract and print the data at the 3rd position (index 4:6)
            third_position_data = data[4:6]
        
        # Check if the data at the 3rd position is '17'
            if third_position_data == '17':
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

            # Combine the 2-byte data at [14:16] and [16:18] into a single decimal value
                if len(data) >= 18:
                    byte_2 = data[14:16]
                    byte_1 = data[16:18]
                    combined_hex = byte_2 + byte_1# Combine the two hex bytes
                    var5 = int(combined_hex, 16)  # Convert combined hex to decimal
                 
                else:
                    var5 = None
                 
            # Print the full decimal values list
              

            # Assign the decimal values to the sliders' variables if they exist
                var1 = decimal_data[0] if len(decimal_data) > 0 else None
                var2 = decimal_data[1] if len(decimal_data) > 1 else None
                var3 = decimal_data[2] if len(decimal_data) > 2 else None
                var4 = decimal_data[3] if len(decimal_data) > 3 else None
                var6 = decimal_data[6] if len(decimal_data) > 6 else None

               

            # Update the sliders with the received values
                if var1 is not None:
                    self.lamp_power_value = var1  # Update lamp power with var1
                    self.update_LAMP_POWER_value(var1)  # Update slider display

                if var2 is not None:
                    self.mvm_symmetry_value = var2  # Update MVM symmetry with var2
                    self.update_MVM_SYMMETRY_value(var2)  # Update slider display

                if var3 is not None:
                    self.trigger_count_value = var3  # Update trigger count with var3
                    self.update_TRIGGER_COUNT_value(var3)  # Update slider display
                if var4 is not None:
                    self.mvm_span_value = var4  # Update lamp power with var1
                    self.update_MVM_SPAN_value(var4)  # Update slider display

                if var5 is not None:
                    self.intr_gain_value = var5  # Update MVM symmetry with var2
                    self.update_intr_gain_value(var5)  # Update slider display

                if var6 is not None:
                    self.amp_gain_value = var6  # Update trigger count with var3
                    self.update_AMP_GAIN_value(var6)
                    
                self.reload_sliders()# Update slider display

            else:
                pass
        else:
            pass


    def settings_Success(self, data):
        
  
        if self.savebutton==True:   
            if data == "40030A0049":
              
                self.save_confirmation = True
        if data == "40031A0059":
              
           pass
            
            
                
    def createContainer(self, x, y, width, height, bg_color, border_radius, border_color):
        # Create a container using QFrame or QWidget
        container = QWidget(self)
        container.setGeometry(x, y, width, height)
        container.setStyleSheet(f"""
            background-color: {bg_color};
            border-radius: {border_radius}px;
            border: 2px solid {border_color};
        """)
        container.show()

    
    def createSlider(self, name, logo_path=None, x=60, y=90, width=900, height=70, padding=40):
        # Create a custom slider with a name (SliderButton) and adjustable padding, and optional logo
        slider = SliderButton(name, logo_path=logo_path, padding=padding, parent=self)
        slider.setObjectName(name)  # Set object name for the slider

        # Set the position and size of the slider widget
        slider.setGeometry(x, y, width, height)

        # Add the slider to the parent layout or window
        slider.setParent(self)

        # Set the initial value for the slider based on the variable for each specific slider
        if name == "LAMP POWER":
            slider.slider.setValue(self.lamp_power_value)  # Set to initialized value self.lamp_power_value
            slider.slider.valueChanged.connect(self.update_LAMP_POWER_value)
        elif name == "MVM SYMMETRY":
            slider.slider.setValue(self.mvm_symmetry_value)  # Set to initialized value self.mvm_symmetry_value
            slider.slider.valueChanged.connect(self.update_MVM_SYMMETRY_value)
        elif name == "TRIGGER COUNT":
            slider.slider.setValue(self.trigger_count_value)  # Set to initialized value self.trigger_count_value
            slider.slider.valueChanged.connect(self.update_TRIGGER_COUNT_value)
        elif name == "MVM SPAN":
            slider.slider.setValue(self.mvm_span_value)  # Set to initialized value self.mvm_span_value
            slider.slider.valueChanged.connect(self.update_MVM_SPAN_value)
        elif name == "AMP GAIN":
            slider.slider.setValue(self.amp_gain_value)  # Set to initialized value self.amp_gain_value
            slider.slider.valueChanged.connect(self.update_AMP_GAIN_value)


            
            
            
    def update_LAMP_POWER_value(self, value):
        # Update the lamp power value and print it
        self.lamp_power_value = value
     
    def update_MVM_SYMMETRY_value(self, value):
        # Update the speed value and print it
        self.mvm_symmetry_value = value
     
    def update_TRIGGER_COUNT_value(self, value):
        # Update the speed value and print it
        self.trigger_count_value = value
      
        
    def update_MVM_SPAN_value(self, value):
        # Update the speed value and print it
        self.mvm_span_value = value
       
        
    def update_intr_gain_value(self, value):
        # Update the speed value and print it
        self.intr_gain_value = value
  
        
    def update_AMP_GAIN_value(self, value):
        # Update the speed value and print it
        self.amp_gain_value = value
    
               
    def createSlider1(self, name, logo_path=None, x=60, y=90, width=900, height=70, padding=40):
        # Create a custom slider with a name (SliderButton) and adjustable padding, and optional logo
        slider1 = SliderButton1(name, logo_path=logo_path, padding=padding, parent=self)
        slider1.setObjectName(name)  # Set object name for the slider

        # Set the position and size of the slider widget
        slider1.setGeometry(x, y, width, height)

        # Add the slider to the parent layout or window
        slider1.setParent(self)
        if name == "INTR GAIN":
            slider1.slider1.setValue(self.intr_gain_value)  # Set to initialized value self.lamp_power_value
            slider1.slider1.valueChanged.connect(self.update_intr_gain_value)





    def createButton(self, name, icon_path, action, x=130, y=487, width=180, height=60):
        self.custom_button = SettingsButton(name=name, action=action, icon_path=icon_path)
        self.custom_button.setParent(self)

        if icon_path:
            icon = QIcon(icon_path)
            self.custom_button.setIcon(icon)

        self.custom_button.setGeometry(x, y, width, height)

        # Explicitly raise the button to make sure it is on top of other widgets
        self.custom_button.raise_()
        self.custom_button.setFocusPolicy(Qt.StrongFocus)
    def createButton1(self, name, icon_path, action, x=60, y=457, width=170, height=60, visible=True):
        self.custom_button = SaveGreenButton(name=name, action=action, icon_path=icon_path)
        self.custom_button.setParent(self)

        if icon_path:
            icon = QIcon(icon_path)
            self.custom_button.setIcon(icon)

        self.custom_button.setGeometry(x, y, width, height)

        # Explicitly raise the button to make sure it is on top of other widgets
        self.custom_button.raise_()
        self.custom_button.setFocusPolicy(Qt.StrongFocus)
        self.custom_button.setVisible(visible)
    
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