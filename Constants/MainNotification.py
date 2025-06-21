from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, Qt,QPoint,QTimer
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QLabel,QFrame

from Controls.gpio_control import GPIOController
import time


class Notification(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set the window as frameless and with a transparent background
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setStyleSheet("background: transparent;")
        self.setFixedSize(800, 100)
        self.controller = GPIOController()

        # Label to display the notification message
        self.label = QLabel("", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("margin: 10px; color: white; font-weight: bold;")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # Initially hide the notification
        self.hide()

    def show_notification(self, message, notification_type="success", duration=3000):
        """
        Display the notification with a message and type.

        :param message: The notification message to display
        :param notification_type: Type of notification ('success' or 'error')
        :param duration: Duration in milliseconds before hiding the notification
        """
        self.label.setText(message)
        
        

        # Apply styles based on notification type
        

        if notification_type == "success":
            self.controller.start_wave(frequency=650, duration=0.2)
            
            QTimer.singleShot(500, lambda: self.setStyleSheet(
                "background-color: rgba(3, 131, 3, .7); "
                "border: 2px solid green; border-radius: 10px;"
            ))  # Clear style after 500ms
        elif notification_type == "error":
            self.controller.start_wave(frequency=650, duration=0.3)
           
            QTimer.singleShot(500, lambda:  self.setStyleSheet(
                "background-color: rgba(255, 0, 0, 0.7); "
                "border: 2px solid red; border-radius: 10px;"
            ))  # Clear style after 500ms
        # Position at the center-top of the parent widget
        if self.parent():
            parent_geometry = self.parent().geometry()
            x = (parent_geometry.width() - self.width()) // 2
            y = 20  # Offset from the top
            self.move(x, y)

        # Show and bring the notification to the front
        self.show()
        self.raise_()

        # Slide down animation from the top
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(1000)
        self.animation.setStartValue(QPoint(self.x(), -self.height()))  # Off-screen at top
        self.animation.setEndValue(QPoint(self.x(), 20))  # 20px below the top edge
        self.animation.setEasingCurve(QEasingCurve.OutBounce)
        self.animation.start()

        # Schedule the notification to slide out and hide after the duration
        QTimer.singleShot(duration, self.hide_notification)

    def hide_notification(self):
        """
        Slide the notification out to the top and hide it.
        """
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(500)
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(QPoint(self.x(), -self.height()))  # Slide out to the top
        self.animation.setEasingCurve(QEasingCurve.InQuad)
        self.animation.finished.connect(self.hide)
        self.animation.start() 
        
  