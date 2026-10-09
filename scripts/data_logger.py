import serial
import time
import csv
import os

COM_PORT = 'COM11'
BAUD_RATE = 115200

# *** תיקון: ה-ESP32 שולח חצי מ-BUFFER_SIZE אחרי חישוב ה-FFT ***
BUFFER_SIZE = 256
NUM_BINS = BUFFER_SIZE // 2  # 128 תאים

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

            # כותרות לפי כמות התדרים (128 עמודות)
            headers = ["Timestamp"] + [f"Freq_Bin_{i}" for i in range(NUM_BINS)]
            writer.writerow(headers)
            file.flush()

            while True:
                if ser.in_waiting > 0:
                    raw_line = ser.readline().decode('utf-8', errors='ignore').strip()

                    # סינון שורות ריקות
                    if not raw_line:
                        continue

                    # --- DEBUG lines from the firmware (I2C success/fail stats) ---
                    if raw_line.startswith("DEBUG:"):
                        print(f"[FIRMWARE STATS] {raw_line}")
                        continue

                    data_points = raw_line.split(',')

                    # *** תיקון: בודקים התאמה ל-128 ערכים ***
                    if len(data_points) == NUM_BINS:
                        try:
                            float_values = [float(val) for val in data_points]

                            # *** תיקון: איפוס תדר 0 (כוח המשיכה) כדי לא ללכלך את ה-Dataset ***
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