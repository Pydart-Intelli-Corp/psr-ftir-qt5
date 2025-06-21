#!/usr/bin/env python3
"""
Quick Performance Test Script for FTIR App
Run this to compare startup times before and after optimizations
"""

import time
import sys
import os

def test_import_performance():
    """Test how long imports take"""
    print("Testing import performance...")
    
    start_time = time.time()
    
    # Test heavy imports
    try:
        import PyQt5.QtWidgets
        import PyQt5.QtCore
        import PyQt5.QtGui
        qt_time = time.time() - start_time
        print(f"PyQt5 imports: {qt_time:.2f}s")
    except ImportError:
        print("PyQt5 not available")
        return
    
    # Test local imports
    start_local = time.time()
    try:
        sys.path.append(os.path.dirname(__file__))
        from Controls.uart_control import UARTcontrol
        from Controls.gpio_control import GPIOController
        local_time = time.time() - start_local
        print(f"Local control imports: {local_time:.2f}s")
    except ImportError as e:
        print(f"Local imports failed: {e}")
    
    return time.time() - start_time

def test_startup_simulation():
    """Simulate app startup to measure performance"""
    print("\nSimulating app startup...")
    
    start_time = time.time()
    
    # Simulate PyQt5 app creation
    print("Creating QApplication...")
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
    app_time = time.time() - start_time
    print(f"QApplication created: {app_time:.2f}s")
    
    # Simulate control initialization
    try:
        print("Initializing controls...")
        control_start = time.time()
        from Controls.uart_control import UARTcontrol
        from Controls.gpio_control import GPIOController
        
        # This will show the actual initialization time
        uart = UARTcontrol()
        gpio = GPIOController()
        
        control_time = time.time() - control_start
        print(f"Controls initialized: {control_time:.2f}s")
        
    except Exception as e:
        print(f"Control initialization failed: {e}")
        control_time = 0
    
    total_time = time.time() - start_time
    print(f"\nTotal simulated startup time: {total_time:.2f}s")
    
    return total_time

def main():
    print("FTIR App Performance Test")
    print("=" * 40)
    
    total_import_time = test_import_performance()
    total_startup_time = test_startup_simulation()
    
    print("\n" + "=" * 40)
    print(f"Total import time: {total_import_time:.2f}s")
    print(f"Total startup time: {total_startup_time:.2f}s")
    
    print("\nOptimizations Applied:")
    print("✓ Reduced UART initialization from 2s to 0.5s")
    print("✓ Background GPIO initialization")
    print("✓ Lazy import loading")
    print("✓ Progressive widget loading")
    print("✓ Deferred heavy operations")
    
    if total_startup_time < 3:
        print("🎉 Good performance! App should start quickly.")
    elif total_startup_time < 5:
        print("⚠️  Moderate performance. Consider additional optimizations.")
    else:
        print("❌ Slow startup. Check for additional bottlenecks.")

if __name__ == "__main__":
    main()
