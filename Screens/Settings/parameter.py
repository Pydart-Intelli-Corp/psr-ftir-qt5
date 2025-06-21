import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QCheckBox, QSpacerItem, QSizePolicy, 
    QHBoxLayout, QScrollArea, QGroupBox, QDialog,QFrame
)

from Constants.MainNotification import Notification

class ParameterSelectionPage(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Parameter Selection")
        self.resize(400, 600)
        self.notification = Notification(self)

        # Define the default parameters
        self.items = [
            "fat_P", "snf_P", "clr_P", "protein_P", "salt_P", "lactose_P", "water_P", "temp_P",
            "urea_P", "maltodextrin_P", "sucrose_P", "ammonium_SO4_P", "glucose_P", "sorbitol_P",
            "melamine_P", "starch_P", "sodium_citrate_P", "sodium_carbonate_P", "sodium_bicarbonate_P", 
            "chemical_emulsifiers_P", "hydrogen_peroxide_P", "veg_oil_P", "detergents_P", "formalin_P",
            "z1_P", "z2_P", "z3_P", "z4_P", "z5_P", "z6_P", "z7_P", "z8_P", "z9_P", "z10_P", "z11_P", 
            "z12_P", "z13_P", "z14_P", "z15_P", "z16_P", "z17_P", "z18_P", "z19_P", "z20_P", "z21_P", 
            "z22_P", "z23_P", "z24_P", "z25_P", "z26_P"
        ]

        # Load the status from the JSON file
        self.item_status = {item: "HIDE" for item in self.items}
        try:
            with open("parameter_status.json", "r") as json_file:
                self.item_status = json.load(json_file)
                print("Loaded parameter status from JSON.")
        except FileNotFoundError:
            print("No existing parameter status file found, initializing defaults.")
            # Default: first 16 items as "VIEW", the rest as "HIDE"
            self.item_status = {item: "VIEW" if i < 24 else "HIDE" for i, item in enumerate(self.items)}
            

        self.check_boxes = {}
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)

        # Add a heading
        heading_label = QLabel("Parameter List", self)
        heading_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333333;")
        layout.addWidget(heading_label)

        # Scroll area for the parameters
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        group_box = QGroupBox()
        group_layout = QVBoxLayout(group_box)

        # Add items with checkboxes
        for item in self.items:
            display_name = item.replace("_P", "")  # Remove _P from the display name

            # Create a horizontal layout for each item
            item_layout = QHBoxLayout()

            # Add the label for the item
            label_widget = QLabel(display_name, self)
            label_widget.setStyleSheet("font-size: 16px; color: black;")
            item_layout.addWidget(label_widget)

            # Add a spacer to separate label and checkbox
            spacer = QSpacerItem(30, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
            item_layout.addItem(spacer)

            # Add the checkbox
            check_box = QCheckBox(self)
            check_box.setChecked(self.item_status.get(item) == "VIEW")
            self.check_boxes[item] = check_box
            item_layout.addWidget(check_box)

            # Add the item layout to the group layout
            group_layout.addLayout(item_layout)

            # Add a horizontal separator
            separator = QFrame(self)
            separator.setFrameShape(QFrame.HLine)
            separator.setFrameShadow(QFrame.Sunken)
            group_layout.addWidget(separator)

        scroll_area.setWidget(group_box)
        layout.addWidget(scroll_area)

        # Buttons at the bottom (Apply and Close)
        button_layout = QHBoxLayout()

        # Apply button
        apply_button = QPushButton("Apply", self)
        apply_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        apply_button.clicked.connect(self.save_selections)
        apply_button.clicked.connect(lambda: self.notification.show_notification("Changes Applied Successfully", "success", 3000))
        button_layout.addWidget(apply_button)

        # Close button
        close_button = QPushButton("Close", self)
        close_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                background-color: #f44336;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        close_button.clicked.connect(self.save_and_close)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)



    def save_and_close(self):
        """Save the selections to the JSON file and close the dialog."""
       
        self.parent().setCurrentIndex(5)
        self.accept()

    def save_selections(self):
        """Save the item statuses to a JSON file."""
        for item, check_box in self.check_boxes.items():
            self.item_status[item] = "VIEW" if check_box.isChecked() else "HIDE"

        with open("parameter_status.json", "w") as json_file:
            json.dump(self.item_status, json_file, indent=4)

        print("Selections saved to parameter_status.json")


