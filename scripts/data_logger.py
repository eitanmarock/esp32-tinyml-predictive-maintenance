import serial
import time
import csv
import os

COM_PORT = 'COM11'
BAUD_RATE = 115200

# *** Fix: the ESP32 sends half of BUFFER_SIZE after computing the FFT ***
BUFFER_SIZE = 256
NUM_BINS = BUFFER_SIZE // 2  # 128 bins

def log_data():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_dir, 'motor_vibration_data.csv')

        ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=2)
        print(f"Connected to {COM_PORT}. Waiting for complete windows...")
        print(f"File will be saved directly to: {csv_file_path}")

        last_row_time = None

        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)

            # Headers based on the number of frequency bins (128 columns)
            headers = ["Timestamp"] + [f"Freq_Bin_{i}" for i in range(NUM_BINS)]
            writer.writerow(headers)
            file.flush()

            while True:
                if ser.in_waiting > 0:
                    raw_line = ser.readline().decode('utf-8', errors='ignore').strip()

                    # Filter out empty lines
                    if not raw_line:
                        continue

                    # --- DEBUG lines from the firmware (I2C success/fail stats) ---
                    if raw_line.startswith("DEBUG:"):
                        print(f"[FIRMWARE STATS] {raw_line}")
                        continue

                    data_points = raw_line.split(',')

                    # *** Fix: check that we got exactly 128 values ***
                    if len(data_points) == NUM_BINS:
                        try:
                            float_values = [float(val) for val in data_points]

                            # *** Fix: zero out bin 0 (gravity / DC) so it doesn't pollute the dataset ***
                            float_values[0] = 0.0

                            now = time.time()
                            row_to_save = [now] + float_values
                            writer.writerow(row_to_save)
                            file.flush()

                            if last_row_time is not None:
                                gap = now - last_row_time
                                print(f"Logged 1 window at {time.strftime('%H:%M:%S')} "
                                      f"(gap since last row: {gap:.2f}s)")
                            else:
                                print(f"Logged 1 window at {time.strftime('%H:%M:%S')} (first row)")
                            last_row_time = now

                        except ValueError:
                            print("Warning: Received malformed text row, skipping...")
                    else:
                        print(f"Skipped line: Got {len(data_points)} points instead of {NUM_BINS} "
                              f"(raw preview: {raw_line[:60]!r})")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    log_data()
