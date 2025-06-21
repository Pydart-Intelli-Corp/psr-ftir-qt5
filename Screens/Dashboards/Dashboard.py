from PyQt5.QtWidgets import QWidget,QMainWindow
from PyQt5.QtCore import pyqtSignal,QObject,QThread
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, pyqtSignal,QTimer
from PyQt5.QtGui import QPalette, QBrush, QPixmap, QImage, QFont
from Constants.Buttons.save_green_button import SaveButtonND
import time
import os
import pyudev
import json
from Constants.MainNotification import Notification
from Controls.gpio_control import GPIOController
from Controls.uart_control import UARTcontrol


class Dashboard(QWidget):
    CONFIG_FILE = "id.json"
    notify_title_bar = pyqtSignal(str, str, str, str, str)
    def __init__(self, text: str, parent=None, uart_thread=None):
        from PyQt5.QtWidgets import QVBoxLayout, QLabel
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QImage,QFontDatabase, QFont
        from Controls.uart_control import UARTcontrol
        from Controls.gpio_control import GPIOController

        super().__init__(parent=parent)
        self.setWindowState(Qt.WindowFullScreen)
        self.setGeometry(0, 0, 1024, 600)
        self.uart = UARTcontrol()
        self.notification = Notification(self)
        self.controller = GPIOController()
        self.toggle_state_file = "toggle_state.json"
        
   




      
        
        self.isNextPressed = False
        self.nextcount = 0
        self.prevcount = 0
        self.speed1, self.speed2, self.time1, self.time2, self.sample_hold, self.clean_count = self.load_speed_values()
        
        self.speed1x=0
        self.speed2x=0
       


        # Set up the layout
        layout = QVBoxLayout()
        image_path = ":/Constants/images/bg4.png"
       

        self.original_image = QImage(image_path)
        if self.original_image.isNull():
              pass
        else:
                self.background_image = self.original_image.scaled(
                    self.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                
        self.current_group_index = 0  # Start with the first group
        self.total_visible_count = 8 
        
        
        

       

            
      
   
        self.count = 0
        self.ID= None
        self.a1="FAT"
        self.b1="SNF"
        self.c1="CLR"
        self.d1="Protein"
        self.e1="Lactose"
        self.f1="Salts"
        self.g1="Water"
        self.h1="Temperature"
        
        ##########
        
        self.a2="Urea"
        self.b2="Maltodextrin"
        self.c2="Sucrose"
        self.d2="Ammonium SO₄"
        self.e2="Glucose"
        self.f2="Sorbitol"
        self.g2="Melamine"
        self.h2="Starch"
        
        ###########
        
        self.a3="Na Citrate"
        self.b3="Na carbonate"
        self.c3="Na Bicarbonate"
        self.d3="Chem. Emulsifiers"
        self.e3="Hydrogen peroxide"
        self.f3="Vegitable Oil"
        self.g3="Detergents"
        self.h3="Formalin"
        
        ###########

        self.a4="Na Citrate"
        self.b4="Na carbonate"
        self.c4="Na Bicarbonate"
        self.d4="Chem. Emulsifiers"
        self.e4="Hydrogen peroxide"
        self.f4="Veg Oil"
        self.g4="Detergents"
        self.h4="Formalin"
        
        ###########
        
        self.a5="Na Citrate"
        self.b5="Na carbonate"
        self.c5="Na Bicarbonate"
        self.d5="Chem. Emulsifiers"
        self.e5="Hydrogen peroxide"
        self.f5="Vegitable Oil"
        self.g5="Detergents"
        self.h5="Formalin"
        
        ###########
        
        self.a6="Na Citrate"
        self.b6="Na carbonate"
        self.c6="Na Bicarbonate"
        self.d6="Chem. Emulsifiers"
        self.e6="Hydrogen peroxide"
        self.f6="Vegitable Oil"
        self.g6="Detergents"
        self.h6="Formalin"
        
        ###########
        
        self.a7="Na Citrate"
        self.b7="Na carbonate"
        self.c7="Na Bicarbonate"
        self.d7="Chem. Emulsifiers"
        self.e7="Hydrogen peroxide"
        self.f7="Vegitable Oil"
        self.g7="Detergents"
        self.h7="Formalin"
        
        ###########
        
        
        for i in range(1, 51):
            setattr(self, f'A{i}', 0)
            
        for i in range(1, 51):
            setattr(self, f'R{i}', 0)
         #initial_value = getattr(self, 'A1')
        
        
      
        
      
        self.fat_P=True
        self.snf_P=True
        self.clr_P=True
        self.protein_P=True
        self.lactose_P=True
        self.salt_P=True
        self.water_P=True
        self.temp_P=True
        
        self.urea_P=True
        self.maltodextrin_P=True
        self.sucrose_P=True
        self.ammonium_SO4_P=True
        self.glucose_P=True
        self.sorbitol_P=True
        self.melamine_P=True
        self.starch_P=True
        
        self.sodium_citrate_P=True
        self.sodium_carbonate_P=True
        self.sodium_bicarbonate_P=True
        self.chemical_emulsifiers_P=True
        self.hydrogen_peroxide_P=True
        self.veg_oil_P=True
        self.detergents_P=True
        self.formalin_P=True




########################################################################################################################

        self.label_image = QLabel(self)
        self.image_pixmap = QPixmap(":/Constants/images/companylogo.png")
        if not self.image_pixmap.isNull():
            self.image_pixmap = self.image_pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_image.setPixmap(self.image_pixmap)
        self.label_image.setAlignment(Qt.AlignCenter)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.label_image.setGeometry(410, 470, 200, 150)

        self.createContainer(
            x=88, y=500, width=850, height=200,
            
           
        )     
 
 
        # Create container
        self.C1, self.L1 = self.Container(x=100, y=40, icon_path=":/Constants/icons/faticon.png", visibility=self.fat_P, permanent_visibility=self.fat_P, label_text=self.a1, icon_size=(50, 50))
        self.C2, self.L2 = self.Container(x=320, y=40, icon_path=":/Constants/icons/snficon.png", visibility=self.snf_P, permanent_visibility=self.snf_P, label_text=self.b1, icon_size=(50, 50))
        self.C3, self.L3 = self.Container(x=540, y=40, icon_path=":/Constants/icons/clricon.png", visibility=self.clr_P, permanent_visibility=self.clr_P, label_text=self.c1, icon_size=(50, 50))
        self.C4, self.L4 = self.Container(x=760, y=40, icon_path=":/Constants/icons/proteinicon.png", visibility=self.protein_P, permanent_visibility=self.protein_P, label_text=self.d1, icon_size=(50, 50))
        self.C5, self.L5 = self.Container(x=100, y=270, icon_path=":/Constants/icons/sugar.png", visibility=self.lactose_P, permanent_visibility=self.lactose_P, label_text=self.e1, icon_size=(50, 50))
        self.C6, self.L6 = self.Container(x=320, y=270, icon_path=":/Constants/icons/nacl.png", visibility=self.salt_P, permanent_visibility=self.salt_P, label_text=self.f1, icon_size=(50, 50))
        self.C7, self.L7 = self.Container(x=540, y=270, icon_path=":/Constants/icons/watericon.png", visibility=self.water_P, permanent_visibility=self.water_P, label_text=self.g1, icon_size=(50, 50))
        self.C8, self.L8 = self.Container(x=760, y=270, icon_path=":/Constants/icons/tempicon.png", visibility=self.temp_P, permanent_visibility=self.temp_P, label_text=self.h1, icon_size=(50, 50))

        ##################################################################

        self.C9, self.L9 = self.Container(x=100, y=40, icon_path=":/Constants/icons/ureaicon.png", visibility=False, permanent_visibility=self.urea_P, label_text=self.a2, icon_size=(50, 50))
        self.C10, self.L10 = self.Container(x=320, y=40, icon_path=":/Constants/icons/maltodextrin.png", visibility=False, permanent_visibility=self.maltodextrin_P, label_text=self.b2, icon_size=(50, 50))
        self.C11, self.L11 = self.Container(x=540, y=40, icon_path=":/Constants/icons/sucrose.png", visibility=False, permanent_visibility=self.sucrose_P, label_text=self.c2, icon_size=(50, 50))
        self.C12, self.L12 = self.Container(x=760, y=40, icon_path=":/Constants/icons/ammonia.png", visibility=False, permanent_visibility=self.ammonium_SO4_P, label_text=self.d2, icon_size=(50, 50))
        self.C13, self.L13 = self.Container(x=100, y=270, icon_path=":/Constants/icons/glucose.png", visibility=False, permanent_visibility=self.glucose_P, label_text=self.e2, icon_size=(50, 50))
        self.C14, self.L14 = self.Container(x=320, y=270, icon_path=":/Constants/icons/sorbitol.png", visibility=False, permanent_visibility=self.sorbitol_P, label_text=self.f2, icon_size=(50, 50))
        self.C15, self.L15 = self.Container(x=540, y=270, icon_path=":/Constants/icons/melamine.png", visibility=False, permanent_visibility=self.melamine_P, label_text=self.g2, icon_size=(50, 50))
        self.C16, self.L16 = self.Container(x=760, y=270, icon_path=":/Constants/icons/starch.png", visibility=False, permanent_visibility=self.starch_P, label_text=self.h2, icon_size=(50, 50))

        ##################################################################

        self.C17, self.L17 = self.Container(x=100, y=40, icon_path=":/Constants/icons/sodiumcitrate.png", visibility=False, permanent_visibility=self.sodium_citrate_P, label_text=self.a3, icon_size=(50, 50))
        self.C18, self.L18 = self.Container(x=320, y=40, icon_path=":/Constants/icons/caustic.png", visibility=False, permanent_visibility=self.sodium_carbonate_P, label_text=self.b3, icon_size=(50, 50))
        self.C19, self.L19 = self.Container(x=540, y=40, icon_path=":/Constants/icons/salicylic.png", visibility=False, permanent_visibility=self.sodium_bicarbonate_P, label_text=self.c3, icon_size=(50, 50))
        self.C20, self.L20 = self.Container(x=760, y=40, icon_path=":/Constants/icons/ammonia.png", visibility=False, permanent_visibility=self.chemical_emulsifiers_P, label_text=self.d3, icon_size=(50, 50))
        self.C21, self.L21 = self.Container(x=100, y=270, icon_path=":/Constants/icons/h2o2.png", visibility=False, permanent_visibility=self.hydrogen_peroxide_P, label_text=self.e3, icon_size=(50, 50))
        self.C22, self.L22 = self.Container(x=320, y=270, icon_path=":/Constants/icons/vegoil.png", visibility=False, permanent_visibility=self.veg_oil_P, label_text=self.f3, icon_size=(50, 50))
        self.C23, self.L23 = self.Container(x=540, y=270, icon_path=":/Constants/icons/detergent.png", visibility=False, permanent_visibility=self.detergents_P, label_text=self.g3, icon_size=(50, 50))
        self.C24, self.L24 = self.Container(x=760, y=270, icon_path=":/Constants/icons/formalinicon.png", visibility=False, permanent_visibility=self.formalin_P, label_text=self.h3, icon_size=(50, 50))

###############################################################################################################
        
        self.all_containers = [
            self.C1, self.C2, self.C3, self.C4, self.C5, self.C6, self.C7, self.C8,
            self.C9, self.C10, self.C11, self.C12, self.C13, self.C14, self.C15, self.C16,
            self.C17, self.C18, self.C19, self.C20, self.C21, self.C22, self.C23, self.C24,
        ]
        self.update_visible_containers()
      
        self._button(
            name="REPORTS", icon_path=":/Constants/icons/list.png",
            action=lambda *args:  self.goto_reports(),
            x=150, y=517, width=70, height=50,
            visible=True, bg_color="rgba(60, 179, 113, 0.0)"
        )
        
        self._button(
            name="SETTINGS", icon_path=":/Constants/icons/Settings.png",
            action=lambda *args: self.goto_settings(),
            x=260, y=517, width=70, height=50,
            visible=True, bg_color="rgba(60, 179, 113, 0.0)"
        )
        
        self._button(
            name="TEST", icon_path=":/Constants/icons/testicon.png",
            action=lambda *args: self.openKeypad(),
            x=370, y=517, width=60, height=50,
            visible=True, bg_color="rgba(60, 179, 113, 0.0)"
        )
        
        self._button(
            name="CLEAN", icon_path=":/Constants/icons/cleanbutton.png",
            action=lambda *args: self.show_CLEAN_alert(),
            x=570, y=510, width=90, height=60,
            visible=True, bg_color="rgba(60, 179, 113, 0.0)"
        )
        self._button(
            name="ZERO", icon_path=":/Constants/icons/zeroicon.png",
            action=lambda *args:  self.check_toggle_state(),
            x=680, y=510, width=90, height=60,
            visible=True, bg_color="rgba(60, 179, 113, 0.0)"
        )

        self._button(
            name="POWER", icon_path=":/Constants/icons/poweroff_icon.png",
            action=lambda *args: self.show_quit_alert(),
            x=800, y=510, width=90, height=60,
            visible=True, bg_color="rgba(60, 179, 113, 0.0)"
        )
        self._button(
            name="", icon_path=":/Constants/icons/setprev.png",
            action=lambda *args: self.previous_group(),
            x=10, y=250, width=90, height=60,
            visible=True, bg_color="rgba(60, 179, 113, 0.0)"
        )
        self._button(
            name="", icon_path=":/Constants/icons/setnext.png",
            action=lambda *args: self.next_group(),
            x=930, y=250, width=90, height=60,
            visible=True, bg_color="rgba(60, 179, 113, 0.0)"
        )
        
        self.initializer(
            x=0, y=0, width=1024, height=610,
            
           
        )

        
    def openKeypad(self):
        from Constants.keypad_ID import NumericKeypad
        from PyQt5.QtWidgets import QDialog
        self.controller.start_wave(frequency=650, duration=0.03)
        self.speed1, self.speed2, self.time1, self.time2, self.sample_hold, self.clean_count = self.load_speed_values()
        
        keypad = NumericKeypad(self)
        if keypad.exec_() == QDialog.Accepted:
            value = keypad.getValue()
            self.ID=value
            print(f"Entered value: {self.ID}") 
            self.save_id()
            self.TEST_button()# Print the entered value
    def TEST_button(self, *args):

        speed1_int = int(self.speed1)
        time1_int = int(self.time1) * 100
        speed2_int = int(self.speed2)
        time2_int = int(self.time2) * 100
        sample_hold_int = int(self.sample_hold)

 
        speed1_hex = format(speed1_int, '02X')  
        speed2_hex = format(speed2_int, '02X') 
        time1_hex = format(time1_int, '04X')   
        time2_hex = format(time2_int, '04X') 
        sample_hold_hex = format(sample_hold_int, '04X') 
       

    
        time1_msb = time1_hex[:2] 
        time1_lsb = time1_hex[2:] 
          
        time2_msb = time2_hex[:2] 
        time2_lsb = time2_hex[2:] 
        
        sample_hold_msb = sample_hold_hex[:2] 
        sample_hold_lsb = sample_hold_hex[2:] 

        command = f"25 00 {speed1_hex} {time1_lsb} {time1_msb} 00 00 {speed2_hex} {time2_lsb} {time2_msb} {sample_hold_lsb} {sample_hold_msb}"
   
        self.uart.send_uart_hex(command)
            
            
    def goto_reports(self):
        
        self.parent().setCurrentIndex(1)
        
    def goto_settings(self):
        
        self.parent().setCurrentIndex(2)
        self.uart.send_uart_hex("32 00")
        
        
        
    def save_id(self):
        import json
        # Save current values to JSON
        data = {
            "id": self.ID,
          
        }
        with open(self.CONFIG_FILE, 'w') as file:
            json.dump(data, file)
            
    
    def load_speed_values(self):
        import json
        try:
            with open("settings_config.json", "r") as file:
                data = json.load(file)
                speed1_value = data.get("speed1_value", 0)
                speed2_value = data.get("speed2_value", 0)
                time1_value = data.get("time1_value", 0)
                time2_value = data.get("time2_value", 0)
                sample_hold_value = data.get("sample_hold_value", 0)
                clean_count = data.get("clean_count", 0)
        except FileNotFoundError:
            # Set all values to zero if the file is not found
            speed1_value = speed2_value = time1_value = time2_value = sample_hold_value = clean_count = 0

        return speed1_value, speed2_value, time1_value, time2_value, sample_hold_value, clean_count
    
    


    def load_parameter_status(self):
        import json
        try:
            with open("parameter_status.json", "r") as json_file:
                item_status = json.load(json_file)
                print("Loaded parameter status from JSON.")
        except FileNotFoundError:
            print("No parameter status file found. Initializing all parameters to 'HIDE'.")
            item_status = {}

        for item, status in item_status.items():
            setattr(self, item, status == "VIEW")
        self.S3()
       



            
            
    def S3(self, group_index=1):
        """
        Dynamically manage and display 8 containers at a time, filling visible gaps from subsequent groups.
        """
        # Group containers into sets of 8
        all_containers = [
            (self.C1, self.fat_P),
            (self.C2, self.snf_P),
            (self.C3, self.clr_P),
            (self.C4, self.protein_P),
            (self.C5, self.lactose_P),
            (self.C6, self.salt_P),
            (self.C7, self.water_P),
            (self.C8, self.temp_P),
            (self.C9, self.urea_P),
            (self.C10, self.maltodextrin_P),
            (self.C11, self.sucrose_P),
            (self.C12, self.ammonium_SO4_P),
            (self.C13, self.glucose_P),
            (self.C14, self.sorbitol_P),
            (self.C15, self.melamine_P),
            (self.C16, self.starch_P),
            (self.C17, self.sodium_citrate_P),
            (self.C18, self.sodium_carbonate_P),
            (self.C19, self.sodium_bicarbonate_P),
            (self.C20, self.chemical_emulsifiers_P),
            (self.C21, self.hydrogen_peroxide_P),
            (self.C22, self.veg_oil_P),
            (self.C23, self.detergents_P),
            (self.C24, self.formalin_P),
        ]

        # Calculate the visible containers for the current group
        visible_containers = []
        total_visible_count = 8
        current_index = 0

        for container, visibility_flag in all_containers:
            if visibility_flag:
                if current_index >= (group_index - 1) * total_visible_count:
                    visible_containers.append(container)
                if len(visible_containers) == total_visible_count:
                    break
                current_index += 1

        # Hide all containers initially
        for container, _ in all_containers:
            container.setVisible(False)

        # Position and show the selected containers
        x, y = 100, 40  # Starting position for the first container
        horizontal_spacing = 220  # Horizontal distance between containers
        vertical_spacing = 230  # Vertical distance between rows
        row_count = 4  # Maximum items per row

        for idx, container in enumerate(visible_containers):
            container.setGeometry(
                x + (idx % row_count) * horizontal_spacing,
                y + (idx // row_count) * vertical_spacing,
                container.width(),
                container.height()
            )
            container.setVisible(True)

                
    def update_visible_containers(self):
        """Update the visibility and position of the containers based on the current group."""
        visible_parameters = [c for c, flag in zip(self.all_containers, self.get_visibility_flags()) if flag]
        visible_count = len(visible_parameters)

        # Calculate the start and end indices for the current group
        start_index = self.current_group_index * 8
        end_index = start_index + 8
        current_group_containers = visible_parameters[start_index:end_index]

        # Hide all containers initially
        for container in self.all_containers:
            container.setVisible(False)

        # Position and show the visible containers for the current group
        x, y = 100, 40  # Starting position for the first container
        horizontal_spacing = 220  # Horizontal distance between containers
        vertical_spacing = 230  # Vertical distance between rows
        row_count = 4  # Maximum containers per row

        for idx, container in enumerate(current_group_containers):
            container.setGeometry(
                x + (idx % row_count) * horizontal_spacing,
                y + (idx // row_count) * vertical_spacing,
                container.width(),
                container.height()
            )
            container.setVisible(True)


    def next_group(self):
        """Move to the next group of containers."""
        visible_parameters = [c for c, flag in zip(self.all_containers, self.get_visibility_flags()) if flag]
        visible_count = len(visible_parameters)

        if visible_count > 8:
            max_index = (visible_count - 1) // 8
            if self.current_group_index < max_index:
                self.current_group_index += 1
                self.update_visible_containers()

    def previous_group(self):
        """Move to the previous group of containers."""
        if self.current_group_index > 0:
            self.current_group_index -= 1
            self.update_visible_containers()

    def get_visibility_flags(self):
        """Get visibility flags for all containers."""
        return [
            self.fat_P, self.snf_P, self.clr_P, self.protein_P, self.lactose_P, self.salt_P, self.water_P, self.temp_P,
            self.urea_P, self.maltodextrin_P, self.sucrose_P, self.ammonium_SO4_P, self.glucose_P, self.sorbitol_P,
            self.melamine_P, self.starch_P, self.sodium_citrate_P, self.sodium_carbonate_P, self.sodium_bicarbonate_P,
            self.chemical_emulsifiers_P, self.hydrogen_peroxide_P, self.veg_oil_P, self.detergents_P, self.formalin_P
        ]

    def createContainer(self, x, y, width, height):
        # Create container widget
        container = QWidget(self)
        container.setGeometry(x, y, width, height)
        container.setStyleSheet(f"""
            background-color: rgba(128, 128, 128, 60);
            border-top-left-radius: 140px;  /* Rounded edges */
        border-top-right-radius: 140px;
          
        """)
        container.show()  # Explicitly show the container

      

        # Add heading label
    

        # Debugging: Ensure visibility
        container.raise_()  # Bring to front
        container.show()
        
        
        

    def initializer(self, x, y, width, height):
    # Create container widget
        container = QWidget(self)
        container.setGeometry(x, y, width, height)
        container.setStyleSheet("""
            background-color: rgba(0, 0, 0, 150);
        """)
        container.show()  # Explicitly show the container

        # Add "Please Wait, Initializing..." text
        message_label = QLabel("Please Wait, Initializing...", container)
        message_label.setGeometry(10, 10, width - 20, height - 20)
        message_label.setStyleSheet("""
            color: white;
            font-size: 20px;
            font-family: Arial, sans-serif;
            text-align: center;
        """)
        message_label.setAlignment(Qt.AlignCenter)  # Center-align the text

        # Automatically hide the container after 30 seconds
        timer = QTimer(container)
        timer.setSingleShot(True)
        timer.timeout.connect(container.hide)
        timer.start(1000)  # 30,000 ms = 30 seconds

        # Debugging: Ensure visibility
        container.raise_()  # Bring to front

   



    def Read_temp(self, *args):
        self.uart.send_uart_hex("10 00")
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



    def cleanup_and_quit(self):
        import RPi.GPIO as GPIO
        GPIO.cleanup()  # Clean up GPIO pins
        QApplication.quit()
    def Container(self, x, y, icon_path, label_text, visibility=True, permanent_visibility=True, initial_value=0, icon_size=(40, 40)):

        from PyQt5.QtGui import QPixmap, QPainter, QColor, QDoubleValidator
        from PyQt5.QtWidgets import QLabel, QLineEdit, QWidget
        from PyQt5.QtCore import Qt

        class PermanentInvisibleContainer(QWidget):
            def __init__(self, parent=None):
                super().__init__(parent)
                self._permanent_visibility = True  # Internal state to track permanent visibility

            def setPermanentVisibility(self, permanent_visibility):
                # If already permanently hidden, enforce hiding
                if not self._permanent_visibility and not permanent_visibility:
                    self.hide()
                    return
                # Update the permanent visibility state
                self._permanent_visibility = permanent_visibility
                if not self._permanent_visibility:
                    self.hide()

            def setVisible(self, visible):
                if self._permanent_visibility:
                    super().setVisible(visible)

            def paintEvent(self, event):
                # Explicitly draw the background color
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setBrush(QColor(60, 60, 60, 180))  # Semi-transparent grey (60, 60, 60, 0.6)
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(self.rect(), 10, 10)  # Rounded corners with radius 10

        # Create the custom container
        container = PermanentInvisibleContainer(self)
        container.setPermanentVisibility(permanent_visibility)
        container.setGeometry(x, y, 160, 190)  # Adjust size to fit icon, label, and number

        # Create a QLabel for the icon inside the container
        icon_label = QLabel(container)
        icon_pixmap = QPixmap(icon_path)
        if not icon_pixmap.isNull():
            icon_pixmap = icon_pixmap.scaled(icon_size[0], icon_size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_label.setPixmap(icon_pixmap)
        icon_label.setGeometry((160 - icon_size[0]) // 2, 10, icon_size[0], icon_size[1])  # Center icon horizontally
        icon_label.setStyleSheet("background-color: transparent;")

        # Create the label below the icon
        label = QLabel(label_text, container)
        label_width = 150  # Width of the label for centering
        label_x = (160 - label_width) // 2  # Center the label horizontally
        label.setGeometry(label_x, icon_label.geometry().bottom() + 10, label_width, 20)
        label.setStyleSheet("color: white; background-color: transparent; font-size: 16px; font-weight: 500;")
        label.setAlignment(Qt.AlignCenter)  # Align text to the center horizontally and vertically

        # Create the read-only number input
        number_input = QLineEdit(container)
        number_input.setPlaceholderText("0")
        number_input.setValidator(QDoubleValidator(0.0, 999999.0, 2))
        number_input.setReadOnly(True)
        number_input.setGeometry(0, label.geometry().bottom() + 30, 160, 40)  # Position below label
        number_input.setAlignment(Qt.AlignCenter)
        number_input.setStyleSheet("""
            color: white; 
            background-color: transparent;
            border: none;
            font-weight: 200; 
            font-size: 45px;
        """)

        # Set initial value
        number_input.setText(str(initial_value))

        # Handle initial visibility
        if permanent_visibility:
            container.setVisible(visibility)
        else:
            container.hide()

        return container, number_input


    def update_dash1_labels(self, data):
        if data.startswith('41') and len(data) >= 40:
            if data[6:8] == '10':
                # Extract relevant data excluding the last two characters (LRC)
                relevant_data = data[8:-2]
                self.notification.show_notification("Test Completed Successfully", "success", 3000)
                # Convert hex pairs to decimal and store in a list
                def hex_to_float(byte1, byte2):
                    return round(int(byte2 + byte1, 16) / 100, 2)

                decimal_values = []
                for i in range(0, len(relevant_data), 4):
                    byte1, byte2 = relevant_data[i:i+2], relevant_data[i+2:i+4]
                    if len(byte1) == 2 and len(byte2) == 2:  # Ensure valid pairs
                        try:
                            decimal_values.append(hex_to_float(byte1, byte2))
                        except ValueError:
                            decimal_values.append(None)
                    else:
                        break

                # Update GUI labels if they exist
                labels = [
                    self.L1, self.L2, self.L3, self.L4, self.L5, self.L6, self.L7, self.L8,
                    self.L9, self.L10, self.L11, self.L12, self.L13, self.L14, self.L15, self.L16,
                    self.L17, self.L18, self.L19, self.L20, self.L21, self.L22, self.L23, self.L24,
                ]

                for label, value in zip(labels, decimal_values):
                    if label is not None and value is not None:
                        label.setText(f"{value:.2f}")
    def update_calibrated_values(self):

        import os
        self.R1, self.R2, self.R3, self.R4, self.R5,self.R6, self.R7,self.R8 = self.load_calibrated_values()

        self.L1.setText(str(self.R1))
        self.L2.setText(str(self.R2))
        self.L3.setText(str(self.R3))
        self.L4.setText(str(self.R4))
        self.L5.setText(str(self.R5))
        self.L6.setText(str(self.R6))
        self.L7.setText(str(self.R7))
        self.L8.setText(str(self.R8))
        if os.path.exists("calibration_values.json"):
            os.remove("calibration_values.json")
            self.notification.show_notification("Loading Calibration Result", "success", 3000)
            
    def load_calibrated_values(self):
        import json
        try:
            with open("calibration_values.json", "r") as file:
                data = json.load(file)
                a = data.get("fat", 0)
                b = data.get("snf", 0)
                c = data.get("clr", 0)
                d = data.get("protein", 0)
                e = data.get("salts", 0)
                f = data.get("lactose", 0)
                g = data.get("water", 0)
                h = data.get("temp", 0)
            
        except FileNotFoundError:
            # Set all values to zero if the file is not found
            a = b = c = d = e = f = g = h = 0
            
            
        

        return a, b, c, d, e, f, g, h
    def resizeEvent(self, event):
        from PyQt5.QtCore import Qt
        
        if hasattr(self, 'original_image'):
            self.background_image = self.original_image.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        self.update()
        
    
    
   
   

    def show_CLEAN_alert(self):
        from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QDialog,QHBoxLayout
        from PyQt5.QtCore import Qt
        self.controller.start_wave(frequency=650, duration=0.03)
        self.speed1, self.speed2, self.time1, self.time2, self.sample_hold, self.clean_count = self.load_speed_values()
        # Create a dialog without any default window buttons or frame
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Cleaning")
        dialog.setFixedSize(400, 250)

        # Remove all window decorations and add rounded corners
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        # Common stylesheet with additional decorations
        button_stylesheet = """
    QDialog {
        border: 2px solid #333;
        border-radius: 0px;
        background-color: #f0f0f0;
    }
    QLabel {
        border: none;
        color: #333;
        font-size: 18px; /* Increase font size */
        font-family: Arial, sans-serif;
        background-color: transparent;
        text-align: center;
    }
    QPushButton {
        color: white;
        border-radius: 5px;
        padding: 10px;
        font-size: 14px; /* Base font size for buttons */
        font-family: Arial, sans-serif;
    }
    QPushButton#Daily {
        background-color: rgba(5, 11, 92, 0.8);
        border: none;
        min-height: 50px; /* Increase button height */
        font-size: 16px; /* Increase font size for Daily button */
    }
    QPushButton#Weekly {
        background-color: rgba(3, 131, 3, 1);
        border: none;
        min-height: 50px; /* Increase button height */
        font-size: 16px; /* Increase font size for Weekly button */
    }
    QPushButton#Close {
        background-color: red;
        color: white;
        border: none;
        font-weight: bold;
        border-radius: 10px;
        width: 15px;
        height: 15px;
    }
    QPushButton#Close:hover {
        background-color: darkred;
    }
"""



        # Create a label with custom alignment and font
        label = QLabel("Please select an option for cleaning.", dialog)
        label.setStyleSheet("""
    QLabel {
        border: none;
        color: #333;
        font-size: 18px; /* Increase font size */
        font-family: Arial, sans-serif;
        background-color: transparent; /* Make background transparent */
    }
""")
        label.setAlignment(Qt.AlignCenter)

        # Create two buttons for cleaning options
        daily_button = QPushButton("Daily", dialog)
        weekly_button = QPushButton("Weekly", dialog)

        # Create a custom close button
        close_button = QPushButton("X", dialog)
        close_button.setObjectName("Close")
        close_button.clicked.connect(dialog.close)
    
        # Set object names to apply different styles
        daily_button.setObjectName("Daily")
        weekly_button.setObjectName("Weekly")

        # Apply stylesheet to dialog
        dialog.setStyleSheet(button_stylesheet)

        # Connect buttons to actions and auto-close the dialog when clicked
        daily_button.clicked.connect(lambda: self.Clean_daily(dialog))
        weekly_button.clicked.connect(lambda: self.Clean_weekly(dialog))

        # Layout for the close button
        top_layout = QHBoxLayout()
        top_layout.addStretch(1)
        top_layout.addWidget(close_button)

        # Main layout
        layout = QVBoxLayout()
        layout.addLayout(top_layout)  # Add the custom close button at the top
        layout.addWidget(label)
        layout.addWidget(daily_button)
        layout.addWidget(weekly_button)

        dialog.setLayout(layout)
        dialog.exec_()
    def send_clean_command(self, mode, dialog, *args):
    # Convert time1 to an integer
        clean_count_int = int(self.clean_count)
        
        # Convert time1 to a 4-digit hexadecimal string
        clean_count_hex = format(clean_count_int, '04X')
        
        # Split the hexadecimal string into MSB and LSB
        clean_count_msb = clean_count_hex[:2]
        clean_count_lsb = clean_count_hex[2:]
        
        # Format the command based on the mode
        command = f"1A {mode} {clean_count_lsb} {clean_count_msb}"
        
        # Send the command via UART
        self.uart.send_uart_hex(command)
        
        # Auto-close the dialog after sending the command
        dialog.accept()

    def Clean_daily(self, dialog, *args):
     
        self.send_clean_command("00", dialog)

    def Clean_weekly(self, dialog, *args):
      
        self.send_clean_command("01", dialog)
    
    def show_quit_alert(self):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
        from PyQt5.QtCore import Qt
        import os
        self.controller.start_wave(frequency=650, duration=0.03)
        dialog = QDialog(self)
        dialog.setWindowTitle("Quit Confirmation")
        dialog.setFixedSize(400, 250)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        # Common stylesheet
        dialog_stylesheet = """
        QDialog {
                border: 2px solid #333;
                border-radius: 0px;
                background-color: #f0f0f0;
        }
        QLabel {
                border: none;
                color: #333;
                font-size: 18px;
                font-family: Arial, sans-serif;
                background-color: transparent;
                text-align: center;
        }
        QPushButton {
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-family: Arial, sans-serif;
        }
        QPushButton#Shutdown {
                background-color: rgba(5, 11, 92, 0.8);
                border: none;
                min-height: 50px;
                font-size: 16px;
        }
        QPushButton#Restart {
                background-color: rgba(255, 165, 0, 1);
                border: none;
                min-height: 50px;
                font-size: 16px;
        }
        QPushButton#Cancel {
                background-color: red;
                border: none;
                font-weight: bold;
                border-radius: 10px;
                min-height: 50px;
                font-size: 16px;
        }
        QPushButton#Close {
                background-color: red;
                color: white;
                border: none;
                font-weight: bold;
                border-radius: 10px;
                width: 15px;
                height: 15px;
        }
        QPushButton#Close:hover {
                background-color: darkred;
        }
        """
        dialog.setStyleSheet(dialog_stylesheet)

        # Create widgets
        label = QLabel("Do you really want to Shut down?", dialog)
        label.setAlignment(Qt.AlignCenter)

        Shutdown = QPushButton("Shutdown", dialog)
        Restart = QPushButton("Restart", dialog)
        Cancel = QPushButton("Cancel", dialog)
        close_button = QPushButton("X", dialog)
        close_button.setObjectName("Close")

        # Set object names for buttons
        Shutdown.setObjectName("Shutdown")
        Restart.setObjectName("Restart")
        Cancel.setObjectName("Cancel")

        # Set button widths
        button_width = 100
        Shutdown.setFixedWidth(button_width)
        Restart.setFixedWidth(button_width)
        Cancel.setFixedWidth(button_width)

        # Button actions
        close_button.clicked.connect(dialog.close)
        Cancel.clicked.connect(dialog.close)
        Shutdown.clicked.connect(self.cleanup_and_quit)
        Restart.clicked.connect(self.restart_application)

        # Layout for the close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_button)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(Shutdown)
        button_layout.addSpacing(10)  # Space between the buttons
        button_layout.addWidget(Restart)
        button_layout.addSpacing(10)  # Space between the buttons
        button_layout.addWidget(Cancel)

        # Center the buttons
        button_layout.addStretch(1)
        button_layout.insertStretch(0, 1)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(close_layout)
        main_layout.addWidget(label)
        main_layout.addLayout(button_layout)

        dialog.setLayout(main_layout)
        dialog.exec_()

    # Ensure `self.shutdown_pi` and `self.restart_application` methods are implemented.
    def restart_application(self):
        os.system("sudo reboot")

    def shutdown_pi(self):
        os.system("sudo shutdown -h now")
    def start_usb_monitor(self):
        class USBMonitorWorker(QObject):
            usb_added = pyqtSignal(str)  # Signal for USB device addition
            usb_removed = pyqtSignal(str)  # Signal for USB device removal

            def start_monitoring(self):
                context = pyudev.Context()
                monitor = pyudev.Monitor.from_netlink(context)
                monitor.filter_by(subsystem='usb')
                for device in iter(monitor.poll, None):
                    if device.action == 'add':
                        self.usb_added.emit(device.device_node)  # Emit device added
                    elif device.action == 'remove':
                        self.usb_removed.emit(device.device_node)  # Emit device removed

        self.thread = QThread()  # Thread instance
        self.worker = USBMonitorWorker()  # Worker instance
        self.worker.moveToThread(self.thread)

        # Connect signals
        self.worker.usb_added.connect(
            lambda device_node: self.notification.show_notification("USB device Detected", "success", 3000) or print(f"USB device attached: {device_node}")
        )
        self.worker.usb_removed.connect(
            lambda device_node: self.notification.show_notification("USB device Removed", "error", 3000) or print(f"USB device detached: {device_node}")
        )
        self.thread.started.connect(self.worker.start_monitoring)

        # Start monitoring
        self.thread.start()
        
        
    def check_toggle_state(self):
        
        
        if os.path.exists(self.toggle_state_file):  # Check if the file exists
            try:
                with open(self.toggle_state_file, "r") as file:
                    toggle_state = json.load(file)  # Load JSON data
                    
                    # Assuming toggle state is stored under a key, e.g., "state"
                    state = toggle_state.get("toggle_state", None)
                    
                    if state == 0:
                     
                        self.disable_cursor()
                    
                    elif state == 2:
                   
                    
                        self.enable_cursor()
                     
                    else:
                        print(f"Unknown state: {state}")
            except json.JSONDecodeError:
                print("Error: The JSON file is corrupted.")
        else:
            print(f"Error: {self.toggle_state_file} does not exist.")

# Call the function to check the toggle state

    def enable_cursor(self):
        """Enable the mouse cursor globally."""
        QApplication.restoreOverrideCursor()
        print("Mouse cursor enabled.")

    def disable_cursor(self):
        """Disable the mouse cursor globally."""
        QApplication.setOverrideCursor(Qt.BlankCursor)
        print("Mouse cursor disabled.")
        

    
            

    def paintEvent(self, event):
  
        from PyQt5.QtGui import  QPainter ,QLinearGradient, QColor

        painter = QPainter(self)

        # Draw the background image
        if hasattr(self, 'background_image') and not self.background_image.isNull():
            painter.drawImage(self.rect(), self.background_image)

        # Add a gradient: fully black from bottom to 3/4, then gradual transparency
        gradient = QLinearGradient(0, self.height(), 0, self.height() // 4)

        # Full black from bottom (0%) to 3/4 (75%)
        gradient.setColorAt(1, QColor(40, 40, 40, 255))  # Fully black at the bottom
        gradient.setColorAt(0.5, QColor(40, 40, 40, 255))  # Fully black until 3/4

        # Gradual transparency from 3/4 (75%) to top (25%)
        gradient.setColorAt(1, QColor(100, 100, 100, 100))  # Fully transparent at the top 1/4

        # Apply the gradient overlay
        painter.fillRect(self.rect(), gradient)
        logo_image_path = ":/Constants/images/companylogo.png"  # Change to your actual image path
        #logo_image = QImage(logo_image_path)
        
       # if not logo_image.isNull():
           # logo_image = logo_image.scaled(220, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            #painter.drawImage(680, 50, logo_image)  # Position the logo at (50, 50)

        super().paintEvent(event)
