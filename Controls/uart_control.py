import serial
import time
import csv

# Constants for UART communication
SERIAL_PORT = '/dev/serial0'  # Update with the correct port if necessary
BAUD_RATE = 256000

class UARTcontrol:
    def __init__(self):
        self.init_uart()

    def init_uart(self):
        """Initialize UART communication with optimized startup."""
        try:
            if hasattr(self, 'serial_conn') and self.serial_conn.is_open:
                self.serial_conn.close()
        except AttributeError:
            pass  # self.serial_conn was not defined yet

        self.serial_conn = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        # Reduced wait time for faster startup - increased from 2s to 0.5s
        time.sleep(0.5)  # Minimal wait for UART to establish
        self.serial_conn.reset_input_buffer()

    def send_uart_hex(self, cmd_data):
        """
        Send command and data over UART.
        - cmd_data: A string containing the command and data in Hex format, e.g., "25 00 05".
        This will be converted to: 40 04 25 00 05 64 and sent over UART.
        """
        # Convert the input command and data into a list of bytes
        cmd_data_bytes = bytes.fromhex(cmd_data.replace(" ", ""))
        
        # Calculate the length byte (number of command and data bytes)
        length_byte = len(cmd_data_bytes) + 1  # +1 to include the command byte itself

        # Create the full message starting with 0x40, length, and cmd_data
        full_message = [0x40, length_byte] + list(cmd_data_bytes)
        
        # Calculate the LRC (XOR of all bytes in the full_message)
        lrc = 0
        for byte in full_message:
            lrc ^= byte
        
        # Append the LRC to the message
        full_message.append(lrc)
        
        # Convert the list of integers to a byte array for sending over UART
        full_message_bytes = bytes(full_message)
        
        # Send the full message over UART
        self.serial_conn.write(full_message_bytes)
        
        # Display sent data in Hex format
        hex_str = ' '.join(f'{b:02X}' for b in full_message)
    
          
    def send_uart_ascii(self, data, is_hex=False):
        """Send data over UART as ASCII or Hex."""
        self.serial_conn.write(data.encode())
        
    def send_csv(self, csv_string):
        """
        Send a CSV string over UART in chunks, without including the filename.
        """
        chunk_size = 256  # Define chunk size
        for i in range(0, len(csv_string), chunk_size):
            chunk = csv_string[i:i + chunk_size]
            self.send_uart_ascii(chunk)  # Send each chunk over UART
            time.sleep(0.1)  # Optional delay between chunks


    def read_uart(self):
        """Read data from UART and return ASCII and Hex format if available."""
        try:
            if self.serial_conn.in_waiting > 0:
                # Read the first byte to determine the delay
                first_byte = self.serial_conn.read(1)
                first_byte_hex = first_byte.hex().upper()

                # Set sleep time based on the first byte
                if first_byte_hex == "40":
                    sleep_time = 0.01
                else:
                    sleep_time = 1  # Default sleep time

                # Sleep based on determined delay
                time.sleep(sleep_time)

                # Read the remaining bytes
                remaining_data = self.serial_conn.read(self.serial_conn.in_waiting)
                received_data = first_byte + remaining_data  # Combine first byte with the rest

                if received_data:
                    # Print the first byte information
             

                    try:
                        # Try to decode the data as ASCII
                        decoded_data = received_data.decode('utf-8').strip()
                        hex_data = received_data.hex().upper()
                        return decoded_data, hex_data
                    except UnicodeDecodeError:
                        # If decoding as ASCII fails, store the data as Hex
                        hex_data = received_data.hex().upper()
                        return None, hex_data
        except Exception as e:
            print(f"Error: {str(e)}")
        return None, None



    def close(self):
        """Close UART connection."""
        if self.serial_conn.is_open:
            self.serial_conn.close()
