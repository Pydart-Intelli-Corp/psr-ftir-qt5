import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QCoreApplication
import resources_rc

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        return os.path.join(os.path.abspath("."), relative_path)

def initialize_app():
    """Initialize the application with optimized loading for faster startup"""
    # Import only when needed to reduce initial load time
    from Controls.uart_control import UARTcontrol
    from Screens.HomeScreen import HomeScreen
    
    # Show splash/loading indicator immediately
    print("Loading FTIR Application...")
    QCoreApplication.processEvents()
    
    # Initialize UART in background thread or defer it
    uart_control = UARTcontrol()
    
    # Create and show home screen
    home_screen = HomeScreen(uart_control)
    home_screen.showFullScreen()
    home_screen.show()
    
    return home_screen

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Show the application window immediately, then initialize heavy components
    def delayed_init():
        home_screen = initialize_app()
        # Store reference to prevent garbage collection
        app.home_screen = home_screen
    
    # Use timer with 0 delay to defer initialization until after event loop starts
    QTimer.singleShot(0, delayed_init)
    
    # Start the event loop
    sys.exit(app.exec_())
