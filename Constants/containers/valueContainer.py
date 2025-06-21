from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame
from PyQt5.QtGui import QFontDatabase, QFont, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal


class CustomContainer(QWidget):
    
    label_text_changed = pyqtSignal(str)  # Signal to notify label text change
    
    def __init__(self, label_text, container_name, background_color="rgba(0, 0, 0, 0.7)", 
                 container_size=(120, 120), font_path="", content_font_size=20, 
                 name_font_size=12, icon_path="", content_position="below", border_radius=10, 
                 border_color="rgba(0, 0, 0, 0.0)", border_width=2):
        super().__init__()
        
        # Initialize label_text
        self._label_text = label_text

        # Load the custom font, if provided
        if font_path:
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                custom_font = QFont(font_family)
            else:
                custom_font = self.font()  # Use default if font fails to load
        else:
            custom_font = self.font()  # Use default font if no path is provided

        # Set up the main layout for the widget
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)  # Center the entire layout (content + name)

        # Create a frame for the container with a border radius and a border
        box = QFrame(self)
        box.setFixedSize(container_size[0], container_size[1])

        # Set the unified background color, border radius, and border
        box.setStyleSheet(f"""
            background-color: {background_color};
            border-radius: {border_radius}px;
            border: {border_width}px solid {border_color};
        """)

        # Create a layout for the container content
        box_layout = QVBoxLayout(box)
        box_layout.setAlignment(Qt.AlignTop)  # Align content to the top inside the container

        # Add a horizontal layout for the top row (icon + name + content label)
        top_layout = QVBoxLayout()  # Using vertical layout for icon, name, and content
        top_layout.setAlignment(Qt.AlignCenter)  # Center all elements horizontally

        # Add the icon if provided
        if icon_path:
            icon_label = QLabel(box)
            pixmap = QPixmap(icon_path).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
            icon_label.setStyleSheet("background: none; border: none; margin-left: -20px;")  # Make the icon fully transparent
            top_layout.addWidget(icon_label)

        # Create a label for the name
        name_label = QLabel(container_name)
        name_label.setAlignment(Qt.AlignCenter)

        # Apply custom font or default font
        name_font = QFont(custom_font)
        name_font.setPointSize(name_font_size)  # Set font size for name
        name_font.setBold(True)  # Make the font bold
        name_label.setFont(name_font)  # Apply bold font

        # Simplify the stylesheet to ensure visibility
        name_label.setStyleSheet(f"""
            color: white;  /* Set text color to white */
            background-color: {background_color};
            margin-left: -50px;
        """)

        # Add the name label to the top layout
        top_layout.addWidget(name_label)

        # Add the top layout to the box layout
        box_layout.addLayout(top_layout)

        # Add a spacer to push the content to the bottom
        box_layout.addStretch()  # Push the next item to the bottom

        # Add a label inside the container for content at the bottom
        self.content_label = QLabel(self._label_text, box) 
        self.content_label.setAlignment(Qt.AlignCenter)
        self.content_label.setStyleSheet(f"border: none; color: white; background: none; margin-bottom: 20px;") 
        content_font = QFont(custom_font)
        content_font.setPointSize(content_font_size)  
        self.content_label.setFont(content_font)  
        
        # Add the content label to the box layout at the bottom
        box_layout.addWidget(self.content_label, alignment=Qt.AlignBottom)  # Align the label at the bottom

        # Set the main layout for the widget
        self.setLayout(main_layout)

    @property
    def label_text(self):
        return self._label_text

    @label_text.setter
    def label_text(self, value):
        self._label_text = value
        self.content_label.setText(value)  # Update the label text
        self.label_text_changed.emit(value)  # Emit the signal when label changes
        self.update()

    def update_label(self, new_text):
        self.label_text = new_text  # This will automatically update the content label


# Example of how to call CustomContainer with a unified background color
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    # Create an instance of CustomContainer with a unified background color
    container = CustomContainer(
        label_text="Content",
        container_name="My Container",
        background_color="rgba(0, 0, 0, 0.7)",  # Light blue with 80% opacity for all background elements
        container_size=(150, 150),
        font_path="",  # Remove or set path to the custom font
        content_font_size=40,  # Set the desired font size for content
        name_font_size=20,  # Increased font size for name for better visibility
        icon_path="",  # Path to the icon
        border_radius=15,  # Border radius
        border_color="rgba(0, 0, 0, 0.5)",  # Transparent border with 50% opacity
        border_width=2,  # Width of the border
        content_position="below"  # Option to set content below or beside the icon
    )

    container.show()
    sys.exit(app.exec_())
