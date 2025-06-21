from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QEasingCurve, QPropertyAnimation, Qt,QPoint
from PyQt5.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout, QApplication, QLabel,QFrame
from PyQt5.QtGui import QColor,QPixmap

from Constants.MainNotification import Notification
import time
import os
import json

class UARTThread(QThread):
    data_received = pyqtSignal(str)

    def __init__(self, uart_control):
        super().__init__()
        self.uart_control = uart_control

    def run(self):
        while True:
            try:
                decoded_data, hex_data = self.uart_control.read_uart()
                if hex_data:
                    self.data_received.emit(hex_data)
                time.sleep(0.01)
            except Exception as e:
                print(f"Error reading UART data: {e}")

class HomeScreen(QWidget):
    def __init__(self, uart_control):
        super().__init__()
        self.setWindowTitle("Poornasree Equipments")
        self.setGeometry(300, 300, 800, 600)
        self.setStyleSheet("background-color: #FFFFFFFF;")
        self.notification = Notification(self)
        
        # Store uart_control reference
        self.uart_control = uart_control
        
        # Layouts
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.middle_layout = QHBoxLayout()
        self.middle_layout.setContentsMargins(0, 0, 0, 0)
        self.middle_layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.middle_layout.addWidget(self.stack, 3)
        self.main_layout.addLayout(self.middle_layout)
        self.setLayout(self.main_layout)

        # Initialize and display the dashboard immediately for faster perceived startup
        self.init_dashboard()
        self.stack.currentChanged.connect(self.on_widget_changed)

        # Defer all heavy initialization to improve startup time
        QTimer.singleShot(50, self.init_other_widgets_progressive)
        
        # Start UART thread after UI is ready
        QTimer.singleShot(100, self.start_uart_thread)

    def init_dashboard(self):
        """Initialize only the dashboard immediately"""
        from Screens.Dashboards.Dashboard import Dashboard
        self.dashboard = Dashboard(self)
        self.stack.addWidget(self.dashboard)
        self.stack.setCurrentWidget(self.dashboard)
        
        # Defer dashboard heavy operations
        QTimer.singleShot(500, self.dashboard.check_toggle_state)
        QTimer.singleShot(100, self.dashboard.load_parameter_status)

    def start_uart_thread(self):
        """Start UART thread after UI is ready"""
        self.uart_thread = UARTThread(self.uart_control)
        self.uart_thread.start()

    def init_other_widgets_progressive(self):
        """Initialize other widgets progressively to avoid blocking"""
        from Controls.uart_control import UARTcontrol
        self.uart = UARTcontrol()
        
        # Load widgets in stages for better performance
        QTimer.singleShot(50, self.load_reports)
        QTimer.singleShot(150, self.load_settings_batch1)
        QTimer.singleShot(250, self.load_settings_batch2)
        QTimer.singleShot(350, self.load_calibration_and_connect)

    def load_reports(self):
        """Load reports widget"""
        from Screens.List.dataList import DataList
        self.reports = DataList(self)
        self.stack.addWidget(self.reports)
        self.reports.start_usb_monitor()

    def load_settings_batch1(self):
        """Load first batch of settings"""
        from Screens.Settings.SettingsScreen import SettingsScreen
        from Screens.Settings.SettingsScreen2 import SettingsScreen2
        
        self.settings1 = SettingsScreen(self)
        self.settings2 = SettingsScreen2(self)
        self.stack.addWidget(self.settings1)
        self.stack.addWidget(self.settings2)

    def load_settings_batch2(self):
        """Load second batch of settings"""
        from Screens.Settings.SettingsScreen3 import SettingsScreen3
        from Screens.Settings.SettingsScreen4 import SettingsScreen4
        from Screens.Settings.parameter import ParameterSelectionPage
        
        self.settings3 = SettingsScreen3(self)
        self.settings4 = SettingsScreen4(self)
        self.parameters = ParameterSelectionPage(self)
        
        self.stack.addWidget(self.settings3)
        self.stack.addWidget(self.settings4)
        self.stack.addWidget(self.parameters)

    def load_calibration_and_connect(self):
        """Load calibration and connect all UART signals"""
        from Screens.Calibration.calibrationScreen import calibrationScreen
        self.calibrationScreen = calibrationScreen(self)
        self.stack.addWidget(self.calibrationScreen)
        
        # Connect UART signals after all widgets are loaded
        self.connect_uart_signals()
        
        # Start monitoring and initial commands
        self.dashboard.start_usb_monitor()
        self.uart.send_uart_hex("17 00")
        QTimer.singleShot(200, self.update_intfr)

    def connect_uart_signals(self):
        """Connect UART signals after all widgets are initialized"""
        if hasattr(self, 'uart_thread'):
            self.uart_thread.data_received.connect(self.request_data)
            self.uart_thread.data_received.connect(self.dashboard.update_dash1_labels)
            self.uart_thread.data_received.connect(self.settings1.update_slider)
            self.uart_thread.data_received.connect(self.settings2.update_measured_temp)
            self.uart_thread.data_received.connect(self.settings3.update_comp)
            self.uart_thread.data_received.connect(self.settings3.update_intfr_mode)
            self.uart_thread.data_received.connect(self.Success_Notification)
            self.uart_thread.data_received.connect(self.calibrationScreen.update_xdata)
            self.uart_thread.data_received.connect(self.reports.update_table)

    def on_widget_changed(self, index):
        """Called whenever the current widget changes in the stack."""
        current_widget = self.stack.widget(index)
        if current_widget == self.dashboard:
            self.dashboard.update_calibrated_values()

    def update_intfr(self):
        self.uart.send_uart_hex("32 00")
        QTimer.singleShot(200, self.settings3.set_initial_radio_button)

    def update_data(self):
        self.uart.send_uart_hex("10 00")

    def request_data(self, data):
        if data.startswith('40'):
            third_position_data = data[4:6]
            if third_position_data == '25':
                if self.stack.currentWidget() == self.dashboard:
                    self.update_data()

    def cleanup_and_quit(self):
        """Clean up resources and exit the application."""
        import RPi.GPIO as GPIO
        GPIO.cleanup()
        QApplication.quit()
        
    def Success_Notification(self, data):
        if data == "4003300073":
            self.notification.show_notification("Compensation Updated Successfully", "success", 3000)
        if data == "4003260065":
            self.notification.show_notification("INTFR mode Updated Successfully", "success", 3000)
        if data == "400318005B":
            self.notification.show_notification("Test Completed & Values Saved Successfully", "success", 3000)
        if data == "40030A0049":
            self.notification.show_notification("Saved Successfully", "success", 3000)
        if data == "40031A0059":
            self.notification.show_notification("Cleaning Completed", "success", 3000)
        if data == "40032A0069":
            self.notification.show_notification("Save Zero Success", "success", 3000)

if __name__ == "__main__":
    import sys
    from Controls.uart_control import UARTcontrol
    app = QApplication(sys.argv)
    uart_control = UARTcontrol()
    home_screen = HomeScreen(uart_control)
    home_screen.show()
    sys.exit(app.exec_())
