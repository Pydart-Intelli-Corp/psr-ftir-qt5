from PyQt5.QtWidgets import  QVBoxLayout, QWidget, QLabel,QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,QMessageBox, QScrollArea,  QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPainter, QImage, QFontDatabase, QFont, QFontMetrics,QIcon
from PyQt5.QtCore import Qt,QSettings,QTimer,pyqtSignal
from Constants.Buttons.save_green_button import SaveGreenButton
from Constants.MainNotification import Notification
from Controls.gpio_control import GPIOController
from Controls.uart_control import UARTcontrol
import csv
import os
import re
import glob
import json
import resources_rc

def natural_sort_key(s):
        """Helper function to sort strings with numbers in natural order."""
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]
class calibrationScreen(QWidget):
    CONFIG_FILE = "calibration_values.json"
    notify_title_bar = pyqtSignal(str, str, str, str, str)
    

    def __init__(self, text: str, parent=None, uart_thread=None):
        super().__init__(parent=parent)
        self.setWindowState(Qt.WindowFullScreen)
        self.uart_thread = uart_thread
        self.previous_row_saved = True
        self.uart = UARTcontrol()
        self.notification=Notification(self)

        self.initUI()
        self.load_settings()
        self.calbration_result= None
        
        

    def initUI(self):
        main_layout = QVBoxLayout(self)

        # Load custom font
        font_id = QFontDatabase.addApplicationFont(":/Constants/Fonts/JosefinSans-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else 'Arial'
        spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        main_layout.addSpacerItem(spacer)

        # Add heading label
        self.heading_label = QLabel("CALIBRATION", self)
        self.heading_label.setContentsMargins(90, 0, 0, 0)
        font = QFont(font_family, 13, QFont.Bold)
        self.createnew= False
        self.x_data= False
        self.x_path="X_data.csv"
        self.FcalibrationScreen=False
        
      

        self.heading_label.setFont(font)
        self.heading_label.setStyleSheet("color: black; font-weight: bold;")
        main_layout.addWidget(self.heading_label)
        spacer = QSpacerItem(50, 50, QSizePolicy.Minimum, QSizePolicy.Fixed)
        main_layout.addSpacerItem(spacer)
        self.file_dropdown = QComboBox(self)
        self.file_dropdown.hide()  # Hide the dropdown initially
        self.file_dropdown.currentIndexChanged.connect(self.on_dropdown_selection)  # Connect selection event
        main_layout.addWidget(self.file_dropdown)
        

        # Populate the dropdown with available CSV files
        self.populate_csv_files() # Populate dropdown with available Y_data CSV files


        # Load background image
        image_path = ":/Constants/images/settingsbg.png"
        self.original_image = QImage(image_path)
        if not self.original_image.isNull():
            self.background_image = self.original_image.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Define all parameter headings
        parameters = [
            "Fat", "SNF", "CLR", "Protein", "Lactose", "Salts",
            "Water", "Temp","Urea", "Maltodextrin", "Sucrose", "Ammonium Sulphate", "Glucose",
            "Sorbitol", "Melamin", "Starch", "Sodium Citrate",
            "Sodium Carbonate", "Sodium Bicarbonate", "Chemical Emulsifiers", "Hydrogen Peroxide", "Vegitable Oil", "Detergents", "Formalin"
        ]

        # Create a table widget for parameters, set as scrollable
        self.table_widget = QTableWidget(1, len(parameters), self)  # 1 row, columns based on parameters
        self.table_widget.setHorizontalHeaderLabels(parameters)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)  # Allows for custom column widths
        
        # Set column widths based on text length
        font_metrics = QFontMetrics(font)
        for i, parameter in enumerate(parameters):
            column_width = font_metrics.horizontalAdvance(parameter) + 20  # Add padding
            self.table_widget.setColumnWidth(i, column_width)

        # Add editable cells under each parameter heading
        for i in range(1, len(parameters)):
            item = QTableWidgetItem("0")  # Default value; editable cell
            item.setTextAlignment(Qt.AlignCenter)  # Center-align text in each cell
            self.table_widget.setItem(0, i, item)

        # Enable horizontal scroll bar for the table widget
        self.table_widget.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)

        # Set up a scroll area for the table
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.table_widget)
        scroll_area.setStyleSheet("""
        QScrollBar:vertical {
            width: 15px;  /* Increase vertical scroll bar width */
        }
        QScrollBar:horizontal {
            height: 15px; /* Increase horizontal scroll bar height */
        }
        QScrollBar::handle:vertical {
            background: #8c8c8c; /* Color of the scroll bar handle */
            min-height: 30px; /* Minimum height of the handle */
        }
        QScrollBar::handle:horizontal {
            background: #8c8c8c; /* Color of the scroll bar handle */
            min-width: 30px; /* Minimum width of the handle */
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            background: none; /* Hide the arrows */
        }
    """)

        
        # Scroll control buttons

    
        # Add scroll area and buttons to main layout
        main_layout.addWidget(scroll_area)
       
        self.make_saved_cells_non_editable()
        self.setLayout(main_layout)
        self._button(
            name="", icon_path=":/Constants/icons/setprev.png",
            action=lambda *args: self.goto_settings(),
            x=10, y=10, width=90, height=60,
            visible=True, bg_color="rgba(60, 179, 113, 0.0)"
        )
        self.button(name=" Load", icon_path=":/Constants/icons/load.png", action=lambda *args: self.show_dropdown(),x=280,y=20, width=90, height=40,visible=True,bg_color="rgba(32, 123, 130, 1)")
        self.button(name=" Create", icon_path=":/Constants/icons/create.png", action=lambda *args: self.create_new_table(),x=390,y=20, width=110, height=40,visible=True,bg_color="rgba(3, 131, 3, 1)")
        self.button(name=" New(L)", icon_path=":/Constants/icons/newline.png", action=lambda *args: self.add_new_row(),x=520,y=20, width=90, height=40,visible=True,bg_color="rgba(5, 11, 92, 0.8)")
        self.button(name=" Save(0)", icon_path=":/Constants/icons/savezero.png", action=lambda *args: self.SaveZero(),x=630,y=20, width=100, height=40,visible=True,bg_color="rgba(32, 123, 130, 1)")
        self.button(name=" Save", icon_path=":/Constants/icons/save_.png", action=lambda *args: self.save_table_to_csv(),x=750,y=20, width=90, height=40,visible=True,bg_color="rgba(3, 131, 3, 1)")
        self.button(name=" Calibrate", icon_path=":/Constants/icons/calibrate_.png", action=lambda *args: self.calibration_set(),x=860,y=20, width=125, height=40,visible=True,bg_color="rgba(26, 5, 114, 1)")
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
    def goto_settings(self):
        
        self.parent().setCurrentIndex(2)
 

        
    

    def populate_csv_files(self):
        """Populate the dropdown with available CSV files starting with 'Y_data' in natural order."""
        try:
            # Get CSV files starting with 'Y_data' and sort them naturally
            csv_files = sorted(
                [f for f in os.listdir() if f.startswith("Y_data") and f.endswith(".csv")],
                key=natural_sort_key
            )
            if not csv_files:
                raise FileNotFoundError("No CSV files found starting with 'Y_data'.")

            self.file_dropdown.addItems(csv_files)
        except Exception as e:
            self.notification.show_notification("Error finding CSV files", "error", 3000)
          

    def show_dropdown(self):
        """Show the dropdown list when the Load button is clicked, refreshing the list each time."""
        self.file_dropdown.clear()  # Clear current items
        self.populate_csv_files()   # Refresh the list of CSV files
        self.file_dropdown.show()
        self.file_dropdown.showPopup()
        

        # Set a timer to hide the dropdown after 10 seconds, only if no selection is made
        def hide_if_no_selection():
                if self.file_dropdown.currentIndex() == -1:  # Check if no item is selected
                    self.file_dropdown.hide()

        QTimer.singleShot(10000, hide_if_no_selection)  # Hide after 10 seconds

    def on_dropdown_selection(self):
        """Hide the dropdown and load the selected CSV file."""
        self.file_dropdown.setStyleSheet("QComboBox { color: green; }")
       
        self.load_selected_csv_data()
        
    def load_selected_csv_data(self):
        """Load the data from the selected CSV file and display it in the table."""
        file_path = self.file_dropdown.currentText()
        if not file_path:
            return

        try:
            # Update self.x_path based on the selected file
            # Extract the suffix from the selected file
            if file_path.startswith("Y_data") and file_path.endswith(".csv"):
                suffix = file_path[6:-4]  # Extract the part between 'Y_data' and '.csv'
                self.x_path = f"X_data{suffix}.csv"  # Construct the new file path

            # Clear any existing rows in the table
            self.table_widget.setRowCount(0)

            # Open the CSV file and read data
            with open(file_path, mode="r") as file:
                reader = csv.reader(file)
                for row_data in reader:
                    row_index = self.table_widget.rowCount()
                    self.table_widget.insertRow(row_index)

                    # Populate each cell in the row
                    for col_index, cell_data in enumerate(row_data):
                        item = QTableWidgetItem(cell_data)
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                        self.table_widget.setItem(row_index, col_index, item)

           
        except Exception as e:
            self.notification.show_notification("Error Loading file", "error", 3000)

   
    def create_new_table(self):
        """Clears all rows from the table widget and renames specific files with unique names if they exist."""
        self.table_widget.setRowCount(0)
        self.createnew= True
        self.x_path="X_data.csv"
        self.FcalibrationScreen=True
        

        def get_unique_filename(filename):
            """Generate a unique filename by appending an incrementing number if needed."""
            base, ext = os.path.splitext(filename)
            counter = 1
            new_filename = f"{base}{counter}{ext}"

            while os.path.exists(new_filename):
                counter += 1
                new_filename = f"{base}{counter}{ext}"

            return new_filename

        # Define the original file paths
        files_to_rename = ["X_data.csv", "Y_data.csv"]
        files_exist = any(os.path.exists(file) for file in files_to_rename)

        # Rename each file if it exists
        if files_exist:
            for old_file in files_to_rename:
                if os.path.exists(old_file):
                    new_file = get_unique_filename(old_file)
                    os.rename(old_file, new_file)
                    print(f"Renamed {old_file} to {new_file}")

        # Call add_new_row() in both cases
        self.previous_row_saved = True
        self.add_new_row()
        self.previous_row_saved = False
        



    def save_table_to_csv(self):
        self.previous_row_saved = True
        

        """Append new rows to Y_data.csv if they don't already exist and print the contents."""
        if self.createnew:
            file_path = "Y_data.csv"
            self.x_path = "X_data.csv"
        else:
            file_path = self.file_dropdown.currentText()
            if not file_path:
                file_path = "Y_data.csv"  # Default to "Y_data.csv" if no file is selected

        # Read existing data into a set of tuples for comparison (if file exists)
        existing_rows = set()
        try:
            with open(file_path, mode="r") as file:
                reader = csv.reader(file)
                for row in reader:
                    existing_rows.add(tuple(row))  # Store rows as tuples for easy comparison
        except FileNotFoundError:
            pass  # No existing rows to check if the file doesn't exist
        
        if self.x_data:
            new_rows_added = False
        
            try:
                with open(file_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    # Append only new rows to the file
                    for row in range(self.table_widget.rowCount()):
                        row_data = [
                            self.table_widget.item(row, col).text() if self.table_widget.item(row, col) and self.table_widget.item(row, col).text() != ""
                            else "0"
                            for col in range(self.table_widget.columnCount())
                        ]
                        row_tuple = tuple(row_data)
                        if row_tuple not in existing_rows:
                            writer.writerow(row_data)
                            new_rows_added = True

                if new_rows_added:
                    
                    self.notification.show_notification("Saved Successfully", "success", 3000)
              
                    self.createnew = False
                    self.previous_row_saved = True
                else:
                    self.notification.show_notification("Failed to save data", "error", 3000)
                    

                # Make cells non-editable
                for row in range(self.table_widget.rowCount()):
                    for col in range(self.table_widget.columnCount()):
                        item = self.table_widget.item(row, col)
                        if item is not None:
                            item.setFlags(item.flags() & ~Qt.ItemIsEditable)

                # Check if there are other files matching "Y_data*.csv" (excluding "Y_data.csv")
                y_data_files = glob.glob("Y_data*.csv")
                other_y_files_exist = len([f for f in y_data_files if f != "Y_data.csv"]) > 0

                # Swap contents only if there are other Y_data*.csv files
                if os.path.exists(file_path) and other_y_files_exist:
                    with open(file_path, mode="r") as file:
                        file_path_data = file.readlines()
                    with open("Y_data.csv", mode="r") as y_file:
                        y_data = y_file.readlines()

                    # Swap contents
                    with open(file_path, mode="w") as file:
                        file.writelines(y_data)
                    with open("Y_data.csv", mode="w") as y_file:
                        y_file.writelines(file_path_data)
                elif not os.path.exists("Y_data.csv"):
                    with open("Y_data.csv", mode="w", newline='') as y_file:
                        with open(file_path, mode="r") as file:
                            y_file.writelines(file.readlines())

                # Swap contents of x_path and X_data.csv if both files exist
                if os.path.exists(self.x_path) and os.path.exists("X_data.csv"):
                    with open(self.x_path, mode="r") as x_file:
                        x_path_data = x_file.readlines()
                    with open("X_data.csv", mode="r") as x_data_file:
                        x_data = x_data_file.readlines()

                    # Swap contents
                    with open(self.x_path, mode="w") as x_file:
                        x_file.writelines(x_data)
                    with open("X_data.csv", mode="w") as x_data_file:
                        x_data_file.writelines(x_path_data)
                        
                elif not os.path.exists("X_data.csv"):
                    with open("X_data.csv", mode="w", newline='') as x_data_file:
                        with open(self.x_path, mode="r") as x_file:
                            x_data_file.writelines(x_file.readlines())
                self.x_path="X_data.csv"
                        
            

            except Exception as e:
                print(f"Error saving to CSV: {e}")
                self.show_error_alert("Could not save the table to a CSV file.")
            self.x_data = False

            



    def show_error_alert(self, message):
        """Display an error alert with a custom message."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        
    def show_success_alert(self, message):
        """Display a success alert with a custom message."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Success")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

        
    def add_new_row(self):
        self.FcalibrationScreen=True
        
        command = f"0F 00"
   
        
        """Adds a new editable row to the table widget if the previous row was saved."""
        if not self.previous_row_saved:
            self.notification.show_notification("Please save the current row before adding a new one.", "error", 3000)
            return
        
        # Insert a new row at the end
        current_row_count = self.table_widget.rowCount()
        self.table_widget.insertRow(current_row_count)

        # Set each cell in the new row to be editable
        for col in range(self.table_widget.columnCount()):
            item = QTableWidgetItem("")  # Empty item
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table_widget.setItem(current_row_count, col, item)
            self.uart.send_uart_hex(command)

        # Reset the flag since the new row needs to be saved
        self.previous_row_saved = False
            
         
   
            

   
        
    def make_saved_cells_non_editable(self):
        """Set saved cells as non-editable."""
        for row in range(self.table_widget.rowCount()):
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                if item:
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
    def show_save_alert(self):
        """Display an alert confirming that settings were saved."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Save Confirmation")
        msg.setText("Settings have been saved successfully.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    def SaveZero(self, *args):
        

        command = f"2A 00"
   
        self.uart.send_uart_hex(command)
      
        





   

    def update_xdata(self, data):
        # Check if the first two characters are '41'
        if data.startswith('41'):
            # Extract the data at the 3rd position (index 4:6)
            third_position_data = data[6:8]
            if self.FcalibrationScreen:
                # Check if the data at the 3rd position is '0F'
                if third_position_data == '0F':
                    # Split the data after the 3rd position (from index 8 onwards), excluding the last two characters (LRC)
                    relevant_data = data[8:-2]
                
                    # Split the relevant data into groups of 4 characters each (2-byte hex values)
                    split_data = [relevant_data[i:i+4] for i in range(0, len(relevant_data), 4)]
                
                    # Convert each 4-character hex group (LSB-MSB) to decimal with byte order correction
                    decimal_data = []
                    for byte_pair in split_data:
                        if len(byte_pair) == 4:
                            # Swap the LSB and MSB: "34" and "56" -> "5634"
                            swapped_hex = byte_pair[2:] + byte_pair[:2]
                            try:
                                decimal_value = int(swapped_hex, 16)  # Convert swapped hex to decimal
                                decimal_data.append(decimal_value)
                            except ValueError:
                                # Append None if there's a conversion error
                                decimal_data.append(None)

                
                    # Check if decimal_data contains all expected values
                    if len(decimal_data) != 1027:
                        print("Warning: The number of data points does not match the expected count of 1027.")
                        self.notification.show_notification("Failed to Save X data", "error", 3000)
                    
                    # Append new data in a new row if the file already exists
                    try:
                        with open(self.x_path, mode="a", newline="") as file:  # Use 'a' mode for appending
                            writer = csv.writer(file)
                            writer.writerow(decimal_data)  # Append new data as a new row
                        print("Data appended successfully to X_data.csv with the latest values.")
                        self.notification.show_notification("X Data Appended Successfully", "success", 3000)
                        self.x_data= True


                        # Overwrite the incoming data in X_new.csv
                        with open("X_new.csv", mode="w", newline="") as file:
                            writer = csv.writer(file)
                            writer.writerow(decimal_data)  # Overwrite data as a new row each tim.e
                        print("Data saved successfully to X_new.csv with the latest values.")
                        self.notification.show_notification("X Data Read Successfully", "success", 3000)
                        self.x_data= True
                        self.FcalibrationScreen=False

                
                                
                    except Exception as e:
                        print(f"Error saving data to X_data.csv: {e}")
                        self.notification.show_notification("Failed to Save X data", "error", 3000)
            else:
                pass



                
    def load_settings(self):
        """Load the saved values from settings storage into the table."""
        settings = QSettings("Poornasree", "MiraScan")
        
        # Load table data
        row_count = settings.beginReadArray("calibrationTable")
        self.table_widget.setRowCount(0)  # Clear existing rows
        
        for row in range(row_count):
            self.table_widget.insertRow(row)  # Insert a new row
            settings.setArrayIndex(row)
            for col in range(self.table_widget.columnCount()):
                value = settings.value(f"col{col}", "0")  # Default to "0" if no value
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_widget.setItem(row, col, item)
        settings.endArray()

    def closeEvent(self, event):
        self.save_settings()  # Ensure settings are saved on exit
        super().closeEvent(event)

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
    def scroll_table(self, amount):
        """Scrolls the table widget horizontally by a specified amount of pixels."""
        current_scroll = self.table_widget.horizontalScrollBar().value()
        self.table_widget.horizontalScrollBar().setValue(current_scroll + amount)

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
        
    def save_calibration_json(self):
        self.calibration_result = (
            3.14, 12.7, 22.7, 5.89, 18.3, 23.14, 7.65, 29.4, 31.7, 16.8,
            9.03, 25.6, 17.1, 14.2, 8.75, 26.9, 11.5, 19.4, 28.3, 24.8,
            6.5, 30.1, 20.9, 15.7, 12.4, 9.8, 27.3, 22.1, 18.6, 7.3,
            13.7, 31.9, 16.4, 10.2, 28.7, 5.4, 21.8, 14.6, 8.3, 30.5,
            19.7, 23.8, 17.9, 6.1, 9.5, 27.4, 11.2, 29.3, 25.7, 13.1
        )

        # Names list (50 total)
        names = [
            "fat", "snf", "clr", "protein", "lactose", "salt", "water", "temp",
            "urea", "maltodextrin", "sucrose", "ammonium_SO4", "glucose", "sorbitol",
            "melamine", "starch", "sodium_citrate", "sodium_carbonate", "sodium_bicarbonate", "chemical_emulsifiers",
            "hydrogen_peroxide", "veg_oil", "detergents", "formalin", "vitaminB12", "riboflavin",
            "niacin", "thiamine", "biotin", "folic_acid", "pantothenic_acid",
            "iodine", "selenium", "manganese", "cobalt", "chromium", "fluoride",
            "molybdenum", "aluminum", "arsenic", "cadmium", "lead", "mercury",
            "boron", "nickel", "vanadium", "antimony", "barium", "bismuth", "gold"
        ]

        # Assign one value to each name
        data = {name: value for name, value in zip(names, self.calibration_result)}

        # Save to JSON file
        try:
            with open(self.CONFIG_FILE, 'w') as file:
                json.dump(data, file, indent=4)
        except IOError as e:
            print(f"Error saving calibration data: {e}")
            
    def calibration_set(self):
        
        try:
            self.save_calibration_json()
            self.notification.show_notification("Calibration Success", "success", 3000)
       
        except Exception as e:
            self.notification.show_notification("Calibration Failed", "Error", 3000)

       