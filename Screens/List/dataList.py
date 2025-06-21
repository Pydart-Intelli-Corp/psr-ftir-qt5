from PyQt5.QtWidgets import (
    QVBoxLayout, QWidget, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QScrollArea, QSpacerItem,QFileDialog, QMessageBox,QSizePolicy, QDialog, QDateEdit,QCalendarWidget,QListWidget, QPushButton,QApplication, QHBoxLayout,QTimeEdit,QMenu,QToolButton,QAction,QSpinBox
)
from PyQt5.QtCore import QDate, Qt, pyqtSignal,QTime,QTimer,QObject,QThread
from PyQt5.QtGui import QFontDatabase, QFont, QIcon
import os
import io
import csv
from datetime import datetime, timedelta
import json
import sys
from Constants.Buttons.save_green_button import SaveGreenButton
from Constants.MainNotification import Notification
from Controls.gpio_control import GPIOController
from Controls.uart_control import UARTcontrol
import resources_rc
import threading
import pyudev





class DataList(QWidget):
    MRST = "mr_start_time.json"
    MRND = "mr_end__time.json"
    EVST = "ev_start_time.json"
    EVND = "ev_end__time.json"
    notify_title_bar = pyqtSignal(str, str, str, str, str)

    def __init__(self, text: str, parent=None, uart_thread=None):
        super().__init__(parent=parent)
        self.setWindowState(Qt.WindowFullScreen)
        self.uart_thread = uart_thread
     
        self.uart = UARTcontrol()

        self.previous_row_saved = True
        self.csv_file_path = "Reports.csv"
        self.json_file_path = "parameter_status.json"# Save the file as Reports.csv
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)

        # Load custom font
        font_id = QFontDatabase.addApplicationFont(":/Constants/Fonts/JosefinSans-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else 'Arial'
        spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        main_layout.addSpacerItem(spacer)
        self.mrstj=None
        self.mrndj=None
        self.evstj=None
        self.evndj=None
        # Add heading label
        self.heading_label = QLabel("REPORTS", self)
        font = QFont(font_family, 13, QFont.Bold)
        self.heading_label.setFont(font)
        self.heading_label.setStyleSheet("color: black; font-weight: bold;")
        self.heading_label.setContentsMargins(90, 0, 0, 0)
        main_layout.addWidget(self.heading_label)
        spacer = QSpacerItem(50, 50, QSizePolicy.Minimum, QSizePolicy.Fixed)
        main_layout.addSpacerItem(spacer)
        self.notification=Notification(self)

        # Define all parameter headings, adding two new columns
        self.parameters = self.load_parameters_from_json()
        
        #self.parameters = ["Date", "Time", "ID", "Fat", "SNF", "CLR", "Protein", "Water", "Temperature", "Urea", "Formalin", "urea", "Ammonium sulphate", "Boric acid", "Caustic soda", "Benzoic acid", "Salicylic acid", "Hydrogen peroxide", "starch", "Melamine", "Sucrose", "Maltodextrin", "Vegetable oils", "glucose", "Sodium citrate", "Sorbitol", "Sodium chloride"]

        
        # Create a table widget for parameters, set as scrollable
        self.table_widget = QTableWidget(0, len(self.parameters), self)  # Start with 0 rows
        self.table_widget.setHorizontalHeaderLabels(self.parameters)
        
        # Make the columns adjustable
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_widget.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)

        # Enable scrollbars for both directions
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Set up a scroll area for the table
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.table_widget)
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)

        # Load data from CSV file
        self.load_csv_data()
        self._button(
            name="", icon_path=":/Constants/icons/setprev.png",
            action=lambda *args: self.goto_HOME(),
            x=10, y=10, width=90, height=60,
            visible=True, bg_color="rgba(60, 179, 113, 0.0)"
        )
      
        self.button(name=" Clear", icon_path=":/Constants/icons/clear.png", action=lambda *args: self.show_Clear_alert(),x=880,y=20, width=90, height=40,visible=True,bg_color="rgba(255, 0, 0, 1)")
        self.button(name=" Filter", icon_path=":/Constants/icons/filter.png", action=lambda *args: self.show_filter_alert(), x=770,y=20, width=90, height=40,visible=True,bg_color="rgba(3, 131, 3, 1)")
        
        self.button(name=" Export", icon_path=":/Constants/icons/export.png", action=lambda *args: self.show_EXPORT_alert(), x=660,y=20, width=90, height=40,visible=True,bg_color="rgba(26, 5, 114, 1)")
        self.button(name=" Refresh", icon_path=":/Constants/icons/refresh.png", action=lambda *args: self.refresh_table(), x=550,y=20, width=90, height=40,visible=True,bg_color="rgba(32, 123, 130, 1)")
    def goto_HOME(self):
        
        self.parent().setCurrentIndex(0)
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
    def load_parameters_from_json(self):
        """
        Load the parameters from the JSON file and filter based on 'VIEW'.
        Ensure 'Date', 'Time', and 'ID' are always included.
        """
        default_parameters = ["Date", "Time", "ID"]  # Always included
        try:
            if os.path.exists(self.json_file_path):
                with open(self.json_file_path, "r") as json_file:
                    json_data = json.load(json_file)
                parameters = [
                    key[:-2] for key, value in json_data.items() if value == "VIEW"
                ]
                return default_parameters + parameters
            else:
                print(f"JSON file '{self.json_file_path}' not found.")
        except Exception as e:
            print(f"Error loading JSON file: {e}")

        # Fallback to default if loading fails
        return default_parameters
    
    
    def show_EXPORT_alert(self):
        
        # Create a dialog without default window buttons
        dialog = QDialog(self)
        dialog.setWindowTitle("Export Alert")
        dialog.setFixedSize(300, 180)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        # Common stylesheet with specific button colors
        dialog_stylesheet = """
            QDialog {
                border: 2px solid #333;
                border-radius: 0px;
                background-color: #d3d3d3; /* Light grey */
            }
            QLabel {
                color: #333;
                font-size: 18px;
                font-family: Arial, sans-serif;
                text-align: center;
                border: none;
                background-color: transparent;
            }
            QPushButton {
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
                font-family: Arial, sans-serif;
            }
            QPushButton#USB {
                background-color: rgba(5, 11, 92, 0.8); /* Dark blue */
                border: none;
                font-size: 16px;
            }
            QPushButton#UART {
                background-color: rgba(3, 131, 3, 1); /* Grey */
                border: none;
                font-size: 16px;
            }
            QPushButton#WIFI {
                background-color: rgba(32, 123, 130, 1); /* Orange */
                border: none;
                font-size: 16px;
            }
            QPushButton#Close {
                background-color: red;
                color: white;
                border: none;
                font-weight: bold;
                border-radius: 10px;
                width: 10px;
                height: 10px;
            }
            QPushButton#Close:hover {
                background-color: darkred;
                border: none;
            }
        """
        dialog.setStyleSheet(dialog_stylesheet)

        # Create widgets
        label = QLabel("Select export option", dialog)
        label.setAlignment(Qt.AlignCenter)

        # Create buttons with updated labels
        USB = QPushButton("USB", dialog)
        UART = QPushButton("UART", dialog)
        WIFI = QPushButton("WIFI", dialog)
        close_button = QPushButton("X", dialog)
        close_button.setObjectName("Close")

        # Set object names for buttons
        USB.setObjectName("USB")
        UART.setObjectName("UART")
        WIFI.setObjectName("WIFI")

        # Increase button width
        button_width = 80
        USB.setFixedWidth(button_width)
        UART.setFixedWidth(button_width)
        WIFI.setFixedWidth(button_width)

        # Button actions
        close_button.clicked.connect(dialog.close)

        def handle_USB_click():
            
            self.save_to_usb()
            dialog.close()

        def handle_UART_click():
            self.export_via_uart()
            dialog.close()

        def handle_WIFI_click():
            self.export_via_uart()
            dialog.close()

        USB.clicked.connect(handle_USB_click)
        UART.clicked.connect(handle_UART_click)
        WIFI.clicked.connect(handle_WIFI_click)

        # Layout for the close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_button)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(USB)
        button_layout.addSpacing(10)
        button_layout.addWidget(UART)
        button_layout.addSpacing(10)
        button_layout.addWidget(WIFI)
        button_layout.addStretch()

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(close_layout)
        main_layout.addWidget(label)
        main_layout.addLayout(button_layout)

        dialog.setLayout(main_layout)
        dialog.exec_()

                    
    def show_filter_alert(self):
        
        # Create a dialog without default window buttons
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Filter")
        dialog.setFixedSize(300, 180)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        # Common stylesheet with specific button colors
        dialog_stylesheet = """
            QDialog {
                border: 2px solid #333;
                border-radius: 0px;
                background-color: #d3d3d3; /* Light grey */
            }
            QLabel {
                color: #333;
                font-size: 18px;
                font-family: Arial, sans-serif;
                text-align: center;
                border: none;
                background-color: transparent;
            }
            QPushButton {
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
                font-family: Arial, sans-serif;
            }
            QPushButton#Time {
                background-color: rgba(5, 11, 92, 0.8); /* Dark blue */
                border: none;
                font-size: 16px;
            }
            QPushButton#Date {
                background-color: rgba(3, 131, 3, 1); /* Grey */
                border: none;
                font-size: 16px;
            }
            QPushButton#ID {
                background-color: rgba(32, 123, 130, 1); /* Orange */
                border: none;
                font-size: 16px;
            }
            QPushButton#Close {
                background-color: red;
                color: white;
                border: none;
                font-weight: bold;
                border-radius: 10px;
                width: 10px;
                height: 10px;
            }
            QPushButton#Close:hover {
                background-color: darkred;
                border: none;
            }
        """
        dialog.setStyleSheet(dialog_stylesheet)

        # Create widgets
        label = QLabel("Select Filter", dialog)
        label.setAlignment(Qt.AlignCenter)

        # Create buttons
        Time = QPushButton("Time", dialog)
        Date = QPushButton("Date", dialog)
        ID = QPushButton("ID", dialog)
        close_button = QPushButton("X", dialog)
        close_button.setObjectName("Close")

        # Set object names for buttons
        Time.setObjectName("Time")
        Date.setObjectName("Date")
        ID.setObjectName("ID")

        # Increase button width
        button_width = 80
        Time.setFixedWidth(button_width)
        Date.setFixedWidth(button_width)
        ID.setFixedWidth(button_width)

        # Button actions
        close_button.clicked.connect(dialog.close)

        def handle_time_click():
            
            self.load_shift_values()
            self.show_TIME_alert()
            dialog.close()
        def handle_DATE_click():
            
          
            self.DATE_filter_table()
            dialog.close()
            
        def handle_IDD_click():
            
          
            self.setup_filter_ui()
            dialog.close()
            
            

        Time.clicked.connect(handle_time_click)
        Date.clicked.connect(handle_DATE_click)
        ID.clicked.connect(handle_IDD_click)


        # Layout for the close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_button)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(Time)
        button_layout.addSpacing(10)
        button_layout.addWidget(Date)
        button_layout.addSpacing(10)
        button_layout.addWidget(ID)
        button_layout.addStretch()

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(close_layout)
        main_layout.addWidget(label)
        main_layout.addLayout(button_layout)

        dialog.setLayout(main_layout)
        dialog.exec_()

    




        
    def show_TIME_alert(self):
        # Create a dialog without default window buttons
        dialog = QDialog(self)
        dialog.setWindowTitle("Shift select")
        dialog.setFixedSize(300, 180)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        # Common stylesheet with specific button colors
        dialog_stylesheet = """
            QDialog {
                border: 2px solid #333;
                border-radius: 0px;
                background-color: #d3d3d3; /* Light grey */
            }
            QLabel {
                color: #333;
                font-size: 16px;
                font-family: Arial, sans-serif;
                text-align: center;
                border: none;
                background-color: transparent;
            }
            QPushButton {
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-family: Arial, sans-serif;
            }
            QPushButton#Morning {
                background-color: rgba(5, 11, 92, 0.8); /* Dark blue */
                border: none;
            }
            QPushButton#Evening {
                background-color: rgba(3, 131, 3, 1); /* Grey */
                border: none;
            }
            QPushButton#Close {
                background-color: red;
                color: white;
                border: none;
                font-weight: bold;
                border-radius: 10px;
                width: 10px;
                height: 10px;
            }
            QPushButton#Close:hover {
                background-color: darkred;
                border: none;
            }
        """
        dialog.setStyleSheet(dialog_stylesheet)

        # Create widgets
        label = QLabel("Select Shift", dialog)
        label.setAlignment(Qt.AlignCenter)

        # Create buttons
        Morning = QPushButton("Morning", dialog)
        Evening = QPushButton("Evening", dialog)
        close_button = QPushButton("X", dialog)
        close_button.setObjectName("Close")

        # Set object names for buttons
        Morning.setObjectName("Morning")
        Evening.setObjectName("Evening")

        # Increase button width
        button_width = 80
        Morning.setFixedWidth(button_width)
        Evening.setFixedWidth(button_width)
        def handle_MRNG_click():
            
            self.filter_table_by_time(self.mrstj, self.mrndj)
            
            dialog.close()
            
        def handle_EVNG_click():
            
            self.filter_table_by_time(self.evstj, self.evndj)
            
            dialog.close()
        # Button actions
        close_button.clicked.connect(dialog.close)
        Morning.clicked.connect(handle_MRNG_click)
        
        Evening.clicked.connect(handle_EVNG_click)
        Evening.clicked.connect(dialog.close)


        # Layout for the close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_button)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(Morning)
        button_layout.addSpacing(10)
        button_layout.addWidget(Evening)
        button_layout.addStretch()

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(close_layout)
        main_layout.addWidget(label)
        main_layout.addLayout(button_layout)

        dialog.setLayout(main_layout)
        dialog.exec_()
        
    def show_Clear_alert(self):
        
        # Create a dialog without default window buttons
        dialog = QDialog(self)
        dialog.setWindowTitle("Clear confirmation")
        dialog.setFixedSize(300, 180)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        # Common stylesheet with specific button colors
        dialog_stylesheet = """
            QDialog {
                border: 2px solid #333;
                border-radius: 0px;
                background-color: #d3d3d3; /* Light grey */
            }
            QLabel {
                color: #333;
                font-size: 16px;
                font-family: Arial, sans-serif;
                text-align: center;
                border: none;
                background-color: transparent;
            }
            QPushButton {
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-family: Arial, sans-serif;
            }
            QPushButton#Yes {
                
                background-color: rgba(3, 131, 3, 1); /* Grey */
                border: none;
            }
            QPushButton#No {
                background-color: rgba(5, 11, 92, 0.8); /* Dark blue */
                border: none;
            }
            QPushButton#Close {
                background-color: red;
                color: white;
                border: none;
                font-weight: bold;
                border-radius: 10px;
                width: 10px;
                height: 10px;
            }
            QPushButton#Close:hover {
                background-color: darkred;
                border: none;
            }
        """
        dialog.setStyleSheet(dialog_stylesheet)

        # Create widgets
        label = QLabel("Do you really want to clear all?", dialog)
        label.setAlignment(Qt.AlignCenter)

        # Create buttons
        Yes = QPushButton("Yes", dialog)
        No = QPushButton("No", dialog)
        close_button = QPushButton("X", dialog)
        close_button.setObjectName("Close")

        # Set object names for buttons
        Yes.setObjectName("Yes")
        No.setObjectName("No")

        # Increase button width
        button_width = 80
        Yes.setFixedWidth(button_width)
        No.setFixedWidth(button_width)
        def handle_no_click():
            
        
            dialog.close()
        # Button actions
        close_button.clicked.connect(dialog.close)
        Yes.clicked.connect(lambda: self.clear_table())
        Yes.clicked.connect(dialog.close)
       
        No.clicked.connect(handle_no_click)


        # Layout for the close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_button)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(Yes)
        button_layout.addSpacing(10)
        button_layout.addWidget(No)
        button_layout.addStretch()

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(close_layout)
        main_layout.addWidget(label)
        main_layout.addLayout(button_layout)

        dialog.setLayout(main_layout)
        dialog.exec_()
     
     
     
        
    def LOAD_ID(self):
        try:
            with open("id.json", "r") as file:
                data = json.load(file)
                id = data.get("id", 0)
           
        except FileNotFoundError:
            # Set all values to zero if the file is not found
            id =  0

        return id
    

    
    def setup_filter_ui(self):
        """Create a floating dialog box for filtering IDs with improved styling and an X close button."""
        # Create the dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Select ID")
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dialog.setFixedSize(300, 400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: rgba(255, 255, 255, 0.95); /* Light floating effect */
                border: 2px solid #5D9CEC; /* Blue border */
                border-radius: 12px;
            }
            QLabel {
                font-size: 18px; /* Increased font size */
                font-weight: bold;
                color: #333;
                margin: 10px 0;
            }
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 5px;
                font-size: 20px; /* Increased font size */
                color: #333;
                background-color: rgba(240, 240, 240, 1);
            }
            QListWidget::item:selected {
                background-color: #5D9CEC;
                color: white;
            }
            QToolButton {
                background-color: red;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                width: 24px;
                height: 24px;
            }
            QToolButton:hover {
                background-color: darkred;
            }
        """)

        # Title label
        title_label = QLabel("Select ID", dialog)
        title_label.setAlignment(Qt.AlignCenter)

        # Create a list widget for IDs
        id_list_widget = QListWidget(dialog)
        id_list_widget.setFixedHeight(300)

        # Add "All" option and unique IDs from the table
        id_list_widget.addItem("All")
        ids = set()
        for row in range(self.table_widget.rowCount()):
            id_item = self.table_widget.item(row, 2)  # Assuming "ID" is in the 3rd column
            if id_item:
                ids.add(id_item.text())
        id_list_widget.addItems(sorted(ids))

        # Filter action on item click
        def apply_filter(item):
            
            selected_id = item.text()
            for row in range(self.table_widget.rowCount()):
                is_match = (selected_id == "All") or (self.table_widget.item(row, 2).text() == selected_id)
                self.table_widget.setRowHidden(row, not is_match)
            dialog.close()  # Close the dialog after selection
        
        id_list_widget.itemClicked.connect(apply_filter)
        
        # Create a floating X button for closing the dialog
        close_button = QToolButton(dialog)
        close_button.setText("X")
        close_button.setToolTip("Close")
        close_button.clicked.connect(dialog.close)
        close_button.setGeometry(270, 10, 24, 24)  # Position in the top-right corner

        # Layout for the dialog
        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(id_list_widget)

        dialog.setLayout(layout)

        # Show the dialog
        dialog.exec_()
    def update_table(self, data):
        """Update the table with the received data and append a new row."""
        if data.startswith('41'):
            third_position_data = data[6:8]

            if third_position_data == '10' and len(data) >= 40:
                self.id = self.LOAD_ID()
                
       
                # Extract values for each parameter
                def hex_to_float(byte2, byte1):
                    return round(int(byte2 + byte1, 16) / 100, 2)

                fat = hex_to_float(data[10:12], data[8:10])
                snf = hex_to_float(data[14:16], data[12:14])
                clr = hex_to_float(data[18:20], data[16:18])
                protein = hex_to_float(data[22:24], data[20:22])
                lactose = hex_to_float(data[26:28], data[24:26])
                salt = hex_to_float(data[30:32], data[28:30])
                water = hex_to_float(data[34:36], data[32:34])
                temp = hex_to_float(data[38:40], data[36:38])
                
                urea = hex_to_float(data[42:44], data[40:42])
                maltodextrin = hex_to_float(data[46:48], data[44:46])
                sucrose = hex_to_float(data[50:52], data[48:50])
                ammonium_SO4 = hex_to_float(data[54:56], data[52:54])
                glucose = hex_to_float(data[58:60], data[56:58])
                sorbitol = hex_to_float(data[62:64], data[60:62])
                melamine = hex_to_float(data[66:68], data[64:66])
                starch  = hex_to_float(data[70:72], data[68:70])
                
                melamine = hex_to_float(data[74:76], data[72:74])
                Sucrose = hex_to_float(data[78:80], data[76:78])
                Maltodextrin = hex_to_float(data[82:84], data[80:82])
                Vegetable_Oils = hex_to_float(data[86:88], data[84:86])
                glucose = hex_to_float(data[90:92], data[88:90])
                Sodium_Citrate = hex_to_float(data[94:96], data[92:94])
                Sorbitol = hex_to_float(data[98:100], data[96:98])
                Sodium_Chloride = hex_to_float(data[102:104], data[100:102])
         
                
                # Append row to the table and save to CSV
                self.append_row_and_save_csv([
                    self.id, fat, snf, clr, protein,
                    lactose, salt, water, temp,urea,maltodextrin,sucrose
                    ,ammonium_SO4,glucose, sorbitol,melamine
                    ,starch ,melamine,Sucrose,Maltodextrin,Vegetable_Oils,glucose,Sodium_Citrate,Sorbitol
                    ,Sodium_Chloride
                ])
    def refresh_table(self):
        
        """Refresh the table by reloading the data from the CSV file."""
        self.clear_table(save=False)  # Clear table without saving
        self.load_csv_data()  # Reload data from CSV file

    def button(self, name, icon_path,bg_color, action, x=60, y=457, width=170, height=60, visible=True,):
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
    def clear_table(self, save=True):
        
        """Clear all the table values and optionally update the CSV file."""
        self.table_widget.setRowCount(0)  # Remove all rows
        if save:
            self.save_table_to_csv()  # Save the empty table to the CSV file
           
    def filter_table_by_time(self, start_time: QTime, end_time: QTime):
        """Filter table rows based on the given start and end time."""
        for row in range(self.table_widget.rowCount()):
            time_item = self.table_widget.item(row, 1)  # Assuming the time column is at index 1
            if time_item:
                row_time = QTime.fromString(time_item.text(), "hh:mm AP")  # Adjust format to your time representation
                if row_time.isValid():
                    # Hide the row if the time is not in range
                    if not (start_time <= row_time <= end_time):
                        self.table_widget.setRowHidden(row, True)
                    else:
                        self.table_widget.setRowHidden(row, False)
                        
    def export_via_uart(self):
        """
        Export the current table data displayed to UART as a CSV file content,
        excluding the filename.
        """
        try:
            # Collect the table data into a list of rows
            csv_data = []
            csv_data.append(self.parameters)  # Add the header row

            # Gather only the visible rows
            for row in range(self.table_widget.rowCount()):
                if not self.table_widget.isRowHidden(row):  # Include only visible rows
                    row_data = [
                        self.table_widget.item(row, col).text() if self.table_widget.item(row, col) else ""
                        for col in range(self.table_widget.columnCount())
                    ]
                    csv_data.append(row_data)

            # Convert the table data to CSV format (as a single string)
            csv_string = '\n'.join([','.join(row) for row in csv_data])

            # Send the CSV string using the UART control class
            self.uart.send_csv(csv_string)

            # Notify the user of success
            self.notification.show_notification("Report exported successfully via UART", "success", 3000)
        except Exception as e:
            # Handle errors and notify the user
            self.notification.show_notification(f"Error exporting table via UART: {str(e)}", "error", 3000)

    def list_usb_drives(self):
        """
        Detect USB drives mounted under `/media/ftir/`.
        """
        media_path = "/media/ftir/"
        detected_drives = []

        try:
            if os.path.exists(media_path):
                detected_drives = [
                    os.path.join(media_path, d)
                    for d in os.listdir(media_path)
                    if os.path.ismount(os.path.join(media_path, d)) or os.path.isdir(os.path.join(media_path, d))
                ]
            print("Detected USB drives:", detected_drives)  # Debugging
            return detected_drives
        except Exception as e:
            print("Error detecting USB drives:", e)  # Debugging
            QMessageBox.critical(self, "Error", f"Error while detecting USB drives: {e}")
        return []


    def save_to_usb(self):
        """
        Save the currently displayed table data to a USB drive, defaulting to 'Report.csv'.
        If the file exists, append a number to the filename (e.g., Report1.csv, Report2.csv).
        """
        usb_drives = self.list_usb_drives()

        if not usb_drives:
            
            self.notification.show_notification("USB Drive not found", "error", 3000)
            return

        # Default file name
        base_name = "Report"
        extension = ".csv"
        save_path = os.path.join(usb_drives[0], f"{base_name}{extension}")

        # Check if a file with the default name exists and generate a unique name
        counter = 1
        while os.path.exists(save_path):
            save_path = os.path.join(usb_drives[0], f"{base_name}{counter}{extension}")
            counter += 1

        try:
            # Save only the visible rows in the table
            with open(save_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(self.parameters)  # Write the header

                for row in range(self.table_widget.rowCount()):
                    # Check if the row is hidden
                    if not self.table_widget.isRowHidden(row):
                        row_data = [
                            self.table_widget.item(row, col).text() if self.table_widget.item(row, col) else ""
                            for col in range(self.table_widget.columnCount())
                        ]
                        writer.writerow(row_data)

            self.notification.show_notification("Report exported successfully to USB Drive", "success", 3000)
        except PermissionError:
            self.notification.show_notification("Error found while exporting Failed", "error", 3000)
        except Exception as e:
            self.notification.show_notification("Error found while exporting Failed", "error", 3000)


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
        
        
        
    
    def append_row_and_save_csv(self, row_data):
        """Append a new row to the table with date and time, adjusted for IST, and save it to a CSV file."""
        row_index = self.table_widget.rowCount()
        self.table_widget.insertRow(row_index)

        # Calculate the current IST date and time (UTC + 5:30)
        current_utc = datetime.utcnow()
        ist_offset = timedelta(hours=5, minutes=30)
        current_ist = current_utc + ist_offset

        current_date = current_ist.strftime("%Y-%m-%d")  # Format: YYYY-MM-DD
        current_time = current_ist.strftime("%I:%M %p")  # Format: HH:MM AM/PM (12-hour format)

        # Insert date as the first column
        date_item = QTableWidgetItem(current_date)
        date_item.setTextAlignment(Qt.AlignCenter)
        date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
        self.table_widget.setItem(row_index, 0, date_item)

        # Insert time as the second column
        time_item = QTableWidgetItem(current_time)
        time_item.setTextAlignment(Qt.AlignCenter)
        time_item.setFlags(time_item.flags() & ~Qt.ItemIsEditable)
        self.table_widget.setItem(row_index, 1, time_item)

        # Add the remaining data to subsequent columns
        for col, value in enumerate(row_data, start=2):  # Start from the third column
            if isinstance(value, (int, float)):  # If value is a number, format it
                item = QTableWidgetItem(f"{value:.2f}")
            else:  # If value is not a number (e.g., id is a string)
                item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.table_widget.setItem(row_index, col, item)

        # Automatically save the table data to a CSV file
        self.save_table_to_csv()

    def save_table_to_csv(self):
        """Save the table data to a CSV file."""
        with open(self.csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write the header
            writer.writerow(self.parameters)

            # Write all rows
            for row in range(self.table_widget.rowCount()):
                row_data = [
                    self.table_widget.item(row, col).text()
                    if self.table_widget.item(row, col) else ""
                    for col in range(self.table_widget.columnCount())
                ]
                writer.writerow(row_data)
    def load_shift_values(self):
        """Load shift times from JSON files and convert them to QTime."""
        def load_time(file_path, key):
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    time_str = data.get(key, "00:00")  # Default to "00:00" if key doesn't exist
                    loaded_time = QTime.fromString(time_str, "hh:mm AP")  # Adjust format as per time representation
                    if loaded_time.isValid():
                        return loaded_time
            return QTime(0, 0)  # Default to midnight if file or key is missing

        # Load times for morning and evening shifts
        self.mrstj = load_time(self.MRST, "mr start")
        self.mrstj.toString('hh:mm AP')
       
        self.mrndj = load_time(self.MRND, "mr end ")
        self.mrndj.toString('hh:mm AP')
       
        self.evstj = load_time(self.EVST, "ev start")
        self.evstj.toString('hh:mm AP')
       
        self.evndj = load_time(self.EVND, "ev end ")
        self.evndj.toString('hh:mm AP')
        
        
    def load_csv_data(self):
        """Load data from the CSV file and display it in the table."""
        if os.path.exists(self.csv_file_path):
            with open(self.csv_file_path, mode='r') as file:
                reader = csv.reader(file)
                # Skip the header row
                next(reader, None)

                for row_data in reader:
                    row_index = self.table_widget.rowCount()
                    self.table_widget.insertRow(row_index)
                    for col, value in enumerate(row_data):
                        item = QTableWidgetItem(value)
                        item.setTextAlignment(Qt.AlignCenter)
                        # Make the cell non-editable
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                        self.table_widget.setItem(row_index, col, item)

       
        
            
    def DATE_filter_table(self):
        """Filter table data based on a date range."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Date Range")

        # Increase the dialog size
        dialog.resize(400, 200)  # Set the width and height of the dialog box

        layout = QVBoxLayout(dialog)

        # Style for QDateEdit
        date_edit_style = """
            QDateEdit {
                height: 40px; /* Increase height of the text box */
                font-size: 16px; /* Increase font size */
                padding: 5px; /* Add padding for better spacing */
            }
            QDateEdit::drop-down {
                width: 30px; /* Increase the size of the down arrow button */
            }
            QDateEdit::down-arrow {
                width: 20px; /* Width of the arrow itself */
                height: 20px; /* Height of the arrow itself */
            }
        """

        # Start date selector
        start_label = QLabel("Start Date:", dialog)
        start_date_edit = QDateEdit(dialog)
        start_date_edit.setCalendarPopup(True)
        start_date_edit.setDate(QDate.currentDate().addMonths(-1))  # Default to one month ago
        start_date_edit.setStyleSheet(date_edit_style)  # Apply style

        # Customize the calendar appearance
        self.customize_calendar(start_date_edit)

        # End date selector
        end_label = QLabel("End Date:", dialog)
        end_date_edit = QDateEdit(dialog)
        end_date_edit.setCalendarPopup(True)
        end_date_edit.setDate(QDate.currentDate())  # Default to today
        end_date_edit.setStyleSheet(date_edit_style)  # Apply style

        # Customize the calendar appearance
        self.customize_calendar(end_date_edit)
        def handle_OK_click():
            dialog.accept
            
            dialog.close()
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK", dialog)
        cancel_button = QPushButton("Cancel", dialog)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        # Connect buttons
        ok_button.clicked.connect(handle_OK_click)
        cancel_button.clicked.connect(dialog.reject)

        # Add widgets to layout
        layout.addWidget(start_label)
        layout.addWidget(start_date_edit)
        layout.addWidget(end_label)
        layout.addWidget(end_date_edit)
        layout.addLayout(button_layout)

        if dialog.exec_() == QDialog.Accepted:
            start_date = start_date_edit.date().toPyDate()
            end_date = end_date_edit.date().toPyDate()
            self.apply_date_filter(start_date, end_date)



    def customize_calendar(self, date_edit):
        """Customize the appearance of the calendar popup and ensure it is fully visible and centered."""
        calendar_widget = date_edit.calendarWidget()

        # Set custom styles for the calendar
        calendar_widget.setStyleSheet("""
            QCalendarWidget QToolButton {
                color: black; /* Black text for month and year */
                font-size: 16px; /* Increase font size */
                height: 40px; /* Larger buttons */
                width: 150px; /* Wider buttons */
            }
            QCalendarWidget QToolButton::menu-indicator { 
                subcontrol-origin: padding;
                subcontrol-position: bottom right; 
            }
            QCalendarWidget QSpinBox {
                font-size: 16px; /* Increase font size in spin boxes */
            }
            QCalendarWidget QAbstractItemView:enabled {
                font-size: 14px; /* Adjust font size for dates */
                color: black; /* Black date text */
                selection-background-color: #8ECAE6; /* Highlight color */
                selection-color: white; /* Selected text color */
            }
        """)

        def center_calendar_popup():
            """Ensure the calendar popup is always centered on the screen."""
            if calendar_widget:
                # Get the usable screen area
                screen_geometry = QApplication.primaryScreen().availableGeometry()
                calendar_geometry = calendar_widget.frameGeometry()

                # Calculate the position to center the calendar popup
                centered_x = (screen_geometry.width() - calendar_geometry.width()) // 2 + screen_geometry.left()
                centered_y = (screen_geometry.height() - calendar_geometry.height()) // 2 + screen_geometry.top()

                # Set the calendar widget to this centered position
                calendar_widget.move(centered_x, centered_y)

        # Hook into the show event of the calendar to adjust its position dynamically
        calendar_widget.showEvent = lambda event: (
            center_calendar_popup(), QCalendarWidget.showEvent(calendar_widget, event)
        )

        # Replace year navigation with a dropdown menu
        def setup_year_dropdown():
            """Set up a dropdown menu for year selection."""
            year_button = calendar_widget.findChild(QToolButton, "qt_calendar_yearbutton")
            if year_button:
                menu = QMenu(year_button)
                current_year = QDate.currentDate().year()

                # Populate the menu with the last 10 years
                for year in range(current_year - 4, current_year + 1):
                    action = QAction(str(year), menu)
                    action.triggered.connect(
                        lambda _, y=year: calendar_widget.setSelectedDate(
                            QDate(y, calendar_widget.selectedDate().month(), calendar_widget.selectedDate().day())
                        )
                    )
                    menu.addAction(action)

                # Set the dropdown menu
                year_button.setPopupMode(QToolButton.InstantPopup)
                year_button.setMenu(menu)
                year_button.setToolTip("Click to select a year")

        # Remove the default spin box navigation for years
        def disable_spinbox():
            """Disable the spin box for year navigation."""
            spinbox = calendar_widget.findChild(QSpinBox)
            if spinbox:
                spinbox.hide()

        # Apply modifications
        QTimer.singleShot(0, setup_year_dropdown)
        QTimer.singleShot(0, disable_spinbox)
        
    def apply_date_filter(self, start_date, end_date):
        """Filter the table rows based on the given date range."""
        filtered_rows = []

        # Collect the rows that fall within the date range
        for row in range(self.table_widget.rowCount()):
            date_item = self.table_widget.item(row, 0)  # Date is assumed to be in the first column
            if date_item:
                try:
                    row_date = datetime.strptime(date_item.text(), "%Y-%m-%d").date()
                    if start_date <= row_date <= end_date:
                        # Collect all data for this row without modification
                        row_data = [
                            self.table_widget.item(row, col).text()
                            if self.table_widget.item(row, col) else ""
                            for col in range(self.table_widget.columnCount())
                        ]
                        filtered_rows.append(row_data)
                except ValueError:
                    continue

        # Clear table and re-add only the filtered rows
        self.clear_table(save=False)  # Clear the table without saving
        for row_data in filtered_rows:
            self.add_original_row(row_data)

    def add_original_row(self, row_data):
        """Add a row to the table using the exact original data."""
        row_index = self.table_widget.rowCount()
        self.table_widget.insertRow(row_index)

        # Insert each original piece of data into the correct column
        for col, value in enumerate(row_data):
            item = QTableWidgetItem(value)
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make cells non-editable
            self.table_widget.setItem(row_index, col, item)          

    
            
     
 
