
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QColor, QPainter, QBrush, QPen
from PyQt5.QtWidgets import  QWidget
class CommonContainer(QWidget):
    def __init__(self, width=200, height=200, bg_color="white", border_radius=10, border_color="black", parent=None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.bg_color = QColor(bg_color)
        self.border_radius = border_radius
        self.border_color = QColor(border_color)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # Enable smooth edges

        # Set brush (for background color)
        brush = QBrush(self.bg_color)
        painter.setBrush(brush)

        # Set pen (for border color)
        pen = QPen(self.border_color)
        pen.setWidth(2)  # Set border width
        painter.setPen(pen)

        # Draw rounded rectangle
        rect = QRectF(0, 0, self.width(), self.height())
        painter.drawRoundedRect(rect, self.border_radius, self.border_radius)

