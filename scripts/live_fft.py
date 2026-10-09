import serial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ==========================================
# Configuration - adjust to match your setup
# ==========================================
COM_PORT = 'COM11'
BAUD_RATE = 115200
NUM_BINS = 128          # BUFFER_SIZE / 2 from the firmware

# Approximate sample rate of the accelerometer loop (samples/sec).
# Based on your DEBUG stats, the nominal loop delay is 10ms -> ~100Hz,
# but actual rate varies with I2C retries. Adjust this if you measure
# a different average from elapsed_ms in your DEBUG lines.
SAMPLE_RATE_HZ = 100.0
BUFFER_SIZE = NUM_BINS * 2  # 256, must match firmware BUFFER_SIZE

# Frequency resolution and axis (only positive-frequency half is sent)
freq_axis = np.fft.fftfreq(BUFFER_SIZE, d=1.0 / SAMPLE_RATE_HZ)[:NUM_BINS]


def read_valid_magnitude_line(ser):
    """Read lines from serial until we get one that's a valid magnitude row
    (exactly NUM_BINS comma-separated floats). Ignores DEBUG:, classification
    text, and any other console prints from the firmware."""
    while True:
        raw_line = ser.readline().decode('utf-8', errors='ignore').strip()
        if not raw_line:
            return None  # timeout, no data right now

        if raw_line.startswith("DEBUG:") or raw_line.startswith("Classification") \
                or raw_line.startswith("  ") or raw_line.startswith("Skipping") \
                or raw_line.startswith("WARNING") or raw_line.startswith("!!!"):
            continue

        parts = raw_line.split(',')
        if len(parts) != NUM_BINS:
            continue

        try:
            values = [float(v) for v in parts]
            return values
        except ValueError:
            continue


def main():
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {COM_PORT}. Waiting for FFT windows...")

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(freq_axis, np.zeros(NUM_BINS), width=(freq_axis[1] - freq_axis[0]) * 0.9)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Magnitude")
    ax.set_title("Live Motor Vibration Spectrum (FFT)")
    ax.set_ylim(0, 5000)  # adjust based on your typical magnitude range

    def update(frame):
        values = read_valid_magnitude_line(ser)
        if values is None:
            return bars

        magnitudes = np.array(values)

        # Auto-scale y-axis to the current window, with a little headroom
        current_max = magnitudes.max()
        if current_max > 0:
            ax.set_ylim(0, current_max * 1.2)

        for bar, h in zip(bars, magnitudes):
            bar.set_height(h)

        return bars

    ani = animation.FuncAnimation(fig, update, interval=50, blit=False, cache_frame_data=False)
    plt.tight_layout()
    plt.show()

    ser.close()


if __name__ == '__main__':
    main()