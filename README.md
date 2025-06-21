# PSR FTIR Qt5 Application

A PyQt5-based desktop application for Fourier Transform Infrared (FTIR) spectroscopy control and data acquisition. This application provides a touchscreen-friendly interface for operating FTIR equipment manufactured by Poornasree Equipments.

## Features

- **Full-Screen Kiosk Mode**: Optimized for 1024x600 touchscreen displays
- **UART Communication**: High-speed data communication with FTIR hardware (256000 baud)
- **GPIO Control**: Hardware interface control for Raspberry Pi
- **Real-time Data Processing**: Live data acquisition and processing
- **Calibration System**: Built-in calibration tools and procedures
- **Dashboard Interface**: User-friendly control panels and data visualization
- **Settings Management**: Configurable parameters and system settings
- **Optimized Performance**: Fast startup and responsive UI

## System Requirements

- **Operating System**: Linux (Raspberry Pi OS recommended) or Windows
- **Python**: 3.7+
- **Hardware**: 
  - Raspberry Pi 4 (recommended) or compatible computer
  - 1024x600 touchscreen display
  - UART-enabled FTIR hardware
  - GPIO pins for hardware control

## Dependencies

### Core Dependencies
- `PyQt5` - GUI framework
- `pyserial` - UART communication
- `RPi.GPIO` - GPIO control (for Raspberry Pi)

### Additional Python Packages
The application uses the following Python packages:
- `sys`, `os` - System operations
- `time` - Timing operations
- `json` - Configuration management
- `csv` - Data export functionality

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Pydart-Intelli-Corp/psr-ftir-qt5.git
cd psr-ftir-qt5
```

### 2. Install Dependencies
```bash
# Install PyQt5
pip install PyQt5

# Install serial communication
pip install pyserial

# For Raspberry Pi GPIO support
pip install RPi.GPIO
```

### 3. Prepare Resources
Generate the Qt resource file:
```bash
pyrcc5 resources.qrc -o resources_rc.py
```

## Running the Application

### Development Mode
```bash
python ftir_app_optimized.py
```

### Production Mode (Recommended)
For better performance, use the optimized version:
```bash
python ftir_app_optimized.py
```

## Building Executable

Create a standalone executable using PyInstaller:

### Basic Build
```bash
pyinstaller --onefile ftir_app_optimized.py
```

### With Resources (Recommended)
```bash
pyinstaller --onefile --add-data "resources_rc.py:." ftir_app_optimized.py
```

## Project Structure

```
ftir/
├── ftir_app.py              # Main application entry point
├── ftir_app_optimized.py    # Optimized main application
├── resources.qrc            # Qt resource file
├── resources_rc.py          # Generated resource module
├── Constants/               # UI constants and components
│   ├── Buttons/            # Custom button widgets
│   ├── containers/         # Container widgets
│   ├── Fonts/             # Application fonts
│   ├── icons/             # Icon resources
│   └── images/            # Image resources
├── Controls/               # Hardware control modules
│   ├── gpio_control.py    # GPIO interface control
│   └── uart_control.py    # UART communication
├── Screens/               # Application screens
│   ├── HomeScreen.py      # Main application screen
│   ├── Calibration/       # Calibration screens
│   ├── Dashboards/        # Data visualization screens
│   ├── List/             # List management screens
│   └── Settings/         # Configuration screens
└── README.md             # This file
```

## Configuration

### UART Settings
Default UART configuration in `Controls/uart_control.py`:
- **Port**: `/dev/serial0` (Linux) 
- **Baud Rate**: 256000
- **Timeout**: 0.1 seconds

### Display Settings
The application is optimized for:
- **Resolution**: 1024x600 pixels
- **Mode**: Full-screen kiosk mode
- **Touch**: Touchscreen compatible

## Hardware Interface

### UART Communication Protocol
The application uses a custom protocol for FTIR hardware communication:
- **Start Byte**: 0x40
- **Length Byte**: Number of data bytes + 1
- **Command/Data**: Hex formatted commands
- **LRC Check**: XOR checksum for data integrity

### GPIO Interface
GPIO pins are used for:
- Hardware control signals
- Status indicators
- Emergency controls

## Performance Optimizations

The application includes several performance optimizations:

1. **Lazy Loading**: Heavy components are loaded only when needed
2. **Deferred Initialization**: Background initialization to improve startup time
3. **Optimized UART**: Reduced initialization delays
4. **Efficient Threading**: Background threads for data acquisition

## Troubleshooting

### Common Issues

1. **UART Connection Failed**
   - Check hardware connections
   - Verify port permissions: `sudo usermod -a -G dialout $USER`
   - Ensure correct port in configuration

2. **GPIO Permission Errors**
   - Run with sudo: `sudo python ftir_app_optimized.py`
   - Or add user to gpio group: `sudo usermod -a -G gpio $USER`

3. **Display Issues**
   - Verify display resolution settings
   - Check Qt5 installation
   - Ensure proper graphics drivers

### Debug Mode
Enable debug output by running:
```bash
QT_LOGGING_RULES="*.debug=true" python ftir_app_optimized.py
```

## Development

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add comments for complex logic
- Update documentation for new features

## License

This project is proprietary software developed by Poornasree Equipments for FTIR spectroscopy applications.

## Support

For technical support and inquiries:
- **Company**: Poornasree Equipments
- **Development**: Pydart Intelli Corp

## Version History

- **Current**: Optimized version with performance improvements
- **Previous**: Initial Qt5 implementation

---

**Note**: This application is designed specifically for FTIR spectroscopy equipment and requires compatible hardware for full functionality.
