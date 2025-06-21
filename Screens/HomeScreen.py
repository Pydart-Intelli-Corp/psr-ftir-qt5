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
        
        # Set up for 1024x600 full screen display
        self.setGeometry(0, 0, 1024, 600)
        self.setFixedSize(1024, 600)
        
        # Set window flags for full screen kiosk mode
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        
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

        # Initialize dashboard immediately but defer heavy initialization
        self.initialize_dashboard()
        
        # Defer all other initialization to after the UI is shown
        QTimer.singleShot(50, self.initialize_other_widgets)
        
        # Defer UART thread startup
        QTimer.singleShot(100, self.start_uart_thread)

    def initialize_dashboard(self):
        """Initialize only the dashboard immediately for faster startup"""
        from Screens.Dashboards.Dashboard import Dashboard
        self.dashboard = Dashboard(self)
        self.stack.addWidget(self.dashboard)
        self.stack.setCurrentWidget(self.dashboard)
        
        # Defer dashboard initialization
        QTimer.singleShot(200, self.dashboard.check_toggle_state)
        QTimer.singleShot(300, self.dashboard.load_parameter_status)
        
        self.stack.currentChanged.connect(self.on_widget_changed)

    def start_uart_thread(self):
        """Start UART thread after UI is initialized"""
        self.uart_thread = UARTThread(self.uart_control)
        self.uart_thread.start()

    def initialize_other_widgets(self):
        """Initialize other widgets after the dashboard is displayed."""
        # Import only when needed
        from Screens.Settings.SettingsScreen3 import SettingsScreen3
        from Screens.Settings.SettingsScreen4 import SettingsScreen4
        from Screens.Settings.SettingsScreen2 import SettingsScreen2
        from Screens.Settings.SettingsScreen import SettingsScreen
        from Screens.Calibration.calibrationScreen import calibrationScreen
        from Screens.List.dataList import DataList
        from Screens.Settings.parameter import ParameterSelectionPage
        from Controls.uart_control import UARTcontrol
        
        self.uart = UARTcontrol()        # Initialize widgets progressively
        QTimer.singleShot(50, self.init_reports)
        QTimer.singleShot(100, self.init_settings)
        QTimer.singleShot(150, self.init_calibration)
        QTimer.singleShot(200, self.connect_uart_signals)

    def init_reports(self):
        """Initialize reports widget"""
        from Screens.List.dataList import DataList
        self.reports = DataList(self)
        self.stack.addWidget(self.reports)
        self.reports.start_usb_monitor()

    def init_settings(self):
        """Initialize settings widgets"""
        from Screens.Settings.SettingsScreen3 import SettingsScreen3
        from Screens.Settings.SettingsScreen4 import SettingsScreen4
        from Screens.Settings.SettingsScreen2 import SettingsScreen2
        from Screens.Settings.SettingsScreen import SettingsScreen
        from Screens.Settings.parameter import ParameterSelectionPage
        
        self.settings1 = SettingsScreen(self)
        self.settings2 = SettingsScreen2(self)
        self.settings3 = SettingsScreen3(self)
        self.settings4 = SettingsScreen4(self)
        self.parameters = ParameterSelectionPage(self)
        
        self.stack.addWidget(self.settings1)
        self.stack.addWidget(self.settings2)
        self.stack.addWidget(self.settings3)
        self.stack.addWidget(self.settings4)
        self.stack.addWidget(self.parameters)

    def init_calibration(self):
        """Initialize calibration widget"""
        from Screens.Calibration.calibrationScreen import calibrationScreen
        self.calibrationScreen = calibrationScreen(self)
        self.stack.addWidget(self.calibrationScreen)

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
        
        self.dashboard.start_usb_monitor()
        self.uart.send_uart_hex("17 00")
        QTimer.singleShot(300, self.update_intfr)
  


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
            self.notification.show_notification("Compensation Updated Successfully", "success", 3000),
              
               
        if data == "4003260065":
              
                self.notification.show_notification("INTFR mode Updated Successfully", "success", 3000),
                
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
