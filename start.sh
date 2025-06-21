#!/bin/bash
# FTIR Application Startup Script for 1024x600 full screen display

# Set display
export DISPLAY=:0

# Set Qt environment variables for consistent display
export QT_QPA_PLATFORM=xcb
export QT_SCALE_FACTOR=1
export QT_AUTO_SCREEN_SCALE_FACTOR=0

# Set screen resolution (if xrandr is available)
if command -v xrandr &> /dev/null; then
    # Try to set 1024x600 resolution
    xrandr --output HDMI-1 --mode 1024x600 2>/dev/null || \
    xrandr --output HDMI-2 --mode 1024x600 2>/dev/null || \
    xrandr --output VGA-1 --mode 1024x600 2>/dev/null || \
    echo "Could not set 1024x600 resolution, using current resolution"
fi

# Log startup
echo "Starting FTIR application at $(date) with 1024x600 resolution" > /tmp/ftir-app.log
echo "DISPLAY=$DISPLAY" >> /tmp/ftir-app.log
echo "QT_QPA_PLATFORM=$QT_QPA_PLATFORM" >> /tmp/ftir-app.log

# Change to application directory
cd /opt/ftir

# Start application (redirecting output to log)
python3 /opt/ftir/ftir_app.py >> /tmp/ftir-app.log 2>&1
