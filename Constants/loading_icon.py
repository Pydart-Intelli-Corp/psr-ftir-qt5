# loading_icon.py

from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap, QTransform
from PyQt5.QtCore import QTimer, Qt

class LoadingIcon:
    def __init__(self, size=60, interval=100, parent=None):
        """Initialize the loading icon with the specified size and rotation interval."""
        self.label_loading = QLabel(parent)
        self.label_loading.setAlignment(Qt.AlignCenter)

        # Load and scale the pixmap
        self.pixmap = QPixmap(":/Constants/icons/psrloading.png").scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_loading.setFixedSize(self.pixmap.size())

        # Rotation logic
        self.rotation_angle = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate_image)
        self.timer.start(interval)

    def rotate_image(self):
        """Rotate the image by a fixed angle and update the QLabel."""
        self.rotation_angle += 10
        if self.rotation_angle >= 360:
            self.rotation_angle = 0
        self.update_loading_image()

    def update_loading_image(self):
        """Apply the rotation transformation to the pixmap and update the QLabel."""
        transform = QTransform().rotate(self.rotation_angle)
        rotated_pixmap = self.pixmap.transformed(transform, Qt.SmoothTransformation)
        self.label_loading.setPixmap(rotated_pixmap)
        self.label_loading.setFixedSize(self.pixmap.size())

    def get_loading_label(self):
        """Return the QLabel that contains the loading icon."""
        return self.label_loading
