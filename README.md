# ESP32 TinyML Predictive Maintenance

Real-time vibration monitoring for a DC motor on an **ESP32-S3**. The system samples an MPU6050 accelerometer over I2C, computes a 256-point FFT on-chip, and classifies the motor state with a **TinyML** model (Edge Impulse). It runs fully at the edge, with no cloud. A dual-core **FreeRTOS** architecture keeps sampling deterministic while the heavy processing runs on the other core.

Embedded Systems course project, Ariel University (2026).

---

## How It Works

```
MPU6050 ──I2C──► Core 0: sampling task ──queue──► Core 1: FFT + TinyML ──► LEDs / motor cut-off
 (X-axis)        100 Hz, double buffer             128 magnitude bins        UART: results + spectrum
```

- **Core 0 (`core0_sampling_task`, priority 5):** reads the X-axis acceleration at ~100 Hz into a ping-pong buffer of 2 × 256 samples. When a buffer is full, its index is sent to Core 1 through a FreeRTOS queue.
- **Core 1 (`core1_processing_task`, priority 4):** runs a radix-2 Cooley-Tukey FFT (`calculate_fft`, written from scratch), converts the result to 128 magnitude bins, and feeds them to the Edge Impulse classifier.
- **Decision logic (`classify_motor_state`):**

| "Normal" score | Status | Action |
|---|---|---|
| ≥ 80% | Normal | Green LED |
| 60–80% | Degrading | Orange LED + UART warning |
| < 60% | Fault | Red LED + **emergency stop**: motor PWM duty is set to 0, and the MOSFET cuts motor current |

**Timing:** one 256-sample window takes about 2.56 s to collect. FFT and inference take about 10 ms, so Core 1 is idle almost all the time.

## Fault Model

| State | Dominant frequency | How it was produced |
|---|---|---|
| Normal | ≈ 35 Hz | Motor with a small balanced weight |
| Anomaly | ≈ 20 Hz | Asymmetric weight added to simulate a mechanical fault |

Sampling at 100 Hz gives a Nyquist limit of 50 Hz and a resolution of 100 / 256 ≈ **0.39 Hz per bin**, which separates the two states clearly.

## Hardware

| Component | Role | Pins |
|---|---|---|
| ESP32-S3 | Dual-core Xtensa LX7 MCU, 240 MHz | |
| MPU6050 | Accelerometer, I2C @ 100 kHz, address `0x68` | SDA 44, SCL 43 |
| IRLZ44N | Logic-level MOSFET for motor switching (PWM 5 kHz, 8-bit) | GPIO 12 |
| Flyback diode | Protects the MOSFET from inductive spikes | |
| LEDs | Green / orange / red status | GPIO 18 / 17 / 21 |
| DC motor | With removable balanced / asymmetric weight | |

## Repository Structure

```
├── main/
│   ├── main.cpp              # Application: tasks, FFT, classification, drivers
│   ├── CMakeLists.txt
│   ├── idf_component.yml
│   └── edge_ai_model/
│       ├── model-parameters/ # Model metadata (exported from Edge Impulse)
│       └── tflite-model/     # Trained, quantized model
├── scripts/
│   ├── data_logger.py        # Captures FFT frames from UART into CSV
│   └── live_fft.py           # Live spectrum plot over serial
├── data/
│   ├── motor_vibration_normal.csv
│   └── motor_vibration_anomaly.csv
├── CMakeLists.txt
├── sdkconfig
└── dependencies.lock
```

### Dataset format

Each row is one FFT window: a `Timestamp` column (Unix time) followed by `Freq_Bin_0` … `Freq_Bin_127` (magnitudes, 0.39 Hz per bin). The normal file contains 101 windows and the anomaly file contains 96.

## Building

1. Install **ESP-IDF** and set the target: `idf.py set-target esp32s3`
2. Export the **C++ library** of the model from Edge Impulse and copy its `edge-impulse-sdk/` folder into `main/edge_ai_model/`. The SDK is not included in this repo because of its size.
3. `idf.py build flash monitor`

On boot the firmware starts the motor, waits for it to stabilize, and runs a sensor health check (`WHO_AM_I` must read 104, Z-axis at rest about 16,000). Then it starts sampling.

## Engineering Challenges

1. **Burned MOSFET:** turning off the inductive motor produced a voltage spike above the MOSFET's 55 V rating. Diagnosed with a Multisim simulation and an oscilloscope, and fixed with a flyback diode.
2. **Sensor returning all zeros:** the MPU6050's internal 8 MHz RC oscillator was unstable under the motor's conducted noise. Fixed with a full reset and by switching the clock source to the gyro PLL (`PWR_MGMT_1 = 0x01`).
3. **Race condition and spectral leakage:** an earlier single-buffer and semaphore design let Core 0 overwrite samples while Core 1 was still reading them, which created false frequencies in the spectrum. Fixed with double buffering and a FreeRTOS queue.

## Limitations

- X-axis only, because of RAM and real-time constraints
- Detects frequencies up to 50 Hz (100 Hz sampling)
- Two-class model (normal vs. asymmetric weight)

## Tools

ESP-IDF · FreeRTOS · C/C++ · Edge Impulse · Python · NI Multisim

## Authors

Eitan Marock & Rebecca Pinto
