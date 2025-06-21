import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, Qt
import resources_rc
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        return os.path.join(os.path.abspath("."), relative_path)

def initialize_app():
    """Initialize the application with lazy loading for faster startup"""
    # Import only when needed
    from Controls.uart_control import UARTcontrol
    from Screens.HomeScreen import HomeScreen
    
    uart_control = UARTcontrol()
    home_screen = HomeScreen(uart_control)
    
    # Set window flags for full screen kiosk mode
    home_screen.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
    
    # Set the window to full screen at 1024x600 resolution
    home_screen.setGeometry(0, 0, 1024, 600)
    home_screen.setFixedSize(1024, 600)
    home_screen.showFullScreen()
    
    return home_screen

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application properties for full screen display
    app.setAttribute(Qt.AA_DisableWindowContextHelpButton, True)
    
    # Get the primary screen and set it to 1024x600 if possible
    screen = app.primaryScreen()
    if screen:
        print(f"Available screen size: {screen.size().width()}x{screen.size().height()}")
    
    # Use QTimer to defer heavy initialization to after app starts
    def delayed_init():
        home_screen = initialize_app()
        # Store reference to prevent garbage collection
        app.home_screen = home_screen
    
    QTimer.singleShot(0, delayed_init)
    
    # Start the event loop
    sys.exit(app.exec_())