import threading
import RPi.GPIO as GPIO 

class GPIOController:
    def __init__(self):
        self.pwm = None  # Initialize PWM attribute
        # Defer GPIO setup to avoid blocking during initialization
        self.gpio_initialized = False
        threading.Thread(target=self.setup_gpio, daemon=True).start()

    def setup_gpio(self):
        """Setup GPIO in background thread for faster startup"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(19, GPIO.OUT)  # Mode selection bit 1
            GPIO.setup(20, GPIO.OUT)  # Mode selection bit 2
            GPIO.setup(16, GPIO.OUT)  # LED 1
            GPIO.setup(12, GPIO.OUT)  # LED 2
            GPIO.setup(21, GPIO.OUT)  # GPIO 21 for PWM wave            # Initial state
            GPIO.output(19, GPIO.LOW)
            GPIO.output(20, GPIO.LOW)
            GPIO.output(16, GPIO.LOW)
            GPIO.output(12, GPIO.LOW)
            
            self.gpio_initialized = True

        except Exception as e:
            print(f"GPIO setup failed: {e}")
            self.gpio_initialized = False

    def set_mode(self, mode):
        """
        Sets the mode based on a 2-bit binary input (00, 01, 10, or 11).
        Turns on LEDs based on the mode:
        - 00: Both LEDs off
        - 01: LED 1 on, LED 2 off
        - 10: LED 1 off, LED 2 on
        - 11: Both LEDs on
        """
        # Wait for GPIO to be initialized if not ready
        if not self.gpio_initialized:
            return
            
        try:
            if mode == "00":
                GPIO.output(19, GPIO.LOW)
                GPIO.output(20, GPIO.LOW)
                GPIO.output(16, GPIO.LOW)
                GPIO.output(12, GPIO.LOW)
            elif mode == "01":
                GPIO.output(19, GPIO.LOW)
                GPIO.output(20, GPIO.HIGH)
                GPIO.output(16, GPIO.HIGH)
                GPIO.output(12, GPIO.LOW)
            elif mode == "10":
                GPIO.output(19, GPIO.HIGH)
                GPIO.output(20, GPIO.LOW)
                GPIO.output(16, GPIO.LOW)
                GPIO.output(12, GPIO.HIGH)
            elif mode == "11":
                GPIO.output(19, GPIO.HIGH)
                GPIO.output(20, GPIO.HIGH)
                GPIO.output(16, GPIO.HIGH)
                GPIO.output(12, GPIO.HIGH)
        except Exception as e:
            print(f"GPIO operation failed: {e}")

    def start_wave(self, frequency=500, duration=None):
        """
        Starts a PWM wave at the specified frequency (default 500 Hz) on GPIO 21.
        If a duration is provided, the wave stops automatically after that duration.
        
        :param frequency: Frequency of the PWM wave (default is 500 Hz).
        :param duration: Duration in seconds to run the wave. If None, wave runs indefinitely.
        """
        try:
            # If a PWM object exists, stop it before creating a new one
            if self.pwm is not None:
                print("Stopping existing PWM instance.")
                self.stop_wave()

            self.pwm = GPIO.PWM(21, frequency)
            self.pwm.start(50)  # 50% duty cycle
            print(f"Started PWM wave at {frequency} Hz.")

            # If duration is specified, stop the wave after the duration
            if duration is not None:
                threading.Timer(duration, self.stop_wave).start()

        except Exception as e:
            print(f"Error starting PWM wave: {e}")

    def stop_wave(self):
        """
        Stops the PWM wave on GPIO 21 if running.
        """
        if self.pwm:
            try:
                self.pwm.stop()
                self.pwm = None
                print("PWM wave stopped.")
            except Exception as e:
                print(f"Error stopping PWM wave: {e}")

    def cleanup(self):
        """
        Cleans up all GPIO settings.
        """
        if self.pwm:
            self.stop_wave()
        GPIO.cleanup()
        print("GPIO cleaned up.")
