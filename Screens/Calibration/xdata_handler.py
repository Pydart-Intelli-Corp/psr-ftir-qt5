import csv
import re

class Notification:
    """A simple notification handler."""
    @staticmethod
    def show_notification(message, level, duration):
        print(f"[{level.upper()}] {message} (duration: {duration}ms)")

class X_data_Handler:
    def __init__(self, x_path):
        # Flag that indicates if we are in the calibration screen
        self.FcalibrationScreen = True
        self.x_path = x_path
        self.x_data = False  # Indicates if the data has been updated/appended
        self.notification = Notification()  # You can replace this with your actual notification handler

    def update_xdata(self, data):
        """
        Processes incoming X calibration data in hex format and appends it to a CSV file.
        
        Steps:
        - Verifies that the data string starts with '41'.
        - Checks if the data at the 3rd position (6:8) equals '0F' when in calibration mode.
        - Extracts the relevant data, splits it into 2-byte groups (LSB-MSB),
          swaps the order to MSB-LSB, and converts each to a decimal value.
        - Verifies the total number of expected data points (1027) and issues a warning if not.
        - Writes the data to both an existing CSV file (appending) and overwrites another CSV.
        - Resets calibration mode upon successful data processing.
        """
        # Check if the first two characters are '41'
        if data.startswith('41'):
            # Extract the data at the 3rd position (index 6 to 8)
            third_position_data = data[6:8]
            if self.FcalibrationScreen:
                # Check if the data at the 3rd position is '0F'
                if third_position_data == '0F':
                    # Extract all relevant data after index 8 up to, but not including, the last two characters (LRC)
                    relevant_data = data[8:-2]

                    # Split the data into groups of 4 characters each (representing two bytes)
                    split_data = [relevant_data[i:i+4] for i in range(0, len(relevant_data), 4)]
                    
                    decimal_data = []
                    for byte_pair in split_data:
                        if len(byte_pair) == 4:
                            # Swap LSB and MSB. For instance, if byte_pair is "3456", it becomes "5634"
                            swapped_hex = byte_pair[2:] + byte_pair[:2]
                            try:
                                decimal_value = int(swapped_hex, 16)  # Convert swapped hex to decimal
                                decimal_data.append(decimal_value)
                            except ValueError:
                                # On conversion error, append None to maintain data structure alignment
                                decimal_data.append(None)

                    # Validate the number of data points against the expected count
                    if len(decimal_data) != 1027:
                        warning_message = (
                            "Warning: The number of data points does not match the expected count of 1027."
                        )
                        print(warning_message)
                        self.notification.show_notification("Failed to Save X data", "error", 3000)
                        return  # Early exit if the data is not valid

                    # Try to append the data to the main CSV file and overwrite the X_new CSV file
                    try:
                        # Append the data as a new row in the main CSV file
                        with open(self.x_path, mode="a", newline="") as file:
                            writer = csv.writer(file)
                            writer.writerow(decimal_data)
                        print("Data appended successfully to X_data.csv with the latest values.")
                        self.notification.show_notification("X Data Appended Successfully", "success", 3000)
                        self.x_data = True

                        # Overwrite the X_new.csv file with the new data
                        with open("X_new.csv", mode="w", newline="") as file:
                            writer = csv.writer(file)
                            writer.writerow(decimal_data)
                        print("Data saved successfully to X_new.csv with the latest values.")
                        self.notification.show_notification("X Data Read Successfully", "success", 3000)
                        self.x_data = True

                        # Exit calibration mode once the data is successfully updated
                        self.FcalibrationScreen = False

                    except Exception as e:
                        error_message = f"Error saving data to CSV files: {e}"
                        print(error_message)
                        self.notification.show_notification("Failed to Save X data", "error", 3000)
        else:
            print("Data does not start with the expected header '41'.")
